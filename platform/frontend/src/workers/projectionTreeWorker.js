const workerCode = () => {
  function computeTreeInWorker(data) {
    const {
      regionAxonTreeArray,
      neuronItems,
      regionNeuronRelation,
      neuronRegionRelation,
      target
    } = data;

    let regionTree = [];
    let regionList = [];
    let maxLength = 0;
    let maxNeuronCount = 0;
    const regionNamesMap = new Map();

    // Pre-process neuron data to build a fast lookup table
    const neuronLookup = new Map();

    // Pre-build projecting Sets to avoid O(n) includes() lookups
    const projectingSets = {};  // key: project|regionUID
    if (neuronItems.length > 0) {
      const projects = Object.keys(regionNeuronRelation);
      for (let p = 0; p < projects.length; p++) {
        const project = projects[p];
        const regions = regionNeuronRelation[project];
        if (!regions) continue;
        const regionUIDs = Object.keys(regions);
        for (let r = 0; r < regionUIDs.length; r++) {
          const uid = regionUIDs[r];
          const arr = regions[uid].projecting_neuron_array;
          if (arr && arr.length) {
            projectingSets[project + '|' + uid] = new Set(arr);
          }
        }
      }
    }

    if (neuronItems.length > 0) {
      neuronItems.forEach(neuron => {
        const project = neuron.projectFullName;
        const projectNN = neuronRegionRelation[project];
        if (!projectNN) return;
        const outputData = projectNN[neuron.id];
        if (!outputData) return;
        if (outputData.output_region_array == undefined) {
          outputData.output_region_array = [];
        }

        outputData.output_region_array.forEach((regionUID, index) => {
          if (!neuronLookup.has(String(regionUID))) {
            neuronLookup.set(String(regionUID), {
              count: 0,
              leftLength: 0,
              rightLength: 0
            });
          }

          const data = neuronLookup.get(String(regionUID));
          const lengths = outputData.output_length_array[index];

          const projSet = projectingSets[project + '|' + regionUID];
          if (projSet && projSet.has(neuron.id)) {
            data.count++;
            data.leftLength += Number(lengths[0]) || 0;
            data.rightLength += Number(lengths[1]) || 0;
          }
        });
      });
    }

    // Optimized parameter accessor
    function getParameter(regionItem) {
      const regionUID = regionItem.regionObj.uid_array[0];
      const data = neuronLookup.get(String(regionUID)) || {
        count: 0,
        leftLength: 0,
        rightLength: 0
      };

      if (data.leftLength > maxLength) maxLength = data.leftLength;
      if (data.rightLength > maxLength) maxLength = data.rightLength;

      return data;
    }

    let id = 0;
    // Build the tree iteratively to avoid recursion
    function buildTreeIterative(nodes) {
      const result = [];
      const stack = [
        {
          nodes,
          parent: null,
          index: 0
        }
      ];

      while (stack.length > 0) {
        const current = stack[stack.length - 1];

        if (current.index >= current.nodes.length) {
          stack.pop();
          continue;
        }

        const node = current.nodes[current.index];
        current.index++;

        const params = getParameter(node);
        const obj = {
          id: id++,
          depth: node.depth,
          name: node.name,
          regionObj: node.regionObj,
          children: [],
          leftLength: params.leftLength,
          rightLength: params.rightLength,
          count: params.count
        };

        regionNamesMap.set(obj.name, obj.id);
        if (obj.count > maxNeuronCount) maxNeuronCount = obj.count;

        if (current.parent) {
          current.parent.children.push(obj);
        } else {
          result.push(obj);
        }

        if (node.children && node.children.length > 0) {
          stack.push({
            nodes: node.children,
            parent: obj,
            index: 0
          });
        } else {
          params.count &&
            regionList.push({
              name: node.name,
              count: params.count,
              leftLength: params.leftLength,
              rightLength: params.rightLength
            });
        }
      }

      return result;
    }

    // Update parent node data via post-order traversal
    function updateParentStats(nodes) {
      // Use recursive post-order traversal to ensure children are processed before parents
      function postOrderTraversal(node) {
        // Process all children first
        if (node.children && node.children.length > 0) {
          let totalLeft = 0;
          let totalRight = 0;
          let totalCount = 0;

          // Recursively process each child
          for (let i = 0; i < node.children.length; i++) {
            const child = node.children[i];
            postOrderTraversal(child);

            // Accumulate child data
            totalLeft += child.leftLength || 0;
            totalRight += child.rightLength || 0;
            totalCount += child.count || 0;
          }

          // Update current node's data
          node.leftLength = totalLeft;
          node.rightLength = totalRight;
          node.count = totalCount;

          // Update global max values
          if (totalCount > maxNeuronCount) maxNeuronCount = totalCount;
          if (totalLeft > maxLength) maxLength = totalLeft;
          if (totalRight > maxLength) maxLength = totalRight;
        }
        // Leaf nodes need no processing, keep their original data
      }

      // Run post-order traversal for each root node
      for (let i = 0; i < nodes.length; i++) {
        postOrderTraversal(nodes[i]);
      }
    }

    if (target === "monkey") {
      regionTree = buildTreeIterative(regionAxonTreeArray);
      if (process.env.VUE_APP_SUB_SPECIES === "SC") {
        updateParentStats(regionTree);
      }
    } else if (target === "mouse" && regionAxonTreeArray.length > 0) {
      regionTree = buildTreeIterative(regionAxonTreeArray[0].children);
    }

    return {
      regionTree,
      regionList,
      maxLength,
      maxNeuronCount,
      regionNamesMap: Array.from(regionNamesMap.entries())
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
