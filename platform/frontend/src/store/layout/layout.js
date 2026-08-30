export const namespaced = true;

export const state = {
  dataFilter: "normal",
  dataViewer: "normal",
  dataAnalyzing: "normal",
  analyzeWidth: 0,
  forbiddenAutoMinimize: 0
};

export const mutations = {
  setForbiddenAutoMinimize(state) {
    state.forbiddenAutoMinimize++;
  },
  setDataFilter(state, data) {
    state.dataFilter = data;
  },
  setDataViewer(state, data) {
    state.dataViewer = data;
  },
  setDataAnalyzing(state, data) {
    state.dataAnalyzing = data;
  },
  setAnalyzeWidth(state, data) {
    state.analyzeWidth = data;
  }
};
