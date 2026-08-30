<template>
  <div class="">
    <div class="setting-item item-title">Mouse Control</div>
    <div class="setting-item">
      <v-switch
        color="#2D68C3"
        v-model="enableRegion"
        inset
        dense
        :disabled="!neuroVizReady"
      ></v-switch>
      <span>Enable region picking</span>
    </div>
    <div class="setting-item">
      <v-switch
        color="#2D68C3"
        v-model="enableNeuron"
        inset
        dense
        :disabled="!neuroVizReady"
      ></v-switch>
      <span>Enable neuron picking</span>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
export default {
  name: "MouseControl",

  components: {},

  data() {
    return {
      isNeuronViz: false,
    };
  },

  watch: {
    neuroVizReady() {
      if (this.neuroVizReady && !this.isNeuronViz) {
        this.isNeuronViz = true;

        window.neuroViz.setNeuronPickable(true);
      }
    },
    "functionMap.set_region_picking_mode": {
      handler(newVal) {
        if (Object.prototype.hasOwnProperty.call(newVal, "mode")) {
          this.enableRegion = newVal.mode;
        }
      },
    },
    "functionMap.set_neuron_picking_mode": {
      handler(newVal) {
        if (Object.prototype.hasOwnProperty.call(newVal, "mode")) {
          this.enableNeuron = newVal.mode;
        }
      },
    },
  },

  computed: {
    ...mapState({
      functionMap: (state) => state.functionMap,
      neuroVizReady: (state) => state.neuroVizReady,
      settingValues: (state) => state.settingValues,
    }),

    enableRegion: {
      get() {
        return this.settingValues.region;
      },
      set(newV) {
        this.$store.commit("setSettingValues", {
          data: newV,
          index: "region",
        });
        window.neuroViz.setRegionPickable(newV);
      },
    },

    enableNeuron: {
      get() {
        return this.settingValues.neuron;
      },
      set(newV) {
        this.$store.commit("setSettingValues", {
          data: newV,
          index: "neuron",
        });
        window.neuroViz.setNeuronPickable(newV);
      },
    },
  },

  methods: {},

  mounted() {},
};
</script>

<style lang="scss" scoped></style>
