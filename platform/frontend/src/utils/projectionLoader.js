import store from "../store";
import axios from "axios";
import { randomColor } from "./uColor";

// Cache computed results
const projectionCache = new Map();

// Extract data processing function
function processProjectionData(neurons, type) {
  const currentType = type === "axon" ? "axonLength" : "terminalCount";
  const result = {};

  // Use for...of instead of forEach
  for (const neuron of neurons) {
    if (!neuron?.file) continue;
    const fileName = neuron.file.slice(0, -4);
    const projectData =
      store.state.projectionFiles[neuron.project]?.[currentType];
    if (projectData && projectData[fileName]) {
      result[fileName] = projectData[fileName];
    }
  }

  return result;
}

// Extract family and color processing logic
function getFamilyAndColor(key) {
  if (process.env.VUE_APP_TARGET === "mouse") {
    const vals = Object.values(store.state.region.regionData)
    const family = getRegionFamily(key);

    const familyItem = vals.find(
      region => region?.acronym === family
    );
    return {
      family,
      color: familyItem?.allenColor
    };
  } else if (process.env.VUE_APP_TARGET === "monkey") {
    const regionInfo = store.state.projectionFiles.regionDict?.find(
      item => item?.region === key
    );
    if (regionInfo) {
      return {
        family: regionInfo.family,
        color: randomColor(0.5)
      };
    }
  }
  return {};
}

// Extract parent node processing logic
function processParentNodes(result) {
  const parents = [];

  // First collect all unique keys and their initial values
  const keyValues = new Map();
  for (const item of Object.values(result)) {
    for (const [key, value] of Object.entries(item)) {
      const currentValue = keyValues.get(key) || 0;
      keyValues.set(key, currentValue + value);
    }
  }

  // Create a parent node for each unique key
  for (const [key, totalValue] of keyValues) {
    const { family, color } = getFamilyAndColor(key);
    parents.push({
      parent: key,
      value: totalValue,
      family,
      familyColor: color
    });
  }

  return parents;
}

function calculateLogValues(values, ignoreZeros = true) {
  if (!values || values.length === 0) {
    return { max: 0, min: 0 };
  }

  const filteredValues = ignoreZeros ? values.filter(v => v > 0) : values;
  if (filteredValues.length === 0) {
    return { max: 0, min: 0 };
  }

  const logValues = filteredValues.map(v => {
    const logVal = Math.log10(v);
    return isFinite(logVal) ? logVal : 0;
  });

  return {
    max: Math.max(...logValues),
    min: Math.min(...logValues)
  };
}

const loadData = (neurons, acronyms, type) => {
  const cacheKey = `${type}-${neurons.map(n => n?.file).join(",")}`;
  if (projectionCache.has(cacheKey)) {
    return projectionCache.get(cacheKey);
  }

  const result = processProjectionData(neurons, type);

  const parents = processParentNodes(result);
  const mapBrain = {};

  let neuronMaxValue = 0;
  let brainMaxValue = 0;
  const logValues = {
    neuronMax: 0,
    neuronMin: Infinity,
    brainMax: 0,
    brainMin: Infinity
  };

  // Process brain region data
  for (const [key, files] of Object.entries(acronyms)) {
    if (!files?.length) continue;

    const obj = {};
    for (const name of files) {
      const neuron = result[name.slice(0, -4)];
      if (!neuron) continue;

      for (const [b, value] of Object.entries(neuron)) {
        if (typeof value === "number" && isFinite(value)) {
          obj[b] = (obj[b] || 0) + value;
        }
      }
    }

    const values = Object.values(obj);
    if (values.length > 0) {
      const maxVal = Math.max(...values);
      if (isFinite(maxVal)) {
        brainMaxValue = Math.max(brainMaxValue, maxVal);
      }

      const { max, min } = calculateLogValues(values);
      logValues.brainMax = Math.max(logValues.brainMax, max);
      if (min > 0) {
        logValues.brainMin = Math.min(logValues.brainMin, min);
      }
    }

    mapBrain[key] = obj;
  }

  // Process neuron data
  for (const item of Object.values(result)) {
    const values = Object.values(item).filter(
      v => typeof v === "number" && isFinite(v)
    );

    if (values.length > 0) {
      const maxVal = Math.max(...values);
      if (isFinite(maxVal)) {
        neuronMaxValue = Math.max(neuronMaxValue, maxVal);
      }

      const { max, min } = calculateLogValues(values);
      logValues.neuronMax = Math.max(logValues.neuronMax, max);
      if (min > 0) {
        logValues.neuronMin = Math.min(logValues.neuronMin, min);
      }
    }
  }

  // Ensure all log values are valid
  if (!isFinite(logValues.neuronMin)) logValues.neuronMin = 0;
  if (!isFinite(logValues.brainMin)) logValues.brainMin = 0;

  const output = {
    brains: parents,
    neurons: result,
    mapBrain,
    logValues,
    neuronMaxValue,
    brainMaxValue,
    visible: false
  };

  projectionCache.set(cacheKey, output);
  return output;
};

const getRegionFamily = parent => {
  return store.state.projectionFiles.regionDict?.find(
    item => (item?.parent == parent || item?.region == parent) // spcd: item?.region == parent
  )?.family;
};

// Cache project→fileMap to avoid rebuilding on every loadProjectionFiles call
const _projectFileMaps = new Map();

export const loadProjectionFiles = async neurons => {
  try {
    const neuronProjects = [...new Set(neurons.map(item => item?.project))];
    const projectionFiles = store.state.projectionFiles;
    // Load region dictionary
    if (!Array.isArray(projectionFiles.regionDict)) {
      const regionUrl =
        process.env.VUE_APP_SRV + store.getters.projectionFileUrls.regionDict;
      const { data: regionData } = await axios.get(regionUrl);
      projectionFiles.regionDict = regionData;
    }

    // Load project data in parallel
    await Promise.all(
      neuronProjects.map(async project => {
        if (projectionFiles[project]) return;

        const [axonData, terminalData] = await Promise.all([
          axios.get(
            process.env.VUE_APP_SRV +
            store.getters.projectionFileUrls[project].axonLength
          ),
          axios.get(
            process.env.VUE_APP_SRV +
            store.getters.projectionFileUrls[project].terminalCount
          )
        ]);

        projectionFiles[project] = {
          axonLength: axonData.data,
          terminalCount: terminalData.data
        };
      })
    );

    // Process neuron data: pre-build a file→acronym Map to avoid nested O(N×K) lookups
    const acronyms = {};
    for (const neuron of neurons) {
      if (!neuron?.project) continue;

      const type = store.getters.projectKeys[neuron.project];
      const neuronData = store.state.neuron.neuronData[type];
      if (!neuronData) continue;

      // Build the file→acronym Map on demand (once per project, cached across calls)
      let fileMap = _projectFileMaps.get(type);
      if (!fileMap) {
        fileMap = new Map();
        for (const item of Object.values(neuronData)) {
          fileMap.set(item.file, item.acronym);
        }
        _projectFileMaps.set(type, fileMap);
      }

      const acronym = fileMap.get(neuron.file);
      if (acronym) {
        if (!acronyms[acronym]) {
          acronyms[acronym] = [];
        }
        acronyms[acronym].push(neuron.file);
      }
    }
    // Deduplicate
    for (const key of Object.keys(acronyms)) {
      acronyms[key] = [...new Set(acronyms[key])];
    }
    const res = {
      axonHeatMapValue: loadData(neurons, acronyms, "axon"),
      terminalHeatMapValue: loadData(neurons, acronyms, "terminal")
    };
    
    return res
  } catch (error) {
    console.error("Error loading projection files:", error);
    throw error;
  }
};
