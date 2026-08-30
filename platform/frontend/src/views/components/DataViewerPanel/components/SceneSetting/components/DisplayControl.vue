<template>
  <div class="">
    <div class="setting-item item-title">Display Control</div>
    <div class="setting-item">
      <v-switch
        color="#2D68C3"
        v-model="enableAxis"
        inset
        dense
        :disabled="!neuroVizReady"
      ></v-switch>
      <span>Show coordinate axis</span>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
export default {
  name: "DisplayControl",

  components: {},

  data() {
    return {
      enableAxis: true
    };
  },

  computed: {
    ...mapState({
      functionMap: state => state.functionMap,
      neuroVizReady: state => state.neuroVizReady
    })
  },

  watch: {
    "functionMap.set_neuron_display_mode": {
      handler(newVal) {
        if (Object.prototype.hasOwnProperty.call(newVal, "mode")) {
          this.enableAxis = newVal.mode;
        }
      }
    },
    enableAxis: {
      handler(newV) {
        if (!this.neuroVizReady) {
          return;
        }
        const axesCanvas = window.neuroViz.getAxesCanvas();
        if (axesCanvas) {
          axesCanvas.style.display = newV ? "block" : "none";
        }
      },
      immediate: true
    }
  },

  methods: {},

  mounted() {}
};
</script>

<style lang="scss" scoped></style>
