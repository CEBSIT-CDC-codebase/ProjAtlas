<template>
  <div class="secondary d-flex flex-column justify-center align-center">
    <div class="title primary-light--text">
      Welcome! <br />
      You may filter some neurons and click the analyze button on the left side of the
      page to view results .
    </div>
    <span
      class="primary-light-1--text"
      style="font-family: Roboto; font-weight: 400; font-size: 13px"
      >Examples</span
    >
    <div ref="cardContainer" class="card-container">
      <div
        v-for="(card, index) in cards"
        :key="index"
        class="card-item"
        :style="{ borderColor: borderColor }"
      >
        <span v-html="card.header" class="accent-2--text"></span>
        <div
          :style="{
            background: 'url(' + require(`@/assets/${card.img}`) + ') no-repeat ',
          }"
        ></div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
export default {
  name: "Welcome",
  data() {
    return {
      cards: [
        {
          header: "Soma Distribution",
          img: "SomaDistribution.png",
        },
        {
          header: "Projection Overview",
          img: "ProjectionOverview.png",
        },
        {
          header: "Projection heatmap<br>(by axon length)",
          img: "ProjectionHeatMapAxon.png",
        },
        {
          header: "Projection heatmap<br>(by terminal points)",
          img: "ProjectionHeatMapTerminalPoints.png",
        },
      ],
    };
  },

  computed: {
    ...mapState({
      theme: (state) => state.theme,
      analyzeWidth: (state) => state.layout.analyzeWidth,
    }),

    borderColor() {
      return this.$vuetify.theme.themes[this.theme]["accent-3"];
    },
  },

  watch: {
    analyzeWidth() {
      if (this.analyzeWidth < 450) {
        this.$refs.cardContainer.classList.add("card-container-middle");
        this.$refs.cardContainer.classList.add("card-container-small");
      } else if (this.analyzeWidth < 500) {
        this.$refs.cardContainer.classList.add("card-container-middle");
      } else {
        this.$refs.cardContainer.classList.remove("card-container-middle");
        this.$refs.cardContainer.classList.remove("card-container-small");
      }
    },
  },

  mounted() {
    if (process.env.VUE_APP_SUB_SPECIES === "SC") {
      const index = this.cards.findIndex((card) =>
        card.header.includes("Projection heatmap<br>(by terminal points)")
      );
      if (index !== -1) {
        this.cards.splice(index, 1);
      }
    }
  },
};
</script>

<style lang="scss" scoped>
.title {
  width: auto;
  text-align: center;
  margin: 45px 10px 40px;
  font-size: 16px !important;
  font-family: Roboto;
  font-weight: 400;
}

@media screen and (max-device-width: 1530px) {
  .title {
    margin-top: 45px;
    margin-bottom: 20px;
  }

  .card-container {
    grid-template-columns: 1fr;
  }
}

.card-container {
  max-width: 445px;
  margin-top: 10px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  grid-column-gap: 13px;
  grid-row-gap: 10px;

  .card-item {
    display: flex;
    flex-direction: column;
    padding: 20px;
    border-style: solid;
    border-width: 1px;

    span {
      display: flex;
      flex-direction: column;
      text-align: center;
      align-content: center;
      margin-bottom: 10px;
      height: 32px;
      line-height: 16px;
    }

    div {
      width: 176px;
      height: 150px;
      background-size: cover !important;
    }
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

.card-container-middle {
  grid-template-columns: 1fr;
  grid-template-rows: repeat(4, 1fr);

  .card-item {
    align-items: center;
  }
}

.card-container-small {
  max-width: 400px;
}
</style>
