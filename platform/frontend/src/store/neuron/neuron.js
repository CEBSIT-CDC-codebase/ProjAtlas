import axios from "axios";
import {
  updateRegionNeuronRelation,
  initCondition,
  createRelationItem,
  filterNeurons,
  isValidCondition,
  enrichNeuronForScene,
  neuronSelectionKey
} from "@/utils/neuronFilterTool";
import { randomColor } from "@/utils/utils";
import {
  setNeuronRegionRelation,
  setNeuronColorScheme
} from "@/utils/neuronLoader";
import workerScriptForNeuronRegionRelation from "@/workers/neuronRegionRelationWorker.js";
import workerScriptForIPLDepth from "@/workers/iplDepthWorker.js";
import WorkerPool from "@/utils/workerPool";
// Create a Worker pool with size 4
const neuronRegionRelationWorkerPool = new WorkerPool(
  workerScriptForNeuronRegionRelation,
  4
);
import Vue from "vue";

export const namespaced = true;

/** Apply filter result: keep frozen catalog refs + select-all by default. */
function applyFilteredNeurons(st, list) {
  st.filteredNeurons = list || [];
  const selected = new Set();
  for (let i = 0; i < st.filteredNeurons.length; i++) {
    const key = neuronSelectionKey(st.filteredNeurons[i]);
    if (key) selected.add(key);
  }
  st.filteredSelected = selected;
  st.selectionRevision++;
}

export const state = {
  neuronData: {},
  neuronType: {},
  getNeuronsDone: false,
  neuronClass: {},
  neuronHeatMapData: null,
  morphotypeHeatMapData: null,
  neuronRegionRelation: {},
  regionNeuronRelation: {},
  filterCondition: initCondition(),
  filteredNeurons: [],
  // Selection for filtered list (file names). Separate from neuron objects so
  // catalog rows can stay Object.freeze'd and non-reactive.
  filteredSelected: new Set(),
  // Bumped on every selection change so Vue 2 components can depend on it.
  selectionRevision: 0,
  viewedNeurons: [],
  viewedFilesSet: new Set(),
  mouseLines: [],
  typeColors: {},
  colorScheme: "random",
  currentNeuronData: null,
  currentChooseGroup: null,
  toSceneGroup: {},
  moveCopyNeuron: null,
  neuronDataSource: false,
  delDialogVisible: false,
  isRemoveSwc: 0,
  batchCurrentColor: "#FF0000FF",
  isBatchSetColor: false,
  neuronListOperation: {},
  updateNeuronColor: { type: "region", trigger: 0 },
  neuronTypesTree: {},
  tobeAnalyzedNeurons: [],
  dendritesIPL: {
    matrix: null, // Float32Array, row-major dense matrix
    neuronIds: [], // string[], index is the row number
    depthCols: [], // string[], column names
    numCols: 0,
    nameToIndex: new Map() // Map<neuronId, rowIndex>, O(1) lookup
  },
  neuronTypeOrder: {},
  // Pre-built file→brain-acronym index (all projects), avoids re-scanning neuronData on every analysis
  fileAcronymMap: null
};

export const mutations = {
  setTobeAnalyzedNeurons(st, payload) {
    st.tobeAnalyzedNeurons = [];

    requestAnimationFrame(() => {
      st.tobeAnalyzedNeurons = payload;
    });
  },

  setUpdateNeuronColor(state, data) {
    state.updateNeuronColor = data;
  },

  setNeuronHeatMapData(state, data) {
    state.neuronHeatMapData = data;
  },

  setMorphotypeHeatMapData(state, data) {
    state.morphotypeHeatMapData = data;
  },

  setNeuronDataSource(state, data) {
    state.neuronDataSource = data;
  },

  setBatchCurrentColor(state, data) {
    state.batchCurrentColor = data;
  },

  setIsBatchSetColor(state, data) {
    state.isBatchSetColor = data;
  },
  setGetNeuronsDone(state, data) {
    state.getNeuronsDone = data;
  },

  clearFilterCondition(st) {
    st.filterCondition = initCondition();
    st.filteredNeurons = [];
    st.filteredSelected = new Set();
    st.selectionRevision++;
  },

  setFilteredNeurons(st, list) {
    applyFilteredNeurons(st, list);
  },

  toggleFilteredSelection(st, key) {
    if (!key) return;
    if (st.filteredSelected.has(key)) {
      st.filteredSelected.delete(key);
    } else {
      st.filteredSelected.add(key);
    }
    st.selectionRevision++;
  },

  setFilteredSelection(st, selected) {
    if (selected) {
      const s = new Set();
      for (let i = 0; i < st.filteredNeurons.length; i++) {
        const key = neuronSelectionKey(st.filteredNeurons[i]);
        if (key) s.add(key);
      }
      st.filteredSelected = s;
    } else {
      st.filteredSelected = new Set();
    }
    st.selectionRevision++;
  },

  /** Replace selection with exact keys (project::file). */
  setFilteredSelectionFromKeys(st, keys) {
    st.filteredSelected = new Set(keys || []);
    st.selectionRevision++;
  },

  // clearItemFilteredNeurons(st,payload){
  //   st.filteredNeurons = [];
  // },

  updateTypeColors(st, payload) {
    st.typeColors[payload.key] = payload.value;
  },

  setToSceneGroup(st, payload) {
    st.toSceneGroup = payload;
  },
  setCurrentChooseGroup(st, payload) {
    st.currentChooseGroup = payload;
  },

  // set neuron color rule
  setColorScheme(st, payload) {
    st.colorScheme = payload;
    setNeuronColorScheme(payload);
  },

  setNeuronListOperation(state, data) {
    state.neuronListOperation = data;
  },

  setMoveCopyNeuron(state, data) {
    state.moveCopyNeuron = data;
  },

  setCurrentNeuronData(state, data) {
    state.currentNeuronData = data;
  },

  setDelDialogVisible(state, data) {
    state.delDialogVisible = data;
  },

  updateFilterCondition(st, payload) {
    const previous = st.filterCondition[payload.key];
    // compare previous value with current value
    // if they are same, we don't need to update the filtered neurons
    if (JSON.stringify(previous) === JSON.stringify(payload.value)) {
      return;
    }

    st.filterCondition[payload.key] = payload.value;

    applyFilteredNeurons(
      st,
      filterNeurons(st.neuronData, st.typeColors, st.filterCondition)
    );
  },

  updateFilterIDCondition(st, payload) {
    st.filterCondition["neuronID"] = payload.neuronID;
    st.filterCondition["sampleID"] = payload.sampleID;

    applyFilteredNeurons(
      st,
      filterNeurons(st.neuronData, st.typeColors, st.filterCondition)
    );
  },

  updateFilterRelationItem(st, payload) {
    st.filterCondition["relationItems"][payload.index][payload.key] =
      payload.value;
    applyFilteredNeurons(
      st,
      filterNeurons(st.neuronData, st.typeColors, st.filterCondition)
    );
  },

  addFilterRelationItem(st) {
    st.filterCondition["relationItems"].push(createRelationItem("Soma", ""));
  },

  deleteFilterRelationItem(st, payload) {
    st.filterCondition["relationItems"].splice(payload, 1);
    if (st.filterCondition["relationItems"].length === 0) {
      st.filterCondition["relationItems"].push(createRelationItem("Soma", ""));
    } else {
      let lastItem =
        st.filterCondition["relationItems"][
          st.filterCondition["relationItems"].length - 1
        ];
      lastItem.relation = "";
    }
    applyFilteredNeurons(
      st,
      filterNeurons(st.neuronData, st.typeColors, st.filterCondition)
    );
  },

  addViewedNeurons(st, payload) {
    // use Set for O(1) dedup instead of O(n) files.indexOf
    // enrich catalog rows with scene colors only at load time
    payload.forEach(el => {
      if (!st.viewedFilesSet.has(el.file)) {
        st.viewedFilesSet.add(el.file);
        const base = enrichNeuronForScene(el, st.typeColors);
        st.viewedNeurons.push({
          ...base,
          visible: true,
          hovered: false,
          colorPicker: false,
          menuVisible: false,
          selected: false,
          somaVisible: true,
          axonVisible: true,
          dendriteVisible: true
        });
      } else {
        const index = st.viewedNeurons.findIndex(item => item.file === el.file);
        if (index !== -1) st.viewedNeurons[index].visible = true;
      }
    });
  },

  removeViewedNeurons(st, payload) {
    payload.forEach(el => {
      const index = st.viewedNeurons.indexOf(el);
      if (index === -1) return;
      st.viewedFilesSet.delete(el.file);
      st.viewedNeurons.splice(index, 1);
    });
  },

  setIsRemoveSwc(st, payload) {
    st.isRemoveSwc = payload;
  },

  setDendritesIPL(state, { matrix, neuronIds, depthCols, numCols }) {
    const nameToIndex = new Map();
    for (let i = 0; i < neuronIds.length; i++) {
      nameToIndex.set(neuronIds[i], i);
    }
    state.dendritesIPL = { matrix, neuronIds, depthCols, numCols, nameToIndex };
  }
};

// ========== Internal helper functions: pure parsing, no Vuex state writes ==========
// Placed outside actions as module-private functions, shared by getNeuronInfo and loadBatchNeuronData

/**
 * Parse a single project's neuron_data API response, returning a structured result (no side effects)
 */
function parseNeuronResponse(data, acronym, name) {
  const keys = Object.keys(data?.neuron_data || {});
  const withProject = {};
  const classArray = [],
    class1Array = [],
    class2Array = [];
  const mouseLines = [];

  keys.forEach(k => {
    withProject[k] = Object.freeze({
      ...data.neuron_data[k],
      project: acronym,
      projectFullName: name,
      id: k
    });

    const itemClass = data.neuron_data[k].class;
    if (itemClass !== undefined && itemClass !== "others") {
      classArray.push(itemClass);
    }
    if (
      data.neuron_data[k].class1 !== undefined &&
      data.neuron_data[k].class1 !== ""
    ) {
      class1Array.push(data.neuron_data[k].class1);
    }
    if (
      data.neuron_data[k].class2 !== undefined &&
      data.neuron_data[k].class2 !== ""
    ) {
      class2Array.push(data.neuron_data[k].class2);
    }
    if (data.neuron_data[k].type_array) {
      mouseLines.push(...data.neuron_data[k].type_array);
    }
  });

  return {
    withProject,
    classArray,
    class1Array,
    class2Array,
    mouseLines,
    neuronType: data.neuron_type,
    name
  };
}

export const actions = {
  // ========== Single-project loading (original logic, unchanged) ==========

  async getNeuronInfo({ state }, payload) {
    const { projects, name, acronym } = { ...payload };
    const project = projects.filter(el => el.name === name)[0];
    const url = process.env.VUE_APP_SRV + "/" + project["files"][0].path;
    const resp = await axios.get(url);

    const data = resp.data;
    const keys = Object.keys(data?.neuron_data || {});
    let withProject = {};
    let classArray = [];
    let class1Array = [];
    let class2Array = [];
    let mouseLines = [];

    keys.forEach(k => {
      withProject[k] = Object.freeze({
        ...data.neuron_data[k],
        project: acronym,
        projectFullName: name,
        id: k
      });
      const itemClass = data.neuron_data[k].class;
      if (itemClass !== undefined && itemClass !== "others") {
        classArray.push(data.neuron_data[k].class);
      }

      if (
        data.neuron_data[k].class1 !== undefined &&
        data.neuron_data[k].class1 !== ""
      ) {
        class1Array.push(data.neuron_data[k].class1);
      }

      if (
        data.neuron_data[k].class2 !== undefined &&
        data.neuron_data[k].class2 !== ""
      ) {
        class2Array.push(data.neuron_data[k].class2);
      }

      if (data.neuron_data[k].type_array) {
        mouseLines.push(...data.neuron_data[k].type_array);
      }
    });

    // Use a Map to deduplicate, O(n) instead of the previous reduce + find O(n²)
    const seen = new Map();
    for (const el of mouseLines.map(m => ({
      selected: false,
      name: m,
      project: acronym
    }))) {
      const key = `${el.name}|${el.project}`;
      if (!seen.has(key)) {
        seen.set(key, true);
        const existsInState = state.mouseLines.find(
          obj => obj.name === el.name && obj.project === el.project
        );
        if (!existsInState) {
          state.mouseLines.push(el);
        }
      }
    }

    // sort mouse line array as string
    state.mouseLines.sort((a, b) => {
      return a.name.localeCompare(b.name);
    });

    // sort class array as number if possible, otherwise as string
    classArray.sort((a, b) => {
      const na = Number(a);
      const nb = Number(b);
      if (!isNaN(na) && !isNaN(nb)) return na - nb;
      return String(a).localeCompare(String(b));
    });

    // sort class1 array as string
    class1Array.sort();

    // sort class2 array as string
    class2Array.sort((a, b) => a.localeCompare(b));

    state.neuronData[name] = Object.freeze(withProject);
    state.neuronType[name] = data.neuron_type;

    // Update the pre-built file→acronym index
    if (!state.fileAcronymMap) state.fileAcronymMap = {};
    const fMap = state.fileAcronymMap;
    Object.keys(withProject).forEach(k => {
      const item = withProject[k];
      if (item && item.file && item.acronym) {
        fMap[item.file] = item.acronym;
      }
    });

    // Use Vue.set to ensure reactive updates
    Vue.set(state.neuronClass, name, {
      class: [...new Set(classArray)],
      class1: [...new Set(class1Array)],
      class2: [...new Set(class2Array)]
    });

    // get all subtypes from neuron type
    let subtypes = [];
    const sub_type_array = state.neuronType[name].sub_type_array;
    if (sub_type_array) {
      subtypes.push(...sub_type_array);
    }
    // remove duplicate
    subtypes = [...new Set(subtypes)];

    // set type color for mouse line
    subtypes.forEach(line => {
      if (state.typeColors[line] === undefined) {
        let newColor = {};
        newColor[line] = randomColor(1.0);
        state.typeColors = Object.assign(state.typeColors, newColor);
      }
    });

    // Only compute filteredNeurons when the filter condition is non-empty; skip when the initial condition is empty
    if (isValidCondition(state.filterCondition)) {
      applyFilteredNeurons(
        state,
        filterNeurons(
          state.neuronData,
          state.typeColors,
          state.filterCondition
        )
      );
    }
  },

  // ========== Batch loading: load all projects in parallel on the root route / ==========

  /**
   * Fetch and parse all projects' neuron_data in parallel, then write to Vuex in a batch
   * Only called by App.vue on the root route /; other routes still go through getNeuronInfo (single project, on demand)
   */
  async loadBatchNeuronData({ state }, { projects }) {
    // Cache check: skip already-loaded projects to avoid redundant HTTP requests
    const unloaded = projects.filter(p => !state.neuronData[p.name]);

    if (unloaded.length === 0) {
      // Everything is already cached; only need to recompute filteredNeurons (handles the timing issue where the condition may be set before the data loads)
      if (isValidCondition(state.filterCondition)) {
        applyFilteredNeurons(
          state,
          filterNeurons(state.neuronData, state.typeColors, state.filterCondition)
        );
      }
      return;
    }

    // Phase 1: Parallel HTTP requests + parsing (no side effects, safe to run concurrently)
    const fetchAndParse = async project => {
      const url = process.env.VUE_APP_SRV + "/" + project.files[0].path;
      const resp = await axios.get(url);
      return {
        ...parseNeuronResponse(resp.data, project.acronym, project.name),
        acronym: project.acronym
      };
    };

    const allResults = await Promise.all(projects.map(fetchAndParse));

    // Phase 2: Collect shared state data (mouseLines / subtypes)
    const allMouseLineEntries = [];
    const allSubtypes = new Set();

    for (const result of allResults) {
      // --- Write to per-project state (different keys, no concurrency conflicts) ---
      state.neuronData[result.name] = Object.freeze(result.withProject);
      state.neuronType[result.name] = result.neuronType;

      // class sort + deduplicate (consistent with the original getNeuronInfo logic)
      const classSorted = [...new Set(result.classArray)].sort((a, b) => {
        const na = Number(a),
          nb = Number(b);
        if (!isNaN(na) && !isNaN(nb)) return na - nb;
        return String(a).localeCompare(String(b));
      });
      Vue.set(state.neuronClass, result.name, {
        class: classSorted,
        class1: [...new Set(result.class1Array)].sort(),
        class2: [...new Set(result.class2Array)].sort((a, b) =>
          a.localeCompare(b)
        )
      });

      // Collect mouseLines
      allMouseLineEntries.push(
        ...result.mouseLines.map(m => ({
          selected: false,
          name: m,
          project: result.acronym
        }))
      );

      // Collect subtypes (used for typeColors), consistent with the original getNeuronInfo logic
      const subTypes = result.neuronType?.sub_type_array;
      if (subTypes) {
        const typeArr = Array.isArray(subTypes) ? subTypes : [subTypes];
        typeArr.forEach(s => allSubtypes.add(s));
      }

    }

    // Phase 3: Write to shared state once (a single write each, rather than once per project)
    // mouseLines: deduplicate + sort
    const seenMl = new Map();
    for (const el of allMouseLineEntries) {
      const key = `${el.name}|${el.project}`;
      if (!seenMl.has(key)) {
        seenMl.set(key, true);
        state.mouseLines.push(el);
      }
    }
    state.mouseLines.sort((a, b) => a.name.localeCompare(b.name));

    // typeColors: assign in one batch
    for (const line of allSubtypes) {
      if (state.typeColors[line] === undefined) {
        state.typeColors = Object.assign(state.typeColors, {
          [line]: randomColor(1.0)
        });
      }
    }

    // Pre-build the file→acronym index for use by Worker heatmap analysis
    // Iterate all projects' neuronData once here so later analysis doesn't need to pass neuronData again
    const fileMap = {};
    for (const pName of Object.keys(state.neuronData)) {
      const items = state.neuronData[pName];
      if (!items) continue;
      for (const k of Object.keys(items)) {
        const item = items[k];
        if (item && item.file && item.acronym) {
          fileMap[item.file] = item.acronym;
        }
      }
    }
    state.fileAcronymMap = fileMap;

    // Once the data is ready: if the caller already set a filter condition (PublicGroupFilter may have set it before the data loaded),
    // force a recompute of filteredNeurons to avoid the "data loaded but results show 0" situation
    if (isValidCondition(state.filterCondition)) {
      applyFilteredNeurons(
        state,
        filterNeurons(state.neuronData, state.typeColors, state.filterCondition)
      );
    }
  },

  async getNeuronRegionRelation({ state }, payload) {
    const { projects, name } = { ...payload };
    const project = projects.filter(el => el.name === name)[0];
    const index = project.files.findIndex(file =>
      file.path.includes("neuron-region")
    );
    const url = process.env.VUE_APP_SRV + "/" + project["files"][index].path;
    const resp = await axios.get(url);
    // Freeze the raw data to avoid Vue's reactivity recursively wrapping every neuron's relation object
    state.neuronRegionRelation[name] = Object.freeze(
      resp.data.neuron_region_relation_data
        ? resp.data.neuron_region_relation_data
        : resp.data
    );

    try {
      // Use the Worker pool to process the data, passing the project name as context
      const result = await neuronRegionRelationWorkerPool.runTask(
        state.neuronRegionRelation[name],
        name
      );

      // Freeze the transposed result too, to avoid Vue reactivity overhead
      state.regionNeuronRelation[name] = Object.freeze(result);
      updateRegionNeuronRelation(name, result);
      setNeuronRegionRelation(result);
    } catch (error) {
      console.error("Error processing neuron region relation:", error);
    }
  },

  async getDendritesIPLInfo({ commit }) {
    const url =
      process.env.VUE_APP_SRV + "/info/mouse/rbm/Dendrites_IPL_info.csv";
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}: ${url}`);
    const buffer = await resp.arrayBuffer();

    await new Promise((resolve, reject) => {
      const worker = new Worker(workerScriptForIPLDepth);
      worker.onmessage = e => {
        if (e.data.type === "READY") {
          commit("setDendritesIPL", e.data.payload);
          worker.terminate();
          resolve();
        } else if (e.data.type === "ERROR") {
          worker.terminate();
          reject(new Error(e.data.message));
        }
      };
      worker.onerror = err => {
        worker.terminate();
        reject(err);
      };
      // Zero-copy transfer of the ArrayBuffer to the Worker
      worker.postMessage({ type: "PARSE", buffer }, [buffer]);
    });
  },

  async getNeuronTypeOrder({ state }, payload) {
    const { projects, name } = { ...payload };
    const project = projects.filter(el => el.name === name)[0];
    const index = project.files.findIndex(file =>
      file.path.includes("Neuron_cluster_order")
    );
    if (index === -1) {
      console.warn(
        `[Neuron_cluster_order] No Neuron_cluster_order file found for project ${name}`
      );
      return;
    }
    const url = process.env.VUE_APP_SRV + "/" + project["files"][index].path;
    const response = await fetch(url);
    if (!response.ok) {
      console.error(
        `[Neuron_cluster_order] Failed to fetch neuron type order for project ${name}: HTTP ${response.status}`
      );
      return;
    }
    const text = await response.text();
    const lines = text.trim().split("\n");
    const header = lines[0].split(",");
    const orderNoIdx = header.findIndex(
      h => h.trim().toLowerCase() === "orderno"
    );
    const clusterIdx = header.findIndex(
      h => h.trim().toLowerCase() === "cluster"
    );
    const typeOrder = [];
    for (let i = 1; i < lines.length; i++) {
      const cols = lines[i].split(",");
      if (cols.length <= Math.max(orderNoIdx, clusterIdx)) continue;
      typeOrder.push({
        orderNo: Number(cols[orderNoIdx].trim()),
        cluster: cols[clusterIdx].trim()
      });
    }
    state.neuronTypeOrder[name] = Object.freeze(typeOrder);
  }
};
