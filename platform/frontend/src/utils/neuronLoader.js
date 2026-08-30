import store from "../store";
import { hexToRgb } from "@/utils/utils.js";
import { enrichNeuronForScene } from "@/utils/neuronFilterTool";
const fastq = require("fastq");
let shouldStop = false;
const worker = task => {
  if (shouldStop) {
    return Promise.reject(new Error("stopped"));
  } else {
    return task();
  }
};

let queue = fastq.promise(worker, 6);

export const stopTasks = () => {
  shouldStop = true;
  queue.kill();
  queue.pause();
  queue = fastq.promise(worker, 6);
  shouldStop = false;
};

let regionData = {};
export const setRegionData = data => {
  regionData = data;
};

let regionColorScheme = "allenColor";
export const setRegionColorScheme = scheme => {
  regionColorScheme = scheme;
};

let neuronColorScheme = "random";
export const setNeuronColorScheme = scheme => {
  neuronColorScheme = scheme;
};

let neuronRegionRelation = {};
export const setNeuronRegionRelation = data => {
  neuronRegionRelation = data;
};

// Dedupe concurrent/duplicate region loads (e.g. root STL fired twice on init).
const regionLoadInFlight = new Map();

export const loadRegion = region => {
  let item = { ...region };
  const uid = item.regionObj.uid_array[0];
  const rawObj = regionData[parseInt(uid)];
  if (!rawObj || !rawObj.file) {
    return Promise.resolve();
  }

  const file = rawObj.file;
  const viewed = store.state.region.viewedRegions.find(
    el => el.file === file || String(el.uid) === String(uid)
  );
  if (viewed) {
    // Already in scene list — reveal mesh if hidden, do not load again.
    if (window.neuroViz) {
      window.neuroViz.load(file);
    }
    store.commit("region/addViewedRegions", [
      Object.assign({}, viewed, { visible: true })
    ]);
    return Promise.resolve();
  }

  if (regionLoadInFlight.has(file)) {
    return regionLoadInFlight.get(file);
  }

  store.commit("addTotalLoadingCount");
  item = Object.assign(
    {
      operationSelected: false,
      viewed: false,
      visible: true,
      hovered: false,
      menuVisible: false,
      uid,
      allenColor: rawObj.allenColor,
      cebsitColor: rawObj.cebsitColor,
      randomColor: rawObj.randomColor,
      colorScheme: regionColorScheme,
      file
    },
    item
  );

  const hex =
    regionColorScheme === "random"
      ? item.randomColor
      : regionColorScheme === "cebsit"
      ? item.cebsitColor
      : item.allenColor;
  item.currentColor = hex;
  const rgb = hexToRgb(hex).map(el => el / 255.0);
  const pending = queue.push(() => {
    return new Promise(resolve => {
      window.neuroViz.load(item.file).then(() => {
        setColorFunc(item, rgb);
        item.selected = false;
        store.commit("region/addViewedRegions", [item]);
        store.commit("addLoadedCount");
        resolve();
      });
    });
  }).finally(() => {
    regionLoadInFlight.delete(file);
  });
  regionLoadInFlight.set(file, pending);
  return pending;
};

const setColorFunc = async (neuron, rgb, mode = null) => {
  if (mode === null) {
    mode = store.state.settingValues.mode;
  }
  const file = neuron.file;
  if (mode) {
    const somaVisible =
      neuron.somaVisible !== undefined ? neuron.somaVisible : true;
    const axonVisible =
      neuron.axonVisible !== undefined ? neuron.axonVisible : true;
    const dendriteVisible =
      neuron.dendriteVisible !== undefined ? neuron.dendriteVisible : true;
    const undefinedVisible =
      neuron.undefinedVisible !== undefined ? neuron.undefinedVisible : true;

    await window.neuroViz.setSWCPartVisibility(
      file,
      somaVisible,
      axonVisible,
      dendriteVisible,
      mode,
      undefinedVisible
    );
  }
  await window.neuroViz.setColor(file, rgb);
};

const getRegionSomaColor = neuron => {
  const projectName = neuron.projectFullName;
  const relationItem = neuronRegionRelation[projectName][neuron.id];
  const somaArray = relationItem.owner_region_array;
  if (somaArray.length === 0) {
    return "#ffffff";
  }

  return regionData[somaArray[somaArray.length - 1]].somaColor;
};

export const loadNeuron = (neuron, somaOnly, explicitMode = null) => {
  store.commit("addTotalLoadingCount");

  // Catalog rows are frozen and may lack scene colors (filter no longer clones).
  // Enrich a mutable copy so hexToRgb always has idColor / structureColor.
  if (!neuron.idColor || !neuron.structureColor) {
    neuron = enrichNeuronForScene(neuron, store.state.neuron.typeColors);
  }

  let rgb = [];
  switch (neuronColorScheme) {
    case "random":
      rgb = hexToRgb(neuron.idColor || "#ffffff").map(el => el / 255.0);
      neuron.currentColor = neuron.idColor;
      break;
    case "mouseLine": {
      const neuronType = Array.isArray(neuron.type_array)
        ? neuron.type_array[0]
        : neuron.type_array;
      neuron.typeColor = store.state.neuron.typeColors[neuronType];
      rgb = hexToRgb(neuron.typeColor || "#ffffff").map(el => el / 255.0);
      neuron.currentColor = neuron.typeColor;
      break;
    }
    case "region": {
      const regionColor = getRegionSomaColor(neuron);
      neuron.regionColor = regionColor;
      neuron.currentColor = regionColor;
      rgb = hexToRgb(regionColor || "#ffffff").map(el => el / 255.0);
      break;
    }
    default:
      rgb = hexToRgb(neuron.idColor || "#ffffff").map(el => el / 255.0);
      neuron.currentColor = neuron.idColor;
      break;
  }

  const mode =
    explicitMode !== null ? explicitMode : store.state.settingValues.mode;
  if (neuronColorScheme === "structure") {
    const { somaColor, axonColor, dentriteColor, undefinedColor } = {
      ...neuron.structureColor
    };
    if (somaOnly) {
      queue.push(() => {
        return new Promise(resolve => {
          window.neuroViz.loadSoma(neuron.file).then(() => {
            setColorFunc(neuron, somaColor, mode);
            store.commit("addLoadedCount");
            store.commit("neuron/addViewedNeurons", [neuron]);
            resolve();
          });
        });
      });
    } else {
      queue.push(() => {
        return new Promise(resolve => {
          window.neuroViz.load(neuron.file).then(() => {
            const val = [
              neuron.file,
              somaColor,
              axonColor,
              dentriteColor,
              undefinedColor,
              mode
            ];
            mode
              ? window.neuroViz.setSWCPartVisibility(...val)
              : window.neuroViz.setSWCPartColor(...val);
            store.commit("addLoadedCount");
            store.commit("neuron/addViewedNeurons", [neuron]);
            resolve();
          });
        });
      });
    }
  } else {
    if (somaOnly) {
      queue.push(() => {
        return new Promise(resolve => {
          window.neuroViz.loadSoma(neuron.file).then(() => {
            setColorFunc(neuron, rgb, mode);
            store.commit("addLoadedCount");
            store.commit("neuron/addViewedNeurons", [neuron]);
            resolve();
          });
        });
      });
    } else {
      queue.push(() => {
        return new Promise(resolve => {
          window.neuroViz.load(neuron.file).then(() => {
            setColorFunc(neuron, rgb, mode);
            store.commit("addLoadedCount");
            store.commit("neuron/addViewedNeurons", [neuron]);

            if (process.env.VUE_APP_SUB_SPECIES === "rbm" && neuron.dendritic) {
              store.commit("addHighResDendritesColor", {
                id: (Math.random() * 100000).toFixed(0),
                file: neuron.dendritic,
                color: rgb
              });
            }
            resolve();
          });
        });
      });
    }
  }
};

export const loadLine = line => {
  store.commit("addTotalLoadingCount");
  queue.push(() => {
    return new Promise(resolve => {
      window.neuroViz.load(line.file).then(para => {
        if (line.parentObj && line.parentObj.name === "Spatial Profile") {
          const color = para[0].color;
          // Converts [0.1, 0.2, 0.3, 1] to #19334dff
          line.colorString =
            "#" +
            color
              .map(el => {
                const hex = Math.floor(el * 255).toString(16);
                return hex.length === 1 ? "0" + hex : hex;
              })
              .join("");
        } else {
          line.colorString = para[0].colorMap;
          window.neuroViz.setLineGradientOpacityScale(line.file, 0.4);
        }

        store.commit("addLoadedCount");
        store.commit("line/addViewedLines", [line]);
        resolve();
      });
    });
  });
};

export const loadCyto = cyto => {
  store.commit("addTotalLoadingCount");
  queue.push(() => {
    return new Promise(resolve => {
      const color = getCytoColor(cyto.name);
      const rgb = hexToRgb(color).map(el => el / 255.0);

      window.neuroViz.load(cyto.file).then(() => {
        window.neuroViz.setColor(cyto.file, rgb);
        store.commit("addLoadedCount");
        store.commit("cyto/addViewedCytos", [{ ...cyto, color }]);
        resolve();
      });
    });
  });
};

export function randomColor(opaticy = null) {
  let r = Math.floor(Math.random() * 255);
  let g = Math.floor(Math.random() * 255);
  let b = Math.floor(Math.random() * 255);
  let op = "";
  if (opaticy) {
    op = Math.floor(255 * opaticy).toString(16);
  }
  return (
    "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1) + op
  );
}
// HACK: should put into cyto info JSON
const getCytoColor = cytoName => {
  switch (cytoName) {
    case "Total(elavl3)":
      return "#c32136";
    case "vglut2a":
      return "#FFFF00";
    case "vglut2b":
      return "#ff0097";
    case "gad1b":
      return "#00ff00";
    case "glyt2":
      return "#0000ff";
    default:
      return randomColor(1);
  }
};
