const assert = require("assert");

const {
  loadInitialRbmRegions
} = require("../src/utils/rbmInitialRegionLoad");

function deferred() {
  let resolve;
  const promise = new Promise(res => {
    resolve = res;
  });

  return { promise, resolve };
}

async function run() {
  const rootGate = deferred();
  const events = [];

  const root = { name: "root", depth: 0 };
  const areaA = { name: "area-a", depth: 1 };
  const areaB = { name: "area-b", depth: 1 };

  const startLoad = region => {
    events.push(`start:${region.name}`);

    if (region === root) {
      return rootGate.promise.then(() => {
        events.push(`end:${region.name}`);
      });
    }

    events.push(`end:${region.name}`);
    return Promise.resolve();
  };

  const pending = loadInitialRbmRegions([root, areaA, areaB], startLoad);

  await Promise.resolve();
  assert.deepStrictEqual(events, ["start:root"]);

  rootGate.resolve();
  await pending;

  assert.deepStrictEqual(events, [
    "start:root",
    "end:root",
    "start:area-a",
    "end:area-a",
    "start:area-b",
    "end:area-b"
  ]);
}

run();
