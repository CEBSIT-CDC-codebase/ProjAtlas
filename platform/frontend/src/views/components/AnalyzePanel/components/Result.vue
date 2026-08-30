<template>
  <div class="d-flex flex-column">
    <div class="header">
      <span style="font-weight: 600">Data:</span>
      <span class="primary-text--text">&nbsp;{{ result.data.dataSource }}</span>
    </div>
    <div
      v-if="result.data.type === 'region'"
      class="d-flex flex-column"
      style="padding: 0 20px; margin-bottom: 20px"
    >
      <span style="margin-bottom: 10px">Basic Information</span>
      <div
        style="
          display: grid;
          grid-template-columns: 320px auto;
          grid-template-rows: 36px 36px 36px 36px;
        "
      >
        <span class="info-span">Acronym</span>
        <span class="info-span">{{
          result.data.acronym.toLocaleUpperCase()
        }}</span>
        <span class="info-span">name</span>
        <span class="info-span">{{
          capitalizedText(
            result.data.name
              .replace(result.data.acronym.toLocaleUpperCase(), "")
              .trim()
          )
        }}</span>
        <span class="info-span">Total neurons (soma in this region)</span>
        <span class="info-span">{{ result.data.somaCount }}</span>
        <span class="info-span"
          >Total neurons (axon project to this region)</span
        >
        <span class="info-span">{{ result.data.projectionCount }}</span>
      </div>
    </div>
    <div class="card-container" v-if="result.data.type !== 'region'">
      <div
        v-for="(card, index) in cards"
        :key="index"
        class="card-item"
        :style="{ borderColor: borderColor }"
        @click="addTab(card)"
      >
        <div class="card-item-left">
          <img :src="require(`@/assets/${card.img}`)" alt="" />
        </div>
        <div class="card-item-right">
          <span class="item-header">{{ card.header }}</span>
          <div class="item-text">{{ card.text }}</div>
          <div class="item-btn">
            View details
            <v-icon size="16"> $ArrowRight</v-icon>
          </div>
        </div>
      </div>
    </div>
    <div style="flex-grow: 1"></div>
  </div>
</template>

<script>
import { mapState } from "vuex";

export default {
  name: "Result",
  props: {
    result: {
      type: Object,
      default: () => {},
      required: true
    },
    frameID: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      cards: [
        {
          header: "Soma Distribution",
          img: "Group 149.png",
          type: "somaDistribution",
          name: "Soma Distribution",
          text:
            "These plots summarize the distribution of neuronal somata along three anatomical axes, together with the number and density of somata across hierarchical brain regions."
        },
        {
          header: "Projection Overview",
          img: "Group 151.png",
          type: "projectionOverview",
          name: "Projection Overview",
          text:
            "These plots summarize the distribution of neuron counts across hierarchical brain regions, as well as the total projection length (µm) across the left and right hemispheres."
        },
        {
          header: "Projection heatmap (by axon length)",
          img: "Group 150.png",
          type: "heatmapAxon",
          name: "Projection heatmap",
          text:
            "These plots summarize regional axon projection patterns based on axon length (µm), with source units defined either as individual neurons or as brain regions containing their somata."
        },
        {
          header: "Projection heatmap (by terminal points)",
          img: "Group 150.png",
          type: "heatmapTerminalPoints",
          name: "Projection heatmap",
          text:
            "These plots summarize regional axon projection patterns based on terminal counts, with source units defined either as individual neurons or as brain regions containing their somata."
        }
      ]
    };
  },
  computed: {
    ...mapState({
      theme: state => state.theme
    }),

    borderColor() {
      return this.$vuetify.theme.themes[this.theme]["accent-3"];
    }
  },
  methods: {
    capitalizedText(text) {
      return text.charAt(0).toUpperCase() + text.slice(1);
    },
    addTab(item) {
      const tab = {
        frameID: this.frameID,
        type: item.type,
        label: this.result.label + " - " + item.name,
        value: (Math.random() * 100000).toFixed(0),
        data: this.result.data
      };

      this.$store.commit("analyze/addTab", tab);
    }
  },
  mounted() {
    if (process.env.VUE_APP_SUB_SPECIES === "rbm") {
      this.cards.push({
        header: "Soma and Dendrite Depth Distribution Analysis",
        img: "Group 149.png",
        type: "dendriteDepthDistribution",
        name: "Soma and Dendrite Depth Distribution Analysis",
        text:
          "This analysis integrates the spatial organization of retinal ganglion cells by mapping soma localization alongside dendritic stratification. The soma distribution plots summarize the positional data of neuronal cell bodies across three primary axes. Complementarily, the dendritic profiles illustrate the stratification depth within the inner plexiform layer (IPL), highlighting the functional segregation of RGCs within the ON and OFF sublaminae."
      });

      // find the header name to be Soma Distribution and remove it
      const index = this.cards.findIndex(
        card => card.header === "Soma Distribution"
      );
      if (index !== -1) {
        this.cards.splice(index, 1);
      }
    }

    if (process.env.VUE_APP_SUB_SPECIES === "SC") {
      const index = this.cards.findIndex(
        card => card.header === "Projection heatmap (by terminal points)"
      );
      if (index !== -1) {
        this.cards.splice(index, 1);
      }
    }
  }
};
</script>

<style lang="scss" scoped>
* {
  font-size: 13px;
}

.header {
  margin: 20px;
  background: #ffc42c19;
  height: 36px;
  border-left: 2px solid #ffc42c;
  display: flex;
  align-items: center;
  padding: 10px;
  font-size: 13px;
}

.card-container {
  width: 100%;
  padding: 0 20px;
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: auto auto;
  grid-column-gap: 13px;
  grid-row-gap: 10px;

  .card-item {
    display: flex;
    padding: 20px;
    border-style: solid;
    border-width: 1px;
    align-items: center;
    cursor: pointer;

    .card-item-left {
      align-self: flex-start;
      margin-right: 20px;
      height: 75px;
      width: 100px;

      img {
        height: 75px;
        width: 100px;
      }
    }

    .card-item-right {
      flex: 1;

      .item-header {
        color: #f5f8ff;
        font-size: 14px;
        line-height: 14px;
      }

      .item-text {
        color: #a5abb9;
        font-size: 14px;
        margin: 10px 0 20px;
      }

      .item-btn {
        color: #7fbefa;
        font-size: 13px;
      }
    }
  }

  .card-item:hover {
    border-color: #7fbefa !important;
  }

  .card-item:first-child {
    span {
      line-height: 32px;
    }
  }

  .card-item:nth-child(2) {
    span {
      line-height: 32px;
    }
  }
}

.info-span {
  border-top: 1px solid #343f5c;
  border-left: 1px solid #343f5c;
  display: flex;
  align-items: center;
  padding-left: 10px;
}

.info-span:nth-child(even) {
  color: #ced4e4;
}

.info-span:nth-child(odd) {
  color: #f5f8ff;
  font-weight: 600;
}

.info-span:nth-last-child(1) {
  border-bottom: 1px solid #343f5c;
}

.info-span:nth-last-child(2) {
  border-bottom: 1px solid #343f5c;
}
</style>
