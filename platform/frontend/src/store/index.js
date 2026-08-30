/* eslint-disable */
import Vue from "vue";
import Vuex from "vuex";
import { validateUser } from "@/api/user";
import { getGroupsFunc } from "@/api/group";
import { getAnimationsFunc } from "@/api/animation";
import * as region from "./region/region";
import * as neuron from "./neuron/neuron";
import { getProjectsInfo } from "@/api/projects";
import * as layout from "./layout/layout";
import * as analyze from "./analyze/analyze";
import * as PickedInformation from "./PickedInformation";
import * as session from "./session/session";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    theme: "dark",
    target: process.env.VUE_APP_TARGET,
    userInfo: null,
    groups: [],
    temporaryGroups: [],
    expirationFlag: false,
    groupFolderTag: false,
    sceneGroups: [],
    projectPath: [
      "/",
      "/pfc",
      "/hipp",
      "/hy",
      "/lha",
      "/pvh_oxt",
      "/cea",

      "/bla",
      "/cea2",
      "/cm",
      "/md",
      "/nac",
      "/pf",
      "/pvt",
      "/rt",
      "/vpl",
      "/vta",

      "/EI",
      "/spcd",
      "/whole-cortex",
      "/rbm",
      "/trimodal"
    ],
    unSaveSceneGroups: [],
    sceneCurrentGroup: {
      name: "All neurons",
      id: "all"
    },
    animations: [],
    currentAnimation: null,
    animationStatus: null,
    visualTarget: process.env.VUE_APP_TARGET,
    loginFlag: false,
    groupsDetailData: {},
    isPublicSwc: false,
    projects: null,
    projectionFiles: {},
    axonData: [],
    terminalData: [],
    axonBrainData: null,
    terminalBrainData: null,
    addFromScene: "",
    groupToScene: false,
    addGroupFlag: false,
    unsaveToScene: false,
    groupAddNeuronFlag: false,
    settingValues: {
      region: false,
      neuron: true,
      mode: false,
      soma: process.env.VUE_APP_SUB_SPECIES === "rbm" ? 0.2 : 1,
      background: "#000000"
    },
    sampleInformation: {},
    addGroupOption: "",
    toolTipVisible: false,
    toolTipDuration: 2500,
    toolTipType: "success",
    toolTipMessage: "The link has been copied to clipboard.",
    neuroVizReady: false,
    highResDendritesVisible: false,
    highResDendriticFiles: [],
    highResDendriticColors: [],
    templateHeaderURL:
      process.env.VUE_APP_SRV + process.env.VUE_APP_REFERENCE_TEMPLATE_HEADER,
    templateDataURL:
      process.env.VUE_APP_SRV + process.env.VUE_APP_REFERENCE_TEMPLATE_DATA,

    annotationHeaderURL:
      process.env.VUE_APP_SRV + process.env.VUE_APP_REFERENCE_ANNOTATION_HEADER,
    annotationDataURL:
      process.env.VUE_APP_SRV + process.env.VUE_APP_REFERENCE_ANNOTATION_DATA,
    totalLoadingCount: 0,
    loadedCount: 0,
    moreSettingDataReady: false,
    functionMap: {
      query_neurons_by_structure: "",
      set_soma_location: "",
      set_axon_projects_to_location: "",
      set_mouse_line: "",
      add_to_scene: "",
      filter_neurons_by_hemisphere: "",
      set_neuron_type:"",
      analyze_neurons: "",
      set_camera: "",
      set_neuron_mirror_state: "",
      set_brain_region_coloring_scheme: "",
      set_neuron_coloring_scheme: "",
      set_reference_planes: "",
      take_screenshot: "",
      play_example_animation: "",
      set_region_picking_mode: "",
      set_neuron_picking_mode: "",
      set_neuron_display_mode: "",
      set_neuron_soma_radius_scale: "",
      set_coordinate_axis_visibility: "",
      set_background_color: ""
    }
  },
  mutations: {
    setMoreSettingDataReady(state, data) {
      state.moreSettingDataReady = data;
    },

    setFunctionMap(state, data) {
      state.functionMap[data.name] = data.args;
    },

    resetLoadingState(state) {
      state.totalLoadingCount = 0;
      state.loadedCount = 0;
    },

    addTotalLoadingCount(state) {
      state.totalLoadingCount++;
    },

    addLoadedCount(state) {
      state.loadedCount++;

      if (state.loadedCount === state.totalLoadingCount) {
        state.loadedCount = 0;
        state.totalLoadingCount = 0;
      }
    },

    setTheme(store, payload) {
      store.theme = payload;
    },
    setUserInfo(state, data) {
      state.userInfo = data;
    },
    setGroupToScene(state, data) {
      state.groupToScene = data;
    },
    setAddFromScene(state, data) {
      state.addFromScene = data;
    },
    setLoginFlag(state, data) {
      state.loginFlag = data;
    },
    setSettingValues(state, { data, index }) {
      state.settingValues[index] = data;
    },
    setSampleInformation(state, { data, key }) {
      Vue.prototype.$set(state.sampleInformation, key, data);
    },
    setGroups(state, data) {
      state.groupsDetailData = {};
      state.groups = data || [];
    },
    setUnsaveToScene(state, data) {
      state.unsaveToScene = data;
    },
    setIsPublicSwc(state, data) {
      state.isPublicSwc = data;
    },
    setAxonData(state, data) {
      state.axonData = data;
    },
    setTerminalData(state, data) {
      state.terminalData = data;
    },
    setAxonBrainData(state, data) {
      state.axonBrainData = data;
    },
    setTerminalBrainData(state, data) {
      state.terminalBrainData = data;
    },
    setGroupAddNeuronFlag(state, data) {
      state.groupAddNeuronFlag = data;
    },
    setSceneGroups(state, data) {
      state.sceneGroups = data;
    },
    setGroupFolderTag(state, data) {
      state.groupFolderTag = data;
    },
    setUnSaveSceneGroups(state, data) {
      state.unSaveSceneGroups = data;
    },
    setSceneCurrentGroup(state, data) {
      state.sceneCurrentGroup = data;
    },
    setAnimations(state, data) {
      data?.map(item => {
        Vue.prototype.$set(item, "onPause", false);
        Vue.prototype.$set(item, "onPlay", false);
        Vue.prototype.$set(item, "onStop", false);
      });
      state.animations = data;
    },
    setCurrentAnimation(state, data) {
      state.currentAnimation = data;
    },
    setAnimationStatus(state, data) {
      state.animationStatus = data;
    },
    setProjects(state, data) {
      state.projects = data;
    },
    setProjectionFiles(state, data) {
      state.projectionFiles = data;
    },
    setAddGroupOption(state, data) {
      state.addGroupOption = data;
    },
    setAddGroupFlag(state, data) {
      state.addGroupFlag = data;
    },
    setExpirationFlag(state, data) {
      state.expirationFlag = data;
    },
    setTemporaryGroups(state, data) {
      state.temporaryGroups = data;
    },
    setToolTipVisible(state, data) {
      state.toolTipVisible = data;
    },
    setToolTipDuration(state, data) {
      state.toolTipDuration = data;
    },
    setToolTipType(state, data) {
      state.toolTipType = data;
    },
    setToolTipMessage(state, data) {
      state.toolTipMessage = data;
    },
    setHighResDendritesVisible(state, data) {
      state.highResDendritesVisible = data;
    },
    setHighResDendriticFiles(state, data) {
      state.highResDendriticFiles = [];

      requestAnimationFrame(() => {
        state.highResDendriticFiles = data;
      });
    },
    setNeuroVizReady(state, data) {
      state.neuroVizReady = data;
    },

    removeHighResDendrites(state, name) {
      const index = state.highResDendriticFiles.findIndex(
        item => item === name
      );
      if (index === -1) {
        return;
      }
      state.highResDendriticFiles.splice(index, 1);
    },

    addHighResDendrites(state, file) {
      state.highResDendriticFiles.push(file);
    },

    addHighResDendritesColor(state, payload) {
      state.highResDendriticColors.push(payload);
    },

    removeHighResDendritesColor(state, payload) {
      const index = state.highResDendriticColors.findIndex(
        item => item.name === payload.name && item.id === payload.id
      );
      if (index === -1) {
        return;
      }
      state.highResDendriticColors.splice(index, 1);
    }
  },

  actions: {
    async getUserInfo({ commit, dispatch }) {
      try {
        const res = await validateUser();
        const status = res?.status || res?.response?.status || 400;

        if (status < 200 || status >= 300) {
          dispatch("clearAuthData");
          commit("setLoginFlag", true);
        } else {
          // 1. Store the user info normally
          commit("setUserInfo", res.data?.data);

          // 2. Compute and store the expiration time (current time + 12 hours)
          const EXPIRE_IN = 12 * 3600 * 1000;
          const expireAt = Date.now() + EXPIRE_IN;
          localStorage.setItem("auth_expire_at", expireAt);
          localStorage.setItem("initial_time", Date.now());

          // 3. Start a timer for users who never refresh the page
          // As long as the page stays open, this fires automatically after 12 hours
          setTimeout(() => {
            dispatch("checkAndLogout");
          }, EXPIRE_IN);
        }
      } catch (error) {
        dispatch("clearAuthData");
      }
    },

    // Unified clear logic
    clearAuthData({ commit }) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("vuex");
      localStorage.removeItem("auth_expire_at");

      commit("setUserInfo", null);
      commit("setGroups", []);
      commit("setLoginFlag", false);
      commit("setExpirationFlag", true);

      // session module
      commit("session/setUserInfo", null);
      commit("session/setSessions", []);
      commit("session/setMessages", []);
      commit("session/setCurrentSession", null);
    },

    // Core check logic
    checkAndLogout({ dispatch }) {
      const expireAt = localStorage.getItem("auth_expire_at");
      if (expireAt && Date.now() > parseInt(expireAt)) {
        dispatch("clearAuthData");
        // If the user is on the page, you could show a dialog or redirect directly
        // window.location.reload(); // Or redirect to the login page
      }
    },

    async getAnimations({ commit }) {
      await getAnimationsFunc().then(res => {
        commit("setAnimations", res.data?.data || []);
      });
    },

    async getGroups({ commit }) {
      await getGroupsFunc().then(res => {
        const result = res.data?.data?.filter(
          item => item?.species === process.env.VUE_APP_TARGET
        );
        commit("setGroups", result);
      });
    },

    getSampleInformation(context, payload) {
      const currentProject = context.state.projects.find(
        item => item?.name === payload
      );
      const currentFile =
        currentProject?.files[currentProject?.files?.length - 1];
      const srv = process.env.VUE_APP_SRV;
      const jsonURL = `${srv}${currentFile?.path}`;
      fetch(jsonURL)
        .then(resp => resp.json())
        .then(data => {
          context.commit("setSampleInformation", {
            data,
            key: payload
          });
        })
        .catch(() => {});
    },

    getProjects({ commit }) {
      getProjectsInfo().then(res => {
        const projects = (res.data?.data || []).filter(
          i => i.species === process.env.VUE_APP_TARGET
        );

        if (process.env.VUE_APP_SUB_SPECIES === "rbm") {
          const rbmProject = projects.filter(i => i.acronym === "rbm");
          commit("setProjects", rbmProject);
          return;
        } else if (process.env.VUE_APP_SUB_SPECIES === "trimodal") {
          const trimodalProject = projects.filter(i => i.acronym === "trimodal");
          commit("setProjects", trimodalProject);
          return;
        } else if (process.env.VUE_APP_SUB_SPECIES === "SC") {
          const scProject = projects.filter(i => i.acronym === "SC");
          commit("setProjects", scProject);
          return;
        } else {
          const restProjects = projects.filter(
            i => i.acronym !== "rbm" && i.acronym !== "trimodal" && i.acronym !== "SC"
          );
          commit("setProjects", restProjects);
        }
      });
    }
  },
  modules: {
    region,
    neuron,
    layout,
    analyze,
    session,
    PickedInformation
  },
  getters: {
    userInfo(state) {
      return state.userInfo;
    },

    groupTips(state) {
      return state.userInfo ? "None" : "Please login to see your data";
    },

    visualType() {
      return process.env.VUE_APP_TARGET;
    },

    projectionFileUrls(state) {
      const obj = {};
      state.projects?.forEach(item => {
        if (!obj["regionDict"]) {
          obj["regionDict"] = item?.projection?.regionDict;
        }
        // const { axonLength, terminalCount } = item?.projection
        obj[item.acronym] = item?.projection;
      });
      return obj;
    },

    projectKeys(state) {
      const obj = {};
      state.projects.map(project => {
        obj[project?.acronym] = project?.name;
      });
      return obj;
    }
  },
  plugins: []
});
