<template>
  <div class="region-data">
    <div class="filter-header">
      <span class="accent-1--text" style="font-size: 16px; font-weight: 500">
        Filter
      </span>
      <div
        class="accent-3"
        style="height: 1px; flex-grow: 1; margin: 0 10px"
      ></div>
      <div
        class="pa-1 refresh-icon"
        style="
          display: flex;
          justify-content: center;
          align-items: center;
          border-radius: 2px;
          cursor: pointer;
        "
        @click="$refs.regionFilter.clearSearch()"
      >
        <v-icon size="16">$FilterRefresh</v-icon>
      </div>
    </div>

    <RegionFilter ref="regionFilter" @loadRoot="loadRoot"></RegionFilter>

    <div class="operation-header">
      <span class="accent-1--text" style="font-size: 16px; font-weight: 500"
        >Operation</span
      >
      <div
        class="accent-3"
        style="height: 1px; flex-grow: 1; margin-left: 10px"
      ></div>
    </div>

    <div class="d-flex flex-column">
      <span
        class="accent-4--text"
        style="font-size: 13px; font-weight: 400; margin-bottom: 10px"
      >
        Visualization
      </span>
      <div class="d-flex flex-row" style="margin-bottom: 16px">
        <span :class="buttonClass" class="button" @click="onAddToScene">
          Add to scene
        </span>
        <span
          :class="buttonClass"
          class="button"
          style="margin-left: 10px"
          @click="onAddToSceneWithNeurons"
        >
          Add to scene with its neurons
        </span>
      </div>
    </div>
    <div
      class="accent-3"
      style="height: 1px"
    ></div>
    <div
      class="d-flex flex-column mt-4"
      @click="onAnalyze"
    >
      <span
        class="accent-4--text"
        style="font-size: 13px; font-weight: 400; margin-bottom: 10px"
      >
        Analyzing
      </span>
      <span :class="enableAnalyze" class="button">Analyze</span>
    </div>
    <NeuronLoadWarning
      title="Add Region with its Neurons"
      :total="tobeLoaddedNeurons.length"
      :showDialog="showNeuronLoadWarning"
      :random="100"
      @close="showNeuronLoadWarning = false"
      @confirm="onApplyNeuronLoadWarning"
    ></NeuronLoadWarning>
  </div>
</template>

<script>
import { mapState } from "vuex";
import RegionFilter from "./components/RegionFilter.vue";
import { formatNeuronData } from "@/utils/neuronFilterTool.js";
import { loadRegion, loadNeuron } from "@/utils/neuronLoader";
import NeuronLoadWarning from "@/components/NeuronLoadWarning.vue";
import { md5 } from "js-md5";
const { loadInitialRbmRegions } = require("@/utils/rbmInitialRegionLoad");
export default {
  name: "RegionData",
  components: {
    RegionFilter,
    NeuronLoadWarning
  },
  data() {
    return {
      tobeLoadedRegions: [],
      tobeLoaddedNeurons: [],
      showNeuronLoadWarning: false
    };
  },
  computed: {
    ...mapState({
      regionData: state => state.region.regionData,
      regionType: state => state.region.regionType,
      filteredRegions: state => state.region.filteredRegions,
      regionNeuronRelation: state => state.neuron.regionNeuronRelation,
      projects: state => state.projects,
      neuronTypeColors: state => state.neuron.typeColors,
      neuronData: state => state.neuron.neuronData,
      regionColorScheme: state => state.region.colorScheme,
      computedAnalysis: state => state.analyze.computedAnalysis,
      results: state => state.analyze.results,
      viewedRegions: state => state.region.viewedRegions
    }),

    buttonClass() {
      return this.filteredRegions?.length === 0
        ? "disabled-button"
        : "background";
    },

    enableAnalyze() {
      return this.filteredRegions?.length !== 1
        ? "disabled-button"
        : "background";
    }
  },

  methods: {
    async loadRoot() {
      if (window.neuroViz) {
        if (process.env.VUE_APP_SUB_SPECIES === "rbm") {
          await loadInitialRbmRegions(this.filteredRegions, loadRegion);
          return;
        }

        this.onAddToScene();
      } else {
        setTimeout(() => {
          this.loadRoot();
        }, 300);
      }
    },

    onAddToScene() {
      // const viewedUIDs = this.viewedRegions.map(el => el.uid);
      if (this.filteredRegions?.length !== 0) {
        let regions = [...this.filteredRegions];
        this.tobeLoadedRegions.push(...regions);
        this.tobeLoadedRegions = [...new Set(this.tobeLoadedRegions)];
        // this.tobeLoadedRegions = this.tobeLoadedRegions.filter(
        //   el => !viewedUIDs.includes(el.regionObj.uid_array[0])
        // );
        this.tobeLoadedRegions.forEach(el => {
          loadRegion(el);
        });

        this.tobeLoadedRegions = [];
      }
    },

    onAddToSceneWithNeurons() {
      if (this.filteredRegions?.length !== 0) {
        this.tobeLoadedRegions.push(...this.filteredRegions);
        this.tobeLoadedRegions = [...new Set(this.tobeLoadedRegions)];
        const regionsForNeurons = [...this.tobeLoadedRegions];

        const viewedUIDs = this.viewedRegions.map(el => el.uid);

        this.tobeLoadedRegions = this.tobeLoadedRegions.filter(
          el => !viewedUIDs.includes(el.regionObj.uid_array[0])
        );

        this.tobeLoadedRegions.forEach(el => {
          loadRegion(el);
        });
        this.tobeLoadedRegions = [];

        this.tobeLoaddedNeurons = [];
        regionsForNeurons.forEach(element => {
          const uid = element.regionObj.uid_array[0];

          // find all the neurons which soma is in this region
          const projectNames = this.projects.map(el => el.name);
          projectNames.forEach(name => {
            const projectData = this.regionNeuronRelation[name];
            if (!projectData) return;
            const relation = projectData[uid];
            if (!relation) return;

            const neuronsUID = relation.owned_neuron_array;
            const neurons = formatNeuronData(
              neuronsUID,
              name,
              this.neuronData,
              this.neuronTypeColors
            );
            this.tobeLoaddedNeurons.push(...neurons);
          });
        });

        if (this.tobeLoaddedNeurons.length > 500) {
          this.showNeuronLoadWarning = true;
        } else {
          this.tobeLoaddedNeurons.forEach(el => {
            loadNeuron(el);
          });
        }
      }
    },

    onApplyNeuronLoadWarning(payload) {
      this.showNeuronLoadWarning = false;
      if (payload.selectedOption === "random") {
        const count = payload.randomCount;
        const randomItems = this.tobeLoaddedNeurons
          .sort(() => Math.random() - 0.5)
          .slice(0, count);
        randomItems.forEach(el => {
          loadNeuron(el);
        });
      } else {
        this.tobeLoaddedNeurons.forEach(el => {
          loadNeuron(el);
        });
      }

      this.tobeLoaddedNeurons = [];
    },

    async onAnalyze() {
      if (this.filteredRegions.length !== 1) {
        return;
      }

      this.$store.commit("analyze/setAddResultFlag", true);
      const region = this.filteredRegions[0];
      let somaNeurons = [];
      let projectionNeurons = [];

      this.projects.forEach(p => {
        const projectRelation = this.regionNeuronRelation[p.name];
        if (!projectRelation) return;
        let relation = projectRelation[region.regionObj.uid_array[0]];
        // If relation is undefined, this region has no related neurons; initialize with empty arrays
        if (!relation) {
          relation = {
            owned_neuron_array: [],
            projecting_neuron_array: [],
            recipient_neuron_array: [],
            terminal_array: []
          };
        }
        const somaNeuronUIDs = relation.owned_neuron_array;
        const somaNeuronItems = somaNeuronUIDs.map(
          uid => (this.neuronData[p.name] || {})[uid]
        ).filter(Boolean);
        somaNeurons.push(...somaNeuronItems);

        const projectionNeuronUIDs = relation.projecting_neuron_array;
        const projectionNeuronItems = projectionNeuronUIDs.map(
          uid => (this.neuronData[p.name] || {})[uid]
        ).filter(Boolean);
        projectionNeurons.push(...projectionNeuronItems);
      });

      somaNeurons = [...new Set(somaNeurons)];
      projectionNeurons = [...new Set(projectionNeurons)];

      const totalNeurons = [...new Set([...somaNeurons, ...projectionNeurons])];

      const fileNames = totalNeurons.map(item => item.file).join("");
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
          this.$store.commit("analyze/setAddResultFlag", false);
          return;
        }
      }
      const somas = [];
      const axonHeatMapValue = {};
      const terminalHeatMapValue = {};
      this.$store.commit("analyze/addResult", {
        md5: md5Code,
        somas,
        somaCount: somaNeurons.length,
        projectionCount: projectionNeurons.length,
        heatMapType: "neuron",
        axonHeatMapValue,
        terminalHeatMapValue,
        items: totalNeurons,
        dataSource: region.name,
        type: "region",
        acronym: this.regionData[region.regionObj.uid_array[0]].acronym,
        name: region.name
      });

      this.$store.commit("analyze/addComputedAnalysis", {
        md5: md5Code,
        somas,
        heatMapType: "neuron",
        axonHeatMapValue,
        terminalHeatMapValue,
        items: totalNeurons,
        dataSource: region.name,
        type: "region",
        acronym: this.regionData[region.regionObj.uid_array[0]].acronym,
        name: region.name
      });
    }
  }
};
</script>

<style lang="scss" scoped>
* {
  font-size: 13px;
  font-family: Roboto;
}

.region-data {
  display: flex;
  flex-direction: column;
}

.filter-header,
.operation-header {
  display: flex;
  align-items: center;
  margin: 10px 0;
}
</style>
