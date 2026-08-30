const workerCode = () => {
  function computeCsvData(data) {
    const { id, type, curData, rowsIndex } = data;
    // Get column indices
    const colsIndex = Object.keys(curData);
    const results = [];

    // Compute each cell's value (direct property access replaces the triple-nested for-in lookup)
    rowsIndex.forEach(brain => {
      const result = [];

      for (let rowTitle in curData) {
        const val = curData[rowTitle];
        result.push(brain in val ? val[brain] : 0);
      }

      results.push(result);
    });

    // Add row headers
    for (let i = 0; i < results.length; i++) {
      results[i].unshift(rowsIndex[i]);
    }

    // Add column headers
    colsIndex.unshift(" ");
    results.unshift(colsIndex);

    return {
      id,
      type,
      results
    };
  }

  self.addEventListener("message", e => {
    const result = computeCsvData(e.data);
    self.postMessage(result);
  });
};

let code = workerCode.toString();
code = code.substring(code.indexOf("{") + 1, code.lastIndexOf("}"));

const blob = new Blob([code], { type: "application/javascript" });
const workerScript = URL.createObjectURL(blob);

export default workerScript;
