<template>
  <v-container fluid style="padding: 0 22px 30px">
    <v-row class="mx-0 mb-2">
      <v-spacer></v-spacer>
      <div
        class="icon-style"
        style="background-color: white; margin-right: 10px"
        @click="toggleFullScreen"
      >
        <v-icon size="16">{{ screenIcon }}</v-icon>
      </div>
      <div
        class="icon-style"
        style="background-color: white"
        @click="closeChat"
      >
        <v-icon size="16">$AI_Delete</v-icon>
      </div>
    </v-row>

    <v-row no-gutters>
      <div class="chat-card">
        <!-- Left sidebar: history list -->
        <List
          @createNewChat="createNewChat"
          @selectHistory="selectHistory"
        ></List>
        <!-- Right side: current session -->
        <div class="main-container">
          <Chat
            :currentFunction="currentFunction"
            :promptInfo="promptInfo"
            :currentPrompt="currentPrompt"
            @summarizationItemClick="onSummarizationItemClick"
          ></Chat>
          <BtnFunctions
            :currentFunction="currentFunction"
            :functionValues="functionValues"
            @setCurrentFunction="setCurrentFunction"
          ></BtnFunctions>
          <UserInput
            v-show="userInputVisible"
            :currentFunction="currentFunction"
            @sendMessage="sendMessage"
          ></UserInput>
        </div>
      </div>
    </v-row>
  </v-container>
</template>
<script>
import List from "./components/List.vue";
import Chat from "./components/Chat.vue";
import BtnFunctions from "./components/BtnFunctions.vue";
import UserInput from "./components/UserInput.vue";
import { mouseTips, macaqueTips } from "./components/tips";
import { mapState } from "vuex";
export default {
  components: { List, Chat, BtnFunctions, UserInput },
  data: () => ({
    isFullScreen: false,
    userInputVisible: true,
    currentFunction: {
      id: 1,
      text: "Paper Interpretation",
      type: "paper"
    },
    functionValues: [
      {
        id: 1,
        text: "Paper Interpretation",
        type: "paper"
      },
      {
        id: 2,
        text: "Neuron Selection",
        type: "form"
      },
      {
        id: 3,
        text: "Brain Visualization",
        type: "neuroviz"
      },
      // {
      //   id: 4,
      //   text: "Viewport",
      //   type: "summarization/viewport"
      // },
      {
        id: 5,
        text: "Textual Summarization",
        type: "summarization"
      }
    ],
    analyzeTypes: {
      soma_distribution: "summarization/soma_distribution",
      axon: "summarization/projection_heatmap_by_axon_length",
      terminal: "summarization/projection_heatmap_by_terminal_points",
      projection: "summarization/projection"
    },
    primaryNeuronKeys: [
      "id",
      "acronym",
      "fullname",
      "file",
      "type_name",
      "parent_type_name",
      "hemisphere",
      "reconstruction_type",
      "class",
      "class1",
      "type_array"
    ],
    primaryRegionKeys: [
      "acronym",
      "color_hex_triplet",
      "file",
      "name",
      "parent_uid",
      "type_array",
      "uid",
      "pathway",
      "caudal",
      "rostral",
      "color_hex_triplet_cebsit",
      "volume",
      "_volume"
    ]
  }),
  computed: {
    ...mapState({
      currentSession: state => state.session.currentSession,
      analyzingValues: state => state.session.analyzingValues,
      messages: state => state.session.messages,
      userInfo: state => state.session.userInfo,
      toolCalls: state => state.session.toolCalls,
      barValues: state => state.analyze.barValues,
      projectionRegionList: state => state.analyze.projectionRegionList,
      viewedNeurons: state => state.neuron.viewedNeurons,
      viewedRegions: state => state.region.viewedRegions,
      functionMap: state => state.functionMap,
      analyzingResult: state => state.session.analyzingResult
    }),

    screenIcon() {
      return this.isFullScreen ? "$AI_NotFullScreen" : "$AI_FullScreen";
    },

    promptInfo() {
      const species = process.env.VUE_APP_TARGET;
      return species === "mouse" ? mouseTips : macaqueTips;
    },

    currentPrompt() {
      return this.promptInfo[this.currentFunction?.type]?.trim() || "";
    }
  },

  watch: {
    toolCalls() {
      if (this.toolCalls?.length) {
        for (const item of this.toolCalls) {
          this.$store.commit("setFunctionMap", {
            name: item?.function?.name,
            args: item?.function?.arguments
          });
        }
      }
    },

    currentFunction() {
      const visible = ["Viewport", "Analyzing"].includes(
        this.currentFunction?.text
      );
      this.userInputVisible = !visible;

      this.$nextTick(() => {
        if (this.currentFunction?.text === "Viewport") {
          this.sendMessage({
            content: "summarization/viewport",
            type: "summarization/viewport"
          });
        }
      });
    },

    analyzingValues() {
      const cur = this.functionValues.find(
        item => item.type === "summarization"
      );
      this.setCurrentFunction(cur);
      this.sendMessage({
        content: cur?.text,
        type: this.analyzeTypes[this.analyzingValues?.type]
      });
    }
  },
  methods: {
    closeChat() {
      // Close the chat window
      this.$emit("close");
    },

    async createNewChat() {
      await this.$store.dispatch("session/addSession", {
        name: "New chat"
      });
      this.$store.commit("session/setAnalyzingResult", null);
      if (this.currentFunction?.type === "summarization") {
        this.currentFunction = this.functionValues[0];
      }
      this.$store.commit("session/setMessages", [
        {
          role: "assistant",
          content: this.currentPrompt,
          functionType: this.currentFunction?.type
        }
      ]);
    },

    setCurrentFunction(val) {
      this.currentFunction = val;
    },

    onSummarizationItemClick(item) {
      const targetItem = this.analyzingResult?.find(
        result => result?.type === item.type
      );
      this.$store.commit("session/setAnalyzingValues", { ...targetItem });
      console.log("onSummarizationItemClick", item, this.analyzingResult);
      // const taskMap = {
      //   "soma-distribution": "summarization/soma_distribution",
      //   "projection-overview": "summarization/projection",
      //   "projection-heatmap-axon-length":
      //     "summarization/projection_heatmap_by_axon_length",
      //   "projection-heatmap-terminal-points":
      //     "summarization/projection_heatmap_by_terminal_points",
      // };
      // const task = taskMap[item.target];
      // if (!task) return;
      // this.sendMessage({ content: item["link-text"], type: task });
    },

    selectHistory(val) {
      this.$store.commit("session/setCurrentSession", val);
      if (this.currentFunction?.type === "summarization") {
        this.currentFunction = this.functionValues[0];
      }
      this.$store.dispatch("session/getMessages", {
        role: "assistant",
        content: this.currentPrompt,
        functionType: this.currentFunction?.type
      });
    },

    toggleFullScreen() {
      // Toggle fullscreen mode
      this.isFullScreen = !this.isFullScreen;
      const dom = document.querySelector(".chat-card");
      dom.style.height = this.isFullScreen ? "calc(100vh - 145px)" : "500px";
    },

    handleSummarizationTypeFunc(obj) {
      if (obj.task === "summarization/viewport") {
        const filterObjectKeys = (obj, keys) =>
          Object.fromEntries(
            Object.entries(obj).filter(([key]) => keys.includes(key))
          );

        obj.neurons = this.viewedNeurons.map(item =>
          filterObjectKeys(item, this.primaryNeuronKeys)
        );

        obj.regions = this.viewedRegions.map(item =>
          filterObjectKeys(item, this.primaryRegionKeys)
        );
        return;
      }

      const { result, projectionType } = this.analyzingValues;

      if (obj.task === "summarization/soma_distribution") {
        const flag = this.isAnalyzed(result);
        if (flag) {
          return;
        }
        obj.regions = result?.map(item => {
          return {
            name: item.name,
            soma_count: item.count
          };
        });
        return;
      }

      if (obj.task === "summarization/projection") {
        const flag = this.isAnalyzed(result);
        if (flag) {
          return;
        }
        const getSortKey =
          projectionType === "number"
            ? item => item.count
            : item => item.leftLength + item.rightLength;

        const res = result
          ?.map(item => ({
            name: item.name,
            ...(projectionType === "number"
              ? { count: item.count }
              : { leftLength: item.leftLength, rightLength: item.rightLength })
          }))
          ?.sort((a, b) => getSortKey(b) - getSortKey(a))
          ?.slice(0, 20);
        obj.regions = res;
        return;
      }

      if (
        [
          "summarization/projection_heatmap_by_axon_length",
          "summarization/projection_heatmap_by_terminal_points"
        ].includes(obj.task)
      ) {
        // invert and sort value for llm
        const matrix = {};
        for (let dest in result) {
          for (let source in result[dest]) {
            matrix[source] = matrix[source] || [];
            matrix[source].push({
              dest,
              value: result[dest][source]
            });
          }
        }

        for (let source in matrix) {
          matrix[source].sort((a, b) => b.value - a.value);
        }

        obj.matrix = matrix;
      }
    },

    isAnalyzed(data = []) {
      if (!data.length) {
        this.$store.commit("setToolTipType", "warning");
        this.$store.commit("setToolTipMessage", "Please analyze first");
        this.$store.commit("setToolTipVisible", true);
        return true;
      }

      return false;
    },

    async sendMessage({ content, type }) {
      console.log("sendMessage", content, type);
      const isMacaque = process.env.VUE_APP_TARGET == "monkey";
      if (isMacaque && ["paper", "form"].includes(type)) {
        type += "-macaque";
      }
      let obj = {
        role: "user",
        content,
        task: type
      };
      const isSummarization = type?.includes("summarization");
      if (!this.currentSession) {
        await this.$store.dispatch("session/addSession", {
          name: "New chat"
        });

        this.$store.commit("session/setMessages", [
          {
            role: "assistant",
            content: this.currentPrompt,
            functionType: this.currentFunction?.type
          }
        ]);
      }
      isSummarization && this.handleSummarizationTypeFunc(obj);

      await this.$store.dispatch("session/addMessage", obj);
      if (this.currentSession?.name === "New chat") {
        await this.$store.dispatch("session/updateSession", {
          name: content.slice(0, 40),
          userId: this.userInfo?.id
        });
      }

      // isSummarization && this.setCurrentFunction(this.functionValues[0]);
    }
  }
};
</script>
<style lang="scss">
.icon-style {
  display: flex;
  width: 24px;
  height: 24px;
  justify-content: center;
  align-items: center;
  gap: 10px;
  border-radius: 4px;
  background: rgba(190, 210, 254, 0.1);
  &:hover {
    cursor: pointer;
    background: rgba(190, 210, 254, 0.2);
  }
}

.chat-card {
  display: flex;
  width: 100%;
  height: 500px;
  border-radius: 26px;
  padding: 20px;
  border: 1px solid #343f5c;
  background: rgba(255, 255, 255, 0.1);
  box-shadow: 0px 0px 30px 0px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(15px);
  .main-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding-left: 20px;
    position: relative;
  }
}

:deep {
  .v-text-field__slot {
    width: 100%;
  }
}
</style>
