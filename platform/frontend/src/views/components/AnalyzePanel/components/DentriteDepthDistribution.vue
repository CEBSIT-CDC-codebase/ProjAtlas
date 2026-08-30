<template>
  <div class="soma-distribution">
    <div class="header">
      <span style="font-weight: 600">Data:</span>
      <span class="primary-text--text truncate">{{ dataSource }}</span>
      <span style="font-weight: 600; margin-left: 30px">Analyzing: </span>
      <span class="primary-text--text truncate"
        >&nbsp;Soma and Dendrite Depth Distribution Analysis</span
      >
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
      <apexchart
        type="area"
        width="600px"
        :height="axisHeight"
        :options="iplOptions"
        ref="ipl"
        :series="iplAxis"
      ></apexchart>
    </div>
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
    text: "Soma: IPL_depth",
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
export default {
  name: "DentriteDepthDistribution",
  props: {
    neuronItems: {
      type: Array,
      default: () => []
    },
    dataSource: {
      type: String,
      default: ""
    }
  },
  components: {
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
      iplAxis: [
        {
          data: []
        }
      ],
      xoptions: options,
      yoptions: {
        ...options,
        title: {
          text: "Soma: Nasal-Temporal",
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
          text: "Soma: Dorsal-Ventral",
          align: "center",
          style: {
            color: "#ffffff"
          }
        },
        colors: ["#0000ff"]
      },
      iplOptions: {
        ...options,
        title: {
          text: "Dendrite: INL-GCL",
          align: "center",
          style: {
            color: "#ffffff"
          }
        },
        yaxis: {
          ...options.yaxis,
          min: 0,
          tickAmount: 5,
          forceNiceScale: true,
          labels: {
            ...options.yaxis.labels,
            formatter: val => {
              if (val === 0) return "0";
              const absVal = Math.abs(val);
              if (absVal >= 0.01) return val.toFixed(3);
              if (absVal >= 0.001) return val.toFixed(4);
              return val?.toExponential(2);
            }
          }
        },
        colors: ["#25d1d8"]
      },
      axisHeight: 200,
      neuroviz: null
    };
  },
  computed: {
    ...mapState({
      theme: state => state.theme,
      results: state => state.region.results,
      barValues: state => state.analyze.barValues,
      dendritesIPL: state => state.neuron.dendritesIPL
    }),

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

    neuronItems: {
      handler: "updateApex",
      immediate: true
    }
  },

  created() {
    const windowHeight = window.innerHeight;
    this.axisHeight = Math.max(150, (windowHeight * 0.5 - 100) / 3);
  },

  methods: {
    getNiceAxisMax(rawMax) {
      if (!Number.isFinite(rawMax) || rawMax <= 0) return 1;
      const target = rawMax * 1.08;
      const magnitude = Math.pow(10, Math.floor(Math.log10(target)));
      const normalized = target / magnitude;
      let nice = 10;
      if (normalized <= 1) nice = 1;
      else if (normalized <= 2) nice = 2;
      else if (normalized <= 2.5) nice = 2.5;
      else if (normalized <= 5) nice = 5;
      return nice * magnitude;
    },

    updateApex(neuronItems) {
      if (neuronItems === undefined || neuronItems.length === 0) {
        return;
      }

      this.updateAxis(0, this.xaxis, this.$refs.x);
      this.updateAxis(1, this.yaxis, this.$refs.y);
      this.updateAxis(2, this.zaxis, this.$refs.z);
      this.updateIPLAxis();
    },

    updateAxis(index, field, ref) {
      const values = this.neuronItems.map(i =>
        index === 0
          ? i["ipl_depth"]
          : index === 1
          ? i["nasal_temporal"]
          : i["dorso_ventral"]
      );
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

    updateIPLAxis() {
      const swcFiles = this.neuronItems.map(i => i["file"]);
      const indexs = swcFiles.map(f => this.dendritesIPL.nameToIndex.get(f));
      const rows = indexs
        .filter(i => i !== undefined)
        .map(i =>
          this.dendritesIPL.matrix.subarray(
            i * this.dendritesIPL.numCols,
            (i + 1) * this.dendritesIPL.numCols
          )
        );

      if (rows.length === 0) {
        this.iplAxis[0].data = [];
        this.$refs.ipl?.updateSeries(this.iplAxis);
        return;
      }

      const values = [];
      for (let i = 0; i < this.dendritesIPL.numCols; i++) {
        let sum = 0;
        for (let j = 0; j < rows.length; j++) {
          sum += rows[j][i];
        }
        values.push(sum);
      }
      const data = this.iplAxis[0].data;
      data.length = 0;

      const max = Math.max(...values);
      const yMax = this.getNiceAxisMax(max);

      this.$refs.ipl?.updateOptions({
        yaxis: {
          ...this.iplOptions.yaxis,
          min: 0,
          max: yMax,
          tickAmount: 5,
          forceNiceScale: true
        }
      });

      if (max === 0) {
        data.push([values[0], values.length]);
      } else {
        for (let i = 0; i < this.dendritesIPL.numCols; i++) {
          data.push([i, values[i]]);
        }
      }

      this.$refs.ipl?.updateSeries(this.iplAxis);
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
