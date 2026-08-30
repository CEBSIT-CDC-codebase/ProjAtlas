<template>
  <div class="">
    <div class="setting-item item-title">Neuron Display Mode</div>
    <div class="setting-item">
      <v-switch
        color="#2D68C3"
        v-model="neuronalBackbone"
        inset
        dense
      ></v-switch>
      <span>Neuronal backbone</span>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
export default {
  name: "NeuronDisplayMode",

  components: {},

  data() {
    return {};
  },

  watch: {
    "functionMap.set_coordinate_axis_visibility": {
      handler(newVal) {
        if (Object.prototype.hasOwnProperty.call(newVal, "visibility")) {
          this.neuronalBackbone = newVal.visibility;
        }
      }
    }
  },

  computed: {
    ...mapState({
      functionMap: state => state.functionMap,
      settingValues: state => state.settingValues,
      viewedNeurons: state => state.neuron.viewedNeurons
    }),
    neuronalBackbone: {
      get() {
        return this.settingValues.mode;
      },
      set(newV) {
        this.$store.commit("setSettingValues", {
          data: newV,
          index: "mode"
        });
        for (let i = 0; i < this.viewedNeurons.length; i++) {
          const item = this.viewedNeurons[i];
          // name,soma,axon,dendrite,mainBranch
          item?.visible &&
            window.neuroViz.setSWCPartVisibility(
              item?.file,
              item?.somaVisible,
              item?.axonVisible,
              item?.dendriteVisible,
              newV,
              item?.undefinedVisible
            );
        }
      }
    }
  },

  methods: {},

  mounted() {}
};
</script>

<style lang="scss" scoped></style>
0
