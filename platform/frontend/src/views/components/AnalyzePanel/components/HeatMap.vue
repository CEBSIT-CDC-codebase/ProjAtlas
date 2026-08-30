<template>
  <div class="heat-map" :id="heatMapParentId">
    <div class="data-info">
      <span style="font-weight: 600">Data:</span>
      <span class="primary-text--text truncate">{{ dataSource }}</span>
      <span style="font-weight: 600; margin-left: 30px">Analyzing:</span>
      <span class="primary-text--text truncate"
        >&nbsp;{{
          chartType === "axon"
            ? "Projection heatmap (axon length)"
            : "Projection heatmap (terminal points)"
        }}</span
      >
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
          'active-header': statisticType === 'brain',
          accent: statisticType !== 'brain',
          'primary-light-1--text': statisticType !== 'brain'
        }"
        style="white-space: nowrap"
        @click="statisticType = 'brain'"
      >
        Brain area
      </span>
      <div
        class="download-button"
        v-show="isSummarization"
        @click="summarizationHeatMapFunc"
      >
        <span
          class="accent-1--text"
          style="padding: 0; margin-left: 4px; white-space: nowrap"
        >
          Summarization heatmap
        </span>
      </div>
      <div
        v-if="!forbiddenDownload"
        class="download-button"
        @click="downloadCSVFunc"
      >
        <v-icon size="16" color="#CED4E4">$Download</v-icon>
        <span
          class="accent-1--text"
          style="padding: 0; margin-left: 4px; white-space: nowrap"
        >
          Download this data
        </span>
      </div>
    </div>

    <div
      :id="canvasParentId"
      class="d-flex align-start"
      style="position: relative"
    >
      <div class="canvas-colorbar-num">
        <div>{{ valueRangeFunc(maxVal) }}</div>
        <div>{{ valueRangeFunc(minVal) }}</div>
      </div>
      <canvas :id="navId"></canvas>

      <div
        v-show="statisticType === 'neuron'"
        class="neuron-canvas-parent"
        ref="neuronCanvas"
        :id="neuronParentId"
      >
        <canvas v-for="item in neuronCanvasIds" :key="item" :id="item"></canvas>
      </div>

      <div
        v-show="statisticType === 'brain'"
        class="brain-canvas-parent"
        :id="brainParentId"
        ref="brainCanvas"
      >
        <canvas v-for="item in brainCanvasIds" :key="item" :id="item"></canvas>
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
        We selected the top 30 brain regions based on the distribution of
        {{ tipText }} for projection analysis.
      </span>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
import { v4 as uuidv4 } from "uuid";
import heatMapChart from "@/utils/heatMapBuilder";
import { downloadCSV } from "@/utils/utils";
import Info from "@/components/icons/Info";
import { formatDecimal } from "@/utils/utils";
import csvWorkerScript from "@/workers/csvDataWorker.js";

export default {
  name: "HeatMap",
  props: {
    chartType: {
      type: String,
      default: ""
    },
    mapData: {
      type: Object,
      default: () => {}
    },
    dataSource: {
      type: String,
      default: ""
    },
    dataMapId: {
      type: String,
      default: ""
    }
  },
  components: {
    Info
  },
  data() {
    return {
      graph: null,
      heatMapessage: "",
      selectedNode: null,
      canvasParentId: `canvas-parent-${uuidv4()}`,
      heatMapParentId: `heat-map-parent-${uuidv4()}`,
      navId: `nav-id-${uuidv4()}`,
      messageId: `heat-map-message-${uuidv4()}`,
      statisticType: "neuron",
      domsId: {},
      widthSum: 0,
      leafWidth: 30,
      isPainted: {
        neuron: false,
        brain: false
      },
      currentType: {
        brain: false,
        neuron: true
      },
      neuronParentId: `neuron-id-${uuidv4()}-parent`,
      brainParentId: `brain-id-${uuidv4()}-parent`,
      neuronCanvasIds: [],
      brainCanvasIds: [],
      neuronLastWidth: 4080,
      brainLastWidth: 4080,
      csvData: {},
      currentMapData: {},
      heatMapCsvKey: "",
      screenMaxWidth: 4080,
      csvWorkerResults: new Map(),
      csvDataWorker: null,
      csvMessageHandler: null,
      analyzeResolvers: []
    };
  },
  watch: {
    mapData: {
      handler(newV, oldV) {
        this.currentMapData =
          newV && Object.keys(newV).length > 0
            ? newV
            : oldV || this.currentMapData;

        if (Object.keys(this.currentMapData).length > 0) {
          ["brain", "neuron"].forEach(item => {
            this.setCanvasCount(item);
            this.computedCsvData(item);
          });

          this.$nextTick(() => {
            this.updateMap();
          });
        }
      }
    },

    statisticType() {
      for (let key in this.currentType) {
        this.currentType[key] = key === this.statisticType ? true : false;
      }
    },

    widthSum: {
      handler() {
        const analyze = document.getElementById("analyze-id");
        if (analyze === null) return;

        const width = document.body.clientWidth - this.widthSum;
        const val = Math.abs(analyze.clientWidth - width);
        // Set a threshold range
        if (val > 5) {
          analyze.style.maxWidth = width + "px";
        }

        if (
          this.dataFilterLayout === "minimize" &&
          this.dataViewerLayout === "minimize"
        ) {
          analyze.style.maxWidth = "calc(100vw)";
        } else if (
          this.dataFilterLayout === "normal" &&
          this.dataViewerLayout === "normal"
        ) {
          analyze.style.maxWidth = "calc((100vw - 460px)/2)";
        }
      }
    }
  },
  computed: {
    ...mapState({
      theme: state => state.theme,
      currentHeadMapInfor: state => state.analyze.currentHeadMapInfor,
      dataFilterLayout: state => state.layout.dataFilter,
      sessionUserInfo: state => state.session.userInfo,
      dataViewerLayout: state => state.layout.dataViewer,
      dataAnalyzingLayout: state => state.layout.dataAnalyzing
    }),

    isMouse() {
      return process.env.VUE_APP_TARGET === "mouse";
    },

    forbiddenDownload() {
      return process.env.VUE_APP_SUB_SPECIES === "rbm";
    },

    isSummarization() {
      return (
        this.sessionUserInfo &&
        this.statisticType === "brain" &&
        this.isMouse &&
        !this.forbiddenDownload
      );
    },

    maxVal() {
      return this.statisticType === "brain"
        ? this.currentMapData?.logValues?.brainMax
        : this.currentMapData?.logValues?.neuronMax;
    },

    minVal() {
      return this.statisticType === "neuron"
        ? this.currentMapData?.logValues?.neuronMin
        : this.currentMapData?.logValues?.brainMin;
    },

    tipText() {
      return this.chartType === "axon" ? "axon length" : "terminal count";
    }
  },
  methods: {
    setCanvasCount(type) {
      console.log("setCanvasCount");
      const isBrain = type === "brain";
      const widthCount = Object.keys(
        isBrain ? this.currentMapData?.mapBrain : this.currentMapData?.neurons
      );
      const leafSumWidth = widthCount.length * this.leafWidth;
      let canvasCount;
      const lastWidth = leafSumWidth % this.screenMaxWidth;
      if (lastWidth) {
        isBrain
          ? (this.brainLastWidth = lastWidth)
          : (this.neuronLastWidth = lastWidth);
      }
      canvasCount =
        leafSumWidth >= this.screenMaxWidth
          ? Math.ceil(leafSumWidth / this.screenMaxWidth)
          : 1;

      const val = [];
      for (let i = 0; i < canvasCount; i++) {
        val.push(`result-id-${uuidv4()}`);
      }
      isBrain ? (this.brainCanvasIds = val) : (this.neuronCanvasIds = val);
    },

    updateMap() {
      console.log("updateMap");

      // Skip rendering when brains is empty since canvas height can't be computed, avoiding an empty-array read error
      if (!this.currentMapData?.brains?.length) {
        console.warn("Brains data is empty, skipping heatmap rendering.");
        return;
      }

      this.graph = new heatMapChart(
        this.navId,
        {
          neuron: this.neuronCanvasIds,
          brain: this.brainCanvasIds
        },
        {
          neuron: this.neuronParentId,
          brain: this.brainParentId
        },
        this.currentMapData,
        this.currentType,
        this.screenMaxWidth,
        {
          neuron: this.neuronLastWidth,
          brain: this.brainLastWidth
        }
      );
      this.chartClick();
      this.chartHover();
    },

    valueRangeFunc(value) {
      if (Number.isInteger(value)) {
        return value;
      }
      return formatDecimal(Math.pow(10, value), 3);
    },

    chartClick() {
      this.graph.on("click", (hit, e, redraw) => {
        if (hit) {
          redraw();
        }
      });
    },

    chartHover() {
      this.messageDialog = document.querySelector("#" + this.messageId);
      const valueKey =
        this.chartType === "axon" ? "Axon Length" : "Terminal Points";

      this.graph.on("hover", (hit, e) => {
        // create update redraw info apple
        if (hit) {
          // emit click event
          this.heatMapessage = {
            "Projection Location": hit["parent"]
          };
          const idKey = this.statisticType.includes("brain")
            ? "Soma Location"
            : "Neuron Id";
          this.heatMapessage[idKey] = hit["valKey"];
          this.heatMapessage[valueKey] = hit["value"];
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
      this.graph.on("out", () => {
        this.messageDialog.style.opacity = 0;
      });
    },

    computedCsvData(type) {
      const id = this.dataMapId;
      // Skip if a result already exists or a computation is in progress, to avoid re-triggering the worker
      if (this.csvData?.[id]?.[type]) return;
      const key = id + "|" + type;
      if (!this._csvPending) this._csvPending = new Set();
      if (this._csvPending.has(key)) return;
      this._csvPending.add(key);

      const curData =
        type === "brain"
          ? this.currentMapData?.mapBrain
          : this.currentMapData?.neurons;
      const rowsIndex = this.currentMapData?.brains.map(item => item.parent);
      // Send data to the worker for processing
      this.csvDataWorker.postMessage({
        id,
        type,
        curData,
        rowsIndex
      });
    },

    onResize() {
      const resizeObserver = new ResizeObserver(entries => {
        entries.forEach(entry => {
          this.domsId[entry.target.id] = entry.contentRect.width;
          let sum = 0;
          Object.values(this.domsId).forEach(val => (sum += val));
          this.widthSum = sum;
        });
      });

      resizeObserver.observe(document.getElementById("data-operation-id"));
      resizeObserver.observe(document.getElementById("data-viewer-id"));
    },

    downloadCSVFunc() {
      // Convert data to CSV format
      const currentData = this.csvData[this.dataMapId][this.statisticType];
      const header = currentData[0].map(key => `${key}`).join(",") + "\n";
      const rowsValue = currentData.slice(1);
      const rows = rowsValue
        .map(row => row.map(value => `="${value}"`).join(","))
        .join("\n");
      const vals = header + rows;

      const fileName =
        "projection_heatmap_data_" +
        (this.statisticType === "brain" ? "byBrainArea" : "byNeuron");
      downloadCSV(vals, fileName);
    },
    summarizationHeatMapFunc() {
      const currentData = this.csvData[this.dataMapId][this.statisticType];
      const result = this.convertAndFilterZeroValues(currentData);
      this.$store.commit("session/setChatIsVisible", true);
      this.$store.commit("session/setAnalyzingValues", {
        result,
        type: this.chartType
      });
    },

    getAnalyzeResult() {
      const data = this.csvData?.[this.dataMapId]?.[this.statisticType];
      // CSV is already ready, return directly
      if (data && data.length) {
        return Promise.resolve(this.buildAnalyzeResult());
      }
      // Can't compute without source data, return an empty result directly to avoid hanging
      if (
        !this.currentMapData ||
        Object.keys(this.currentMapData).length === 0
      ) {
        return Promise.resolve(this.buildAnalyzeResult());
      }
      // CSV is generated asynchronously by the worker; make sure the computation is triggered, and it will resolve via message once done (however long it takes)
      const promise = new Promise(resolve => {
        this.analyzeResolvers.push(resolve);
      });
      this.computedCsvData(this.statisticType);
      return promise;
    },

    buildAnalyzeResult() {
      const currentData = this.csvData?.[this.dataMapId]?.[this.statisticType];
      const result = this.convertAndFilterZeroValues(currentData);
      return {
        result,
        type: this.chartType
      };
    },

    flushAnalyzeResolvers() {
      if (!this.analyzeResolvers.length) return;
      const data = this.csvData?.[this.dataMapId]?.[this.statisticType];
      if (!(data && data.length)) return;
      const result = this.buildAnalyzeResult();
      this.analyzeResolvers.forEach(resolve => resolve(result));
      this.analyzeResolvers = [];
    },

    convertAndFilterZeroValues(dataArray) {
      if (!Array.isArray(dataArray) || dataArray.length < 1) {
        return {};
      }

      const headers = dataArray[0];
      const result = {};

      for (let i = 1; i < dataArray.length; i++) {
        const currentRow = dataArray[i];
        if (!Array.isArray(currentRow) || currentRow.length < 1) continue;

        const key = currentRow[0];
        const valueObj = {};

        for (let j = 1; j < headers.length && j < currentRow.length; j++) {
          const value = currentRow[j];
          // Only add to the object when the value exists and is not 0
          if (value !== 0 && value !== null && value !== undefined) {
            valueObj[headers[j]] = value;
          }
        }

        // Only add to the result when valueObj is not empty
        if (Object.keys(valueObj).length > 0) {
          result[key] = valueObj;
        }
      }

      return result;
    }
  },
  mounted() {
    this.onResize();
    ["brainCanvas", "neuronCanvas"].forEach(refName => {
      this.$refs[refName].addEventListener("wheel", e => {
        e.preventDefault();
        this.$refs[refName].scrollLeft += e.deltaY * 0.5;
      });
    });
    // Instance-level worker, to avoid interference between multiple HeatMap instances sharing one
    this.csvDataWorker = new Worker(csvWorkerScript);
    this.csvMessageHandler = e => {
      const { id, type, results } = e.data;
      if (!this.csvData[id]) this.csvData[id] = {};
      if (!this.csvData[id][type]) {
        this.csvData[id][type] = results;
      }
      this._csvPending?.delete(id + "|" + type);
      this.flushAnalyzeResolvers();
    };
    this.csvDataWorker.addEventListener("message", this.csvMessageHandler);
  },
  beforeDestroy() {
    if (this.graph) this.graph.destroy();
    if (this.csvDataWorker) {
      if (this.csvMessageHandler) {
        this.csvDataWorker.removeEventListener(
          "message",
          this.csvMessageHandler
        );
      }
      this.csvDataWorker.terminate();
      this.csvDataWorker = null;
    }
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
.brain-canvas-parent {
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

  :nth-child(2) {
    padding: 0 10px;
    border-radius: 2px 0 0 2px;
    cursor: pointer;
  }

  :nth-child(3) {
    padding: 0 10px;
    border-radius: 0px 2px 2px 0px;
    cursor: pointer;
  }
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
