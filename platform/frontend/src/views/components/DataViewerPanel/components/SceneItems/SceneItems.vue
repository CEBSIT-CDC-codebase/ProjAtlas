<template>
  <div>
    <div
      class="scene-items"
      :style="totalStyle"
      v-draggable
      v-show="showPanels"
    >
      <div
        class="scene-items-header atlas-draggable-header"
        :style="headerStyle"
      >
        <span class="primary-light--text">Items in the scene</span>
        <v-icon size="16" @click="showPanels = !showPanels"
          >$DoubleLearrow</v-icon
        >
      </div>
      <div class="scene-items-tabs">
        <span
          class="accent-1--text"
          v-for="(tabItem, index) in sceneTabs"
          :key="index"
          @click="targetTab = tabItem.value"
          :style="targetTab !== tabItem.value ? inactiveTabStyle : ''"
          >{{ tabItem.label }}
        </span>
      </div>
      <Neurons v-show="showPanels && targetTab === 'neurons'"></Neurons>
      <Regions v-show="showPanels && targetTab === 'regions'"></Regions>
    </div>

    <div class="scene-visible-items" v-show="!showPanels" :style="totalStyle">
      <v-icon
        size="16"
        @click="showPanels = !showPanels"
        style="transform: rotate(180deg)"
        >$DoubleLearrow</v-icon
      >
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
import Neurons from "./components/Neurons/Neurons.vue";
import Regions from "./components/Regions/Regions.vue";

export default {
  name: "SceneItems",
  components: {
    Neurons,
    Regions
  },
  data() {
    return {
      sceneTabs: [
        {
          label: "Neurons",
          value: "neurons"
        },
        {
          label: "Regions",
          value: "regions"
        }
      ],
      targetTab: "neurons",
      panelPosition: [10, 71],
      showPanels: true
    };
  },
  computed: {
    ...mapState({
      theme: state => state.theme
    }),

    headerStyle() {
      return {
        borderTop:
          "2px solid " +
          this.$vuetify.theme.themes[this.theme]["primary-light"],
        background: this.$vuetify.theme.themes[this.theme]["primary-bar"]
      };
    },

    totalStyle() {
      return {
        background: this.$vuetify.theme.themes[this.theme]["accent-5"] + "80",
        top: this.panelPosition[1] + "px",
        right: this.panelPosition[0] + "px"
      };
    },

    inactiveTabStyle() {
      return {
        background:
          this.$vuetify.theme.themes[this.theme]["accent"] + " !important",
        color:
          this.$vuetify.theme.themes[this.theme]["primary-light-1"] +
          " !important",
        "backdrop-filter": "blur(15px)"
      };
    }
  },

};
</script>

<style lang="scss" scoped>
.scene-items {
  width: 300px;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(15px);
  user-select: none;
  position: absolute;
  z-index: 2;
}
.scene-items-header {
  display: flex;
  border-top-width: 1px;
  justify-content: space-between;
  align-items: center;
  padding: 4px 10px;
  font-size: 13px;
  font-weight: 500;

  :deep(.v-icon) {
    cursor: pointer;
  }
}

.scene-visible-items {
  position: absolute;
  z-index: 2;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  width: 32px;
  height: 32px;
  fill: rgba(74, 96, 150, 0.3);
  backdrop-filter: blur(2px);
}

.scene-items-tabs {
  display: flex;

  span {
    text-align: center;
    cursor: pointer;
    padding: 4px 0;
    font-size: 13px;
    font-weight: 400;
    flex-grow: 1;
  }
}

:deep(.v-icon) {
  &::after {
    display: none !important;
  }
}
</style>
