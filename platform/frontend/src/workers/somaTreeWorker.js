const workerCode = () => {
  function computeTreeInWorker(data) {
    const {
      regionSomaTreeArray,
      neuronItems,
      regionNeuronRelation,
      regionData,
      target
    } = data;

    let regionTree = [];
    const regionList = [];
    let maxSomaCount = 0;
    let maxDensity = 0;

    // Pre-build (project, regionUID) → Set<neuronId> index to avoid O(n) includes() lookups
    const ownedIndex = {};
    const projects = Object.keys(regionNeuronRelation);
    for (let p = 0; p < projects.length; p++) {
      const project = projects[p];
      const regions = regionNeuronRelation[project];
      if (!regions) continue;
      const regionUIDs = Object.keys(regions);
      for (let r = 0; r < regionUIDs.length; r++) {
        const uid = regionUIDs[r];
        const arr = regions[uid].owned_neuron_array;
        if (arr && arr.length) {
          const key = project + '|' + uid;
          ownedIndex[key] = new Set(arr);
        }
      }
    }

    function getSomaCount(regionItem) {
      if (neuronItems.length === 0) {
        return 0;
      }
      let count = 0;
      const regionUID = regionItem.regionObj.uid_array[0];
      const ownedSets = {};
      // Collect the owned Set for this region across projects
      for (let p = 0; p < projects.length; p++) {
        const key = projects[p] + '|' + regionUID;
        if (ownedIndex[key]) ownedSets[projects[p]] = ownedIndex[key];
      }
      neuronItems.forEach(neuron => {
        const project = neuron.projectFullName;
        const owned = ownedSets[project];
        if (owned && owned.has(neuron.id)) {
          count++;
        }
      });

      if (count > maxSomaCount) {
        maxSomaCount = count;
      }

      return count;
    }

    let id = 0;
    const computeTreeNode = rawNode => {
      const obj = {
        id,
        depth: rawNode.depth,
        name: rawNode.name,
        regionObj: rawNode.regionObj,
        volume: (regionData[rawNode.regionObj.uid_array[0]] || {}).volume || 0,
        children: []
      };

      const hasNeuron = neuronItems.length > 0;
      if (hasNeuron) {
        obj.somaCount = getSomaCount(obj);
        obj.density = obj.volume === 0 ? 0 : obj.somaCount / obj.volume;
      } else {
        obj.somaCount = 0;
        obj.density = 0;
      }

      id++;

      if (obj.density > maxDensity) {
        maxDensity = obj.density;
      }

      if (rawNode.children.length) {
        rawNode.children.forEach(child => {
          obj.children.push(computeTreeNode(child));
        });
      } else {
        if (obj.somaCount) {
          regionList.push({
            name: obj.name,
            count: obj.somaCount
          });
        }
      }
      return obj;
    };

    if (target === "monkey") {
      const obj = {
        children: regionSomaTreeArray
      };
      obj.children.forEach(child => {
        regionTree.push(computeTreeNode(child));
      });

      const updateDensity = node => {
        if (node.children.length > 0) {
          node.children.forEach(child => {
            updateDensity(child);
          });
          const nodesSomaCount = node.children.reduce((acc, child) => {
            return acc + child.somaCount;
          }, 0);

          const nodesVolume = node.children.reduce((acc, child) => {
            return acc + Number(child.volume);
          }, 0);

          node.somaCount = nodesSomaCount;
          node.volume = nodesVolume;
          node.density = node.volume === 0 ? 0 : nodesSomaCount / nodesVolume;

          if (node.density > maxDensity) {
            maxDensity = node.density;
          }

          if (node.somaCount > maxSomaCount) {
            maxSomaCount = node.somaCount;
          }
        }
      };

      regionTree.forEach(node => {
        updateDensity(node);
      });
    }

    if (target === "mouse") {
      if (regionSomaTreeArray.length > 0) {
        regionSomaTreeArray[0].children.forEach(child => {
          regionTree.push(computeTreeNode(child));
        });
      }
    }

    return {
      neuronItems,
      regionTree,
      regionList,
      maxSomaCount,
      maxDensity
    };
  }

  self.addEventListener("message", e => {
    const result = computeTreeInWorker(e.data);
    self.postMessage(result);
  });
};

let code = workerCode.toString();
code = code.substring(code.indexOf("{") + 1, code.lastIndexOf("}"));

const blob = new Blob([code], { type: "application/javascript" });
const workerScript = URL.createObjectURL(blob);

export default workerScript;
