import {
  fetchGetMessages,
  fetchAddMessage,
  fetchGetSessions,
  fetchAddSession,
  fetchDeleteSession,
  fetchUpdateSession
} from "@/api/ai-interface";

// Controls the abort for the current message polling (recreated on every send message, old one discarded)
let pollAbortController = null;

export const namespaced = true;

export const state = {
  userInfo: null,
  chatIsVisible: false,
  sessions: [],
  messages: [],
  currentSession: null,
  isLoading: false,
  toolCalls: null,
  analyzingValues: null,
  isAnalyzing: false,
  analyzingResult: null
};

export const mutations = {
  setIsAnalyzing(state, payload) {
    state.isAnalyzing = payload;
  },

  setAnalyzingResult(state, payload) {
    state.analyzingResult = payload;
  },

  setUserInfo(state, payload) {
    state.userInfo = payload;
  },

  setChatIsVisible(state, payload) {
    state.chatIsVisible = payload;
  },

  setAnalyzingValues(state, payload) {
    state.analyzingValues = payload;
  },

  setToolCalls(state, payload) {
    state.toolCalls = payload;
  },

  setSessions(state, payload) {
    if (!payload) return;
    if (Array.isArray(payload)) {
      state.sessions = payload;
    } else {
      state.sessions.unshift(payload);
    }
  },

  setMessages(state, payload) {
    if (!payload) return;
    if (Array.isArray(payload)) {
      state.messages = payload;
    } else {
      state.messages.push(payload);
    }
  },

  setCurrentSession(state, payload) {
    state.currentSession = payload;
  },

  setIsLoading(state, payload) {
    state.isLoading = payload;
  }
};

export const actions = {
  async getSessions({ state, commit }) {
    await fetchGetSessions(state.userInfo?.id).then(resp => {
      commit("setSessions", resp.data?.sessions);
    });
  },

  async addSession({ state, commit }, payload) {
    await fetchAddSession({
      ...payload,
      userId: state.userInfo?.id
    }).then(resp => {
      commit("setSessions", resp.data?.session);
      commit("setCurrentSession", resp.data?.session);
    });
  },
  /* eslint-disable */
  async deleteSession({ state, commit }, payload) {
    await fetchDeleteSession(payload).then(() => {
      commit("setSessions", state.sessions.filter(item => item.id !== payload));
    });
  },

  async getMessages({ state, commit }, payload) {
    await fetchGetMessages(state.currentSession?.id).then(resp => {

      const result = resp.data?.messages || []
      if (payload && payload?.content) result.push(payload);
      commit("setMessages", result);
    });
  },

  async updateSession({ state }, payload) {
    await fetchUpdateSession(state.currentSession?.id, payload).then(() => {
      // commit("setCurrentSession", resp.data?.session);
      state.currentSession.name = payload.name;
      state.sessions.find(item => {
        if (item.id === state.currentSession.id) {
          item.name = payload.name;
          return true;
        }
        return false;
      });
    });
  },

  async addMessage({ commit, state }, payload) {
    try {
      // 1. Send the user message
      const resp = await fetchAddMessage({
        ...payload,
        sessionId: state.currentSession?.id
      });
      commit("setMessages", resp.data?.message);
      commit("setIsLoading", true);

      // 2. Abort controller for this polling round (recreated on every send message, old one discarded)
      pollAbortController = new AbortController();
      const signal = pollAbortController.signal;

      // 3. Backoff polling configuration
      const baseDelay = 1000; // Initial interval 1 second
      const maxDelay = 10000; // Max interval 10 seconds
      const factor = 1.5; // Backoff factor
      let delay = baseDelay;
      let attempt = 0; // Current attempt count
      const maxAttempts = 8; // Max attempts (10)

      // Abortable wait: on abort, clear the timer immediately and resolve, so clicking stops it right away
      const wait = (ms) =>
        new Promise((resolve) => {
          if (signal.aborted) {
            resolve();
            return;
          }
          const t = setTimeout(resolve, ms);
          signal.addEventListener(
            "abort",
            () => {
              clearTimeout(t);
              resolve();
            },
            { once: true }
          );
        });

      // 4. Backoff polling with an attempt limit
      const poll = async () => {
        // Aborted: exit polling immediately and hide loading
        if (signal.aborted) {
          commit("setIsLoading", false);
          return;
        }

        attempt++;
        if (attempt > maxAttempts) {
          commit("setIsLoading", false);
          commit("setMessages", {
            role: "assistant",
            content: "AI response timeout, please try again later"
          });
          return;
        }

        try {
          const resp = await fetchGetMessages(state.currentSession?.id);
          const messages = resp.data?.messages || [];
          const lastMsg = messages[messages.length - 1];

          if (lastMsg?.role === "assistant") {
            // Successfully received the AI reply
            commit("setMessages", lastMsg);
            commit("setIsLoading", false);

            if(!lastMsg.toolCalls) return;

            const fixed = lastMsg.toolCalls?.replace(/\\\\+/g, '\\');
            const parsed = JSON.parse(fixed);

            const tools = parsed
              .map(item => typeof item === 'string' ? JSON.parse(item) : item)
              .filter(item => item?.function?.arguments);

            if (tools.length) commit("setToolCalls", tools);
            return;
          }
 
          // No reply received yet, continue backoff polling
          await wait(delay);
          if (signal.aborted) { commit("setIsLoading", false); return; } // Aborted
          delay = Math.min(delay * factor, maxDelay);
          await poll();
        } catch (error) {
          // Also continue backoff polling on failure (counts toward the attempt limit)
          await wait(delay);
          if (signal.aborted) { commit("setIsLoading", false); return; } // Aborted
          delay = Math.min(delay * factor, maxDelay);
          await poll();
        }
      };

      await poll();
    } catch (error) {
      commit("setIsLoading", false);
      commit("setError", "消息发送失败: " + error.message); // Catch the initial request error
    }
  },

  abortMessage({ commit }) {
    // Only aborts the "frontend wait/poll", hiding loading; the backend may still finish, and the result will be picked up next time the session opens
    if (pollAbortController) pollAbortController.abort();
    commit("setIsLoading", false);
  }
};
