/* eslint-disable */
const workerCode = function () {
  /**
   * Parse the IPL depth CSV
   * Format: the first row is the header (neuron_id, IPL_depth_0, IPL_depth_1, ...)
   *         each subsequent row: neuron_id, val0, val1, ...
   *
   * Stored as a row-major dense Float32Array:
   *   matrix[rowIndex * numCols + colIndex] = value
   */
  function parseIPLDepthCSV(arrayBuffer) {
    const text = new TextDecoder('utf-8').decode(new Uint8Array(arrayBuffer));
    const lines = text.split('\n');

    // ---------- Parse the header ----------
    const headers = lines[0].split(',');
    const depthCols = headers.slice(1).map(function (h) { return h.trim(); });
    const numCols = depthCols.length;

    // ---------- Count valid rows (skip empty lines) ----------
    var validRows = 0;
    for (var i = 1; i < lines.length; i++) {
      if (lines[i].trim()) validRows++;
    }

    // ---------- Allocate a precisely-sized TypedArray in one pass ----------
    var matrix = new Float32Array(validRows * numCols);
    var neuronIds = [];

    var r = 0;
    for (var i = 1; i < lines.length; i++) {
      var line = lines[i].trim();
      if (!line) continue;

      var cols = line.split(',');
      neuronIds.push(cols[0]);

      var offset = r * numCols;
      for (var c = 0; c < numCols; c++) {
        matrix[offset + c] = parseFloat(cols[c + 1]) || 0;
      }
      r++;
    }

    return {
      matrix: matrix,       // Float32Array, size = validRows × numCols
      neuronIds: neuronIds, // string[], length = validRows (order preserved for building a Map on the main thread)
      depthCols: depthCols, // string[], length = numCols
      numCols: numCols
    };
  }

  self.onmessage = function (e) {
    var type = e.data.type;

    if (type === 'PARSE') {
      try {
        var result = parseIPLDepthCSV(e.data.buffer);
        // Transfer matrix's buffer to the main thread (zero-copy); other fields are passed normally
        self.postMessage(
          { type: 'READY', payload: result },
          [result.matrix.buffer]
        );
      } catch (err) {
        self.postMessage({ type: 'ERROR', message: err.message });
      }
    }
  };
};

let code = workerCode.toString();
code = code.substring(code.indexOf('{') + 1, code.lastIndexOf('}'));

const blob = new Blob([code], { type: 'application/javascript' });
const workerScript = URL.createObjectURL(blob);

export default workerScript;
