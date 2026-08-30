<template>
  <div class="neuron-data">
    <div class="filter-header">
      <span class="accent-1--text" style="font-size: 16px; font-weight: 500"
        >Data source</span
      >
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
          margin-right: 10px;
          width: 24px;
          height: 24px;
        "
        @click="onDataSourceClearCondition"
      >
        <v-icon size="16">$FilterRefresh</v-icon>
      </div>
      <div
        style="
          width: 24px;
          height: 24px;
          border: 1px solid #343f5c;
          border-radius: 2px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
        "
        @click="showDataSource = !showDataSource"
      >
        <v-icon
          size="16"
          :style="{
            transform: this.showDataSource ? 'rotate(0deg)' : 'rotate(180deg)'
          }"
          >$ArrowDown</v-icon
        >
      </div>
    </div>

    <div v-show="!showDataSource" style="margin: 10px 0">
      <div
        class="d-flex align-center"
        style="justify-content: center; cursor: pointer"
        @click="showDataSource = true"
      >
        <v-icon size="16" style="margin-right: 6px">$Expand</v-icon>
        <span
          class="primary-light--text"
          style="font-size: 13px; font-weight: 400"
        >
          Expand hidden datasource...
        </span>
      </div>
    </div>

    <div v-show="showDataSource">
      <ContentBlock title="Data Group" class="block-item">
        <template>
          <DataGroupFilter
            ref="dataGroupFilter"
            @onFilterClearCondition="onFilterClearCondition"
          ></DataGroupFilter>
        </template>
      </ContentBlock>
    </div>

    <div class="filter-header" style="margin-bottom: 0">
      <span class="accent-1--text" style="font-size: 16px; font-weight: 500"
        >Filter</span
      >
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
          margin-right: 10px;
          width: 24px;
          height: 24px;
        "
        @click="onFilterClearCondition"
      >
        <v-icon size="16">$FilterRefresh</v-icon>
      </div>
      <div
        style="
          width: 24px;
          height: 24px;
          border: 1px solid #343f5c;
          border-radius: 2px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
        "
        @click="showFilter = !showFilter"
      >
        <v-icon
          size="16"
          :style="{
            transform: this.showFilter ? 'rotate(0deg)' : 'rotate(180deg)'
          }"
          >$ArrowDown</v-icon
        >
      </div>
    </div>

    <div v-show="!showFilter" style="margin: 10px 0">
      <div
        class="d-flex align-center"
        style="justify-content: center; cursor: pointer"
        @click="showFilter = true"
      >
        <v-icon size="16" style="margin-right: 6px">$Expand</v-icon>
        <span
          class="primary-light--text"
          style="font-size: 13px; font-weight: 400"
          >Expand hidden filters...</span
        >
      </div>
    </div>

    <div v-show="showFilter">
      <NeuronFilter
        ref="neuronFilter"
        style="overflow: auto; flex-grow: 1; padding-top: 10px"
        @clearCondition="showQueryResult = false"
      ></NeuronFilter>
      <!-- :style="{ maxHeight: 'calc(100vh - ' + filterMinusHeight + 'px )' }" -->
    </div>
    <QueryResult
      v-show="showQueryResult"
      ref="queryResult"
      @showAll="onShowAll"
      @hideAll="filterMinusHeight = 520"
    >
    </QueryResult>

    <div class="operation-header">
      <span class="accent-1--text" style="font-size: 16px; font-weight: 500"
        >Operation</span
      >
      <div
        class="accent-3"
        style="height: 1px; flex-grow: 1; margin-left: 10px; margin-right: 10px"
      ></div>
      <div
        style="
          width: 24px;
          height: 24px;
          border: 1px solid #343f5c;
          border-radius: 2px;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
        "
        @click="showOperations = !showOperations"
      >
        <v-icon
          size="16"
          :style="{
            transform: this.showOperations ? 'rotate(0deg)' : 'rotate(180deg)'
          }"
          >$ArrowDown</v-icon
        >
      </div>
    </div>

    <div v-show="!showOperations" style="margin: 8px 0">
      <div
        class="d-flex align-center"
        style="justify-content: center; cursor: pointer"
        @click="showOperations = true"
      >
        <v-icon size="16" style="margin-right: 6px">$Expand</v-icon>
        <span
          class="primary-light--text"
          style="font-size: 13px; font-weight: 400"
          >Expand hidden operations...</span
        >
      </div>
    </div>

    <div v-show="showOperations">
      <div
        style="
          display: grid;
          grid-template-columns: 1fr 1fr 1fr;
          height: 24px;
          margin-top: 8px;
          margin-bottom: 10px;
        "
      >
        <span
          class="inactive-operation"
          style="text-align: center; line-height: 24px; cursor: pointer"
          :class="currentOperation === operation.name ? 'active-operation' : ''"
          v-for="(operation, index) in operations"
          :key="index"
          @click="currentOperation = operation.name"
          >{{ operation.text }}</span
        >
      </div>
    </div>

    <div v-show="currentOperation === 'visualization' && showOperations">
      <div class="d-flex flex-row mb-2" style="gap: 10px">
        <span
          :class="disabledBtnTag"
          class="button"
          style="width: calc((100% - 10px) / 2)"
          @click="onAddToScene(false)"
        >
          Add to scene
        </span>

        <span
          :class="disabledBtnTag"
          class="button"
          style="width: calc((100% - 10px) / 2)"
          @click="onAddUnsaveGroupFunc"
        >
          Add to scene as a group
        </span>
      </div>
      <div class="d-flex flex-row mb-4" style="gap: 10px">
        <span
          :class="disabledBtnTag"
          class="button"
          style="width: calc((100% - 10px) / 2)"
          @click="onAddToScene(true)"
        >
          Add to scene with soma only
        </span>
        <span
          v-if="showHiResDendritesBtn"
          :class="disabledBtnTag"
          class="button"
          style="width: calc((100% - 10px) / 2)"
          @click="showHiResDendrites"
        >
          Add to scene with Hi-Res dendrites
        </span>
      </div>
      <div v-if="showExtremeButton" class="d-flex flex-row mb-4">
        <span
          :class="disabledBtnTag"
          class="button extreme-btn"
          style="width: 100%"
          @click="onAddToSceneExtreme"
        >
          Add to scene extreme mode
        </span>
      </div>
    </div>
    <div v-show="currentOperation === 'analyzing' && showOperations">
      <div class="d-flex flex-row mb-4">
        <span
          @click="onAnalyze"
          :class="analyzeDisabledBtnTag"
          class="button"
          style="margin-right: 10px"
          >Analyze</span
        >
        <span class="button" style="opacity: 0"> </span>
      </div>
    </div>
    <div v-show="currentOperation === 'more' && showOperations">
      <div class="d-flex flex-row mb-4">
        <span
          :class="disabledBtnTag"
          class="button"
          style="margin-right: 10px"
          @click="saveGroupFunc"
        >
          Save as a group
        </span>
        <span
          v-if="!forbiddenDownload"
          :class="disabledBtnTag"
          class="button"
          @click="downloadFunc"
        >
          Download
        </span>
      </div>
    </div>
    <a-dialog
      :visible.sync="saveGroupVisible"
      @confirm="saveGroupConfirmFunc"
      width="460"
      title="Save as Group"
      cancelbtnText="Cancel"
      surebtnText="Save"
      :footerVisible="true"
    >
      <div class="save-dialog">
        <div>
          <div class="d-flex">
            <label class="radio-container"
              >Create a New Group
              <input
                type="radio"
                checked="checked"
                name="create"
                value="create"
                v-model="saveGroupRadio"
              />
              <span class="checkmark"></span>
            </label>
          </div>
          <div style="margin: 5px 0 2px 24px">
            <p style="margin-bottom: 4px">Group Name:</p>
            <input
              :disabled="saveGroupRadio !== 'create'"
              class="save-input"
              v-model="saveGroupName"
              type="text"
              placeholder="please input"
            />
          </div>
        </div>
        <div>
          <div class="mt-2 d-flex">
            <label class="radio-container"
              >Save to an Existing Group
              <input
                type="radio"
                name="exist"
                value="exist"
                v-model="saveGroupRadio"
              />
              <span class="checkmark"></span>
            </label>
          </div>
          <div style="margin: 5px 0 2px 24px">
            <com-select
              :disabled="saveGroupRadio !== 'exist'"
              v-model="currentGroupId"
              color="info"
              item-text="name"
              item-value="id"
              :items="groupInfo"
              :menu-props="{
                bottom: true,
                contentClass: 'save-group-menu',
                offsetY: true
              }"
              height="32"
              placeholder="select"
              append-icon="$ArrowDown"
            >
              <template v-slot:item="{ item, attrs, on }">
                <v-list-item v-on="on" v-bind="attrs" :disabled="item?.locked">
                  <v-list-item-title class="d-flex">
                    <span
                      class="group-name-item"
                      :style="{
                        opacity: item?.locked ? '.5' : '.87'
                      }"
                    >
                      {{ item.name }}
                    </span>
                    <lock style="margin-left: 5px" v-show="item?.locked"></lock>
                  </v-list-item-title>
                </v-list-item>
              </template>
            </com-select>
          </div>
        </div>
      </div>
    </a-dialog>
    <NeuronLoadWarning
      title="Add Selected Neurons"
      :showDialog="showLoadWaring"
      :total="selectedUniqueCount"
      :random="100"
      @close="onCloseNeuronLoadWarning"
      @confirm="onApplyNeuronLoadWarning"
    ></NeuronLoadWarning>

    <a-dialog
      :visible.sync="showAnalyzingLoadWaring"
      width="380"
      title="Analyzing Selected Neurons"
      draggable
      persistent
    >
      <template>
        <div class="d-flex flex-column" style="padding: 14px">
          <div
            class="primary-text--text"
            style="margin-bottom: 10px; font-size: 13px; font-weight: 400"
          >
            {{ selectedResult.length }} neurons are selected to analyze.
            Analyzing more than 3000 neurons may cause the page to freeze or
            become unresponsive. It is recommended to analyze 3000 or fewer at
            once.
          </div>
          <div class="select-group">
            <v-radio-group v-model="analyzeOption" dense hide-details row>
              <div
                class="d-flex align-center primary-text--text"
                style="margin-bottom: 6px; font-size: 13px; font-weight: 400"
              >
                <v-radio color="#7fbefa" label="" value="all"></v-radio>
                <span>All {{ selectedResult.length }} neurons</span>
              </div>
              <div class="d-flex align-center" style="margin-bottom: 10px">
                <v-radio color="#7fbefa" label="" value="random"></v-radio>
                <div
                  class="primary-text--text"
                  style="flex-grow: 1; font-size: 13px; font-weight: 400"
                >
                  <span style="width: 90px; flex-basis: 90px; flex-shrink: 0"
                    >Randomly analyze</span
                  >
                  <input
                    v-model="analyzeRandomCount"
                    class="random-input primary-text--text"
                    style="width: 60px; font-size: 13px; font-weight: 400"
                  />
                  <span style="width: 54px; flex-basis: 54px; flex-shrink: 0"
                    >neurons</span
                  >
                </div>
              </div>
            </v-radio-group>
          </div>
          <div class="d-flex" style="justify-content: right">
            <div
              class="cancel-button primary-text--text"
              @click="onCancelAnalyze"
            >
              Cancel
            </div>
            <div class="confirm-button" @click="onConfirmAnalyze">Confirm</div>
          </div>
        </div>
      </template>
    </a-dialog>

    <a-dialog
      :visible.sync="showMaxDownload"
      width="360"
      title="Warning"
      :footerVisible="false"
    >
      <div class="mb-4">
        Please select 10000 or fewer neurons to download. Or you may go to the
        <a style="color: #7fbefa" @click="$router.push('./download')"
          >Data Download</a
        >
        page to download full data.
      </div>
    </a-dialog>
  </div>
</template>

<script>
/* eslint-disable */
import { mapState, mapGetters } from "vuex";
import ContentBlock from "@/components/ContentBlock.vue";
import DataGroupFilter from "./components/components/DataGroupFilter/DataGroupFilter.vue";
import Lock from "@/components/icons/Lock";
import NeuronFilter from "./components/NeuronFilter.vue";
import ADialog from "@/components/ADialog";
import ComSelect from "@/components/ComSelect";
import NeuronLoadWarning from "@/components/NeuronLoadWarning.vue";
import { getGroupDetailFunc, createOrCopyGroupFunc, updateGroupFunc } from "@/api/group";
import { loadNeuron } from "@/utils/neuronLoader";
// import { loadProjectionFiles } from "@/utils/projectionLoader";
import QueryResult from "./components/QueryResult.vue";
import { md5 } from "js-md5";
import { initCondition } from "@/utils/neuronFilterTool";
import { v4 as uuidv4 } from "uuid";
import {
  buildGroupPartsFromNeurons,
  attachGroupToNeurons
} from "@/utils/neuronGroup";
import {
  neuronSelectionKey,
  uniqueNeuronsByFile
} from "@/utils/neuronFilterTool";
import loadProjectionFilesWorker from "@/workers/loadProjectionFilesWorker.js";

export default {
  name: "NeuronData",
  data() {
    return {
      tobeLoaded: [],
      saveGroupVisible: false,
      projectionWorker: null,
      saveGroupRadio: "create",
      saveGroupName: "",
      currentGroupId: "",
      showLoadWaring: false,
      showAnalyzingLoadWaring: false,
      extremeMode: false,
      extremeEnabled:
        new URLSearchParams(window.location.search).get("extreme") === "true",
      analyzeOption: "random",
      analyzeRandomCount: 500,
      loadSomaOnly: false,
      loadHiResDendritesAfterWarning: false,
      currentOperation: "visualization",
      operations: [
        {
          name: "visualization",
          text: "Visualization",
        },
        {
          name: "analyzing",
          text: "Analyzing",
        },
        {
          name: "more",
          text: "More",
        },
      ],
      showOperations: true,
      showFilter: true,
      showDataSource: true,
      filterMinusHeight: 520,
      isOldNum: 0,
      isUnsaveGroup: false,
      showQueryResult: false,
      showMaxDownload: false,
    };
  },
  components: {
    NeuronFilter,
    ADialog,
    ContentBlock,
    Lock,
    DataGroupFilter,
    ComSelect,
    NeuronLoadWarning,
    QueryResult,
  },
  watch: {
    filteredNeurons() {
      if (JSON.stringify(this.filterCondition) === JSON.stringify(initCondition())) {
        this.showQueryResult = false;
      } else {
        // check if there any valid region neuron filter
        let numOfValidRelation = 0;
        const relationItems = this.filterCondition.relationItems;
        relationItems.forEach((item) => {
          if (item.region !== "" && item.region !== undefined) {
            numOfValidRelation++;
          }
        });

        if (numOfValidRelation > 0) {
          this.showQueryResult = true;
          return;
        }

        // check if smapleID or neuronID is not emputy
        if (
          this.filterCondition.sampleID !== "" ||
          this.filterCondition.neuronID !== ""
        ) {
          this.showQueryResult = true;
          return;
        }

        // check if there any valid line filter
        if (this.filterCondition.mouseLine.length > 0) {
          this.showQueryResult = true;
          return;
        }

        // check if there any group
        if (
          this.filterCondition.publicGroup !== "" ||
          this.filterCondition.customGroup !== "" ||
          this.filterCondition.temporaryGroup !== ""
        ) {
          this.showQueryResult = true;
          return;
        }
      }
      this.showQueryResult = false;
    },

    "functionMap.add_to_scene": {
      handler(newVal) {
        if (newVal?.add) {
          this.onAddToScene();
        }
      },
    },

    "functionMap.analyze_neurons": {
      handler(newVal) {
        if (newVal) {
          this.onAnalyze(true);
        }
      },
    },

    tobeAnalyzedNeurons() {
      if (this.tobeAnalyzedNeurons.length > 0) {
        this.onAnalyzing(this.tobeAnalyzedNeurons);
        this.$store.commit("neuron/setTobeAnalyzedNeurons", []);
      }
    },
  },

  computed: {
    ...mapState({
      addGroupFlag: state => state.addGroupFlag,
      temporaryGroups: state => state.temporaryGroups,
      addResultFlag: state => state.analyze.addResultFlag,
      projectionFiles: state => state.projectionFiles,
      groupFolderTag: state => state.groupFolderTag,
      visualTarget: state => state.visualTarget,
      functionMap: state => state.functionMap,
      groups: state => state.groups,
      groupsDetailData: state => state.groupsDetailData,
      filteredNeurons: state => state.neuron.filteredNeurons,
      filteredSelected: state => state.neuron.filteredSelected,
      selectionRevision: state => state.neuron.selectionRevision,
      toSceneGroup: state => state.neuron.toSceneGroup,
      neuronColorScheme: state => state.neuron.colorScheme,
      neuronRegionRelation: state => state.neuron.neuronRegionRelation,
      neuronDataSource: state => state.neuron.neuronDataSource,
      viewedNeurons: state => state.neuron.viewedNeurons,
      neuronData: state => state.neuron.neuronData,
      fileAcronymMap: state => state.neuron.fileAcronymMap,
      regionData: state => state.region.regionData,
      computedAnalysis: state => state.analyze.computedAnalysis,
      results: state => state.analyze.results,
      filterCondition: state => state.neuron.filterCondition,
      tobeAnalyzedNeurons: state => state.neuron.tobeAnalyzedNeurons
    }),

    ...mapGetters(["userInfo", "groupTips", "projectionFileUrls", "projectKeys"]),

    selectedResult() {
      // depend on selectionRevision (Set is not reactive by itself)
      void this.selectionRevision;
      const selected = this.filteredSelected;
      if (!selected || selected.size === 0) return [];
      return this.filteredNeurons.filter(el =>
        selected.has(neuronSelectionKey(el))
      );
    },

    /** Unique SWC files among selection (what NeuroViz actually loads). */
    selectedUniqueCount() {
      return uniqueNeuronsByFile(this.selectedResult).length;
    },

    disabledBtnTag() {
      return this.selectedResult?.length === 0 ? "disabled-button" : null;
    },

    analyzeDisabledBtnTag() {
      // Disable directly if nothing is selected
      if (!this.selectedResult?.length) return "disabled-button";
      return null;
    },

    groupInfo() {
      const n = {
        id: this.groupTips,
        name: this.groupTips,
        disabled: true,
      };
      const s = this.groups?.length ? this.groups : [n];
      const u = this.temporaryGroups?.length ? this.temporaryGroups : [n];
      return [{ header: "My Saved group" }, ...s, { header: "Unsaved group" }, ...u];
    },

    forbiddenDownload() {
      return process.env.VUE_APP_SUB_SPECIES === "rbm";
    },

    showHiResDendritesBtn() {
      return process.env.VUE_APP_SUB_SPECIES === "rbm";
    },

    showExtremeButton() {
      return this.extremeEnabled;
    }
  },

  methods: {
    initWorker() {
      this.projectionWorker = new Worker(loadProjectionFilesWorker);
    },

    async callProjectionWorker(neurons) {
      return new Promise((resolve) => {
        this.projectionWorker.onmessage = (e) => resolve(e.data?.data);
        // All external variables needed by the Worker must be packaged and passed in
        this.projectionWorker.postMessage({
          neurons,
          config: {
            VUE_APP_SRV: process.env.VUE_APP_SRV,
            TARGET: process.env.VUE_APP_TARGET,
            SUB_SPECIES: process.env.VUE_APP_SUB_SPECIES,
          },
          stateData: {
            // Pass the necessary URL mapping and the base snapshot from the store
            urls: this.projectionFileUrls,
            projectKeys: this.projectKeys,
            projectionFiles: this.projectionFiles,
            neuronData: this.neuronData,
            fileAcronymMap: this.fileAcronymMap,
            regionData: this.regionData,
          },
        });
      });
    },

    downloadFunc() {
      if (this.userInfo) {
        if (this.selectedResult.length > 10000) {
          this.showMaxDownload = true;
          return;
        }

        this.$emit("downloadNeurons", [...this.selectedResult]);
      } else {
        this.$store.commit("setLoginFlag", true);
      }
    },

    /**
     * Resolve load-warning choice to the exact neuron list to load.
     * Dedupes by SWC file so progress / viewedNeurons match user count.
     */
    resolveLoadWarningNeurons(payload) {
      let pool = uniqueNeuronsByFile(this.selectedResult);
      if (payload?.selectedOption === "random") {
        const count = Math.min(
          parseInt(payload.randomCount, 10) || 0,
          pool.length
        );
        pool = pool
          .slice()
          .sort(() => Math.random() - 0.5)
          .slice(0, count);
      }
      this.$store.commit(
        "neuron/setFilteredSelectionFromKeys",
        pool.map(el => neuronSelectionKey(el))
      );
      return pool;
    },

    onApplyNeuronLoadWarning(payload) {
      this.showLoadWaring = false;
      const neurons = this.resolveLoadWarningNeurons(payload);

      if (
        process.env.VUE_APP_SUB_SPECIES === "rbm" &&
        this.loadHiResDendritesAfterWarning
      ) {
        this.openHiResDendritesPanel();
      }

      if (this.extremeMode) {
        this.extremeMode = false;
        this.addNeuronsToSceneExtreme(neurons);
      } else {
        this.addNeuronsToScene(this.loadSomaOnly, neurons);
        this.loadSomaOnly = false;
      }
    },

    onCloseNeuronLoadWarning() {
      this.showLoadWaring = false;
      this.loadSomaOnly = false;
      this.loadHiResDendritesAfterWarning = false;
      this.extremeMode = false;
    },

    onAnalyzingNeuronLoadWarning(payload) {
      this.resolveLoadWarningNeurons(payload);
      this.onAnalyzing(this.selectedResult);
    },

    openHiResDendritesPanel() {
      const dendriticFiles = [
        ...new Set(this.selectedResult.map((item) => item.dendritic).filter(Boolean)),
      ];
      this.$store.commit("setHighResDendriticFiles", dendriticFiles);
      this.$store.commit("setHighResDendritesVisible", true);
    },

    showHiResDendrites() {
      const unique = uniqueNeuronsByFile(this.selectedResult);
      this.showLoadWaring = unique.length > 500;
      this.loadHiResDendritesAfterWarning = true;
      if (!this.showLoadWaring) {
        this.openHiResDendritesPanel();
        this.addNeuronsToScene(false, unique);
      }
    },

    onAddToScene(somaOnly = false) {
      this.loadSomaOnly = somaOnly;
      const unique = uniqueNeuronsByFile(this.selectedResult);
      if (unique.length > 500) {
        this.showLoadWaring = true;
      } else {
        this.addNeuronsToScene(somaOnly, unique);
        this.loadSomaOnly = false;
      }
    },

    onAddToSceneExtreme() {
      const unique = uniqueNeuronsByFile(this.selectedResult);
      if (unique.length > 500) {
        this.extremeMode = true;
        this.showLoadWaring = true;
      } else {
        this.addNeuronsToSceneExtreme(unique);
      }
    },

    addNeuronsToSceneExtreme(neuronList) {
      const neurons = uniqueNeuronsByFile(neuronList || this.selectedResult);
      const files = neurons.map(el => el.file);
      const total = files.length;
      if (total === 0) return;

      this.$store.commit("resetLoadingState");
      this.$store.state.totalLoadingCount = total;

      const onProgress = (loaded, t) => {
        this.$store.state.loadedCount = loaded;
        if (t != null) this.$store.state.totalLoadingCount = t;
      };

      window.neuroViz.mergeBatchSWCs(files, {
        onProgress,
        swcOptions: { mainBranch: false, axon: true, dendrite: true, undefined: true }
      }).then(() => {
        this.$store.commit("neuron/addViewedNeurons", neurons);
        this.$store.commit("resetLoadingState");
        this.isOldNum = 0;
        this.$store.commit("setIsPublicSwc", true);
      }).catch(err => {
        console.error("mergeBatchSWCs failed:", err);
        this.$store.commit("resetLoadingState");
      });
    },

    addNeuronsToScene(somaOnly, neuronList) {
      let isPublic = false;
      const source = uniqueNeuronsByFile(neuronList || this.selectedResult);
      if (source.length !== 0) {
        // "to scene as group" within a group
        if (this.isUnsaveGroup) {
          this.isUnsaveGroup = false;
        } else if (this.toSceneGroup?.id) {
          // Currently selected group
          this.setPartsFileFunc(
            {
              id: this.toSceneGroup.id,
              name: this.toSceneGroup.name,
              parts: this.toSceneGroup.parts,
            },
            this.toSceneGroup?.userID ? "save" : "unsave"
          );
        } else {
          isPublic = true;
        }
        this.tobeLoaded.push(...source);

        if (this.tobeLoaded.length > 20000) {
          const newV = true;
          this.$store.commit("setSettingValues", {
            data: newV,
            index: "mode",
          });
          const viewedCopy = [...this.viewedNeurons];
          viewedCopy.forEach((item) => {
            item?.visible && loadNeuron(item, false, newV);
          });
        }

        this.tobeLoaded.forEach((element) => {
          const currentItem = this.viewedNeurons.find(
            (item) => item.file === element.file
          );
          if (currentItem) {
            loadNeuron(currentItem, somaOnly);
          } else {
            loadNeuron(element, somaOnly);
          }
        });
        // Currently public neurons, folder = all
        this.$store.commit("setIsPublicSwc", isPublic);
        if (this.isOldNum === this.tobeLoaded.length) {
          // If everything in the group view is identical, the group folder update won't be triggered
          this.$store.commit("setGroupFolderTag", !this.groupFolderTag);
        }
        this.tobeLoaded = [];
      }
    },

    onAnalyze(forceWarning = true) {
      if (this.selectedResult.length > 3000 || forceWarning) {
        this.analyzeOption = "random";
        this.analyzeRandomCount = Math.min(
          500,
          Math.max(1, Math.floor(this.selectedResult.length * 0.1))
        );
        this.showAnalyzingLoadWaring = true;
        return;
      }

      this.onAnalyzing(this.selectedResult);
    },

    onCancelAnalyze() {
      this.showAnalyzingLoadWaring = false;
    },

    onConfirmAnalyze() {
      this.showAnalyzingLoadWaring = false;

      if (this.analyzeOption === "all") {
        this.onAnalyzing(this.selectedResult);
      } else if (this.analyzeOption === "random") {
        var count = Math.min(
          parseInt(this.analyzeRandomCount) || 500,
          this.selectedResult.length
        );
        var randomItems = this.selectedResult
          .slice()
          .sort(function () { return Math.random() - 0.5; })
          .slice(0, count);
        this.onAnalyzing(randomItems);
      }
    },

    async onAnalyzing(targetItems) {
      if (this.addResultFlag || targetItems.length === 0) return;
      this.$store.commit("analyze/setAddResultFlag", true);
      const fileNames = targetItems.map((item) => item.file).join("");

      const md5Code = md5(fileNames);
      // check if the neurons has been analyzed already
      // if not, analyze the neurons
      // 1. Check cache logic (unchanged).
      const analysisItem = this.computedAnalysis.find((item) => item.md5 === md5Code);
      if (analysisItem) {
        // if the result is displayed on the tab, just set it as the current tab
        const targetTab = this.results.find(
          (result) => result.data.md5 === analysisItem.md5
        );

        if (targetTab) {
          this.$store.commit("analyze/setAddResultFlag", false);
          this.$store.commit("analyze/setFocusTab", targetTab);
          return;
        }

        this.$store.commit("analyze/addResult", analysisItem);
        return;
      }

      try {
        const promises = [
          this.callProjectionWorker(targetItems)
        ];

        const results = await Promise.all(promises);

        const [{ axonHeatMapValue, terminalHeatMapValue }] = results;

        let str = targetItems.length + " neurons (";
        if (targetItems.length > 2) {
          str +=
            targetItems
              .slice(0, 2)
              .map((item) => item.file.slice(0, -4))
              .join(",") + "... )";
        } else {
          str += targetItems.map((item) => item.file.slice(0, -4)).join(",") + ")";
        }

        const finalResult = {
          md5: md5Code,
          somas: [],
          axonHeatMapValue,
          terminalHeatMapValue,
          items: [...targetItems],
          dataSource: str,
          heatMapType: "neuron",
          type: "neuron",
        };

        this.$store.commit("analyze/addResult", finalResult);
        this.$store.commit("analyze/addComputedAnalysis", finalResult);
      } catch (error) {
        console.error("Analysis failed:", error);
      }
    },

    onAddUnsaveGroupFunc() {
      if (this.selectedResult?.length !== 0) {
        this.isUnsaveGroup = true;
        const obj = {
          id: "untitled-" + uuidv4(),
          name: "untitled-" + this.temporaryGroups.length,
          species: this.visualTarget,
          selected: false,
          operation: false,
          count: this.selectedResult.length,
          parts: this.getGroupPartsFunc(),
        };
        this.$store.commit("setTemporaryGroups", [...this.temporaryGroups, obj]);
        this.setPartsFileFunc(
          {
            id: obj.id,
            name: obj.name,
            parts: obj.parts,
          },
          "unsave"
        );
        this.onAddToScene();
        this.$store.commit("setAddGroupFlag", !this.addGroupFlag);
      }
    },

    getGroupPartsFunc() {
      return buildGroupPartsFromNeurons(this.selectedResult);
    },

    setPartsFileFunc({ id, name, parts }, save = "unsave") {
      const fileSet = new Set();
      (parts || []).forEach((projectPart) => {
        (projectPart?.files || []).forEach((file) => fileSet.add(file));
      });

      const targetNeurons = this.selectedResult.filter((neuron) =>
        fileSet.has(neuron.file)
      );

      const { existingCount } = attachGroupToNeurons({
        neurons: targetNeurons,
        viewedNeurons: this.viewedNeurons,
        groupId: id,
        groupName: name,
        save,
      });

      this.isOldNum = existingCount;
    },

    saveGroupFunc() {
      if (this.userInfo) {
        this.saveGroupVisible = true;
        return;
      }
      this.$store.commit("setLoginFlag", true);
    },

    saveGroupConfirmFunc() {
      if (this.saveGroupName.length <= 50) {
        this.createOrEditGroup();
      } else {
        this.$store.commit("setToolTipType", "error");
        this.$store.commit("setToolTipMessage", "group name length should <= 50");
        this.$store.commit("setToolTipVisible", true);
      }
    },

    async createOrEditGroup() {
      const val_parts = this.getGroupPartsFunc();
      if (this.saveGroupRadio === "create") {
        await createOrCopyGroupFunc({
          name: this.saveGroupName,
          species: this.visualTarget,
          parts: val_parts,
        });
        this.saveGroupName = "";
        this.$store.dispatch("getGroups");
      } else {
        const currentGroup = this.temporaryGroups.find(
          (item) => item.id === this.currentGroupId
        );
        if (currentGroup) {
          // Update the unsaved group
          this.updateGroupFilesFunc(val_parts, currentGroup);
        } else {
          if (!this.groupsDetailData[this.currentGroupId]) {
            this.groupsDetailData[this.currentGroupId] = await getGroupDetailFunc(
              this.currentGroupId
            );
          }
          this.updateGroupFilesFunc(
            val_parts,
            this.groupsDetailData[this.currentGroupId]
          );
          await updateGroupFunc(
            this.currentGroupId,
            this.groupsDetailData[this.currentGroupId]
          );
          this.$store.dispatch("getGroups");
        }
      }
      this.$store.commit("setAddGroupFlag", !this.addGroupFlag);
      this.saveGroupVisible = false;
    },

    updateGroupFilesFunc(addParts = [], group) {
      for (let i = 0; i < addParts.length; i++) {
        const currP = group?.parts.find((item) => item.project === addParts[i].project);

        if (currP) {
          currP.files = currP.files.concat(addParts[i].files);
          currP.files = [...new Set(currP.files)];
          continue;
        }
        group?.parts.push(addParts[i]);
      }
    },

    onDataSourceClearCondition() {
      // this.$store.commit("neuron/clearFilterCondition");
      this.$refs.neuronFilter.clearCondition();
      this.$store.commit("neuron/setNeuronDataSource", !this.neuronDataSource);
    },

    onFilterClearCondition() {
      this.$refs.neuronFilter.clearCondition();
    },

    onShowAll() {
      this.filterMinusHeight = 656;
      // this.$nextTick(() => {
      //   this.$refs.queryResult.$el.scrollIntoView();
      // });
    },
  },

  mounted() {
    this.initWorker();
  },
};
</script>

<style lang="scss">
* {
  font-size: 13px;
  font-family: Roboto;
  user-select: none;
}

.neuron-data {
  display: flex;
  flex-direction: column;
}

.filter-header,
.operation-header {
  display: flex;
  align-items: center;
  margin: 10px 0;
}

.save-dialog {
  height: 208px;

  .save-input {
    width: 100%;
    display: flex;
    color: #ced4e4;
    height: 32px;
    padding: 5px 10px;
    align-items: center;
    gap: 5px;
    align-self: stretch;
    border-radius: 2px;
    outline: none;
    border: 1px solid var(--StrokeLine, #343f5c);
  }

  :deep {
    .v-select__selections input {
      border: none;
    }

    .v-select__slot {
      padding-left: 10px;
    }
  }
}

.active-operation {
  background: #2d68c3 !important;
  color: #ffffff !important;
}

.inactive-operation {
  background: #1f283e;
  color: #a5abb9;
}

.block-item {
  margin-bottom: 10px;
  padding: 14px 10px 10px 10px;
}

.random-input {
  padding: 5px 10px;
  border: 1px solid #343f5c;
  border-radius: 2px;
  margin: 0 10px;
  height: 24px;
}

.cancel-button {
  padding: 6px 14px;
  border-radius: 21px;
  border: 1px solid #343f5c;
  height: 24px;
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-right: 10px;
}

.confirm-button {
  padding: 6px 14px;
  border-radius: 21px;
  height: 24px;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.select-group {
  :deep(.v-input) {
    margin: 4px 0 !important;

    .v-label {
      font-size: 13px !important;
    }

    .v-input--selection-controls__ripple {
      display: none;
    }

    .v-input--selection-controls__input {
      width: 16px !important;
      height: 16px !important;
      margin-right: 4px !important;
    }
  }

  .v-input--radio-group.v-input--radio-group--row .v-radio {
    margin-right: 10px;
  }
}
</style>
