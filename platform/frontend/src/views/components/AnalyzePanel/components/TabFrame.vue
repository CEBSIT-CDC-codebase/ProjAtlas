<template>
  <div
    style="display: flex; flex-direction: column"
    :style="{ maxWidth: headerMaxWidth }"
  >
    <div
      class="align-center accent tabs"
      style="overflow: scroll"
      :style="{
        maxWidth: headerMaxWidth,
        display: tabs.length > 0 ? 'flex' : 'none'
      }"
      ref="tabs"
    >
      <div
        v-for="(tabItem, index) in tabs"
        :ref="'tab_' + tabItem.value"
        :key="index"
        :style="targetTab === tabItem.value ? activeTabStyle : ''"
        :class="{
          'tab-item': true,
          'tab-item-active': targetTab === tabItem.value
        }"
        @click="onChangeTab(tabItem)"
      >
        <v-icon class="union-icon" size="14" v-if="tabItem.type === 'result'"
          >$UnionTag</v-icon
        >
        <span class="primary-light-1--text tab-item-text"
          >{{ tabItem.label }}
        </span>
        <v-icon
          size="16"
          style="margin-right: 10px"
          @click.stop="openContextMenu($event, tabItem)"
          >$Menu</v-icon
        >
        <v-icon size="16" @click="onRemoveTab(tabItem)">$Close</v-icon>
        <div
          v-if="tabs.length > 1 && index !== tabs.length - 1"
          style="
            width: 1px;
            height: 16px;
            background-color: #343f5c;
            position: absolute;
            right: 0;
          "
        ></div>
      </div>
    </div>
    <v-menu
      v-model="contextMenu.open"
      :position-x="contextMenu.x"
      :position-y="contextMenu.y"
      absolute
      offset-y
    >
      <v-list class="accent-6" style="padding: 0">
        <v-list-item @click="onMoveTab('horizental')" style="cursor: pointer">
          <v-list-item-title>Move horizentally</v-list-item-title>
        </v-list-item>
        <v-list-item @click="onMoveTab('vertical')" style="cursor: pointer">
          <v-list-item-title>Move vertically</v-list-item-title>
        </v-list-item>
      </v-list>
    </v-menu>
    <div
      style="overflow: auto; width: 100%"
      :style="{
        maxHeight:
          displayMode === 'horizental'
            ? 'calc(50vh - 46px)'
            : 'calc(100vh - 92px)'
      }"
    >
      <Welcome v-if="showWelcome"></Welcome>

      <Result
        v-if="showResult"
        dataSource=""
        :result="currentResult"
        :frameID="frameID"
      ></Result>

      <SomaDistribution
        ref="somaDistribution"
        v-show="showSomaDistribution"
        :isRegionType="isRegionType"
        :somas="currentTab ? currentTab.data.somas : []"
        :neuronItems="currentTab ? currentTab.data.items : []"
        :dataSource="currentTab ? currentTab.data.dataSource : ''"
      ></SomaDistribution>

      <HeatMap
        ref="axonHeatMap"
        v-show="showAxonHeatMap"
        chartType="axon"
        :dataMapId="currentTab ? currentTab.data.md5 + 'axon' : ''"
        :mapData="currentTab ? currentTab.data.axonHeatMapValue : {}"
        :dataSource="currentTab ? currentTab.data.dataSource : ''"
      ></HeatMap>

      <HeatMap
        ref="terminalHeatMap"
        v-show="showTerminalHeatMap"
        chartType="terminal"
        :dataMapId="currentTab ? currentTab.data.md5 + 'terminal' : ''"
        :mapData="currentTab ? currentTab.data.terminalHeatMapValue : {}"
        :dataSource="currentTab ? currentTab.data.dataSource : ''"
      ></HeatMap>

      <NeuronalWiringEstimation
        v-show="showNeuronalWiringEstimation"
        :dataMapId="currentTab ? currentTab.data.md5 + 'neuronalWiring' : ''"
        :neuronMapData="currentTab ? currentTab.data?.neuronHeatMapData : {}"
        :typeMapData="currentTab ? currentTab.data?.morphotypeHeatMapData : {}"
        :dataSource="currentTab ? currentTab.data.dataSource : ''"
      ></NeuronalWiringEstimation>

      <NeuronProjection
        ref="neuronProjection"
        v-show="showProjection"
        :isRegionType="isRegionType"
        :neuronItems="currentTab ? currentTab.data.items : []"
        :dataSource="currentTab ? currentTab.data.dataSource : ''"
      ></NeuronProjection>
      <DentriteDepthDistribution
        v-if="showDendriteDepthDistribution"
        :dataSource="currentTab ? currentTab.data.dataSource : ''"
        :neuronItems="currentTab ? currentTab.data.items : []"
      ></DentriteDepthDistribution>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
import Welcome from "./Welcome.vue";
import Result from "./Result.vue";
import SomaDistribution from "./SomaDistribution.vue";
import NeuronProjection from "./NeuronProjection.vue";
import HeatMap from "./HeatMap.vue";
import NeuronalWiringEstimation from "./NeuronalWiringEstimation.vue";
import DentriteDepthDistribution from "./DentriteDepthDistribution.vue";

export default {
  name: "TabFrame",
  components: {
    Welcome,
    HeatMap,
    Result,
    SomaDistribution,
    NeuronProjection,
    NeuronalWiringEstimation,
    DentriteDepthDistribution
  },
  props: {
    frameID: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      targetTab: "",
      headerMaxWidth: "100px",
      contextMenu: {
        open: false,
        x: 0,
        y: 0,
        tab: null
      },
      latestResults: []
    };
  },

  computed: {
    ...mapState({
      theme: state => state.theme,
      dataViewerLayout: state => state.layout.dataViewer,
      dataAnalyzingLayout: state => state.layout.dataAnalyzing,
      visualTarget: state => state.visualTarget,
      frames: state => state.analyze.frames,
      displayMode: state => state.analyze.displayMode,
      totalTabs: state => state.analyze.tabs,
      focusTabTrigger: state => state.analyze.focusTabTrigger,
      analyzingResult: state => state.session.analyzingResult
    }),

    isRegionType() {
      if (this.currentResult) {
        return this.currentResult.data.type === "region";
      }
      return false;
    },

    tabs() {
      return this.totalTabs.filter(tab => tab.frameID === this.frameID);
    },

    showWelcome() {
      return this.tabs.length === 0;
    },

    currentTab() {
      return this.tabs.find(tab => tab.value === this.targetTab);
    },

    showSomaDistribution() {
      return this.currentTab && this.currentTab.type === "somaDistribution";
    },

    showAxonHeatMap() {
      return this.currentTab && this.currentTab.type === "heatmapAxon";
    },

    showTerminalHeatMap() {
      return (
        this.currentTab && this.currentTab.type === "heatmapTerminalPoints"
      );
    },

    showProjection() {
      return this.currentTab && this.currentTab.type === "projectionOverview";
    },

    showNeuronalWiringEstimation() {
      return (
        this.currentTab &&
        this.currentTab.type === "heatmapNeuronWiringEstimation"
      );
    },

    showDendriteDepthDistribution() {
      return (
        this.currentTab && this.currentTab.type === "dendriteDepthDistribution"
      );
    },

    activeTabStyle() {
      return {
        background: this.$vuetify.theme.themes[this.theme].primary,
        color:
          this.$vuetify.theme.themes[this.theme]["accent-1"] + " !important"
      };
    },

    showResult() {
      const currentTab = this.tabs.find(tab => tab.value === this.targetTab);
      return currentTab && currentTab.type === "result";
    },

    currentResult() {
      return this.tabs.find(
        tab => tab.value === this.targetTab && tab.type === "result"
      );
    },

    focusTab() {
      return this.frames[this.frameID].focusTab;
    }
  },
  watch: {
    async currentResult() {
      if (!this.currentResult) return;
      // Wait for child components to mount/update, ensuring refs are available (user watchers run before render watchers)
      await this.$nextTick();
      // If the overlay is already on when entering, this is a newly started analysis, so keep "analyzing" until the result is computed
      const wasAnalyzing = this.addResultFlag;
      if (wasAnalyzing) this.$store.commit("session/setIsAnalyzing", true);

      try {
        const results = [];

        const projection = this.$refs.neuronProjection;
        if (projection) results.push(await projection.getAnalyzeResult());

        const somaDistribution = this.$refs.somaDistribution;
        if (somaDistribution)
          results.push(await somaDistribution.getAnalyzeResult());

        const axonHeatMap = this.$refs.axonHeatMap;
        if (axonHeatMap) results.push(await axonHeatMap.getAnalyzeResult());

        const terminalHeatMap = this.$refs.terminalHeatMap;
        if (terminalHeatMap)
          results.push(await terminalHeatMap.getAnalyzeResult());

        this.latestResults = results;
        this.$store.commit("session/setAnalyzingResult", [...results]);
      } finally {
        // Unconditionally turn off the "analyzing" state and overlay once the result is ready (or errored)
        this.$store.commit("session/setIsAnalyzing", false);
        this.$store.commit("analyze/setAddResultFlag", false);
      }
    },

    showProjection() {
      if (this.showProjection) {
        this.$refs.neuronProjection.updatePercentBarStyle();
      }
    },

    showSomaDistribution() {
      if (this.showSomaDistribution) {
        this.$refs.somaDistribution.updatePercentBarStyle();
      }
    },

    focusTabTrigger() {
      if (this.focusTab) {
        this.targetTab = this.focusTab.value;

        this.$nextTick(() => {
          const targetElement = this.$refs["tab_" + this.targetTab];
          if (targetElement && targetElement.length > 0) {
            targetElement[0].scrollIntoView({
              behavior: "smooth"
            });
          }
        });
      }
    },

    displayMode() {
      this.updateHeaderMaxWidth();
    }
  },

  mounted() {
    this.$refs.tabs.addEventListener("wheel", this.onHorizentalScrollTabs);
    this.updateHeaderMaxWidth();
    window.addEventListener("resize", this.updateHeaderMaxWidth);
  },

  beforeDestroy() {
    if (this.$refs.tabs) {
      this.$refs.tabs.removeEventListener("wheel", this.onHorizentalScrollTabs);
    }
    window.removeEventListener("resize", this.updateHeaderMaxWidth);
  },

  methods: {
    onChangeTab(tab) {
      this.$store.commit("analyze/setFocusTab", tab);
    },
    openContextMenu(event, tabItem) {
      this.contextMenu = {
        open: true,
        x: event.clientX,
        y: event.clientY,
        tab: tabItem
      };
    },

    onRemoveTab(tab) {
      this.$store.commit("analyze/removeTab", tab);
    },

    onHorizentalScrollTabs(e) {
      e.preventDefault();
      this.$refs.tabs.scrollLeft += e.deltaY * 0.5;
    },

    updateHeaderMaxWidth() {
      // calculate the width of analysis panel, give the header a max-width
      const anaylyzePanel = document.querySelector(".analyze-panel-main");
      this.headerMaxWidth = window.getComputedStyle(anaylyzePanel).width;

      // if there are two frames, the max width is half ot the anaylyze panel
      if (this.displayMode === "vertical") {
        this.headerMaxWidth = parseInt(this.headerMaxWidth) / 2 + "px";
      }
    },

    onMoveTab(direction) {
      this.$store.commit("analyze/moveTab", {
        tab: this.contextMenu.tab,
        direction
      });
    }
  }
};
</script>

<style lang="scss" scoped>
.tabs {
  flex-wrap: nowrap;
  z-index: 1;
  height: 32px;

  span {
    cursor: pointer;
    user-select: none;
  }

  :deep(.union-icon) {
    path {
      fill: #ffffff;
    }
  }

  @include hide-scrollbar();
}

.tab-item {
  display: flex;
  align-items: center;
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
  // min-width: 115px;

  padding: 10px 14px;

  :deep(.union-icon) {
    flex-grow: 1;

    path {
      fill: #a5abb9;
    }
  }

  .tab-item-text {
    padding: 0 10px;
    font-size: 13px;
    flex-shrink: 0;
  }

  :deep(.v-icon) {
    &::after {
      display: none !important;
    }
  }
}

.tab-item-active {
  :deep(.union-icon) {
    path {
      fill: #ffffff !important;
    }
  }

  .tab-item-text {
    color: #ffffff !important;
  }
}

:deep(.v-list-item) {
  padding: 4px 8px;
  min-height: 28px !important;
  height: 28px !important;
  display: flex;
  align-items: center !important;
  width: 120px;

  .v-list-item__title {
    font-size: 12px;
  }
}
</style>
