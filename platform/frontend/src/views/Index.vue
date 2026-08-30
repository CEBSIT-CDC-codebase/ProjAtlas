<template>
  <div
    style="
      width: 100%;
      height: 100%;
      display: flex;
      flex-direction: column;
      position: relative;
    "
  >
    <div class="main" :style="mainStyle">
      <div v-show="dataFilterLayout === 'normal'">
        <DataOperationPanel
          class="data-operation"
          id="data-operation-id"
          :style="operationPanelStyle"
        ></DataOperationPanel>
      </div>

      <DataViewerPanel
        id="data-viewer-id"
        v-show="dataViewerLayout !== 'minimize'"
      ></DataViewerPanel>
      <AnalyzePanel
        id="analyze-id"
        v-show="dataAnalyzingLayout !== 'minimize'"
        :style="analyzePanelStyle"
      ></AnalyzePanel>
      <img
        src="@/assets/chat.gif"
        class="chat-icon"
        alt=""
        v-show="!chatVisible && isSpecificTarget"
        @click="isChatVisible"
      />
      <div class="analyze-chat" v-if="isSpecificTarget">
        <Chat v-show="chatVisible" @close="chatVisible = false"></Chat>
      </div>
    </div>
    <div class="footer">
      <div
        class="footer-item primary-bar accent-4--text align-center"
        style="border-top: 2px solid #76e6ff !important"
        v-for="(item, index) in footerItems"
        :key="index"
        @click="item.onClick"
      >
        <span style="flex-grow: 1">{{ item.text }}</span>
        <v-icon size="16">$FullScreenSquare</v-icon>
      </div>
    </div>
  </div>
</template>

<script>
import DataOperationPanel from "./components/DataOperationPanel/DataOperationPanel.vue";
import DataViewerPanel from "./components/DataViewerPanel/DataViewerPanel.vue";
import AnalyzePanel from "./components/AnalyzePanel/AnalyzePanel.vue";
import Chat from "./components/Chat/index.vue";
import { mapState } from "vuex";

export default {
  name: "HomePage",
  components: {
    DataOperationPanel,
    DataViewerPanel,
    AnalyzePanel,
    Chat,
  },

  computed: {
    ...mapState({
      theme: (state) => state.theme,
      expirationFlag: (state) => state.expirationFlag,
      dataFilterLayout: (state) => state.layout.dataFilter,
      dataViewerLayout: (state) => state.layout.dataViewer,
      dataAnalyzingLayout: (state) => state.layout.dataAnalyzing,
      totalLoadingCount: (state) => state.totalLoadingCount,
      sessionUserInfo: (state) => state.session.userInfo,
      chatIsVisible: (state) => state.session.chatIsVisible,
      loadedCount: (state) => state.loadedCount,
    }),

    isSpecificTarget() {
      if (process.env.VUE_APP_SUB_SPECIES === "rbm") {
        return false;
      }

      const arr = ["mouse", "monkey"];
      return arr.includes(process.env.VUE_APP_TARGET);
    },

    chatVisible: {
      get() {
        return this.chatIsVisible;
      },
      set(newV) {
        this.$store.commit("session/setChatIsVisible", newV);
      },
    },

    footerItems() {
      let items = [];
      if (this.dataFilterLayout === "minimize") {
        items.push({
          // icon: "mdi-filter",
          text: "Data Operation",
          onClick: () => {
            this.$store.commit("layout/setDataFilter", "normal");
          },
        });
      }

      if (this.dataViewerLayout === "minimize") {
        items.push({
          // icon: "mdi-eye",
          text: "Data Viewer",
          onClick: () => {
            this.$store.commit("layout/setDataViewer", "normal");
          },
        });
      }

      if (this.dataAnalyzingLayout === "minimize") {
        items.push({
          // icon: "mdi-chart-line",
          text: "Analyzing",
          onClick: () => {
            this.$store.commit("layout/setDataAnalyzing", "normal");
            this.$store.commit("layout/setForbiddenAutoMinimize");
          },
        });
      }

      return items;
    },

    operationPanelStyle() {
      return {
        "border-right":
          "1px solid " +
          this.$vuetify.theme.themes[this.theme]["border-light"] +
          " !important",
      };
    },

    analyzePanelStyle() {
      return {
        "border-left":
          "1px solid " +
          this.$vuetify.theme.themes[this.theme]["border-light"] +
          " !important",
        "flex-shrink": "0 !important",
      };
    },

    mainStyle() {
      const layouts = [
        this.dataFilterLayout,
        this.dataViewerLayout,
        this.dataAnalyzingLayout,
      ];

      const normalCount = layouts.filter((layout) => layout === "normal").length;
      const minimizeCount = layouts.filter((layout) => layout === "minimize").length;

      if (normalCount === 3) {
        return {
          display: "grid",
          "grid-template-columns": "460px 1fr 1fr",
        };
      } else if (minimizeCount === 2) {
        return {
          display: "grid",
          "grid-template-columns": "1fr",
        };
      } else if (minimizeCount === 1) {
        if (this.dataFilterLayout === "minimize") {
          return {
            display: "grid",
            "grid-template-columns": "1fr 1fr",
          };
        } else {
          return {
            display: "grid",
            "grid-template-columns": "460px  1fr",
          };
        }
      }

      return {};
    },
  },

  watch: {
    expirationFlag() {
      if (this.expirationFlag) {
        this.chatVisible = false;
      }
    },
  },

  methods: {
    isChatVisible() {
      if (this.sessionUserInfo?.id) {
        this.chatVisible = true;
      } else {
        this.$store.commit("setLoginFlag", true);
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.main {
  display: grid;
  flex-grow: 1;
  grid-template-columns: 460px 1fr 1fr;
}

#analyze-id {
  z-index: 0;
  max-width: calc((100vw - 460px) / 2);
}

.footer {
  z-index: 999;
  position: absolute;
  bottom: 0;
  right: 0;
  height: 32px;
  display: flex;
  align-items: center;
}

.footer-item {
  cursor: pointer;
  padding: 0 10px;
  font-size: 12px;
  font-weight: 500;
  border-top: 2px solid #76e6ff !important;
  width: 140px;
  display: flex;
  align-items: center;
  height: 100%;
  margin-left: 4px;
}

.data-operation {
  width: 460px;
  flex-basis: 460px;
  flex-shrink: 0;
  height: 100%;
}

.chat-icon {
  position: absolute;
  z-index: 999;
  right: 0;
  bottom: 0;
  cursor: pointer;
  width: 150px;
  height: 150px;
}

.analyze-chat {
  width: 900px;
  position: absolute;
  z-index: 999;
  right: 0;
  bottom: 0;
  text-align: right;
}
</style>
