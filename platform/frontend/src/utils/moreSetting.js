import axios from "axios";
import store from "@/store";

let regionData = {};
export const setRegionDataForMoresetting = data => {
  regionData = data;
};

const hippSources = {
  mode: [
    {
      type: "contralateral",
      subtype: "terminalNum",
      srv: "all_contra_terminal_num.json"
    },
    {
      type: "contralateral",
      subtype: "cableLength",
      srv: "all_contra_cable_length.json"
    },
    {
      type: "contralateral",
      subtype: "branchPoint",
      srv: "all_contra_branch_point.json"
    },
    {
      type: "ipsilateral",
      subtype: "terminalNum",
      srv: "all_ipsi_terminal_num.json"
    },
    {
      type: "ipsilateral",
      subtype: "cableLength",
      srv: "all_ipsi_cable_length.json"
    },
    {
      type: "ipsilateral",
      subtype: "branchPoint",
      srv: "all_ipsi_branch_point.json"
    },
    {
      type: "all",
      subtype: "branchPoint",
      srv: "all_branch_point.json"
    },
    {
      type: "all",
      subtype: "terminalNum",
      srv: "all_terminal_num.json"
    },
    {
      type: "all",
      subtype: "cableLength",
      srv: "all_cable_length.json"
    }
  ],
  pathway: [
    {
      type: "all",
      subtype: "branchPoint",
      srv: "all_branch_point.json"
    },
    {
      type: "all",
      subtype: "terminalNum",
      srv: "all_terminal_num.json"
    },
    {
      type: "all",
      subtype: "cableLength",
      srv: "all_cable_length.json"
    },
    {
      type: "caudal",
      subtype: "branchPoint",
      srv: "caudal_branch_point.json"
    },
    {
      type: "caudal",
      subtype: "cableLength",
      srv: "caudal_cable_length.json"
    },
    {
      type: "caudal",
      subtype: "terminalNum",
      srv: "caudal_terminal_num.json"
    },
    {
      type: "rostral",
      subtype: "branchPoint",
      srv: "rostral_branch_point.json"
    },
    {
      type: "rostral",
      subtype: "cableLength",
      srv: "rostral_cable_length.json"
    },
    {
      type: "rostral",
      subtype: "terminalNum",
      srv: "rostral_terminal_num.json"
    }
  ]
};

const hySources = {
  mode: [
    {
      type: "contralateral",
      subtype: "terminalNum",
      srv: "hy_all_contra_terminal_num_df.json"
    },
    {
      type: "contralateral",
      subtype: "cableLength",
      srv: "hy_all_contra_cable_length_df.json"
    },
    {
      type: "contralateral",
      subtype: "branchPoint",
      srv: "hy_all_contra_branchpoint_num_df.json"
    },
    {
      type: "ipsilateral",
      subtype: "terminalNum",
      srv: "hy_all_ipsi_terminal_num_df.json"
    },
    {
      type: "ipsilateral",
      subtype: "cableLength",
      srv: "hy_all_ipsi_cable_length_df.json"
    },
    {
      type: "ipsilateral",
      subtype: "branchPoint",
      srv: "hy_all_ipsi_branchpoint_num_df.json"
    },
    {
      type: "all",
      subtype: "branchPoint",
      srv: "hy_all_branchpoint_num_df.json"
    },
    {
      type: "all",
      subtype: "terminalNum",
      srv: "hy_all_terminal_num_df.json"
    },
    {
      type: "all",
      subtype: "cableLength",
      srv: "hy_all_cable_length_df.json"
    }
  ],
  pathway: []
};

const pfcSources = {
  mode: [
    {
      type: "contralateral",
      subtype: "terminalNum",
      srv: "pfc_all_contra_terminal_num_df.json"
    },
    {
      type: "contralateral",
      subtype: "cableLength",
      srv: "pfc_all_contra_cable_length_df.json"
    },
    {
      type: "contralateral",
      subtype: "branchPoint",
      srv: "pfc_all_contra_branchpoint_num_df.json"
    },
    {
      type: "ipsilateral",
      subtype: "terminalNum",
      srv: "pfc_all_ipsi_terminal_num_df.json"
    },
    {
      type: "ipsilateral",
      subtype: "cableLength",
      srv: "pfc_all_ipsi_cable_length_df.json"
    },
    {
      type: "ipsilateral",
      subtype: "branchPoint",
      srv: "pfc_all_ipsi_branchpoint_num_df.json"
    },
    {
      type: "all",
      subtype: "branchPoint",
      srv: "pfc_all_branchpoint_num_df.json"
    },
    {
      type: "all",
      subtype: "terminalNum",
      srv: "pfc_all_terminal_num_df.json"
    },
    {
      type: "all",
      subtype: "cableLength",
      srv: "pfc_all_cable_length_df.json"
    }
  ],
  pathway: []
};

const generateDefaultSource = (
  project,
  projectName,
  type,
  subtype,
  projecting
) => {
  const regionUIDs = Object.keys(regionData);
  let data = {};
  regionUIDs.forEach(uid => {
    data[uid] = [];
  });

  return { project, projectName, type, subtype, data, projecting };
};

const generateTotalDefaultSource = (project, projectName) => {
  const types = ["all", "caudal", "rostral", "ipsilateral", "contralateral"];
  const subtypes = ["branchPoint", "terminalNum", "cableLength"];
  const projecting = ["mode"];
  const sources = [];
  for (let i = 0; i < types.length; i++) {
    for (let j = 0; j < subtypes.length; j++) {
      for (let k = 0; k < projecting.length; k++) {
        sources.push(
          generateDefaultSource(
            project,
            projectName,
            types[i],
            subtypes[j],
            projecting[k]
          )
        );
      }
    }
  }
  return sources;
};

export const getMoreSettingSources = () => {
  return [
    {
      project: "hipp",
      sources: hippSources,
      projectName: "Mouse Hippocampus"
    },
    {
      project: "hy",
      sources: hySources,
      projectName: "Mouse Hypothalamus"
    },
    {
      project: "lha",
      sources: hySources,
      projectName: "Mouse LHA"
    },
    {
      project: "pfc",
      sources: pfcSources,
      projectName: "Mouse prefrontal cortex"
    },
    {
      project: "pvh_oxt",
      sources: null,
      projectName: "Mouse PVH OXT"
    },
    {
      project: "cea",
      sources: null,
      projectName: "Mouse CeA"
    },
    {
      project: "spcd",
      sources: null,
      projectName: "Mouse SPCD"
    }
  ];
};

const getMoreSettingDataCount = () => {
  const sources = getMoreSettingSources().filter(item => item.sources !== null);
  let count = 0;
  for (const sourceItem of sources) {
    const sourceData = sourceItem.sources;
    count += sourceData["mode"].length;
    count += sourceData["pathway"].length;
  }

  return count;
};

const totalMoreSettingDataCount = getMoreSettingDataCount();

export const moreSettingData = [];
export const getAllMoreSettingData = () => {
  return [
    ...moreSettingData,
    ...generateTotalDefaultSource("pvhoxt", "Mouse PVH OXT"),
    ...generateTotalDefaultSource("cea", "Mouse CeA"),
    ...generateTotalDefaultSource("spcd", "Mouse SPCD")
  ];
};

export const getMoreSettingData = async () => {
  const requestFunc = async (
    url,
    project,
    projectName,
    type,
    subtype,
    projecting
  ) => {
    const resp = await axios.get(url);
    if (resp.status === 200) {
      const data = resp.data;
      moreSettingData.push({
        project,
        projectName,
        type,
        subtype,
        data,
        projecting: projecting
      });
    }
  };

  const sources = getMoreSettingSources().filter(item => item.sources !== null);
  for (const sourceItem of sources) {
    const project = sourceItem.project;
    const projectName = sourceItem.projectName;
    const sourceData = sourceItem.sources;
    const preURL =
      process.env.VUE_APP_SRV +
      `/info/mouse/${project === "pfc" ? "" : project}/pathway/`;

    // mode data
    const modeSource = sourceData["mode"];
    for (let i = 0; i < modeSource.length; i += 3) {
      const ps = [];
      {
        const modeItem = modeSource[i];
        const type = modeItem.type;
        const subtype = modeItem.subtype;
        const srv = modeItem.srv;
        const url = preURL + srv;
        ps.push(requestFunc(url, project, projectName, type, subtype, "mode"));
      }

      if (i + 1 < modeSource.length) {
        const modeItem = modeSource[i + 1];
        const type = modeItem.type;
        const subtype = modeItem.subtype;
        const srv = modeItem.srv;
        const url = preURL + srv;
        ps.push(requestFunc(url, project, projectName, type, subtype, "mode"));
      }

      if (i + 2 < modeSource.length) {
        const modeItem = modeSource[i + 2];
        const type = modeItem.type;
        const subtype = modeItem.subtype;
        const srv = modeItem.srv;
        const url = preURL + srv;
        ps.push(requestFunc(url, project, projectName, type, subtype, "mode"));
      }

      await Promise.all(ps);

      if (moreSettingData.length === totalMoreSettingDataCount) {
        store.commit("setMoreSettingDataReady", true);
      }
    }

    // pathway data
    const pathwaySource = sourceData["pathway"];
    for (let i = 0; i < pathwaySource.length; i += 3) {
      const ps = [];
      {
        const pathwayItem = pathwaySource[i];
        const type = pathwayItem.type;
        const subtype = pathwayItem.subtype;
        const srv = pathwayItem.srv;
        const url = preURL + srv;
        ps.push(
          requestFunc(url, project, projectName, type, subtype, "pathway")
        );
      }

      if (i + 1 < pathwaySource.length) {
        const pathwayItem = pathwaySource[i + 1];
        const type = pathwayItem.type;
        const subtype = pathwayItem.subtype;
        const srv = pathwayItem.srv;
        const url = preURL + srv;
        ps.push(
          requestFunc(url, project, projectName, type, subtype, "pathway")
        );
      }

      if (i + 2 < pathwaySource.length) {
        const pathwayItem = pathwaySource[i + 2];
        const type = pathwayItem.type;
        const subtype = pathwayItem.subtype;
        const srv = pathwayItem.srv;
        const url = preURL + srv;
        ps.push(
          requestFunc(url, project, projectName, type, subtype, "pathway")
        );
      }

      await Promise.all(ps);
      if (moreSettingData.length === totalMoreSettingDataCount) {
        store.commit("setMoreSettingDataReady", true);
      }
    }
  }
};
