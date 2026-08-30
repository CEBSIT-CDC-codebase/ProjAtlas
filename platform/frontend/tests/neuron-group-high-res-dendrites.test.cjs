const assert = require("assert");

const {
  removeHighResDendritesForNeurons
} = require("../src/utils/highResDendrites");

function createStore() {
  const commits = [];

  return {
    commits,
    commit(type, payload) {
      commits.push({ type, payload });
    }
  };
}

function run() {
  const rbmStore = createStore();
  removeHighResDendritesForNeurons(rbmStore, "rbm", [
    { file: "main-a.swc", dendritic: "den-a.swc" },
    { file: "main-b.swc" },
    { file: "main-c.swc", dendritic: "den-c.swc" }
  ]);

  assert.deepStrictEqual(rbmStore.commits, [
    { type: "removeHighResDendrites", payload: "den-a.swc" },
    { type: "removeHighResDendrites", payload: "den-c.swc" }
  ]);

  const nonRbmStore = createStore();
  removeHighResDendritesForNeurons(nonRbmStore, "mouse", [
    { file: "main-a.swc", dendritic: "den-a.swc" }
  ]);

  assert.deepStrictEqual(nonRbmStore.commits, []);
}

run();
