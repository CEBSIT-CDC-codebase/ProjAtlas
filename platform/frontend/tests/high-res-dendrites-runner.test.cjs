const assert = require("assert");

const { createLatestAsyncRunner } = require("../src/utils/highResDendrites");

function deferred() {
  let resolve;
  const promise = new Promise(res => {
    resolve = res;
  });

  return { promise, resolve };
}

async function run() {
  const steps = [];
  const first = deferred();
  const second = deferred();
  const gates = [first, second];

  const runner = createLatestAsyncRunner(async files => {
    steps.push(`start:${files.join(",")}`);
    await gates.shift().promise;
    steps.push(`end:${files.join(",")}`);
  });

  const firstRun = runner(["a", "b"]);
  const secondRun = runner(["a"]);

  first.resolve();
  await Promise.resolve();
  second.resolve();

  await Promise.all([firstRun, secondRun]);

  assert.deepStrictEqual(steps, ["start:a,b", "end:a,b", "start:a", "end:a"]);
}

run();
