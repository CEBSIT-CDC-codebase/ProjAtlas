const workerCode = () => {
  function isRegionContainSoma(region, regionNeuronRelation) {
    const projects = Object.keys(regionNeuronRelation);

    const uids = region.regionObj.uid_array;
    for (let i = 0; i < uids.length; ++i) {
      for (let j = 0; j < projects.length; ++j) {
        const projectData = regionNeuronRelation[projects[j]];
        if (!projectData) continue;
        const relation = projectData[uids[i]];
        if (
          relation &&
          relation.owned_neuron_array &&
          relation.owned_neuron_array.length > 0
        ) {
          return true;
        }
      }
    }

    if (region.children.length > 0) {
      for (let i = 0; i < region.children.length; ++i) {
        if (isRegionContainSoma(region.children[i], regionNeuronRelation)) {
          return true;
        }
      }
    }
    return false;
  }

  function computeRegionSomaTree(regionType, regionNeuronRelation) {
    // if region type is not set, we return empty array
    if (!regionType) {
      return [];
    }

    // create empty array as the init region soma tree array
    const regionSomaTreeArray = [];

    // based on neuronType, build the tree like array
    // loop the main types
    let totalIDs = 0;
    const addChildType = (parentObj, typeName) => {
      let obj = {};
      //id
      obj.id = totalIDs;
      totalIDs++;

      obj.depth = parentObj ? parentObj.depth + 1 : 0;

      //name
      if (typeName.includes("(") && typeName.includes(")")) {
        let parts = typeName.split("(");
        let arc = parts[0].trim().toLocaleUpperCase();
        let main = parts[1].split(")")[0].trim();
        obj.name = arc + " " + main;
      } else {
        obj.name = typeName;
      }

      //Children
      obj.children = [];

      if (parentObj == null) {
        obj.regionObj = regionType[typeName];
        obj.parentObj = null;
      } else {
        obj.regionObj = parentObj.regionObj[typeName];
        obj.parentObj = parentObj;
        parentObj.children.push(obj);
      }

      //if there are any subarray, iterate the subarray
      if (
        Object.prototype.hasOwnProperty.call(obj.regionObj, "sub_type_array")
      ) {
        let subTypes = obj.regionObj["sub_type_array"];
        subTypes.forEach(type => {
          addChildType(obj, type);
        });
      }
      return obj;
    };
    // loop the main types
    const mainTypes = regionType.sub_type_array;
    if (!mainTypes || !Array.isArray(mainTypes)) return [];
    mainTypes.forEach(mainType => {
      let obj = addChildType(null, mainType);
      regionSomaTreeArray.push(obj);
    });

    // filter with soma
    const cleanSomaArray = obj => {
      if (!isRegionContainSoma(obj, regionNeuronRelation) && obj.parentObj) {
        const index = obj.parentObj.children.indexOf(obj);
        obj.parentObj.children.splice(index, 1);
      } else if (obj.children.length > 0) {
        for (let i = 0; i < obj.children.length; ++i) {
          cleanSomaArray(obj.children[i]);
        }
      }
    };

    for (let i = 0; i < regionSomaTreeArray.length; ++i) {
      cleanSomaArray(regionSomaTreeArray[i]);
    }

    return regionSomaTreeArray;
  }

  self.addEventListener("message", e => {
    const { regionType, regionNeuronRelation } = e.data;
    const result = computeRegionSomaTree(regionType, regionNeuronRelation);
    self.postMessage(result);
  });
};

let code = workerCode.toString();
code = code.substring(code.indexOf("{") + 1, code.lastIndexOf("}"));
const blob = new Blob([code], { type: "application/javascript" });
const workerScript = URL.createObjectURL(blob);
export default workerScript;
