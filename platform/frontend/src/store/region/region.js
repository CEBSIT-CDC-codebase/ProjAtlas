import axios from "axios";
import { randomColor } from "@/utils/utils";
import { setRegionType } from "../../utils/neuronFilterTool";
import { setRegionData, setRegionColorScheme } from "../../utils/neuronLoader";
import { setRegionDataForMoresetting } from "../../utils/moreSetting";

export const namespaced = true;

export const state = {
  regionData: {},
  regionType: {},
  viewedRegions: [],
  filteredRegions: [],
  regionAxonTreeArray: [],
  regionSomaTreeArray: [],
  colorScheme: "allen",
  viewedRegionsCount: 0
};

export const mutations = {
  setColorScheme(state, payload) {
    state.colorScheme = payload;
    setRegionColorScheme(payload);
  },

  setRegionAxonTreeArray(state, payload) {
    state.regionAxonTreeArray = payload;
  },

  setRegionSomaTreeArray(state, payload) {
    state.regionSomaTreeArray = payload;
  },

  setFilteredRegions(state, payload) {
    state.filteredRegions = payload;
  },

  addViewedRegions(state, payload) {
    const loadedSet = new Set(state.viewedRegions.map(el => el.file));

    // Handle existing items: restore visible
    payload.forEach(payloadItem => {
      if (loadedSet.has(payloadItem.file)) {
        const idx = state.viewedRegions.findIndex(el => el.file === payloadItem.file);
        if (idx !== -1) state.viewedRegions[idx].visible = true;
      }
    });

    // Filter out new items
    const newItems = payload.filter(p => !loadedSet.has(p.file));
    if (newItems.length === 0) return;

    // Contour goes first
    const contour = newItems.find(item => item.name === "C Contour");
    if (contour) {
      state.viewedRegions.unshift(contour);
      const rest = newItems.filter(item => item !== contour);
      state.viewedRegions.push(...rest);
    } else {
      state.viewedRegions.push(...newItems);
    }
    state.viewedRegionsCount += newItems.length;
  },

  removeViewedRegion(state, payload) {
    for (let i = 0; i < state.viewedRegions.length; ++i) {
      if (state.viewedRegions[i].uid === payload.uid) {
        state.viewedRegions.splice(i, 1);
        break;
      }
    }
  }

  // removeViewedRegions(state, payload) {
  //   let beforeDelete = state.viewedRegions.length;
  //   state.viewedRegions.forEach(element => {
  //     let isReservedItem =
  //       element.regionName === "root" || element.regionName === "C Contour";
  //     if (isReservedItem && !payload) return;
  //     state.regionData[parseInt(element.uid)].viewed = false;
  //   });

  //   if (!payload) {
  //     state.viewedRegions = state.viewedRegions.filter(
  //       item => item.name === "root" || item.name === "C Contour"
  //     );
  //   }

  //   let afterDelete = state.viewedRegions.length;
  //   state.viewedRegionsCount += afterDelete - beforeDelete;
  // }
};

export const actions = {
  async getRegionData({ state }) {
    let url =
      process.env.VUE_APP_SRV +
      `/info/${process.env.VUE_APP_TARGET}/${process.env.VUE_APP_TARGET}.region.info.json`;
    if (process.env.VUE_APP_SUB_SPECIES === "rbm") {
      url =
        process.env.VUE_APP_SRV +
        `/info/${process.env.VUE_APP_TARGET}/rbm/${process.env.VUE_APP_TARGET}.region.info.json`;
    } else if (process.env.VUE_APP_SUB_SPECIES === "SC") {
      url =
        process.env.VUE_APP_SRV +
        `/info/${process.env.VUE_APP_TARGET}/sc/${process.env.VUE_APP_TARGET}.region.info.json`;
    }
    await axios.get(url).then(resp => {
      if (resp.status === 200) {
        let regionData = resp.data.region_data;
        let regionsUid = Object.keys(regionData);
        regionsUid.forEach(uid => {
          const rColor = randomColor(0.3);
          regionData[uid] = Object.assign(
            {
              viewed: false,
              visible: true,
              allenColor: "#" + regionData[uid].color_hex_triplet + "4C",
              somaColor: rColor.slice(0, -2) + "ff",
              cebsitColor:
                "#" + regionData[uid].color_hex_triplet_cebsit + "4C",
              randomColor: rColor,
              hovered: false,
              menuVisible: false,
              colorPicker: false,
              colorScheme: "allenColor",
              currentColor: "#" + regionData[uid].color_hex_triplet + "4C"
            },
            regionData[uid]
          );
        });

        state.regionData = regionData;
        state.regionType = resp.data.region_type;

        setRegionType(state.regionType);
        setRegionData(state.regionData);
        setRegionDataForMoresetting(state.regionData);
      }
    });
  }
};
