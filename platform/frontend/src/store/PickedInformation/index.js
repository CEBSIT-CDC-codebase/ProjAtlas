export const namespaced = true;

export const state = {
  // neuron
  neuronItem: null,
  // region
  regionItem: null,

  pickedNeuronWorldPosition: [0, 0, 0],
  pickedRegionWorldPosition: [0, 0, 0]
};

export const mutations = {
  setRegionItem(state, payload) {
    state.regionItem = payload;
  },

  setNeuronItem(state, payload) {
    state.neuronItem = payload;
  },

  setPickedNeuronWorldPosition(state, payload) {
    state.pickedNeuronWorldPosition = payload;
  },

  setPickedRegionWorldPosition(state, payload) {
    state.pickedRegionWorldPosition = payload;
  }
};

export const getters = {};
