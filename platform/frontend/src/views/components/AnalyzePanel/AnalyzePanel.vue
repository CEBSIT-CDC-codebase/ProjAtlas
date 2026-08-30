<template>
  <div style="position: relative">
    <div class="analyze-panel-main secondary">
      <PanelHeader
        title="Analyzing"
        :enable-horizental="true"
        :enable-vertical="true"
        :enable-minimize="dataViewerLayout !== 'minimize'"
        @minimize="onMinimize"
        @fullScreen="onFullScreen"
        @vertical="onVertical"
        @horizental="onHorizental"
      ></PanelHeader>
      <div v-show="addResultFlag" class="analyze-loading">
        <v-progress-circular
          :size="70"
          color="#2d68c3"
          indeterminate
          class="mb-2"
        ></v-progress-circular>
        Loading...
      </div>
      <div class="frame-container" :style="frameContainerStyle">
        <TabFrame
          ref="tabFrame"
          frameID="0"
          :style="firstFrameStyle"
        ></TabFrame>
        <div v-show="displayMode !== 'single'">
          <TabFrame
            ref="tabFrame2"
            frameID="1"
            :style="secondFrameStyle"
          ></TabFrame>
        </div>
      </div>

      <!-- <v-btn @click="queryDownstream">123</v-btn> -->
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
import PanelHeader from "@/components/PanelHeader.vue";
import TabFrame from "./components/TabFrame.vue";
export default {
  name: "AnalyzePanel",
  components: {
    PanelHeader,
    TabFrame
  },

  data() {
    return {
      autoMinimize: true
    };
  },
  computed: {
    ...mapState({
      dataViewerLayout: state => state.layout.dataViewer,
      dataAnalyzingLayout: state => state.layout.dataAnalyzing,
      dataFilterLayout: state => state.layout.dataFilter,
      displayMode: state => state.analyze.displayMode,
      addResultFlag: state => state.analyze.addResultFlag,
      filteredNeurons: state => state.neuron.filteredNeurons,
      forbiddenAutoMinimize: state => state.layout.forbiddenAutoMinimize
    }),

    frameContainerStyle() {
      if (this.displayMode === "single") {
        return {
          gridTemplateColumns: "1fr",
          gridTemplateRows: "1fr"
        };
      } else if (this.displayMode === "horizental") {
        return {
          gridTemplateColumns: "1fr",
          gridTemplateRows: "1fr 1fr"
        };
      } else {
        return {
          gridTemplateColumns: "1fr 1fr",
          gridTemplateRows: "1fr"
        };
      }
    },

    firstFrameStyle() {
      if (this.displayMode === "vertical") {
        return {
          borderRight: "1px solid #343f5c"
        };
      } else if (this.displayMode === "horizental") {
        return { borderBottom: "1px solid #343f5c" };
      }
      return {};
    },

    secondFrameStyle() {
      if (this.displayMode === "vertical") {
        return {
          borderLeft: "1px solid #343f5c"
        };
      } else if (this.displayMode === "horizental") {
        return { borderTop: "1px solid #343f5c" };
      }
      return {};
    }
  },
  watch: {
    dataViewerLayout() {
      setTimeout(() => {
        this.$refs.tabFrame.updateHeaderMaxWidth();
        this.$refs.tabFrame2.updateHeaderMaxWidth();
        this.updateWidth();
      }, 300);
    },
    dataFilterLayout() {
      setTimeout(() => {
        this.$refs.tabFrame.updateHeaderMaxWidth();
        this.$refs.tabFrame2.updateHeaderMaxWidth();
        this.updateWidth();
      }, 300);
    },
    dataAnalyzingLayout() {
      setTimeout(() => {
        this.$refs.tabFrame.updateHeaderMaxWidth();
        this.$refs.tabFrame2.updateHeaderMaxWidth();
        this.updateWidth();
      }, 300);
    },
    forbiddenAutoMinimize() {
      this.autoMinimize = false;
    },
    addResultFlag() {
      this.$store.commit("session/setIsLoading", this.addResultFlag);
    }
  },

  methods: {
    updateWidth() {
      const analyzePanel = document.querySelector("#analyze-id");
      if (!analyzePanel) return;
      let width = getComputedStyle(analyzePanel).getPropertyValue("width");
      if (isNaN(parseInt(width))) {
        return;
      }
      width = parseInt(width.replace("px", ""));
      this.$store.commit("layout/setAnalyzeWidth", width);

      // if width < 460, then minimize anaylyze panel
      if (width < 460 && this.autoMinimize) {
        this.onMinimize();
      }
    },

    onMinimize() {
      this.$store.commit("layout/setDataAnalyzing", "minimize");
    },

    onFullScreen() {
      if (this.dataAnalyzingLayout === "fullScreen") {
        this.$store.commit("layout/setDataFilter", "normal");
        this.$store.commit("layout/setDataAnalyzing", "normal");
        this.$store.commit("layout/setDataViewer", "normal");
      } else {
        this.$store.commit("layout/setDataFilter", "minimize");
        this.$store.commit("layout/setDataViewer", "minimize");
        this.$store.commit("layout/setDataAnalyzing", "fullScreen");
      }

      setTimeout(() => {
        this.$refs.tabFrame.updateHeaderMaxWidth();
        this.$refs.tabFrame2.updateHeaderMaxWidth();
      }, 300);
    },

    onVertical() {
      if (this.displayMode === "vertical") {
        this.$store.commit("analyze/setDisplayMode", "single");
      } else {
        this.$store.commit("analyze/setDisplayMode", "vertical");
      }
    },

    onHorizental() {
      if (this.displayMode === "horizental") {
        this.$store.commit("analyze/setDisplayMode", "single");
      } else {
        this.$store.commit("analyze/setDisplayMode", "horizental");
      }
    }
  },

  mounted() {
    window.addEventListener("resize", this.updateWidth);
    this.updateWidth();
  },

  beforeDestroy() {
    window.removeEventListener("resize", this.updateWidth);
  }
};
</script>

<style lang="scss" scoped>
.analyze-panel-main {
  display: flex;
  flex-direction: column;
  position: relative;
  z-index: 1;
  height: 100%;

  .analyze-loading {
    font-size: 18px;
    height: 100%;
    width: 100%;
    z-index: 999;
    position: absolute;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background-color: rgba(0, 0, 0, 0.5);
  }

  .frame-container {
    display: grid;
    flex-grow: 1;
  }
}
</style>
