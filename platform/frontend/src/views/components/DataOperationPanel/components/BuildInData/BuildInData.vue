<template>
  <div class="build-in-data">
    <div
      class="data-types"
      :style="{ 'grid-template-columns': `repeat(${dataTypes.length}, 1fr)` }"
    >
      <span
        class="accent primary-light-1--text"
        :style="targetDataType === typeItem.value ? activeTabStyle : ''"
        style="font-size: 13px;"
        v-for="(typeItem, index) in dataTypes"
        :key="index"
        @click="setTargetDataType(typeItem.value)"
      >
        {{ typeItem.label }}</span
      >
    </div>
    <NeuronData
      v-show="targetDataType === 'neuron'"
      v-on="$listeners"
      style="height: 100%;"
    ></NeuronData>
    <RegionData v-show="targetDataType === 'region'"></RegionData>
  </div>
</template>

<script>
import { mapState } from "vuex";
import RegionData from "./components/RegionData/RegionData.vue";
import NeuronData from "./components/NeuronData/NeuronData.vue";

export default {
  name: "BuildInData",
  components: {
    NeuronData,
    RegionData
  },
  data() {
    return {
      targetDataType: "neuron"
    };
  },

  computed: {
    ...mapState({
      theme: state => state.theme,
      target: state => state.target
    }),

    dataTypes() {
      return [
        { value: "neuron", label: "Neuron" },
        { value: "region", label: "Region" }
      ];
    },

    activeTabStyle() {
      return {
        background:
          this.$vuetify.theme.themes[this.theme].background + " !important",
        color:
          this.$vuetify.theme.themes[this.theme]["accent-1"] + " !important"
      };
    }
  },

  methods: {
    setTargetDataType(type) {
      this.targetDataType = type;
    }
  }
};
</script>

<style lang="scss" scoped>
* {
  font-size: 13px;
  font-family: Roboto;
}

.build-in-data {
  display: flex;
  flex-direction: column;
  padding: 10px;
  max-height: calc(100vh - 92px);
  overflow: auto;
}

.data-types {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  text-align: center;
  font-size: 13px;
  font-weight: 400;
  height: 24px;
  line-height: 24px;

  span {
    cursor: pointer;
  }

  span:nth-child(1) {
    border-radius: 4px 0 0 4px;
  }

  span:nth-child(4) {
    border-radius: 0 4px 4px 0;
  }
}
</style>
