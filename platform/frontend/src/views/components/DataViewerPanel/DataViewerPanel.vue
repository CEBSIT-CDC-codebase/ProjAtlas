<template>
  <div>
    <div
      id="scene-view"
      class="d-flex flex-column"
      style="position: relative; width: 100%; height: 100%"
    >
      <PanelHeader
        title="Data Viewer"
        @minimize="onMinimize"
        @fullScreen="onFullScreen"
        :enableMinimize="dataAnalyzingLayout !== 'minimize'"
      ></PanelHeader>
      <ViewHeader></ViewHeader>
      <SceneItems></SceneItems>
      <HighResolutionDendrites></HighResolutionDendrites>
      <div
        class="load-progress"
        v-show="loadedCount !== 0 && totalLoadingCount !== 0"
      >
        <LoadProgress></LoadProgress>
      </div>

      <PickedNeuronInformation
        id="neuron-information"
        style="position: fixed; z-index: 1; display: none"
      />
      <PickedRegionInformation
        id="region-information"
        style="position: fixed; z-index: 1; display: none"
      />
    </div>
  </div>
</template>

<script>
import PanelHeader from "@/components/PanelHeader.vue";
import ViewHeader from "./components/ViewHeader.vue";
import SceneItems from "./components/SceneItems/SceneItems.vue";
import HighResolutionDendrites from "./components/HighResolutionDendrites.vue";
import LoadProgress from "@/components/LoadProgress.vue";
import { mapState } from "vuex";
import PickedRegionInformation from "@/components/PickedRegionInformation.vue";
import PickedNeuronInformation from "@/components/PickedNeuronInformation.vue";

export default {
  name: "DataViewerPanel",

  components: {
    PanelHeader,
    ViewHeader,
    SceneItems,
    HighResolutionDendrites,
    LoadProgress,
    PickedNeuronInformation,
    PickedRegionInformation
  },

  data() {
    return {
      pageX: 0,
      pageY: 0,
      isPickPropFunc: false
    };
  },

  created() {
    // pageX/pageY are only used for DOM positioning in onPickProp and don't need Vue reactivity
    // Redefine them as plain properties in created() so mousemove won't trigger watcher/dep updates
    Object.defineProperty(this, 'pageX', { value: 0, writable: true, enumerable: false, configurable: true });
    Object.defineProperty(this, 'pageY', { value: 0, writable: true, enumerable: false, configurable: true });
  },

  watch: {
    neuroVizReady() {
      if (this.neuroVizReady && !this.isPickPropFunc) {
        this.isPickPropFunc = true;
        window.neuroViz.on("pick", this.onPickProp);
        const axesCanvas = window.neuroViz.getAxesCanvas();
        if (axesCanvas) {
          axesCanvas.classList.add("axes-canvas");
          const newParent = document.getElementById("scene-view");
          if (newParent) {
            newParent.appendChild(axesCanvas);
          }
        }
      }
    }
  },

  computed: {
    ...mapState({
      dataAnalyzingLayout: state => state.layout.dataAnalyzing,
      dataViewerLayout: state => state.layout.dataViewer,
      loadedCount: state => state.loadedCount,
      neuroVizReady: state => state.neuroVizReady,
      totalLoadingCount: state => state.totalLoadingCount,
      viewedNeurons: state => state.neuron.viewedNeurons,
      viewedRegions: state => state.region.viewedRegions
    })
  },

  methods: {
    onMinimize() {
      this.$store.commit("layout/setDataViewer", "minimize");
    },

    onFullScreen() {
      if (this.dataViewerLayout === "fullScreen") {
        this.$store.commit("layout/setDataFilter", "normal");
        this.$store.commit("layout/setDataAnalyzing", "normal");
        this.$store.commit("layout/setDataViewer", "normal");
      } else {
        this.$store.commit("layout/setDataFilter", "minimize");
        this.$store.commit("layout/setDataAnalyzing", "minimize");
        this.$store.commit("layout/setDataViewer", "fullScreen");
      }
    },

    setCurrentMousePos(event) {
      this.pageX = event.pageX;
      this.pageY = event.pageY;
    },

    onPickProp(data) {
      let neuronDiv = document.getElementById("neuron-information");
      let regionDiv = document.getElementById("region-information");
      if (data.eventType == "click" && data.name) {
        if (data.name.slice(-3) == "swc") {
          this.$store.commit(
            "PickedInformation/setPickedNeuronWorldPosition",
            data.worldPosition
          );
          this.viewedNeurons.forEach(neuron => {
            if (neuron.file === data.name) {
              this.$store.commit("PickedInformation/setNeuronItem", neuron);
            }
          });
        }
        if (data.name.slice(-3) == "stl") {
          regionDiv.style.display = "grid";
          regionDiv.style.top = this.pageY + "px";
          regionDiv.style.left = this.pageX + "px";
          this.$store.commit(
            "PickedInformation/setPickedRegionWorldPosition",
            data.worldPosition
          );
          this.viewedRegions.forEach(region => {
            if (region.file === data.name) {
              this.$store.commit("PickedInformation/setRegionItem", region);
            }
          });
        } else {
          regionDiv.style.display = "none";
        }
      }

      if (Object.keys(data).length == 0) {
        neuronDiv.style.display = "none";
        regionDiv.style.display = "none";
      }
    }
  },

  mounted() {
    window.addEventListener("mousemove", this.setCurrentMousePos);
  },

  beforeDestroy() {
    window.neuroViz.off("pick", this.onPickProp);
    window.removeEventListener("mousemove", this.setCurrentMousePos);
  }
};
</script>

<style lang="scss" scoped>
.load-progress {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}
</style>
