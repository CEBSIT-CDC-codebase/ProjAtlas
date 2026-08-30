import { formatResult } from "@/utils/analyzeTool";

export const namespaced = true;

export const state = {
  tabs: [],
  results: [],
  computedAnalysis: [],
  frames: {
    "0": {
      focusTab: null
    },
    "1": {
      focusTab: null
    }
  },
  displayMode: "single", // single or horizental or vertical
  focusTabTrigger: 0,
  addResultFlag: false,
  barValues: [],
  cachedSomaTrees: {},
  cachedSomaMaxCount: {},
  cachedSomaMaxDensity: {},

  cachedAxonTrees: {},
  cachedAxonMaxLength: {},
  cachedAxonMaxCount: {},
  cachedAxonList: {}
};

export const mutations = {
  addCachedSomaTree(state, { key, tree, maxCount, maxDensity, list }) {
    state.cachedSomaTrees[key] = tree;
    state.cachedAxonList[key] = list;
    state.cachedSomaMaxCount[key] = maxCount;
    state.cachedSomaMaxDensity[key] = maxDensity;
  },

  addCachedAxonTree(state, { key, tree, maxLength, maxCount }) {
    state.cachedAxonTrees[key] = tree;
    state.cachedAxonMaxLength[key] = maxLength;
    state.cachedAxonMaxCount[key] = maxCount;
  },

  setAddResultFlag(state, payload) {
    state.addResultFlag = payload;
  },

  setBarValues(state, payload) {
    state.barValues = payload;
  },

  setFocusTab(state, tab) {
    // if the tab is not in the tabs, add it
    const existTab = state.tabs.find(
      t => t.label === tab.label && t.type === tab.type
    );

    if (!existTab) {
      // for result type, alwasy add to the start of the tabs
      if (tab.type === "result") {
        state.tabs.unshift(tab);
      } else {
        state.tabs.push(tab);
      }
    }

    const frameID = tab.frameID;
    state.frames[frameID].focusTab = tab;
    state.focusTabTrigger++;
  },

  setDisplayMode(state, mode) {
    if (state.displayMode !== "single" && mode === "single") {
      state.tabs = state.tabs.map(t => {
        t.frameID = "0";
        return t;
      });
    } else if (state.displayMode === "single" && mode !== "single") {
      const frameID0Tabs = state.tabs.filter(t => t.frameID === "0");
      if (frameID0Tabs.length > 1) {
        const currentTab = state.frames["0"].focusTab;
        const index = frameID0Tabs.findIndex(t => t === currentTab);
        state.frames["0"].focusTab =
          index < frameID0Tabs.length - 1
            ? frameID0Tabs[index + 1]
            : frameID0Tabs[index - 1];
        currentTab.frameID = "1";
        state.frames["1"].focusTab = currentTab;
        state.focusTabTrigger++;
      }
    }

    state.displayMode = mode;
  },

  addComputedAnalysis(state, result) {
    state.computedAnalysis.push(result);
  },

  addTab(state, tab) {
    const frameID = tab.frameID;
    // avoid add duplicate tab
    const existTab = state.tabs.find(
      t => t.label === tab.label && t.type === tab.type
    );

    if (existTab) {
      state.frames[existTab.frameID].focusTab = existTab;
      state.focusTabTrigger++;
      return;
    }

    // find current focus tab index
    const focusTabIndex = state.tabs.findIndex(
      t => t === state.frames[frameID].focusTab
    );

    state.tabs.splice(focusTabIndex + 1, 0, tab);
    state.frames[frameID].focusTab = tab;
    state.focusTabTrigger++;
  },

  removeTab(state, tab) {
    // after the removem, focus the previous one
    const frameTabs = state.tabs.filter(t => t.frameID === tab.frameID);
    const tabIndex = frameTabs.findIndex(t => t === tab);
    if (frameTabs.length > 1) {
      state.frames[tab.frameID].focusTab =
        tabIndex < frameTabs.length - 1
          ? frameTabs[tabIndex + 1]
          : frameTabs[tabIndex - 1];
      state.focusTabTrigger++;
    }

    state.tabs = state.tabs.filter(t => t !== tab);

    const frameID0Count = state.tabs.filter(t => t.frameID === "0").length;
    const frameID1Count = state.tabs.filter(t => t.frameID === "1").length;

    if (frameID1Count === 0) {
      state.displayMode = "single";
    } else if (frameID0Count === 0) {
      state.displayMode = "single";
      state.tabs = state.tabs.map(t => {
        t.frameID = "0";
        return t;
      });
    }
  },

  moveTab(state, { tab, direction }) {
    const id = tab.frameID;
    // update previous focus tab
    const frameTabs = state.tabs.filter(t => t.frameID === id);
    const tabIndex = frameTabs.findIndex(t => t === tab);
    if (frameTabs.length > 1) {
      state.frames[id].focusTab =
        tabIndex < frameTabs.length - 1
          ? frameTabs[tabIndex + 1]
          : frameTabs[tabIndex - 1];
    }

    const targetId = id === "0" ? "1" : "0";
    tab.frameID = targetId;
    // update current focus tab
    state.frames[targetId].focusTab = tab;

    if (direction !== state.displayMode) {
      state.displayMode = direction;
    }

    state.focusTabTrigger++;
  },

  // Add to tab (4 charts)
  addResult(state, result) {
    const obj = formatResult(result);
    const resultTab = {
      frameID: "0", // for every result, add the result tab to the first frame tab
      type: "result",
      id: obj.id,
      label: obj.name + " " + obj.id,
      value: obj.value,
      data: obj.data
    };
    state.results.push(resultTab);

    // for result type, alwasy add to the start of the tabs
    state.tabs.unshift(resultTab);
    const frameID = resultTab.frameID;
    state.frames[frameID].focusTab = resultTab;
    state.focusTabTrigger++;
  }
};
