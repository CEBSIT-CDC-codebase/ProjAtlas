const workerCode = () => {
  function computeNeuronRegionRelation(neuronRegionRelation) {
    const region_neuron_relationMap = new Map();

    // Predefine the default structure to avoid repeated creation
    const createDefaultRelation = () => ({
      recipient_neuron_array: [],
      projecting_neuron_array: [],
      owned_neuron_array: [],
      terminal_array: []
    });

    // Helper function to get or create a region relation
    const getOrCreateRegionRelation = regionUid => {
      if (!region_neuron_relationMap.has(regionUid)) {
        region_neuron_relationMap.set(regionUid, createDefaultRelation());
      }
      return region_neuron_relationMap.get(regionUid);
    };

    // Use Object.entries instead of Object.keys to save a lookup
    Object.keys(neuronRegionRelation).forEach(uid => {
      const neuronData = neuronRegionRelation[uid];
      const {
        input_region_array: inputRegions,
        owner_region_array: ownerRegions,
        output_region_array: outputRegions,
        output_terminal_count: terminalCounts
      } = neuronData;

      // Handle input-to-region relations
      if (inputRegions?.length) {
        inputRegions.forEach(regionUid => {
          getOrCreateRegionRelation(regionUid).recipient_neuron_array.push(uid);
        });
      }

      // Handle project-to-region relations
      if (outputRegions?.length) {
        outputRegions.forEach((regionUid, index) => {
          const relation = getOrCreateRegionRelation(regionUid);
          relation.projecting_neuron_array.push(uid);

          // Only add when terminalCounts is present
          if (terminalCounts?.[index] !== undefined) {
            relation.terminal_array.push({
              uid: uid,
              count: terminalCounts[index]
            });
          }
        });
      }

      // Handle owner-to-region relations
      if (ownerRegions?.length) {
        ownerRegions.forEach(regionUid => {
          getOrCreateRegionRelation(regionUid).owned_neuron_array.push(uid);
        });
      }
    });

    return Object.fromEntries(region_neuron_relationMap);
  }

  self.addEventListener("message", e => {
    try {
      const messageData = e.data;
      const taskId = messageData.taskId;
      const data = messageData.data;

      // Compute the result
      const result = computeNeuronRegionRelation(data);

      // Return the result, including the task ID
      self.postMessage({
        taskId: taskId,
        result: result
      });
    } catch (error) {
      self.postMessage({
        taskId: e.data.taskId,
        error: error.message
      });
    }
  });
};

let code = workerCode.toString();
code = code.substring(code.indexOf("{") + 1, code.lastIndexOf("}"));
const blob = new Blob([code], { type: "application/javascript" });
const workerScript = URL.createObjectURL(blob);
export default workerScript;
