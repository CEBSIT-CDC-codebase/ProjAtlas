const assert = require("assert");

const {
  partitionHighResDendriteColors
} = require("../src/utils/highResDendrites");

function run() {
  const colors = [
    { id: "1", file: "den-a.swc", color: [1, 0, 0, 1] },
    { id: "2", file: "den-b.swc", color: [0, 1, 0, 1] },
    { id: "3", file: "den-c.swc", color: [0, 0, 1, 1] }
  ];

  const result = partitionHighResDendriteColors({
    colors,
    loadedFiles: ["den-b.swc", "den-c.swc"]
  });

  assert.deepStrictEqual(
    result.ready.map(item => item.file),
    ["den-b.swc", "den-c.swc"]
  );
  assert.deepStrictEqual(
    result.pending.map(item => item.file),
    ["den-a.swc"]
  );
}

run();
