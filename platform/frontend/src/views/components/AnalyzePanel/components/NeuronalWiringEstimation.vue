<template>
  <div class="heat-map" :id="heatMapParentId">
    <div class="data-info">
      <span style="font-weight: 600">Data:</span>
      <span class="primary-text--text truncate">{{ dataSource }}</span>
      <span style="font-weight: 600; margin-left: 30px">Analyzing:</span>
      <span class="primary-text--text truncate">
        &nbsp;Neuronal Wiring Estimation
      </span>
    </div>

    <div class="statistics-header">
      <span
        class="accent-1--text"
        style="margin-right: 10px; white-space: nowrap"
      >
        Statistics by
      </span>

      <span
        :class="{
          'active-header': statisticType === 'neuron',
          accent: statisticType !== 'neuron',
          'primary-light-1--text': statisticType !== 'neuron'
        }"
        @click="statisticType = 'neuron'"
        style="white-space: nowrap"
      >
        Neuron
      </span>

      <span
        :class="{
          'active-header': statisticType === 'morphotype',
          accent: statisticType !== 'morphotype',
          'primary-light-1--text': statisticType !== 'morphotype'
        }"
        style="white-space: nowrap"
        @click="statisticType = 'morphotype'"
      >
        Morphotype
      </span>
      <div style="margin:0 20px"></div>

      <span
        class="accent-1--text"
        style="margin-right: 10px; white-space: nowrap"
      >
        Statistics by
      </span>
      <span
        :class="{
          'active-header': estimationType === 'upstream',
          accent: estimationType !== 'upstream',
          'primary-light-1--text': estimationType !== 'upstream'
        }"
        style="white-space: nowrap"
        @click="estimationType = 'upstream'"
      >
        Upstream
      </span>
      <span
        :class="{
          'active-header': estimationType === 'downstream',
          accent: estimationType !== 'downstream',
          'primary-light-1--text': estimationType !== 'downstream'
        }"
        @click="estimationType = 'downstream'"
        style="white-space: nowrap"
      >
        Downstream
      </span>
    </div>

    <div
      :id="canvasParentId"
      class="d-flex align-start"
      style="position: relative"
    >
      <div class="canvas-colorbar-num">
        <!-- <div>{{ valueRangeFunc(maxVal) }}</div>
        <div>{{ valueRangeFunc(minVal) }}</div> -->
      </div>

      <div
        class="canvas-container"
        ref="morphotype_upstream"
        v-show="statisticType === 'morphotype' && estimationType === 'upstream'"
      >
        <canvas :id="canvasIds.morphotype_upstream"></canvas>
      </div>

      <div
        class="canvas-container"
        ref="morphotype_downstream"
        v-show="
          statisticType === 'morphotype' && estimationType === 'downstream'
        "
      >
        <canvas :id="canvasIds.morphotype_downstream"></canvas>
      </div>

      <div
        class="canvas-container"
        ref="neuron_upstream"
        v-show="statisticType === 'neuron' && estimationType === 'upstream'"
      >
        <canvas :id="canvasIds.neuron_upstream"></canvas>
      </div>

      <div
        class="canvas-container"
        ref="neuron_downstream"
        v-show="statisticType === 'neuron' && estimationType === 'downstream'"
      >
        <canvas :id="canvasIds.neuron_downstream"></canvas>
      </div>

      <div ref="no-data-info" style="margin-top:8px;color:#a5abb9">
        {{ noDataInfo }}
      </div>
    </div>

    <div :id="messageId" class="heat-map-message">
      <span v-for="(val, key) in heatMapessage" :key="key">
        <span style="font-weight: bold">{{ key }}: </span>{{ val }} <br />
      </span>
    </div>

    <div class="heat-tips">
      <Info style="margin-right: 8px"></Info>
      <span>
        {{ tipInfo }}
      </span>
    </div>
  </div>
</template>

<script>
import { v4 as uuidv4 } from "uuid";
import Info from "@/components/icons/Info";
import heatMapChart from "@/utils/noNavheatMap";
import { debounce } from "@/utils/utils";

export default {
  name: "HeatMap",
  props: {
    dataMapId: {
      type: String,
      default: ""
    },
    dataSource: {
      type: String,
      default: ""
    },
    neuronMapData: {
      type: Object,
      default: () => {}
    },
    typeMapData: {
      type: Object,
      default: () => {}
    }
  },
  components: {
    Info
  },
  data() {
    return {
      // Base IDs
      heatMapParentId: `heat-map-p-${uuidv4()}`,
      navId: `nav-${uuidv4()}`,
      renderedMap: new Map(), // Structure becomes: Map<dataMapId, Map<key, graph>>
      canvasParentId: `canvas-parent-${uuidv4()}`,
      messageId: `heat-map-message-${uuidv4()}`,
      heatMapessage: {},
      // State control
      statisticType: "neuron", // 'morphotype' | 'neuron'
      estimationType: "upstream", // 'upstream' | 'downstream'
      currentNeuronData: {},
      currentTypeData: {},
      refNames: [
        "morphotype_upstream",
        "morphotype_downstream",
        "neuron_upstream",
        "neuron_downstream"
      ],
      scrollHandlers: {},
      // 4 fixed Canvas container IDs
      // This way each combination has its own dedicated "slot" and stays put once drawn
      canvasIds: {
        morphotype_upstream: `canvas-m-up-${uuidv4()}`,
        morphotype_downstream: `canvas-m-down-${uuidv4()}`,
        neuron_upstream: `canvas-n-up-${uuidv4()}`,
        neuron_downstream: `canvas-n-down-${uuidv4()}`
      }
    };
  },

  computed: {
    tipInfo() {
      const res =
        this.statisticType === "neuron" ? `100 neurons` : `30 morphotype`;
      return `We only show the first ${res} (sorted by name).`;
    },

    noDataInfo() {
      return `No ${this.estimationType} connection`;
    }
  },

  methods: {
    chartHover(graph) {
      this.messageDialog = document.querySelector("#" + this.messageId);
      graph.on("hover", (hit, e) => {
        if (hit) {
          const { ...rest } = hit;
          // NA value (-1): show tooltip as --
          this.heatMapessage = {
            ...rest,
            value: rest.value < 0 ? '--' : rest.value
          };
          this.messageDialog.style.opacity = 1;
          if (
            document.querySelector("#" + this.heatMapParentId).offsetWidth <
            e.clientX + this.messageDialog.offsetWidth
          ) {
            this.messageDialog.style.left =
              e.pageX - this.messageDialog.offsetWidth + "px"; // div position
          } else {
            this.messageDialog.style.left = e.pageX + "px"; // div position
          }
          this.messageDialog.style.top =
            e.pageY + this.messageDialog.offsetHeight / 3 + "px"; // div position
        } else {
          this.messageDialog.style.opacity = 0;
        }
      });

      graph.on("hover-clear", () => {
        this.messageDialog.style.opacity = 0;
      });
    },

    // Unified drawing entry point
    renderCurrentHeatMap(data) {
      // 1. Get the current tab's identifier
      const tabId = this.dataMapId;
      if (!tabId) return;

      // 2. Build the current canvas's function key (e.g. axon_mean)
      const key = `${this.statisticType}_${this.estimationType}`;

      // 4. Get the data and DOM
      data = data?.[this.estimationType];
      const canvasId = this.canvasIds[key];
      const dom = this.$refs[key];
      const canvasDom = document.getElementById(canvasId);
      if (!dom) {
        console.log("Canvas node not yet rendered");
        return;
      }
      const colCount = data?.columns.length;
      const rowCount = data?.rows.length;
      if (!colCount || !rowCount) {
        canvasDom.style.display = "none";
        this.$refs["no-data-info"].style.display = "block";
        return;
      }
      canvasDom.style.display = "block";
      this.$refs["no-data-info"].style.display = "none";

      // 5. Perform the drawing (destroy the old graph first to avoid event leaks)
      const prevGraph = this.renderedMap.get(key);
      if (prevGraph) prevGraph.destroy();
      const graph = new heatMapChart(canvasId, data);
      this.renderedMap.set(key, graph);
      this.chartHover(graph);
    },

    debouncedRender: debounce(function() {
      // 1. Check whether the data exists
      const data =
        this.statisticType === "neuron"
          ? this.currentNeuronData
          : this.currentTypeData;
      if (!data || Object.keys(data).length === 0) return;

      // 2. Key point: enter nextTick to ensure $refs are destructured and mounted
      this.$nextTick(() => {
        this.renderCurrentHeatMap(data);
      });
    }, 50)
  },

  watch: {
    statisticType: "debouncedRender",
    estimationType: "debouncedRender",
    neuronMapData(newV, oldV) {
      // Only override when newV actually has content, otherwise keep the existing reference
      this.currentNeuronData =
        newV && Object.keys(newV).length > 0
          ? newV
          : oldV || this.currentNeuronData;
      if (Object.keys(this.currentNeuronData).length > 0) {
        this.debouncedRender();
      }
    },
    typeMapData(newV, oldV) {
      this.currentTypeData =
        newV && Object.keys(newV).length > 0
          ? newV
          : oldV || this.currentTypeData;
      if (Object.keys(this.currentTypeData).length > 0) {
        this.debouncedRender();
      }
    }
  },

  mounted() {
    console.log("moutted time12123");

    this.refNames.forEach(refName => {
      const dom = this.$refs[refName];
      if (dom) {
        // 1. Create and save the function reference
        this.scrollHandlers[refName] = e => {
          e.preventDefault();
          dom.scrollLeft += e.deltaY * 0.5;
        };
        // 2. Bind (note: passive must be false if preventDefault is needed)
        dom.addEventListener("wheel", this.scrollHandlers[refName], {
          passive: false
        });
      }
    });
  },

  beforeDestroy() {
    this.refNames.forEach(refName => {
      const dom = this.$refs[refName];
      if (dom && this.scrollHandlers[refName]) {
        dom.removeEventListener("wheel", this.scrollHandlers[refName]);
      }
    });
    this.scrollHandlers = {};

    // Destroy all graph instances and release canvas event listeners
    this.renderedMap.forEach(graph => {
      if (graph && graph.destroy) graph.destroy();
    });
    this.renderedMap.clear();
  }
};
</script>

<style lang="scss" scoped>
.heat-map {
  padding: 20px;
}

.heat-tips {
  display: flex;
  // width: 680px;
  margin-top: 10px;
  padding: 4px 10px;
  align-items: center;
  background: rgba(255, 255, 255, 0.08);
  color: #7f8490;
  font-family: Roboto;
  font-size: 12px;
  font-style: normal;
  font-weight: 400;
  line-height: normal;
}

.neuron-canvas-parent,
.morphotype-canvas-parent {
  display: flex;
  width: inherit;
  overflow: auto;
}

.canvas-colorbar-num {
  position: absolute;
  font-size: 12px;
  left: 20px;

  div:nth-child(1) {
    transform: translateY(12px);
  }

  div:nth-child(2) {
    transform: translateY(52px);
  }
}

.heat-map-message {
  position: fixed;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 200px;
  min-height: 45px;
  white-space: nowrap;
  opacity: 0;
  padding-left: 10px;
  padding-right: 10px;
  background-color: white;
  color: black;
  font-size: 13px;
  border: 1px solid #ccc;
  box-shadow: 0.1px 1.3px 2px rgba(0, 0, 0, 0.014),
    0.1px 3.2px 4.5px rgba(0, 0, 0, 0.021),
    0.3px 6.3px 7.9px rgba(0, 0, 0, 0.026),
    0.5px 11.7px 13.6px rgba(0, 0, 0, 0.03),
    1px 22.5px 25.1px rgba(0, 0, 0, 0.037), 2px 45px 80px rgba(0, 0, 0, 0.07);
}

.data-info {
  padding: 10px;
  display: flex;
  align-items: center;
  border-left: 2px solid #ffc42c;
  background: #ffc42c1a;
  margin-bottom: 20px;
}

.statistics-header {
  display: flex;
  align-items: center;
  height: 24px;

  span {
    height: 24px;
    line-height: 24px;
  }

  :nth-child(2),
  :nth-child(6) {
    padding: 0 10px;
    border-radius: 2px 0 0 2px;
    cursor: pointer;
  }

  :nth-child(3),
  :nth-child(7) {
    padding: 0 10px;
    border-radius: 0px 2px 2px 0px;
    cursor: pointer;
  }
}

.canvas-container {
  display: flex;
  width: inherit;
  overflow: auto;
  padding-bottom: 20px;
}

::v-deep .active-header {
  color: #ffffff !important;
  background: #2d68c3 !important;
}

:deep(.v-icon) {
  path {
    fill: #ffffff;
  }
}
</style>
