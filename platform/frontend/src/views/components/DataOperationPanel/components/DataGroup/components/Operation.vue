<template>
  <div>
    <div class="filter-header">
      <span class="accent-1--text" style="font-size: 16px; font-weight: 500"
        >Operation</span
      >
      <div
        class="accent-3"
        style="height: 1px; flex-grow: 1; margin-left: 10px"
      ></div>
    </div>

    <div class="d-flex flex-column my-4">
      <span
        class="accent-4--text"
        style="font-size: 13px; font-weight: 400; margin-bottom: 10px"
      >
        Visualization
      </span>
      <div class="d-flex flex-row">
        <span
          class="button"
          :class="disabledBtnTag"
          @click="onAddToScene(false)"
        >
          Add to scene
        </span>
        <span
          class="button"
          :class="disabledBtnTag"
          @click="onAddToScene(true)"
          style="margin-left: 10px"
        >
          Add to scene with soma only
        </span>
        <span
          v-if="showExtremeButton"
          class="button extreme-btn"
          :class="disabledBtnTag"
          @click="onAddToSceneExtreme"
          style="margin-left: 10px"
        >
          Add to scene extreme mode
        </span>
      </div>
    </div>
    <div class="accent-3" style="height: 1px"></div>
    <div class="d-flex flex-column my-4">
      <span
        class="accent-4--text"
        style="font-size: 13px; font-weight: 400; margin-bottom: 10px"
      >
        Analyzing
      </span>
      <div class="d-flex flex-row">
        <span class="button" :class="disabledBtnTag" @click="onAnalyze">
          Analyze
        </span>
      </div>
    </div>
    <div class="accent-3" style="height: 1px"></div>
    <div class="d-flex flex-column my-4">
      <span
        class="accent-4--text"
        style="font-size: 13px; font-weight: 400; margin-bottom: 10px"
      >
        Operation
      </span>
      <div class="d-flex flex-row">
        <span class="button" :class="disabledBtnTag" @click="downloadFunc">
          Download
        </span>
      </div>
    </div>
    <NeuronLoadWarning
      title="Add Selected Neurons"
      :showDialog="showLoadWaring"
      :total="tobeLoaded.length"
      :random="100"
      @close="showLoadWaring = false"
      @confirm="onApplyNeuronLoadWarning"
    ></NeuronLoadWarning>
  </div>
</template>

<script>
import { mapState, mapGetters } from "vuex";
import { loadNeuron } from "@/utils/neuronLoader";
import { loadProjectionFiles } from "@/utils/projectionLoader";
import { randomColor, throttle } from "@/utils/utils.js";
import NeuronLoadWarning from "@/components/NeuronLoadWarning.vue";
import { md5 } from "js-md5";

export default {
  name: "Operation",
  data() {
    return {
      tobeLoaded: [],
      showLoadWaring: false,
      loadSomaOnly: false,
      extremeMode: false
    };
  },

  components: {
    NeuronLoadWarning
  },

  watch: {
    sceneGroupsData() {
      this.tobeLoaded = [];
      this.sceneGroupsData.map(currentGroup => {
        this.setPartsFileFunc(
          {
            id: currentGroup?.id,
            name: currentGroup?.name,
            parts: currentGroup?.parts
          },
          typeof currentGroup?.count === "number" ? "save" : "unsave"
        );
      });
    },

    unsaveToScene() {
      setTimeout(() => {
        this.onAddToScene();
      }, 300);
    }
  },

  computed: {
    ...mapState({
      addGroupFlag: state => state.addGroupFlag,
      addGroupOption: state => state.addGroupOption,
      filteredNeurons: state => state.neuron.filteredNeurons,
      axonData: state => state.axonData,
      terminalData: state => state.terminalData,
      groups: state => state.groups,
      sceneGroups: state => state.sceneGroups,
      groupToScene: state => state.groupToScene,
      unsaveToScene: state => state.unsaveToScene,
      unSaveSceneGroups: state => state.unSaveSceneGroups,
      viewedNeurons: state => state.neuron.viewedNeurons,
      neuronColorScheme: state => state.neuron.colorScheme,
      computedAnalysis: state => state.analyze.computedAnalysis,
      results: state => state.analyze.results
    }),

    ...mapGetters(["userInfo"]),

    sceneGroupsData() {
      return [...this.sceneGroups, ...this.unSaveSceneGroups];
    },

    disabledBtnTag() {
      return this.chooseGroupTag ? "disabled-button" : null;
    },

    chooseGroupTag() {
      return this.tobeLoaded?.length === 0;
    },

    showExtremeButton() {
      return new URLSearchParams(window.location.search).get("extreme") === "true";
    }
  },

  methods: {
    async onAnalyze() {
      const fileNames = this.tobeLoaded.map(item => item.file).join("");
      const md5Code = md5(fileNames);
      // check if the neurons has been analyzed already
      // if not, analyze the neurons
      const analysisItem = this.computedAnalysis.find(
        item => item.md5 === md5Code
      );
      if (analysisItem) {
        // if the result is displayed on the tab, just set it as the current tab
        const targetTab = this.results.find(
          result => result.data.md5 === analysisItem.md5
        );

        if (targetTab) {
          this.$store.commit("analyze/setFocusTab", targetTab);
          return;
        }

        // Already cached, no need to execute again
        this.$store.commit("analyze/addResult", analysisItem);
        return;
      }

      const {
        axonHeatMapValue,
        terminalHeatMapValue
      } = await loadProjectionFiles(this.tobeLoaded);
      const somas = await Promise.all(
        this.tobeLoaded.map(i => window.neuroViz.getSoma(i.file))
      );

      let str = this.tobeLoaded.length + " neurons (";
      if (this.tobeLoaded.length > 2) {
        str +=
          this.tobeLoaded
            .slice(0, 2)
            .map(item => item.file.slice(0, -4))
            .join(",") + "... )";
      } else {
        str +=
          this.tobeLoaded.map(item => item.file.slice(-4, -1)).join(",") + " )";
      }
      this.$store.commit("analyze/addResult", {
        md5: md5Code,
        somas,
        heatMapType: "neuron",
        axonHeatMapValue,
        terminalHeatMapValue,
        items: [...this.tobeLoaded],
        dataSource: str,
        type: "neuron"
      });

      this.$store.commit("analyze/addComputedAnalysis", {
        md5: md5Code,
        somas,
        heatMapType: "neuron",
        axonHeatMapValue,
        terminalHeatMapValue,
        items: [...this.tobeLoaded],
        dataSource: str,
        type: "neuron"
      });
    },

    setPartsFileFunc({ id, name, parts }, save = "unsave") {
      for (let i = 0; i < parts?.length; i++) {
        parts[i]?.files?.forEach(item => {
          // Check whether there was a previous overlapping entry
          const lastNeuron = this.tobeLoaded.find(
            neuron => neuron.file === item
          );
          if (lastNeuron) {
            lastNeuron.groups.push({ id, name, save });
          } else {
            this.tobeLoaded.push({
              groups: [{ id, name, save }],
              colorScheme: "random",
              selected: false,
              project: parts[i].project,
              file: item,
              idColor: randomColor(1.0)
            });
          }
        });
      }
    },

    setCallback() {
      if (window.neuroViz) {
        window.neuroViz.on("load", this.loadedCallback);
      } else {
        setTimeout(() => {
          this.setCallback();
        }, 300);
      }
    },

    onApplyNeuronLoadWarning(payload) {
      this.showLoadWaring = false;
      // Dedup by file first (NeuroViz keys by filename), then random sample
      const seen = new Set();
      this.tobeLoaded = this.tobeLoaded.filter(el => {
        if (!el?.file || seen.has(el.file)) return false;
        seen.add(el.file);
        return true;
      });
      if (payload.selectedOption === "random") {
        const count = Math.min(
          parseInt(payload.randomCount, 10) || 0,
          this.tobeLoaded.length
        );
        this.tobeLoaded = this.tobeLoaded
          .slice()
          .sort(() => Math.random() - 0.5)
          .slice(0, count);
      }
      if (this.extremeMode) {
        this.extremeMode = false;
        this.addNeuronsToSceneExtreme();
      } else {
        this.addNeuronsToScene(this.loadSomaOnly);
        this.loadSomaOnly = false;
      }
    },

    loadedCallback(para) {
      // loadNeuron already commits addViewedNeurons in its promise chain,
      // so we only need to clean up tobeLoaded here (avoiding double-commit)
      const idx = this.tobeLoaded.findIndex(el => el.file === para.filename);
      if (idx !== -1) {
        this.tobeLoaded.splice(idx, 1);
      }
    },

    onAddToSceneExtreme: throttle(function() {
      if (!this.chooseGroupTag) {
        if (this.tobeLoaded.length > 500) {
          this.showLoadWaring = true;
          this.extremeMode = true;
        } else {
          this.addNeuronsToSceneExtreme();
        }
      }
    }, 2000),

    addNeuronsToSceneExtreme() {
      const files = this.tobeLoaded.map(el => el.file);
      const total = files.length;
      if (total === 0) return;

      this.$store.commit("resetLoadingState");
      this.$store.commit("addTotalLoadingCount");

      const onProgress = (loaded, t) => {
        this.$store.state.loadedCount = loaded;
        this.$store.state.totalLoadingCount = t;
      };

      window.neuroViz.mergeBatchSWCs(files, {
        onProgress,
        swcOptions: { mainBranch: false, axon: true, dendrite: true, undefined: true }
      }).then(() => {
        // Commit all loaded neurons to viewedNeurons at once
        this.$store.commit("neuron/addViewedNeurons", this.tobeLoaded);
        this.$store.commit("resetLoadingState");
        this.tobeLoaded = [];
        this.$store.commit("setAddFromScene", "group");
        setTimeout(() => {
          this.$store.commit("setGroupToScene", !this.groupToScene);
        }, 600);
      }).catch(err => {
        console.error("mergeBatchSWCs failed:", err);
        this.$store.commit("resetLoadingState");
      });
    },

    addNeuronsToScene(somaOnly) {
      if (this.tobeLoaded.length > 20000) {
        const newV = true;
        this.$store.commit("setSettingValues", {
          data: newV,
          index: "mode"
        });
        const viewedCopy = [...this.viewedNeurons];
        viewedCopy.forEach(item => {
          item?.visible && loadNeuron(item, false, newV);
        });
      }
      // Triggered repeatedly, so the data needs to be saved
      this.tobeLoaded.forEach(element => {
        // Previously this sometimes wouldn't trigger loadedback, but the group info still needs to be updated
        const currentItem = this.viewedNeurons.find(
          item => item.file === element.file
        );
        if (currentItem) {
          // Use the already-loaded viewedNeurons object (preserving user-modified properties like color), only update groups
          currentItem.groups = element?.groups;
          loadNeuron(currentItem, somaOnly);
        } else {
          loadNeuron(element, somaOnly);
        }
      });
      this.$store.commit("setAddFromScene", "group");
      setTimeout(() => {
        this.$store.commit("setGroupToScene", !this.groupToScene);
      }, 600);
    },

    downloadFunc() {
      if (this.userInfo) {
        this.$emit("downloadNeurons", [...this.tobeLoaded]);
        return;
      }
      this.$store.commit("setLoginFlag", true);
    }
  },

  mounted() {
    this.setCallback();
  },

  beforeDestroy() {
    if (window.neuroViz) {
      window.neuroViz.off("load", this.loadedCallback);
    }
  }
};
</script>

<style lang="scss" scoped></style>
