const assert = require("assert");

const {
  collectSyncedDendriticFiles
} = require("../src/utils/highResDendrites");

function run() {
  const requestedFiles = ["den-a.swc", "den-b.swc", "den-a.swc"];

  const initialSync = collectSyncedDendriticFiles({
    requestedFiles,
    viewedNeurons: [],
    hasTrackedMainView: false
  });

  assert.deepStrictEqual(initialSync.files, ["den-a.swc", "den-b.swc"]);
  assert.strictEqual(initialSync.hasTrackedMainView, false);

  const trackedSync = collectSyncedDendriticFiles({
    requestedFiles,
    viewedNeurons: [
      {
        file: "main-a.swc",
        dendritic: "den-a.swc",
        visible: true,
        dendriteVisible: true
      },
      {
        file: "main-b.swc",
        dendritic: "den-b.swc",
        visible: false,
        dendriteVisible: true
      }
    ],
    hasTrackedMainView: false
  });

  assert.deepStrictEqual(trackedSync.files, ["den-a.swc"]);
  assert.strictEqual(trackedSync.hasTrackedMainView, true);

  const hiddenDendriteSync = collectSyncedDendriticFiles({
    requestedFiles,
    viewedNeurons: [
      {
        file: "main-a.swc",
        dendritic: "den-a.swc",
        visible: true,
        dendriteVisible: false
      }
    ],
    hasTrackedMainView: true
  });

  assert.deepStrictEqual(hiddenDendriteSync.files, []);
  assert.strictEqual(hiddenDendriteSync.hasTrackedMainView, true);

  const unloadRemovedSync = collectSyncedDendriticFiles({
    requestedFiles,
    viewedNeurons: [],
    hasTrackedMainView: true
  });

  assert.deepStrictEqual(unloadRemovedSync.files, []);
  assert.strictEqual(unloadRemovedSync.hasTrackedMainView, true);
}

run();
