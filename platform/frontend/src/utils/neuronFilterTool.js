import { hexToRgb, randomColor } from "./utils";
import store from "@/store";
import { getAllMoreSettingData, getMoreSettingSources } from "./moreSetting";

let regionNeuronRelation = {};
let regionType = undefined;

import workerScriptForRegionSomaTree from "@/workers/regionSomaTreeWorker.js";

export const setRegionType = data => {
  regionType = data;
  const regionSomaTreeWorker = new Worker(workerScriptForRegionSomaTree);
  regionSomaTreeWorker.postMessage({ regionType, regionNeuronRelation });

  regionSomaTreeWorker.onmessage = e => {
    const result = e.data;
    store.commit("region/setRegionSomaTreeArray", result);
    regionSomaTreeWorker.terminate();
  };
};

export const updateRegionNeuronRelation = (project, relation) => {
  regionNeuronRelation[project] = relation;
  // No longer creating a Worker every time; the caller invokes computeRegionSomaTree once instead
};

/**
 * Batch-compute regionSomaTree
 * Should be called once, after all projects' neuronRegionRelation data has finished loading
 */
export const computeRegionSomaTree = () => {
  const regionSomaTreeWorker = new Worker(workerScriptForRegionSomaTree);
  regionSomaTreeWorker.postMessage({ regionType, regionNeuronRelation });
  regionSomaTreeWorker.onmessage = e => {
    const result = e.data;
    store.commit("region/setRegionSomaTreeArray", result);
    regionSomaTreeWorker.terminate();
  };
};

const getRelationNeurons = relation => {
  // Use a local variable to access store data
  const storeNeuronData = store.state.neuron.neuronData;
  const moreSettingProjects = getMoreSettingSources().map(el => el.projectName);

  const neurons = [];
  const projects = Object.keys(regionNeuronRelation);
  projects.forEach(project => {
    const relations = regionNeuronRelation[project];
    if (!relations) return;
    let ids = [];
    const regionUID = relation.region;
    if (relation.type === "Soma" && relations[regionUID]) {
      ids.push(...relations[regionUID].owned_neuron_array);
    } else if (relations[regionUID]) {
      let axonNeurons = relations[regionUID].projecting_neuron_array;
      const originalAxonNeurons = [...axonNeurons];

      // get filtering target
      const projectingTarget = relation.moreSetting.projectionTarget;

      // based on the target, we get the corresponding source data
      let filteringSourceData = [];
      const moreSettingData = getAllMoreSettingData();
      moreSettingData.forEach(dataItem => {
        if (
          projectingTarget === "Projection Mode" &&
          dataItem.projecting === "mode"
        ) {
          let modeType = relation.moreSetting.projectionMode;
          if (!modeType) {
            modeType = "all";
          }

          if (modeType && dataItem.type === modeType) {
            filteringSourceData.push(dataItem);
          } else if (!modeType) {
            filteringSourceData.push(dataItem);
          }
        } else if (
          projectingTarget === "Projection Pathway" &&
          dataItem.projecting === "pathway"
        ) {
          // begin filtering
          const pathwayType = relation.moreSetting.projectionPathway;
          if (dataItem.type === pathwayType) {
            filteringSourceData.push(dataItem);
          }
        }
      });

      // now we filter the three kinds subtypes
      const branchPointArray = filteringSourceData.filter(el => {
        return el.subtype === "branchPoint" && el.projectName === project;
      });

      const terminalNumArray = filteringSourceData.filter(el => {
        return el.subtype === "terminalNum" && el.projectName === project;
      });

      const cableLengthArray = filteringSourceData.filter(el => {
        return el.subtype === "cableLength" && el.projectName === project;
      });

      // filter with branch points
      if (
        relation.moreSetting.branchPointsMin ||
        relation.moreSetting.branchPointsMax
      ) {
        const branchFilterResult = [];
        branchPointArray.forEach(branchPointItem => {
          let branchObject = branchPointItem.data[regionUID];

          if (branchObject) {
            let withZeroBranchObject = {};
            originalAxonNeurons.forEach(element => {
              withZeroBranchObject[element] = 0;
            });

            branchObject = { ...withZeroBranchObject, ...branchObject };
            const branchNeurons = Object.keys(branchObject);
            branchFilterResult.push(
              ...branchNeurons.filter(el => {
                const branchPoint = branchObject[el];
                if (
                  relation.moreSetting.branchPointsMin &&
                  branchPoint < relation.moreSetting.branchPointsMin
                ) {
                  return false;
                }

                if (
                  relation.moreSetting.branchPointsMax &&
                  branchPoint > relation.moreSetting.branchPointsMax
                ) {
                  return false;
                }

                return true;
              })
            );
          }
        });

        axonNeurons = axonNeurons.filter(
          el =>
            branchFilterResult.includes(el) &&
            moreSettingProjects.includes(project)
        );
      }

      if (
        relation.moreSetting.terminalPointsMin ||
        relation.moreSetting.terminalPointsMax
      ) {
        let terminalFilterResult = [];
        terminalNumArray.forEach(terminalNumItem => {
          let terminalObject = terminalNumItem.data[regionUID];
          if (terminalObject) {
            let withZeroTerminalObject = {};
            originalAxonNeurons.forEach(element => {
              withZeroTerminalObject[element] = 0;
            });

            terminalObject = { ...withZeroTerminalObject, ...terminalObject };
            const terminalNeurons = Object.keys(terminalObject);

            terminalFilterResult.push(
              ...terminalNeurons.filter(el => {
                const terminalPoint = terminalObject[el];
                if (
                  relation.moreSetting.terminalPointsMin &&
                  terminalPoint < relation.moreSetting.terminalPointsMin
                ) {
                  return false;
                }

                if (
                  relation.moreSetting.terminalPointsMax &&
                  terminalPoint > relation.moreSetting.terminalPointsMax
                ) {
                  return false;
                }

                return true;
              })
            );
          }
        });

        axonNeurons = axonNeurons.filter(
          el =>
            terminalFilterResult.includes(el) &&
            moreSettingProjects.includes(project)
        );
      }

      // if projection mode is selected, we filter with cable length >0 if no cable length is defined
      const enableCableLengthFilter =
        relation.moreSetting.projectionTarget === "Projection Mode" &&
        relation.moreSetting.projectionMode;

      if (
        relation.moreSetting.cableLengthMin ||
        relation.moreSetting.cableLengthMax ||
        enableCableLengthFilter
      ) {
        const cableFilterResult = [];
        cableLengthArray.forEach(cableLengthItem => {
          let cableObject = cableLengthItem.data[regionUID];
          if (cableObject) {
            let withZeroCableObject = {};
            originalAxonNeurons.forEach(element => {
              withZeroCableObject[element] = 0;
            });

            let modeType = relation.moreSetting.projectionMode;
            if (!modeType) {
              modeType = "all";
            }
            cableObject = { ...withZeroCableObject, ...cableObject };
            const cableNeurons = Object.keys(cableObject);
            cableFilterResult.push(
              ...cableNeurons.filter(el => {
                const cableLength = cableObject[el];
                if (
                  relation.moreSetting.cableLengthMin &&
                  cableLength < relation.moreSetting.cableLengthMin
                ) {
                  return false;
                }
                const notAll =
                  modeType !== "all" &&
                  relation.moreSetting.projectionTarget === "Projection Mode";

                if (notAll) {
                  if (
                    cableLength <=
                    (relation.moreSetting.cableLengthMin
                      ? relation.moreSetting.cableLengthMin
                      : 0)
                  ) {
                    return false;
                  }
                }

                if (
                  enableCableLengthFilter &&
                  relation.moreSetting.cableLengthMin === "" &&
                  cableLength < 0
                ) {
                  return false;
                }

                if (
                  relation.moreSetting.cableLengthMax &&
                  cableLength > relation.moreSetting.cableLengthMax
                ) {
                  return false;
                }

                return true;
              })
            );
          }
        });

        axonNeurons = axonNeurons.filter(
          el =>
            cableFilterResult.includes(el) &&
            moreSettingProjects.includes(project)
        );
      }

      ids.push(...axonNeurons);
    }

    neurons.push(...ids.map(id => {
      const projectNeurons = storeNeuronData[project];
      return projectNeurons ? projectNeurons[id] : undefined;
    }).filter(Boolean));
  });
  return neurons;
};
const getRelationNeuronFiles = relation => {
  return getRelationNeurons(relation).map(el => el.file);
};

const filterWithSingleRelation = (inputNeurons, relation) => {
  const neuronFiles = new Set(getRelationNeuronFiles(relation));
  return inputNeurons.filter(el => neuronFiles.has(el.file));
};

const filterWithRelations = (inputNeurons, relations) => {
  // check valid relations
  const validRelations = relations.filter(el => {
    return el.region !== "";
  });

  if (validRelations.length === 0) {
    return inputNeurons;
  } else if (validRelations.length === 1) {
    const relation = validRelations[0];
    return filterWithSingleRelation(inputNeurons, relation);
  } else {
    let targetNeurons = [];
    for (let i = 0; i < validRelations.length; i++) {
      if (i === 0) {
        targetNeurons = filterWithSingleRelation(
          inputNeurons,
          validRelations[i]
        );
      } else {
        const currentNeuronFiles = new Set(getRelationNeuronFiles(validRelations[i]));
        const previousRelationType = validRelations[i - 1].relation;

        if (previousRelationType === "Overlap") {
          targetNeurons = targetNeurons.filter(el =>
            currentNeuronFiles.has(el.file)
          );
        } else if (previousRelationType === "Exclude") {
          targetNeurons = targetNeurons.filter(el =>
            !currentNeuronFiles.has(el.file)
          );
        } else {
          const currentResult = filterWithSingleRelation(
            inputNeurons,
            validRelations[i]
          );
          targetNeurons = [...new Set([...targetNeurons, ...currentResult])];
        }
      }
    }
    return targetNeurons;
  }
};

export const initCondition = () => {
  return {
    axonAndDentrite: true,
    axonOnly: true,
    dendriteOnly: true,
    undefinedRecon: true,
    left: true,
    right: true,
    sampleID: "",
    neuronID: "",
    publicGroup: "",
    customGroup: "",
    temporaryGroup: "",
    class: [],
    mouseLine: [],
    relationItems: [
      createRelationItem("Soma", "Overlap"),
      createRelationItem("Axon", "")
    ]
  };
};

export const createRelationItem = (type, relation = "") => {
  return {
    type,
    region: "",
    relation,
    moreSetting: {
      projectionTarget: "Projection Mode",
      projectionMode: null,
      projectionPathway: "All",
      terminalPointsMin: null,
      terminalPOintsMax: null,
      cableLengthMin: null,
      cableLengthMax: null,
      branchPointsMin: null,
      branchPointsMax: null
    }
  };
};

// Precompute structureColor to avoid repeating hexToRgb + map on every addInformationToNeuron call
const _defaultStructureColor = {
  dentriteColor: hexToRgb("#FFE040").map(el => el / 255.0),
  somaColor: hexToRgb("#FF4BE2").map(el => el / 255.0),
  axonColor: hexToRgb("#00FE00").map(el => el / 255.0),
  undefinedColor: hexToRgb("#FFFFFF").map(el => el / 255.0)
};

/**
 * Stable unique key for a filtered-list row.
 * `file` alone is not unique across projects (same SWC can appear in multiple).
 */
export const neuronSelectionKey = neuron => {
  if (!neuron) return "";
  return `${neuron.project || neuron.projectFullName || ""}::${neuron.file || ""}`;
};

/**
 * Deduplicate neurons by SWC file (NeuroViz / viewedNeurons key by filename).
 * Keeps first occurrence.
 */
export const uniqueNeuronsByFile = neurons => {
  const seen = new Set();
  const out = [];
  for (let i = 0; i < (neurons || []).length; i++) {
    const n = neurons[i];
    const f = n?.file;
    if (!f || seen.has(f)) continue;
    seen.add(f);
    out.push(n);
  }
  return out;
};

/**
 * Build a scene/UI-enriched neuron from a frozen catalog row.
 * Call only when loading into scene / analyzing — not for every filter result.
 */
export const enrichNeuronForScene = (neuron, neuronTypeColors) => {
  if (!neuron) return neuron;
  // already enriched (e.g. re-load of viewed neuron)
  if (neuron.colorScheme !== undefined && neuron.idColor !== undefined) {
    return neuron;
  }
  const neuronType = Array.isArray(neuron.type_array)
    ? neuron.type_array[0]
    : neuron.type_array;
  const typeColors = neuronTypeColors || store.state.neuron.typeColors;
  return {
    ...neuron,
    colorScheme: "random",
    idColor: randomColor(1.0),
    structureColor: _defaultStructureColor,
    typeColor: typeColors ? typeColors[neuronType] : undefined,
    regionColor: "",
    currentColor: "",
    mouseLine: neuronType
  };
};

// backwards-compatible alias
const addInformationToNeuron = enrichNeuronForScene;

export const isValidCondition = condition => {
  if (
    condition.sampleID !== "" ||
    condition.neuronID !== "" ||
    condition.publicGroup !== "" ||
    condition.customGroup !== "" ||
    condition.temporaryGroup !== "" ||
    condition.class.length > 0 ||
    condition.mouseLine.length > 0
  ) {
    return true;
  }

  const relationItems = condition.relationItems;
  for (let i = 0; i < relationItems.length; i++) {
    if (relationItems[i].region !== "") {
      return true;
    }
  }

  return false;
};

export const filterNeurons = (neuronData, neuronTypeColors, condition) => {
  // Total neurons for the current project
  let totalNeurons = [];
  if (!isValidCondition(condition)) {
    return totalNeurons;
  }
  // not group: if it already exists in the view, no need to assign again
  const currentGroup = condition.customGroup || condition.temporaryGroup;
  if (currentGroup) {
    const id = currentGroup?.split("___")[1];
    let curGroup = store.state.groupsDetailData[id];
    let parts;
    if (curGroup) {
      parts = store.state.groupsDetailData[id]?.parts;
    } else {
      curGroup = store.state.temporaryGroups.find(g => g.id === id);
      parts = curGroup?.parts;
    }

    parts?.forEach(item => {
      const el = store.state.projects?.find(
        pro => item?.project === pro?.acronym
      );
      item?.files?.forEach(file => {
        const projectsValue = Object.values(neuronData[el?.name]);
        const result = projectsValue.find(neuron => neuron?.file === file);
        // result.group = [{ id, name: curGroup.name, save: flag }]
        totalNeurons.push(Object.assign(result));
      });
    });
  } else {
    const projectsName = Object.keys(neuronData);
    projectsName
      .filter(project => {
        if (condition.publicGroup === "All public data") {
          return true;
        }
        return project === condition.publicGroup;
      })
      .forEach(el => {
        const ids = Object.keys(neuronData[el]);
        totalNeurons.push(
          ...ids.map(id => {
            return neuronData[el][id];
          })
        );
      });
  }

  // ===== Merge filters into a single pass: class / sampleID / neuronID / mouseLine / recon / side =====
  // The first 6 filters can be merged into a single pass, avoiding a new array on every filter (50K elements × 6 passes)
  const classFilters = condition.class;
  const sampleIDs = condition.sampleID;
  const neuronIDs = condition.neuronID;
  const mouseLines = condition.mouseLine;
  const hasClass = classFilters.length > 0;
  const hasSample = sampleIDs.length > 0;
  const hasNeuron = neuronIDs.length > 0;
  const hasMouseLine = mouseLines.length > 0;
  const hasRecon = !condition.axonOnly || !condition.axonAndDentrite || !condition.dendriteOnly || !condition.undefinedRecon;
  const hasSide = !condition.left || !condition.right;

  if (hasClass || hasSample || hasNeuron || hasMouseLine || hasRecon || hasSide) {
    const target = store.state.target;
    const mouseLineSet = hasMouseLine ? new Set(mouseLines) : null;
    totalNeurons = totalNeurons.filter(el => {
      if (hasClass && !classFilters.some(cls => el[cls.type] === cls.value)) return false;
      if (hasSample) {
        const id = target !== "monkey" ? el.file.split("_")[0] : el.file.split("-")[0];
        if (!sampleIDs.includes(id)) return false;
      }
      if (hasNeuron) {
        const id = el.file.split(".")[0];
        if (!neuronIDs.includes(id)) return false;
      }
      if (hasMouseLine) {
        const matched = el.type_array.some(t => mouseLineSet.has(t));
        if (!matched) return false;
      }
      if (hasRecon) {
        const rt = el.reconstruction_type.toLowerCase();
        if (!condition.axonOnly && rt === "axon_only") return false;
        if (!condition.axonAndDentrite && rt === "axon_and_dendrite") return false;
        if (!condition.dendriteOnly && rt === "dendrite_only") return false;
        if (!condition.undefinedRecon && rt === "undefined") return false;
      }
      if (hasSide) {
        const h = el.hemisphere.toLowerCase();
        if (!condition.left && h === "left") return false;
        if (!condition.right && h === "right") return false;
      }
      return true;
    });
  }

  // filter with relation (logic is complex, kept separate)
  totalNeurons = filterWithRelations(totalNeurons, condition.relationItems);

  // Return frozen catalog refs only — no per-row clone / Vue reactive wrappers.
  // Selection lives in store.filteredSelected; scene colors via enrichNeuronForScene.
  return totalNeurons;
};

export const formatNeuronData = (
  uids,
  project,
  neuronData,
  neuronTypeColors
) => {
  let neurons = [];
  uids.forEach(uid => {
    neurons.push(neuronData[project][uid]);
  });
  neurons = neurons.map(el => {
    return addInformationToNeuron(el, neuronTypeColors);
  });

  return neurons;
};
