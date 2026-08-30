<template>
  <div class="primary d-flex flex-column" style="z-index: 1">
    <PanelHeader
      title="Data Filter & Operation"
      :enable-full-screen="false"
      @minimize="onMinimize"
    ></PanelHeader>

    <div class="d-flex flex-row align-center accent tabs">
      <span
        class="primary-light-1--text"
        v-for="(tabItem, index) in allTabs"
        :key="index"
        :style="targetTab === tabItem.value ? activeTabStyle : ''"
        @click="targetTab = tabItem.value"
        >{{ tabItem.label }}</span
      >
    </div>

    <BuildInData
      v-show="showBuildInData"
      @downloadNeurons="onDownloadNeurons"
      style="flex-grow: 1"
    ></BuildInData>

    <DataGroup v-show="showDataGroup" @downloadNeurons="onDownloadNeurons"></DataGroup>

    <v-dialog v-model="downloadingDialog" persistent width="400px">
      <div class="download-progress-container">
        <div
          class="d-flex align-center primary-text--text"
          style="justify-content: space-between; margin-bottom: 11px; font-size: 13px"
        >
          <span>{{ progressMessage }}</span>
          <span style="margin-left: 8px"> {{ progressPercent }}% </span>
        </div>
        <div class="d-flex align-center" style="width: 100%">
          <div
            style="
              flex-grow: 1;
              height: 6px;
              display: flex;
              align-items: center;
              background: #ffffff33;
              height: 100%;
              border-radius: 3px; ;
            "
          >
            <div
              :style="{
                width: progressPercent + '%',
              }"
              style="
                background: linear-gradient(to right, #20f2ff, #0066ff);
                height: 100%;
                border-radius: 3px;
                height: 6px;
              "
            ></div>
          </div>
        </div>
      </div>
    </v-dialog>

    <div class="load_warning_div" v-show="showMaxDownloading">
      <div class="warning_div">
        <div class="warning_header">
          <span>Warning</span>
          <v-icon small style="margin-right: 11px" @click="showMaxDownloading = false">
            $Close
          </v-icon>
        </div>
        <p style="margin: 0 10px">
          Please select 10000 or fewer neurons to download. Or you may go to the
          <a @click="toDownloadPage" style="color: #7fbefa">Data Download</a>
          page to download full data.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
import PanelHeader from "../../../components/PanelHeader.vue";
import { throttle } from "@/utils/utils";
import BuildInData from "./components/BuildInData/BuildInData.vue";
import DataGroup from "./components/DataGroup/DataGroup.vue";
import axios from "axios";
import { zip } from "fflate";

export default {
  name: "DataOperationPanel",
  components: {
    PanelHeader,
    BuildInData,
    DataGroup,
  },
  data() {
    return {
      targetTab: "build-in",
      allTabs: [
        { value: "build-in", label: "Query" },
        { value: "data-group", label: "Data Management" },
      ],
      downloadingDialog: false,
      downloadingValue: 0,
      downloadingTotal: 1,
      showMaxDownloading: false,
      showWarningDialog: false,
      // zipping: false,
      // zippingPercent: 0
    };
  },

  watch: {
    addGroupFlag() {
      this.targetTab = "data-group";
    },
  },

  computed: {
    ...mapState({
      theme: (state) => state.theme,
      addGroupFlag: (state) => state.addGroupFlag,
      viewedNeurons: (state) => state.neuron.viewedNeurons,
    }),

    showBuildInData() {
      return this.targetTab === "build-in";
    },
    showDataGroup() {
      return this.targetTab === "data-group";
    },
    activeTabStyle() {
      return {
        background: this.$vuetify.theme.themes[this.theme].primary,
        color: this.$vuetify.theme.themes[this.theme]["accent-1"] + " !important",
      };
    },
    progressMessage() {
      if (this.downloadingValue > 0 && this.downloadingValue === this.downloadingTotal) {
        return "Zipping files...";
      } else {
        return `Processing: ${this.downloadingValue}/${this.downloadingTotal}`;
      }
    },

    progressPercent() {
      if (this.downloadingValue > 0 && this.downloadingValue <= this.downloadingTotal) {
        return ((this.downloadingValue / this.downloadingTotal) * 100).toFixed(0);
      }
      return 0;

      // return this.zippingPercent;
    },
  },

  methods: {
    toDownloadPage() {
      this.showWarningDialog = false;
      this.$router.push("./download");
    },

    hideWaringDialog() {
      this.showWarningDialog = false;
    },

    onMinimize() {
      this.$store.commit("layout/setDataFilter", "minimize");
    },

    async downloadSWC(items, fileObj) {
      let ps = [];
      const species = process.env.VUE_APP_TARGET;
      let url = `${process.env.VUE_APP_SRV}/info/${species}/`;
      for (let i = 0; i < items.length; i += 1) {
        let currentUrl,
          fileName = items[i].file?.slice(0, -4);
        let fullName;
        if (species == "mouse") {
          if (items[i]?.project === "pfc") {
            currentUrl = `pfc_neuron_download/${fileName}_reg.swc`;
            fullName = `${fileName}_reg.swc`;
          }
          if (items[i]?.project === "hy" || items[i]?.project === "lha") {
            currentUrl = `hy/hy_neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }

          if (items[i]?.project === "hipp") {
            currentUrl = `hipp/hipp_neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }

          if (items[i]?.project === "pvh_oxt") {
            currentUrl = `pvh_oxt/pvh_oxt_neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }

          if (items[i]?.project === "cea") {
            currentUrl = `cea/pvh_oxt_neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }

          if (items[i]?.project === "ei") {
            currentUrl = `/ei_neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }

          if (items[i]?.project === "spcd") {
            currentUrl = `spcd/spcd_neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }

          if (items[i]?.project === "whole-cortex") {
            currentUrl = `cortex/neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }

          if (items[i]?.project === "bla") {
            currentUrl = `bla/bla_neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }
          if (items[i]?.project === "cea2") {
            currentUrl = `cea2/cea2_neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }
          if (items[i]?.project === "cm") {
            currentUrl = `cm/cm_neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }
          if (items[i]?.project === "md") {
            currentUrl = `md/md_neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }
          if (items[i]?.project === "nac") {
            currentUrl = `nac/nac_neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }
          if (items[i]?.project === "pf") {
            currentUrl = `pf/pf_neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }
          if (items[i]?.project === "pvt") {
            currentUrl = `pvt/pvt_neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }
          if (items[i]?.project === "rt") {
            currentUrl = `rt/rt_neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }
          if (items[i]?.project === "vpl") {
            currentUrl = `vpl/vpl_neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }
          if (items[i]?.project === "vta") {
            currentUrl = `vta/vta_neuron_download/${fileName}.swc`;
            fullName = `${fileName}.swc`;
          }
        }
        if (species == "monkey") {
          currentUrl = `${items[i]?.project}/neuron_download/${fileName}.swc`;
          fullName = `${fileName}.swc`;
        }

        const p1 = axios
          .get(url + currentUrl, { responseType: "arraybuffer" })
          .then(async (resp) => {
            fileObj[fullName] = new Uint8Array(resp.data);
          });
        ps.push(p1);

        if (items[i]?.project === "pfc" && species === "mouse") {
          const currentUrl = `pfc_neuron_download/${fileName}_orig.swc`;
          const p2 = axios
            .get(url + currentUrl, { responseType: "arraybuffer" })
            .then(async (resp) => {
              fileObj[`${fileName}_orig.swc`] = new Uint8Array(resp.data);
            });
          ps.push(p2);
        }
      }

      if (ps.length > 0) {
        await Promise.all(ps);
      }
    },

    onDownloadNeurons: throttle(async function (neuronItems) {
      if (neuronItems.length == 0) {
        return;
      }

      if (neuronItems.length >= 10000) {
        this.showMaxDownloading = true;
        return;
      }
      this.downloadingDialog = true;
      this.downloadingTotal = neuronItems.length;

      const batchSize = 100;
      const numberOfBatches = Math.ceil(neuronItems.length / batchSize);
      for (let b = 0; b < numberOfBatches; b += 1) {
        let files = {};
        const batchItems = neuronItems.slice(b * batchSize, (b + 1) * batchSize);

        const concurrent = 4;
        for (let i = 0; i < batchItems.length; i += concurrent) {
          const items = batchItems.slice(i, i + concurrent);
          await this.downloadSWC(items, files);
          this.downloadingValue += items.length;
        }

        zip(files, (err, zipped) => {
          if (err) {
            console.error("Error zipping files:", err);
            return;
          }

          // Create a Blob from the zipped output for downloading
          const blob = new Blob([zipped], { type: "application/zip" });
          const link = document.createElement("a");
          link.href = URL.createObjectURL(blob);
          link.download = `neurons_${b + 1}_${numberOfBatches}.zip`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);

          if (numberOfBatches === b + 1) {
            setTimeout(() => {
              this.downloadingDialog = false;
              this.downloadingValue = 0;
              this.downloadingTotal = 1;
            }, 100);
          }
        });
      }

      const tracks = [];

      let url = `${process.env.VUE_APP_SRV}/info/${process.env.VUE_APP_TARGET}/`;
      for (let i = 0; i < neuronItems.length; i += 1) {
        const item = neuronItems[i];

        let currentUrl;
        let fileName = item.file?.slice(0, -4);

        if (process.env.VUE_APP_TARGET == "mouse") {
          if (item?.project === "pfc") {
            currentUrl = `pfc_neuron_download/${fileName}_reg.swc`;

            const origCurrentUrl = `pfc_neuron_download/${fileName}_orig.swc`;
            tracks.push(["trackLink", url + origCurrentUrl, "download"]);
          }
          if (item?.project === "hy" || item?.project === "lha") {
            currentUrl = `hy/hy_neuron_download/${fileName}.swc`;
          }

          if (item?.project === "hipp") {
            currentUrl = `hipp/hipp_neuron_download/${fileName}.swc`;
          }

          if (item?.project === "pvh_oxt") {
            currentUrl = `pvh_oxt/pvh_oxt_neuron_download/${fileName}.swc`;
          }

          if (item?.project === "cea") {
            currentUrl = `cea/pvh_oxt_neuron_download/${fileName}.swc`;
          }

          if (item?.project === "spcd") {
            currentUrl = `spcd/spcd_neuron_download/${fileName}.swc`;
          }

          if (item?.project === "whole-cortex") {
            currentUrl = `cortex/neuron_download/${fileName}.swc`;
          }
        }

        if (process.env.VUE_APP_TARGET == "monkey") {
          currentUrl = `${item?.project}/neuron_download/${fileName}.swc`;
        }

        tracks.push(["trackLink", url + currentUrl, "download"]);
      }

      window._paq?.push(...tracks);
    }, 3000),
  },
};
</script>

<style lang="scss" scoped>
.tabs {
  span {
    padding: 0 14px;
    cursor: pointer;
    user-select: none;
    height: 32px;
    line-height: 32px;
  }
}
.load_warning_div {
  position: absolute;
  z-index: 100003;
  background-color: rgba(0, 0, 0, 0.5);
  top: 0px;
  left: 0px;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}
.warning_div {
  width: 340px;
  height: 138px;
  display: flex;
  flex-direction: column;
  border-radius: 4px;
  background: #313237;
  border: 1px solid #353539;
}

.warning_div p {
  font-size: 13px;
  color: #c4c4c4;
  margin: 0 20px;
}

.warning_header {
  display: flex;
  height: 46px;
  justify-content: space-between;
  align-items: center;
}

.warning_header span {
  margin-left: 10px;
  font-size: 13px;
  line-height: 16px;
  text-align: left;
  color: #ffffff;
}

.warning_footer {
  height: 24px;
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.warning_footer span {
  height: 24px;
  width: 40px;
  font-size: 12px;
  color: #ffffff;
  text-align: center;
  line-height: 24px;
  border-radius: 2px;
  cursor: pointer;
}
.download-progress-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 10px;
  width: 400px;
  color: #ffffff;
  background-color: #ffffff33;
}
</style>
