<template>
  <div class="download-table-main">
    <div class="table-header">Download Data</div>
    <div class="table-content" style="border-top: 1px solid #586075">
      <div class="row-first" style="border-left: 1px solid #586075">
        Dataset Name
      </div>
      <div class="row-first">Release Date</div>
      <div class="row-first">Data Access</div>
    </div>

    <div class="table-content" v-for="item in currentDataset" :key="item.name">
      <div class="row-rest" style="border-left: 1px solid #586075">
        {{ item.name }}
      </div>
      <div class="row-rest">{{ item.date }}</div>
      <div class="row-rest" v-if="item.download">
        <v-tooltip top :disabled="item.file !== 'Coming soon'">
          <template v-slot:activator="{ on, attrs }">
            <v-icon
              v-bind="attrs"
              v-on="on"
              size="16"
              color="#7FBEFA"
              @click="item.file !== 'Coming soon' && openTarget(item.link)"
              :style="{
                cursor: item.file === 'Coming soon' ? 'not-allowed' : 'pointer',
                opacity: item.file === 'Coming soon' ? 0.5 : 1
              }"
            >
              $Download
            </v-icon>
          </template>
          <span>Coming soon</span>
        </v-tooltip>
      </div>
      <div class="row-rest" v-else>
        <span>BSDS</span>
        <v-icon size="16" style="cursor: pointer" @click="openTarget(item.link)"
          >$ExternalLink</v-icon
        >
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
export default {
  name: "DownloadTable",
  data() {
    return {
      datasets: {
        mouse: [
          {
            name: "Single-neuron datasets for mouse prefrontal cortex",
            date: "2022-04-29",
            link:
              (process.env.VUE_APP_DATACENTER_URL || "") + "/datacenter/web/#/dataSet/details?id=1585453592638009346"
          },
          {
            name:
              " Single-neuron projectome of mouse prefrontal cortex (with dendrite)",
            date: "2023-05-22",
            link:
              (process.env.VUE_APP_DATACENTER_URL || "") + "/datacenter/web/#/dataSet/details?id=1681926304704638978"
          },
          {
            name: "Single-neuron datasets for mouse hippocampus",
            date: "2024-02-07",
            link: "https://doi.org/10.12412/BSDC.1667278800.20001"
          },
          {
            name: "Single-neuron datasets for mouse hypothalamus",
            date: "2024-06-12",
            link:
              (process.env.VUE_APP_DATACENTER_URL || "") + "/datacenter/web/#/dataSet/details?id=1800731789745954817"
          },
          {
            name:
              "Single-neuron projectome of somatosensory ascending pathways in the mouse brain",
            date: "2025-01-15",
            link: "https://cstr.cn/33145.11.BSDC.1737015588.1879450714607951874"
          },
          {
            name: "Single-neuron projectome of mouse whole cortex",
            date: "2025-05-21",
            link: "https://doi.org/10.12412/BSDC.1747279998.20001"
          }
        ],
        monkey: [
          {
            name:
              "Single-neuron projectomes of macaque prefrontal cortex (PFC)",
            date: "2025-06-27",
            link: "https://cstr.cn/33145.11.BSDC.1751075408.1938544706988793858"
          }
        ]
      }
    };
  },

  computed: {
    ...mapState({
      userInfo: state => state.userInfo,
      loginFlag: state => state.loginFlag
    }),

    currentDataset() {
      return this.datasets[process.env.VUE_APP_TARGET];
    }
  },

  methods: {
    openTarget(target) {
      if (!this.userInfo) {
        this.$store.commit("setLoginFlag", true);
      } else {
        window.open(target, "_blank");
      }
    }
  },

  mounted() {
    if (process.env.VUE_APP_SUB_SPECIES === "rbm") {
      this.datasets["mouse"].push({
        name:
          "Single-neuron datasets for mouse retina （with Hi-Res dendrites）",
        date: "coming soon",
        link: ""
      });
    }
  }
};
</script>

<style lang="scss" scoped>
.download-table-main {
  display: flex;
  flex-direction: column;

  .table-header {
    font-size: 32px;
    font-weight: 500;
    color: #f5f8ff;
    padding: 16px 0;
  }

  .table-content {
    display: grid;
    grid-template-columns: auto 200px 200px;
    /* grid-template-rows: 48px 48px 48px; */

    .row-first {
      font-size: 16px;
      background: #26272b;
      color: #f5f8ff;
      padding: 10px 20px;
      border-right: 1px solid #586075;
      border-bottom: 1px solid #586075;
    }

    .row-rest {
      font-size: 16px;
      color: #ced4e4;
      font-weight: 400;
      padding: 10px 20px;
      border-right: 1px solid #586075;
      border-bottom: 1px solid #586075;
      display: flex;
      align-items: center;

      span {
        color: #7fbefa;
        font-weight: 400;
        margin-right: 6px;
      }
    }
  }
}
</style>
