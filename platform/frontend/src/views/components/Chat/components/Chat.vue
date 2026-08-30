<template>
  <div class="chat-container" ref="chatContainer">
    <div v-show="firstTipVisible" class="user-message message-item-container">
      <img src="@/assets/machine.png" alt="" />
      <div
        class="message-content selectable-markdown"
        style="background-color: white"
        @mouseup="handleSelection"
      >
        <div v-html="parseMarkdown(currentPrompt)"></div>
      </div>
    </div>
    <div
      v-if="
        firstTipVisible &&
        currentFunction &&
        currentFunction.type === 'summarization' &&
        (isAnalyzing || showSummarizationItems)
      "
      class="user-message message-item-container"
    >
      <img src="@/assets/machine.png" alt="" />
      <div class="message-content selectable-markdown" style="background-color: white">
        <div v-if="isAnalyzing" class="analyzing-status">
          <div class="loader"></div>
          <span>Analyzing...</span>
        </div>
        <ul v-else-if="showSummarizationItems" class="summarization-list">
          <li
            v-for="item in summarizationItems"
            :key="item.target"
            class="summarization-item"
          >
            <span
              class="summarization-link"
              @click="handleSummarizationItemClick(item)"
              >{{ item["link-text"] }}</span
            >
            <span class="summarization-desc"> — {{ item.description }}</span>
          </li>
        </ul>
        <div
          v-if="showSummarizationItems"
          v-html="parseMarkdown(summarizationWarning)"
        ></div>
      </div>
    </div>
    <div v-for="(message, index) in messages" :key="index" class="message-container">
      <div
        v-if="message.role === 'assistant'"
        class="user-message message-item-container"
      >
        <img src="@/assets/machine.png" alt="" />
        <div
          class="message-content selectable-markdown"
          style="background-color: white"
          @mouseup="handleSelection"
        >
          <div v-html="parseMarkdown(message.content)"></div>
        </div>
      </div>
      <div v-else class="bot-message message-item-container">
        <div
          class="message-content selectable-markdown"
          style="background-color: #accdff"
          @mouseup="handleSelection"
          v-html="parseMarkdown(message.content)"
        ></div>
        <img src="@/assets/user.png" alt="" />
      </div>
      <div
        v-if="
          message.functionType === 'summarization' &&
          (isAnalyzing || showSummarizationItems)
        "
        class="user-message message-item-container"
      >
        <img src="@/assets/machine.png" alt="" />
        <div class="message-content selectable-markdown" style="background-color: white">
          <div v-if="isAnalyzing" class="analyzing-status">
            <div class="loader"></div>
            <span>Analyzing...</span>
          </div>
          <ul v-else-if="showSummarizationItems" class="summarization-list">
            <li
              v-for="item in summarizationItems"
              :key="item.target"
              class="summarization-item"
            >
              <span
                class="summarization-link"
                @click="handleSummarizationItemClick(item)"
                >{{ item["link-text"] }}</span
              >
              <span class="summarization-desc"> — {{ item.description }}</span>
            </li>
          </ul>
          <div
            v-if="showSummarizationItems"
            v-html="parseMarkdown(summarizationWarning)"
          ></div>
        </div>
      </div>
    </div>
    <div v-if="isLoading" class="d-flex" style="padding: 6px 10px">
      <img src="@/assets/machine.png" alt="" />
      <div class="loader"></div>
    </div>

    <!-- <div class="message-tip" v-if="messages.length === 0">
      Hi~ Please enter your question and I will answer it for you.
    </div> -->
  </div>
</template>
<script>
import { mapState } from "vuex";
import { marked } from "marked";
import { summarizationItems, summarizationWarning } from "./tips";
marked.setOptions({
  // Some options may help improve DOM structure, but styling mostly relies on CSS
  mangle: false, // Do not obfuscate email addresses
  headerIds: false, // Do not auto-add header ids, to reduce nesting
});
export default {
  props: ["currentFunction", "promptInfo", "currentPrompt"],
  data: () => ({
    selectionTimer: null,
    clickHandlers: new Set(),
    summarizationItems,
    summarizationWarning,
  }),
  components: {},
  computed: {
    ...mapState({
      isLoading: (state) => state.session.isLoading,
      messages: (state) => state.session.messages,
      currentSession: (state) => state.session.currentSession,
      isAnalyzing: (state) => state.session.isAnalyzing,
      analyzingResult: (state) => state.session.analyzingResult,
    }),

    firstTipVisible() {
      return !this.currentSession && this.currentPrompt;
    },

    showSummarizationItems() {
      return (
        this.currentFunction?.type === "summarization" &&
        !this.isAnalyzing &&
        this.analyzingResult?.length > 0
      );
    },
  },

  watch: {
    analyzingResult() {
      console.log("analyzingResult changed", this.analyzingResult);
    },
    messages() {
      this.$nextTick(() => {
        this.scrollToBottom();
      });
    },

    currentFunction() {
      if (this.messages?.length > 0) {
        const obj = {
          role: "assistant",
          content: this.currentPrompt,
          functionType: this.currentFunction?.type,
        };
        const currentMessages = this.messages.filter((item) => !item?.functionType);
        this.$store.commit(
          "session/setMessages",
          this.currentPrompt ? [...currentMessages, obj] : currentMessages
        );
      }
    },
  },

  methods: {
    scrollToBottom() {
      const chatContainer = this.$refs.chatContainer;
      chatContainer.scrollTop = chatContainer.scrollHeight;
    },

    parseMarkdown(text) {
      if (text === "executing") return "Execution Completed";

      // Strip special LLM chat template tags,
      // otherwise <s> gets rendered as strikethrough in the browser
      const cleaned = String(text || "")
        // <s>[OUT]、<s>[INST]、<s>[]、<xxx>[xxx]
        .replace(/<[a-z][a-z0-9_-]*>\s*\[[^\]]*\]/gi, "")

        // Common closing tags such as </s>, </INST>, </OUT>
        .replace(
          /<\/(?:s|inst|out|sys|system|user|assistant|think|analysis|final|tool|function|message)>/gi,
          ""
        )

        // Tags such as [INST], [/INST], [OUT], [/OUT]
        .replace(
          /\[\/?(?:INST|OUT|SYS|SYSTEM|USER|ASSISTANT|THINK|ANALYSIS|FINAL)\]/gi,
          ""
        )

        // Tags such as <|im_start|>, <|im_end|>, <|assistant|>, <|eot_id|>
        .replace(/<\|[^|>]*\|>/g, "")

        // Isolated ** on its own line
        .replace(/^\s*\*\*\s*$/gm, "")
        .trim();

      return marked.parse(cleaned);
    },

    handleSummarizationItemClick(item) {
      this.$emit("summarizationItemClick", item);
    },

    handleSelection(event) {
      clearTimeout(this.selectionTimer);
      this.selectionTimer = setTimeout(() => {
        const selection = window.getSelection();
        const selectedText = selection.toString().trim();

        if (selectedText.length > 0) {
          this.createCopyButton(event, selectedText);
        }
      }, 50);
    },
    createCopyButton(event, text) {
      // Remove any existing copy buttons
      this.removeExistingCopyButtons();

      // Create a new button
      const button = document.createElement("button");
      button.className = "copy-selection-button";
      button.textContent = "Copy";
      button.style.position = "fixed";
      button.style.left = `${event.clientX}px`;
      button.style.top = `${event.clientY}px`;

      button.onclick = (e) => {
        e.stopPropagation();
        this.copyToClipboard(text);
        button.remove();
      };

      document.body.appendChild(button);

      // Remove the button when clicking elsewhere
      const clickHandler = (e) => {
        if (!button.contains(e.target)) {
          button.remove();
          document.removeEventListener("click", clickHandler);
          this.clickHandlers.delete(clickHandler);
        }
      };
      this.clickHandlers.add(clickHandler);

      document.addEventListener("click", clickHandler);
    },
    removeExistingCopyButtons() {
      // Clean up leftover click listeners
      this.clickHandlers.forEach((h) => document.removeEventListener("click", h));
      this.clickHandlers.clear();
      document.querySelectorAll(".copy-selection-button").forEach((btn) => btn.remove());
    },
    async copyToClipboard(text) {
      try {
        await navigator.clipboard.writeText(text);
        this.$message.success("已复制到剪贴板");
      } catch (err) {
        console.error("Copy failed:", err);
        // Fallback approach
        const textarea = document.createElement("textarea");
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
        this.$message.success("已使用兼容方式复制");
      }
    },
  },

  beforeDestroy() {
    clearTimeout(this.selectionTimer);
    this.clickHandlers.forEach((h) => document.removeEventListener("click", h));
    this.clickHandlers.clear();
    this.removeExistingCopyButtons();
  },
};
</script>
<style scoped lang="scss">
.chat-container {
  flex: 1;
  overflow: auto;
  .message-tip {
    font-size: 18px;
    height: 100%;
    width: 100%;
    /* text-align: center; */
    /* margin: 0 auto; */
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .message-container {
    height: inherit;
  }
}

.message-item-container {
  display: flex;
  padding: 6px 10px;
  align-items: center;
  gap: 10px;
  flex: 1 0 0;
  img {
    width: 32px;
    height: 32px;
    aspect-ratio: 1/1;
    align-self: flex-start;
  }
}


.message-content {
  position: relative; /* Needed in case of absolutely positioned inner elements */
  z-index: 1; /* Ensure content stays on top */
  display: flex;
  flex-direction: column;
  flex-wrap: wrap;
  padding: 6px 10px;
  gap: 10px;
  border-radius: 10px;
  color: #303030;
  font-size: 12px;
  font-weight: 400;
  text-align: left;

  user-select: text !important; /* Force text selection to be allowed */
  -webkit-user-select: text !important; /* Safari */
  -moz-user-select: text !important; /* Firefox */
  -ms-user-select: text !important;
}

.message-content ::v-deep(*) {
  user-select: text !important; /* Force text selection to be allowed */
  -webkit-user-select: text !important; /* Webkit browser prefix */
  -moz-user-select: text !important; /* Firefox prefix */
  -ms-user-select: text !important; /* IE/Edge prefix */
  pointer-events: auto !important; /* Ensure the element can receive mouse events */
}

.bot-message {
  justify-content: end;
}

/* HTML: <div class="loader"></div> */
.loader {
  margin-left: 10px;
  width: 24px;
  aspect-ratio: 2;
  --_g: no-repeat radial-gradient(circle closest-side, rgb(172, 205, 255) 90%, #0000);
  background: var(--_g) 0% 50%, var(--_g) 50% 50%, var(--_g) 100% 50%;
  background-size: calc(100% / 3) 50%;
  animation: l3 1s infinite linear;
}
@keyframes l3 {
  20% {
    background-position: 0% 0%, 50% 50%, 100% 50%;
  }
  40% {
    background-position: 0% 100%, 50% 0%, 100% 50%;
  }
  60% {
    background-position: 0% 50%, 50% 100%, 100% 0%;
  }
  80% {
    background-position: 0% 50%, 50% 50%, 100% 100%;
  }
}

/* Key styling - ensure content is selectable */
.selectable-markdown {
  user-select: text;
  cursor: text;
}

/* Clickable list for summarization */
.summarization-list {
  list-style: none;
  margin: 6px 0 0;
  padding: 0;
}
.summarization-item {
  margin-bottom: 6px;
  line-height: 1.5;
}
.summarization-link {
  color: #000;
  font-weight: 700;
  cursor: pointer;
}
.summarization-link:hover {
  text-decoration: underline;
}
.summarization-desc {
  color: #666;
}

/* "analysis in progress" state for summarization */
.analyzing-status {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 6px;
  color: #303030;
}

/* Copy button styling */
.copy-selection-button {
  padding: 4px 8px;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  z-index: 1000;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.copy-selection-button:hover {
  background: #1565c0;
}
</style>
