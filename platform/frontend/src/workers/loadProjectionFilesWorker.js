const workerCode = () => {
    var projectionCache = new Map();

    function randomColor(opaticy) {
        var r = Math.floor(Math.random() * 255);
        var g = Math.floor(Math.random() * 255);
        var b = Math.floor(Math.random() * 255);
        var op = "";
        if (opaticy) {
            op = Math.floor(255 * opaticy).toString(16);
            if (op.length === 1) op = "0" + op;
        }
        return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1) + op;
    }

    var getRegionFamily = function (parent, regionDict) {
        if (!regionDict) return null;
        for (var i = 0; i < regionDict.length; i++) {
            var item = regionDict[i];
            if (item.parent == parent || item.region == parent) return item.family;
        }
        return null;
    };

    var calculateLogValues = function (values, ignoreZeros) {
        if (!values || values.length === 0) return { max: 0, min: 0 };
        var filtered = values.filter(function (v) { return ignoreZeros ? v > 0 : true; });
        if (filtered.length === 0) return { max: 0, min: 0 };
        var logs = filtered.map(function (v) {
            var res = Math.log10(v);
            return isFinite(res) ? res : 0;
        });
        return { max: Math.max.apply(null, logs), min: Math.min.apply(null, logs) };
    };

    function computedFunc(payload) {
        var neurons = payload.neurons;
        var config = payload.config;
        var stateData = payload.stateData;
        var VUE_APP_SRV = config.VUE_APP_SRV;
        var TARGET = config.TARGET;
        var projectionFiles = stateData.projectionFiles;

        // 1. Deduplicate project (ES5 style)
        var neuronProjects = neurons.map(function (n) { return n && n.project; })
            .filter(function (v, i, self) { return v && self.indexOf(v) === i; });

        var cacheKey = TARGET + "-" + neurons.map(function (n) { return n.file; }).sort().join(",");
        if (projectionCache.has(cacheKey)) return Promise.resolve(projectionCache.get(cacheKey));

        // 2. Load dictionary
        var fetchDict = projectionFiles.regionDict
            ? Promise.resolve(projectionFiles.regionDict)
            : fetch(VUE_APP_SRV + stateData.urls.regionDict).then(function (r) { return r.json(); });

        return fetchDict.then(function (dict) {
            projectionFiles.regionDict = dict;

            // 3. Load project data
            return Promise.all(neuronProjects.map(function (proj) {
                if (projectionFiles[proj]) return Promise.resolve();
                return Promise.all([
                    fetch(VUE_APP_SRV + stateData.urls[proj].axonLength).then(function (r) { return r.json(); }),
                    fetch(VUE_APP_SRV + stateData.urls[proj].terminalCount).then(function (r) { return r.json(); })
                ]).then(function (res) {
                    // Fix slicedToArray error: avoid [a, b] = res destructuring, index directly instead
                    projectionFiles[proj] = { axonLength: res[0], terminalCount: res[1] };
                });
            }));
        }).then(function () {
            // 4. Compute acronyms (using the pre-built file→acronym Map, no longer iterating neuronData)
            var acronyms = {};
            var fileToAcronym = stateData.fileAcronymMap || {};
            neurons.forEach(function (n) {
                if (!n.project) return;
                var acronym = fileToAcronym[n.file];
                if (acronym) {
                    if (!acronyms[acronym]) acronyms[acronym] = [];
                    if (acronyms[acronym].indexOf(n.file) === -1) acronyms[acronym].push(n.file);
                }
            });

            var loadDataInternal = function (type) {
                var field = type === "axon" ? "axonLength" : "terminalCount";
                var result = {};
                neurons.forEach(function (n) {
                    var fileName = n.file.slice(0, -4);
                    var data = (projectionFiles[n.project] || {})[field];
                    if (data && data[fileName]) result[fileName] = data[fileName];
                });

                var parents = [];
                var keyValues = {}; // Map downgraded to Object
                Object.keys(result).forEach(function (rKey) {
                    var item = result[rKey];
                    Object.keys(item).forEach(function (k) {
                        keyValues[k] = (keyValues[k] || 0) + item[k];
                    });
                });

                // Pre-build regionDict/regionData lookup tables to avoid O(n^2) .find()
                var regionDictMap = {};
                if (projectionFiles.regionDict) {
                  for (var di = 0; di < projectionFiles.regionDict.length; di++) {
                    var entry = projectionFiles.regionDict[di];
                    if (entry && entry.region) regionDictMap[entry.region] = entry;
                  }
                }
                var regionByAcronym = {};
                if (TARGET !== "monkey") {
                  var rData = stateData.regionData || {};
                  var rKeys = Object.keys(rData);
                  for (var ri = 0; ri < rKeys.length; ri++) {
                    var rItem = rData[rKeys[ri]];
                    if (rItem && rItem.acronym) regionByAcronym[rItem.acronym] = rItem;
                  }
                }

                Object.keys(keyValues).forEach(function (k) {
                    var fam = "", col = "";
                    if (TARGET === "monkey") {
                        const key = config?.SUB_SPECIES === 'SC' ? 'parent' : 'family';
                        var info = regionDictMap[k];
                        if (info) {
                            fam = info[key] || "";
                            col = randomColor(0.5);
                        }
                    } else {
                        fam = getRegionFamily(k, projectionFiles.regionDict);
                        var fItem = regionByAcronym[fam];
                        col = fItem ? fItem.allenColor : "";
                    }
                    parents.push({ parent: k, value: keyValues[k], family: fam, familyColor: col });
                });

                // --- Replace the mapBrain/MaxMin logic inside loadDataInternal ---

                var mapBrain = {};
                var neuronMaxValue = 0;
                var brainMaxValue = 0;
                var logValues = {
                    neuronMax: 0,
                    neuronMin: Infinity,
                    brainMax: 0,
                    brainMin: Infinity
                };

                // 1. Process mapBrain (replaces Object.entries(acronyms))
                var acronymKeys = Object.keys(acronyms);
                for (var i = 0; i < acronymKeys.length; i++) {
                    var key = acronymKeys[i];
                    var files = acronyms[key];
                    var obj = {};

                    for (var j = 0; j < files.length; j++) {
                        var name = files[j];
                        var neuron = result[name.slice(0, -4)];
                        if (!neuron) continue;

                        // Replaces for (const [b, v] of Object.entries(neuron))
                        var neuronKeys = Object.keys(neuron);
                        for (var k = 0; k < neuronKeys.length; k++) {
                            var b = neuronKeys[k];
                            var v = neuron[b];
                            if (typeof v === "number" && isFinite(v)) {
                                obj[b] = (obj[b] || 0) + v;
                            }
                        }
                    }

                    // Replaces Object.values(obj)
                    var vals = Object.keys(obj).map(function (k) { return obj[k]; });
                    if (vals.length > 0) {
                        // Replaces Math.max(...vals)
                        var currentMax = Math.max.apply(null, vals);
                        brainMaxValue = Math.max(brainMaxValue, currentMax);

                        // Replaces const { max, min } = calculateLogValues(vals)
                        var brainLogs = calculateLogValues(vals, true);
                        logValues.brainMax = Math.max(logValues.brainMax, brainLogs.max);
                        if (brainLogs.min > 0) {
                            logValues.brainMin = Math.min(logValues.brainMin, brainLogs.min);
                        }
                    }
                    mapBrain[key] = obj;
                }

                // 2. Process neuron data (replaces Object.values(result))
                var resultKeys = Object.keys(result);
                for (var index = 0; index < resultKeys.length; index++) {
                    var item = result[resultKeys[index]];
                    // Replaces Object.values(item).filter(...)
                    var itemVals = Object.keys(item).map(function (k) { return item[k]; }).filter(function (v) {
                        return typeof v === "number" && isFinite(v);
                    });

                    if (itemVals.length > 0) {
                        var currentNeuronMax = Math.max.apply(null, itemVals);
                        neuronMaxValue = Math.max(neuronMaxValue, currentNeuronMax);

                        var neuronLogs = calculateLogValues(itemVals, true);
                        logValues.neuronMax = Math.max(logValues.neuronMax, neuronLogs.max);
                        if (neuronLogs.min > 0) {
                            logValues.neuronMin = Math.min(logValues.neuronMin, neuronLogs.min);
                        }
                    }
                }

                if (!isFinite(logValues.neuronMin)) logValues.neuronMin = 0;
                if (!isFinite(logValues.brainMin)) logValues.brainMin = 0;

                return {
                    brains: parents,
                    neurons: result,
                    mapBrain: mapBrain,
                    logValues: logValues,
                    neuronMaxValue: neuronMaxValue,
                    brainMaxValue: brainMaxValue
                };

            };

            var final = { axonHeatMapValue: loadDataInternal("axon"), terminalHeatMapValue: loadDataInternal("terminal") };
            projectionCache.set(cacheKey, final);
            return final;
        });
    }

    self.onmessage = function (e) {
        computedFunc(e.data).then(function (res) {
            self.postMessage({ success: true, data: res });
        }).catch(function (err) {
            self.postMessage({ success: false, error: err.toString() });
        });
    };
};
// --- Build the Worker Blob ---
let code = workerCode.toString();
// Extract the function body
code = code.substring(code.indexOf("{") + 1, code.lastIndexOf("}"));
const blob = new Blob([code], { type: "application/javascript" });

export default URL.createObjectURL(blob);