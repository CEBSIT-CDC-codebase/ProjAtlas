function removeHighResDendritesForNeurons(store, subSpecies, neurons) {
  if (subSpecies !== "rbm") {
    return;
  }

  (neurons || []).forEach(item => {
    if (item?.dendritic) {
      store.commit("removeHighResDendrites", item.dendritic);
    }
  });
}

function uniqueFiles(files) {
  return [...new Set((files || []).filter(Boolean))];
}

function partitionHighResDendriteColors({ colors, loadedFiles }) {
  const loaded = new Set(uniqueFiles(loadedFiles));

  return (colors || []).reduce(
    (acc, item) => {
      if (item?.file && loaded.has(item.file)) {
        acc.ready.push(item);
      } else {
        acc.pending.push(item);
      }
      return acc;
    },
    {
      ready: [],
      pending: []
    }
  );
}

function createLatestAsyncRunner(task) {
  let inFlight = null;
  let pendingArgs = null;
  let rerunRequested = false;

  const flush = async () => {
    try {
      while (pendingArgs) {
        const args = pendingArgs;
        pendingArgs = null;
        rerunRequested = false;
        await task(args);
      }
    } finally {
      inFlight = null;
      if (rerunRequested && pendingArgs) {
        inFlight = flush();
      }
    }
  };

  return args => {
    pendingArgs = args;
    rerunRequested = true;

    if (!inFlight) {
      inFlight = flush();
    }

    return inFlight;
  };
}

function collectSyncedDendriticFiles({
  requestedFiles,
  viewedNeurons,
  hasTrackedMainView
}) {
  const normalizedRequestedFiles = uniqueFiles(requestedFiles);
  const matchingNeurons = (viewedNeurons || []).filter(
    neuron =>
      neuron &&
      neuron.dendritic &&
      normalizedRequestedFiles.includes(neuron.dendritic)
  );
  const nextHasTrackedMainView =
    hasTrackedMainView || matchingNeurons.length > 0;

  if (!nextHasTrackedMainView) {
    return {
      files: normalizedRequestedFiles,
      hasTrackedMainView: false
    };
  }

  return {
    files: uniqueFiles(
      matchingNeurons
        .filter(neuron => neuron.visible && neuron.dendriteVisible !== false)
        .map(neuron => neuron.dendritic)
    ),
    hasTrackedMainView: true
  };
}

module.exports = {
  createLatestAsyncRunner,
  partitionHighResDendriteColors,
  removeHighResDendritesForNeurons,
  collectSyncedDendriticFiles
};
