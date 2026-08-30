<template>
  <div class="soma-distribution">
    <div class="header">
      <span style="font-weight: 600">Data:</span>
      <span class="primary-text--text truncate">{{ dataSource }}</span>
      <span style="font-weight: 600; margin-left: 30px">Analyzing: </span>
      <span class="primary-text--text truncate">&nbsp;Soma distribution</span>
    </div>
    <div style="display: flex; justify-content: end; margin-right: 20px">
      <div
        v-if="isSummarization"
        class="download-button"
        @click="analyzeSomaDistributionFunc"
      >
        <span
          class="accent-1--text"
          style="padding: 0; margin-left: 4px; white-space: nowrap"
        >
          Summarization of soma distribution
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

    <div class="distribution-charts">
      <apexchart
        type="area"
        width="600px"
        :height="axisHeight"
        :options="xoptions"
        ref="x"
        :series="xaxis"
      ></apexchart>
      <apexchart
        type="area"
        width="600px"
        :height="axisHeight"
        :options="yoptions"
        ref="y"
        :series="yaxis"
      ></apexchart>
      <apexchart
        type="area"
        width="600px"
        :height="axisHeight"
        :options="zoptions"
        ref="z"
        :series="zaxis"
      ></apexchart>
    </div>
    <div class="bar-charts-title">Neuron Summation</div>
    <div class="bar-charts" ref="bCharts">
      <apexchart
        v-if="barValues && barValues.length > 0"
        type="bar"
        :height="axisHeight"
        :options="boptions"
        ref="b"
        :series="baxis"
      ></apexchart>
    </div>

    <SomaDistributionTree
      v-show="!forbiddenDownload"
      ref="somaDistributionTree"
      :neuronItems="neuronItems"
      :isRegionType="isRegionType"
      style="width: 100%"
    />
  </div>
</template>

<script>
const options = {
  chart: {
    height: 200,
    type: "line",
    zoom: {
      enabled: false
    },
    toolbar: {
      show: false
    }
  },
  dataLabels: {
    enabled: false
  },
  tooltip: {
    enabled: false
  },
  stroke: {
    curve: "smooth",
    width: 3
  },
  title: {
    text: "Anterior - Posterior",
    align: "center",
    style: {
      color: "#ffffff"
    }
  },
  grid: {
    borderColor: "#404040",
    strokeDashArray: 7
  },
  xaxis: {
    type: "numeric",
    labels: {
      style: {
        colors: "#9D9FA4"
      }
    }
  },
  yaxis: {
    labels: {
      style: {
        colors: "#9D9FA4"
      }
    }
  },
  colors: ["#ff0000"]
};
const chartOptions = {
  chart: {
    type: "bar",
    height: 350,
    zoom: {
      enabled: true
    },
    toolbar: {
      show: false
    }
  },
  plotOptions: {
    bar: {
      columnWidth: 30
    }
  },
  dataLabels: {
    enabled: false
  },
  grid: {
    borderColor: "#404040",
    strokeDashArray: 7
  },
  stroke: {
    show: true,
    width: 2,
    colors: ["transparent"]
  },
  // title: {
  //   text: "Neuron Summation",
  //   align: "center",
  //   floating: true,
  // },
  xaxis: {
    categories: [],
    labels: {
      show: true,
      rotate: -45,
      rotateAlways: false,
      hideOverlappingLabels: true,
      trim: true,
      style: {
        colors: "#9D9FA4",
        fontSize: "10px"
      }
    },
    tickPlacement: "on"
  },
  yaxis: {
    labels: {
      style: {
        colors: "#9D9FA4"
      }
    }
  },
  fill: {
    opacity: 1
  }
};
import { mapState } from "vuex";
import SomaDistributionTree from "./SomaDistributionTree.vue";
import { downloadCSV } from "@/utils/utils";
export default {
  name: "SomaDistribution",
  props: {
    somas: {
      type: Array,
      default: () => []
    },
    neuronItems: {
      type: Array,
      default: () => []
    },
    dataSource: {
      type: String,
      default: ""
    },
    isRegionType: {
      type: Boolean
    }
  },
  components: {
    SomaDistributionTree,
    apexchart: () => ({
      component: import("vue-apexcharts"),
      loading: null,
      error: null,
      delay: 0,
      timeout: 3000
    })
  },
  data() {
    return {
      xaxis: [
        {
          data: []
        }
      ],
      yaxis: [
        {
          data: []
        }
      ],
      zaxis: [
        {
          data: []
        }
      ],
      baxis: [
        {
          name: "count",
          data: []
        }
      ],
      xoptions: options,
      yoptions: {
        ...options,
        title: {
          text: "Dorsal - Ventral",
          align: "center",
          style: {
            color: "#ffffff"
          }
        },
        colors: ["#00ff00"]
      },
      zoptions: {
        ...options,
        title: {
          text: "Lateral - Medial",
          align: "center",
          style: {
            color: "#ffffff"
          }
        },
        colors: ["#0000ff"]
      },
      axisHeight: 200,
      neuroviz: null,
      // Locally lazy-loaded soma data
      localSomas: [],
      somaLoadBatches: 0
    };
  },
  computed: {
    ...mapState({
      theme: state => state.theme,
      results: state => state.region.results,
      regionType: state => state.region.regionType,
      regionData: state => state.region.regionData,
      sessionUserInfo: state => state.session.userInfo,
      barValues: state => state.analyze.barValues
    }),

    // Prefer the somas passed in via prop, otherwise use the locally lazy-loaded data
    effectiveSomas() {
      if (this.somas && this.somas.length > 0) {
        return this.somas;
      }
      return this.localSomas;
    },

    isMouse() {
      return process.env.VUE_APP_TARGET === "mouse";
    },

    forbiddenDownload() {
      return process.env.VUE_APP_SUB_SPECIES === "rbm";
    },

    isSummarization() {
      return this.sessionUserInfo && this.isMouse && !this.forbiddenDownload;
    },

    boptions() {
      const categories =
        this.barValues?.map(item => item.name.split(" ")[0] || item.name) || [];
      const width = this.barValues.length * 60;
      return {
        ...chartOptions,
        chart: {
          ...chartOptions.chart,
          width: width < 600 ? 600 : width
        },
        xaxis: {
          ...chartOptions.xaxis,
          categories: categories,
          labels: {
            ...chartOptions.xaxis.labels,
            show: true,
            rotate: -45,
            rotateAlways: false,
            hideOverlappingLabels: false,
            trim: false,
            minHeight: 60,
            maxHeight: 120
          },
          axisTicks: {
            show: true
          },
          axisBorder: {
            show: true
          }
        },
        tooltip: {
          style: {
            padding: "10px"
          },
          enabled: true,
          shared: true,
          intersect: false, // Allow triggering anywhere within the bar area
          followCursor: true, // Follow the cursor
          custom: ({ series, seriesIndex, dataPointIndex }) => {
            const neuronName =
              this.barValues[dataPointIndex]?.name?.split(" ")[0] || "Unknown";

            return (
              '<div class="bar-box" style="padding:10px">' +
              "<div style='padding-bottom:10px'>Soma location: " +
              neuronName +
              "</div>" +
              "<div>Soma count: " +
              series[seriesIndex][dataPointIndex] +
              "</div>" +
              "</div>"
            );
          }
        }
      };
    }
  },
  watch: {
    boptions: {
      handler: "updateBarChart",
      immediate: false
    },

    somas: {
      handler: "loadSomasIfNeeded",
      immediate: true
    },

    effectiveSomas: {
      handler: "updateApex",
      immediate: true
    },

    neuronItems: {
      handler: "loadSomasIfNeeded",
      immediate: true
    },

    regionType: {
      handler: "loadRoot",
      immediate: true
    },

    barValues: {
      handler: "updateBarChart",
      deep: true,
      immediate: true
    }
  },

  created() {
    const windowHeight = window.innerHeight;
    this.axisHeight = Math.max(150, (windowHeight * 0.5 - 100) / 3);
  },

  mounted() {
    this.$nextTick(() => {
      setTimeout(() => {
        this.updateBarChart();
      }, 100);
    });
  },

  methods: {
    initView() {
      if (this.neuroviz === null && window.NeuroViz !== undefined) {
        this.neuroviz = new window.NeuroViz(
          process.env.VUE_APP_NEUROVIZ + "/experiments/lib/",
          process.env.VUE_APP_NEUROVIZ_SRV
        );

        return this.neuroviz
          .init({
            useTHREE: process.env.VUE_APP_NEUROVIZ_USE_THREE === "true",
            background: [0, 0, 0],
            rootContainer: document.querySelector("#somas-view")
          })
          .then(() => {
            this.neuroviz.setSpecies(
              process.env.VUE_APP_TARGET === "monkey"
                ? "macaque"
                : process.env.VUE_APP_TARGET
            );
            if (process.env.VUE_APP_SUBTYPE === "lc") {
              this.neuroviz.setSomaSize(5);
            }
            this.neuroviz.setCamera("sagittal");
            this.neuroviz.setCubeAxesVisibility(false);
            this.loadRoot();
            return this.neuroviz;
          });
      }

      return Promise.resolve(this.neuroviz);
    },

    analyzeSomaDistributionFunc() {
      this.$store.commit("session/setChatIsVisible", true);
      this.$store.commit("session/setAnalyzingValues", {
        result: this.barValues,
        type: "soma_distribution"
      });
    },

    async getAnalyzeResult() {
      // Wait for the worker to finish via the child component, to avoid barValues in the store not yet being updated
      const tree = this.$refs.somaDistributionTree;
      const result = tree ? await tree.getAnalyzeResult() : this.barValues;
      return {
        result,
        type: "soma_distribution"
      };
    },

    downloadCSVFunc() {
      // Convert data to CSV format
      const somaData = this.effectiveSomas;
      const header = "NeuronId,x,y,z\n";
      const rowsValue = somaData.map((item, index) => {
        return [this.neuronItems[index]?.file, item[0], item[1], item[2]];
      });
      const rows = rowsValue
        .map(row => row.map(value => `="${value}"`).join(","))
        .join("\n");
      const vals = header + rows;
      downloadCSV(vals, "soma_ coordinates");
    },

    updateApex(somas) {
      if (somas === undefined || somas.length === 0) {
        return;
      }

      this.updateAxis(somas, 0, this.xaxis, this.$refs.x);
      this.updateAxis(somas, 1, this.yaxis, this.$refs.y);
      this.updateAxis(somas, 2, this.zaxis, this.$refs.z);
    },

    updateAxis(somas, index, field, ref) {
      const values = somas.map(i => i[index]);
      const min = Math.min(...values);
      const max = Math.max(...values);
      const data = field[0].data;
      data.length = 0;

      if (min === max) {
        data.push([values[0], values.length]);
      } else {
        const binSize = 20;
        const bin = {};
        const step = (max - min) / binSize;
        for (let i = 0; i < binSize; i++) {
          bin[min + i * step] = 0;
        }
        values.forEach(v => {
          const index = Math.round((v - min) / step) * step + min;
          if (!bin[index]) {
            bin[index] = 1;
          } else {
            bin[index]++;
          }
        });

        for (let k in bin) {
          data.push([Number(k), bin[k]]);
        }

        data.sort((a, b) => {
          if (a[0] > b[0]) {
            return 1;
          } else {
            return -1;
          }
        });

        ref?.updateSeries(field);
      }
    },

    updateSomas() {
      if (!this.isRegionType) {
        this.$refs.somaDistributionTree?.computeTree();
      }
    },

    async loadSomasIfNeeded() {
      // No need to load again if soma data already exists (from prop or already loaded)
      if (this.effectiveSomas && this.effectiveSomas.length > 0) return;
      // Can't load without neuronItems
      if (!this.neuronItems || this.neuronItems.length === 0) return;
      // Avoid duplicate loading if already in progress
      if (this.somaLoadBatches > 0) return;

      const BATCH_SIZE = 30;
      const items = this.neuronItems;
      const results = [];
      this.somaLoadBatches = 0;

      try {
        for (let i = 0; i < items.length; i += BATCH_SIZE) {
          const batch = items.slice(i, i + BATCH_SIZE);
          const batchResults = await Promise.all(
            batch.map(item =>
              window.neuroViz?.getSoma(item.file).catch(() => null)
            )
          );
          results.push(...batchResults.filter(Boolean));
          this.somaLoadBatches++;
          // Update incrementally so the chart is displayed progressively
          this.localSomas = [...results];
        }
      } catch (e) {
        console.warn("Soma lazy load failed:", e);
      }
    },

    updateBarChart() {
      if (!this.barValues || this.barValues.length === 0) {
        return;
      }

      const series = [
        {
          name: "Soma Count",
          data: this.barValues.map(item => item.count)
        }
      ];

      const options = this.boptions;

      this.$nextTick(() => {
        if (this.$refs.b) {
          this.$refs.b.updateOptions(options, false, true);
          this.$refs.b.updateSeries(series, true);
        } else {
          console.log("Chart reference not available");
        }
      });

      // Avoid adding the wheel listener more than once
      if (this.$refs.bCharts && !this._bChartsWheelBound) {
        this._bChartsWheelBound = true;
        this.$refs.bCharts.addEventListener(
          "wheel",
          this.onHorizentalScrollTabs
        );
      }
    },

    onHorizentalScrollTabs(e) {
      e.preventDefault();
      this.$refs.bCharts.scrollLeft += e.deltaY * 0.5;
    },

    loadRoot() {
      const rootSubTypeArray = this.regionType["sub_type_array"];
      if (this.neuroviz !== null && rootSubTypeArray) {
        const uid = this.regionType[rootSubTypeArray[0]]["uid_array"][0];
        const root = this.regionData[uid];
        this.neuroviz.load(root.file).then(() => {
          this.neuroviz.setColor(root.file, [1, 1, 1, 0.3]);
        });
      }
    },

    updatePercentBarStyle() {
      this.$refs.somaDistributionTree.updatePercentBarStyle();
    }
  },

  beforeDestroy() {
    if (this.$refs.bCharts && this._bChartsWheelBound) {
      this.$refs.bCharts.removeEventListener(
        "wheel",
        this.onHorizentalScrollTabs
      );
    }
  }
};
</script>

<style lang="scss" scoped>
.header {
  margin: 20px;
  background: #ffc42c19;
  height: 36px;
  border-left: 2px solid #ffc42c;
  display: flex;
  align-items: center;
  padding: 10px;
  font-size: 13px;
}

.distribution-charts {
  display: flex;
  justify-content: space-around;
  flex-wrap: wrap;
  align-items: center;
}

.bar-charts {
  margin: 0 auto;
  max-width: 600px;
  overflow-y: hidden;
  overflow-x: auto;
}
.bar-charts-title {
  text-align: center;
  color: #ffffff;
}

// .apexcharts-yaxis {
//   transform: translate(0, 0);
// }

:deep {
  .apexcharts-tooltip {
    background: #f3f3f3;
    color: black !important;
  }

  .apexcharts-title-text {
    font-weight: normal;
  }

  // .apexcharts-xaxis-label {
  //   color: #ff0000;
  // }
}
</style>
