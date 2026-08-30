<template>
  <div class="main">
    <div class="tree-header accent">
      <span>Structure</span>
      <span class="truncate">Soma Count (pcs)</span>
      <span class="truncate">Density (pcs/µm³)</span>
    </div>
    <v-treeview
      ref="regionTree"
      :items="regionTree"
      :dense="true"
      selected-color="light-blue"
      :activatable="true"
      :hoverable="true"
      :open.sync="openItems"
      color="#c4c4c4;"
      open-on-click
      item-key="id"
    >
      <template v-slot:label="{ item, open }">
        <div class="tree-item">
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <span
                v-bind="attrs"
                v-on="on"
                :style="{
                  paddingLeft: `${item.depth * 10 +
                    (item.children.length === 0 ? 16 : 0)}px`
                }"
              >
                <v-icon v-if="item.children.length > 0" size="16">{{
                  open ? "mdi-menu-down" : "mdi-menu-right"
                }}</v-icon>
                {{ item.name }}
              </span>
            </template>
            <span>{{ item.name }}</span>
          </v-tooltip>
          <div class="soma-count-container">
            <div class="soma-count-bar-container">
              <div
                class="soma-count-bar"
                :style="{
                  width: 'calc(' + (item.somaCount / maxSomaCount) * 100 + '%)'
                }"
              ></div>
            </div>
            <span class="primary-text--text soma-value-span"
              >{{ item.somaCount }}
            </span>
          </div>
          <div class="density-container">
            <div class="density-bar-container">
              <div
                class="density-bar"
                :style="{
                  width: (item.density / maxDensity) * 100 + '%'
                }"
              ></div>
            </div>
            <span class="density-value-span">{{
              item?.density?.toExponential(3)
            }}</span>
          </div>
        </div>
      </template>
    </v-treeview>
  </div>
</template>

<script>
import { mapState } from "vuex";
import { md5 } from "js-md5";
import { computeRegionSomaTree } from "@/utils/neuronFilterTool";
import workerScript from "@/workers/somaTreeWorker.js";

export default {
  name: "SomaDistributionTree",
  props: {
    neuronItems: {
      type: Array,
      default: () => []
    },
    isRegionType: {
      type: Boolean
    }
  },
  data() {
    return {
      regionTree: [],
      openItems: [],
      // totalDensity: 1,
      maxSomaCount: 1,
      maxDensity: 0,
      isComputing: false,
      analyzeResolvers: [],
      pendingResponses: 0,
      treeRecomputed: false
    };
  },
  computed: {
    ...mapState({
      regionSomaTreeArray: state => state.region.regionSomaTreeArray,
      regionNeuronRelation: state => state.neuron.regionNeuronRelation,
      regionData: state => state.region.regionData,
      getNeuronsDone: state => state.neuron.getNeuronsDone,
      cachedTrees: state => state.analyze.cachedSomaTrees,
      cachedList: state => state.analyze.cachedAxonList,
      cachedMaxCount: state => state.analyze.cachedSomaMaxCount,
      cachedMaxDensity: state => state.analyze.cachedSomaMaxDensity
    })

    // totalSomaCount() {
    //   if (this.neuronItems.length === 0) {
    //     return 10000;
    //   }

    //   return this.neuronItems.length;
    // }
  },
  watch: {
    // regionSomaTreeArray: {
    //   handler() {
    //     if (!this.isRegionType) {
    //       this.computeTree();
    //     }
    //   },
    //   deep: true,
    // },

    neuronItems() {
      if (!this.isRegionType) {
        this.computeTree();
      }
      // When there are pending analysis requests, re-trigger once neurons are ready
      if (this.analyzeResolvers.length && !this.isComputing) {
        this.ensureCompute();
      }
    },

    regionSomaTreeArray() {
      // Retry still-pending analysis requests once dependent data is ready/recomputed
      if (this.analyzeResolvers.length && !this.isComputing) {
        this.ensureCompute();
      }
    },

    getNeuronsDone() {
      // Retry still-pending analysis requests once neuron data has finished loading
      if (this.analyzeResolvers.length && !this.isComputing) {
        this.ensureCompute();
      }
    },

    openItems: {
      handler() {
        this.updatePercentBarStyle();
      },
      deep: true
    }
  },
  methods: {
    onDownloadData() {
      const dataStr =
        "data:text/json;charset=utf-8," +
        encodeURIComponent(JSON.stringify(this.regionTree));
      const downloadAnchorNode = document.createElement("a");
      downloadAnchorNode.setAttribute("href", dataStr);
      downloadAnchorNode.setAttribute(
        "download",
        "soma-distribution" + ".json"
      );
      document.body.appendChild(downloadAnchorNode); // required for firefox
      downloadAnchorNode.click();
      downloadAnchorNode.remove();
    },

    getSomaCount(regionItem) {
      if (this.neuronItems.length === 0) {
        return 0;
      }
      let count = 0;
      const regionUID = regionItem.regionObj.uid_array[0];
      this.neuronItems.forEach(neuron => {
        const project = neuron.projectFullName;
        const projectData = this.regionNeuronRelation[project];
        if (!projectData) return;
        const relationItem = projectData[regionUID];

        if (
          relationItem &&
          relationItem.owned_neuron_array.includes(neuron.id)
        ) {
          count++;
        }
      });

      if (count > this.maxSomaCount) {
        this.maxSomaCount = count;
      }

      return count;
    },

    computeTree() {
      this.regionTree = [];
      if (this.regionSomaTreeArray.length === 0) {
        return;
      }
      // Skip computation for empty neurons, to avoid polluting results with an empty outcome
      if (!this.neuronItems || this.neuronItems.length === 0) {
        return;
      }

      const md5Code = md5(JSON.stringify(this.neuronItems));

      // A cache hit also requires a non-empty result, otherwise fall through to recompute via the worker
      if (this.cachedTrees[md5Code] && this.cachedList[md5Code]?.length) {
        this.regionTree = JSON.parse(this.cachedTrees[md5Code]);
        this.maxSomaCount = this.cachedMaxCount[md5Code];
        this.maxDensity = this.cachedMaxDensity[md5Code];
        this.$store.commit("analyze/setBarValues", this.cachedList[md5Code]);
        this.resolveAnalyzeResult();
        return;
      }

      this.$store.commit("analyze/addCachedSomaTree", {
        key: md5Code,
        list: [],
        tree: JSON.stringify(this.regionTree),
        maxCount: this.maxSomaCount,
        maxDensity: this.maxDensity
      });

      // Prepare the data to send to the worker
      const workerData = {
        regionSomaTreeArray: this.regionSomaTreeArray,
        neuronItems: this.neuronItems,
        regionNeuronRelation: this.regionNeuronRelation,
        regionData: this.regionData,
        target: process.env.VUE_APP_TARGET
      };

      // Send data to the worker for processing
      this.pendingResponses++;
      this.isComputing = true;
      this.somaWorker.postMessage(workerData);
    },

    getAnalyzeResult() {
      const current = this.$store.state.analyze.barValues;
      // A result already exists and is not being computed, return directly
      if (!this.isComputing && current && current.length) {
        return Promise.resolve(current);
      }
      const promise = new Promise(resolve => {
        this.analyzeResolvers.push(resolve);
      });
      this.ensureCompute();
      return promise;
    },

    ensureCompute() {
      if (this.isComputing) return;
      // Dependent data isn't ready yet, park and wait for the watcher to retry once it is
      if (this.regionSomaTreeArray.length === 0) return;
      if (!this.neuronItems || this.neuronItems.length === 0) return;
      this.computeTree();
      // computeTree did not enter async computation (cache hit already resolved), no further action needed
    },

    resolveAnalyzeResult() {
      this.isComputing = false;
      const result = this.$store.state.analyze.barValues;
      this.analyzeResolvers.forEach(resolve => resolve(result));
      this.analyzeResolvers = [];
    },

    updatePercentBarStyle() {
      this.$nextTick(() => {
        const countBarDivs = document.querySelectorAll(".soma-count-bar");
        const densityBarDivs = document.querySelectorAll(".density-bar");
        const allBarDivs = [...countBarDivs, ...densityBarDivs];
        allBarDivs.forEach(div => {
          const widthInPercent =
            div.style.width.replace("calc(", "").replace("% - 60px)", "") * 1;
          const widthInPixel = window
            .getComputedStyle(div)
            .getPropertyValue("width")
            .replace("px", "");
          if (widthInPercent > 0 && widthInPixel < 1) {
            div.style.borderLeftWidth = "1px";
            div.style.borderLeftStyle = "solid";
            div.style.borderImage =
              "linear-gradient(to bottom, black 20%, transparent 20%,     black 40%, transparent 40%,     black 60%, transparent 60%,     black 80%, transparent 80%,     black 100%) 1 100%";
          }
        });
      });
    }
  },

  created() {
    // Each component instance owns its own worker, to avoid cross-talk between listeners
    // when multiple instances share the same worker (one reply triggering every instance's listener)
    this.somaWorker = new Worker(workerScript);
  },

  mounted() {
    // Listen for the result returned by the worker
    this.somaWorker.addEventListener("message", e => {
      const {
        neuronItems,
        regionTree,
        regionList,
        maxSomaCount,
        maxDensity
      } = e.data;

      // Cache the result (regardless of whether it's from the latest request)
      const md5Code = md5(JSON.stringify(neuronItems));
      this.$store.commit("analyze/addCachedSomaTree", {
        key: md5Code,
        list: regionList,
        tree: JSON.stringify(regionTree),
        maxCount: maxSomaCount,
        maxDensity: maxDensity
      });

      // When there are multiple computations, only take the last response, to avoid resolving early with a stale/empty response
      if (this.pendingResponses > 0) this.pendingResponses--;
      if (this.pendingResponses > 0) return;

      this.regionTree = regionTree;
      this.maxSomaCount = maxSomaCount;
      this.maxDensity = maxDensity;

      if (regionList.length) {
        regionList.sort((a, b) => b.count - a.count);
        this.$store.commit("analyze/setBarValues", regionList);
        this.resolveAnalyzeResult();
      } else if (this.getNeuronsDone) {
        if (this.treeRecomputed) {
          // The tree is still empty after recomputing with the current full data, treat it as the final result
          this.resolveAnalyzeResult();
        } else {
          // regionSomaTreeArray may have been over-pruned while data wasn't fully loaded, recompute once with the current full data
          this.treeRecomputed = true;
          this.isComputing = false;
          computeRegionSomaTree();
        }
      } else {
        // Data is still loading, keep waiting; recompute once regionSomaTreeArray/getNeuronsDone updates
        this.isComputing = false;
      }
    });
  },

  beforeDestroy() {
    // Terminate the worker when the component is destroyed
    this.somaWorker.terminate();
  }
};
</script>

<style lang="scss" scoped>
* {
  font-size: 13px;
  font-family: Roboto;
  font-weight: 400;
}

.main {
  display: flex;
  flex-direction: column;
  padding: 0 20px;
}
.download-container {
  display: flex;
  align-items: center;
  justify-content: right;
}

.tree-header {
  margin-top: 12px;
  height: 32px;
  display: grid;
  grid-template-columns: 250px 1fr 1fr;
  align-items: center;

  span {
    padding: 0 10px;
  }
}

.tree-item {
  display: grid;
  grid-template-columns: 250px 1fr 1fr;
  align-items: center;
  height: 32px;

  :nth-child(1) {
    //max-width: 250px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.soma-count-container {
  position: relative;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: right;

  .soma-count-bar-container {
    flex-basis: calc(100% - 60px);
    height: 100%;
    display: flex;
    justify-content: left;
    align-items: center;
  }

  .soma-count-bar {
    background: #48d2ff;
    height: 20px;
  }

  .soma-value-span {
    margin-left: 4px;
    width: 60px;
    flex-basis: 60px;
    flex-shrink: 0;
  }
}

.density-container {
  position: relative;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: right;

  .density-bar-container {
    flex-basis: calc(100% - 60px);
    height: 100%;
    display: flex;
    justify-content: left;
    align-items: center;
  }

  .density-bar {
    background: #56f3a8;
    height: 20px;
  }

  .density-value-span {
    margin-right: 10px;
    margin-left: 4px;
    width: 60px;
    flex-basis: 60px;
    flex-shrink: 0;
  }
}

::v-deep .v-treeview-node__level {
  width: 0;
}

::v-deep .v-treeview-node__toggle {
  display: none !important;
}

::v-deep .v-treeview-node__content {
  margin: 0;
}

::v-deep .v-treeview-node__root {
  padding: 0;
}
</style>
