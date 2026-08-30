<template>
  <div class="d-flex flex-column color-scheme" v-draggable>
    <div
      class="color-title color-scheme-header atlas-draggable-header"
      :style="headerStyle"
    >
      <span
        class="primary-light--text"
        style="font-size: 13px; font-weight: 500"
        >Coloring Scheme
      </span>
      <v-icon size="16" style="cursor: pointer" @click="onClose"
        >$Close
      </v-icon>
    </div>
    <!-- begin region -->
    <div class="region d-flex flex-column">
      <span style="color: #ffffff; font-weight: 500; font-size: 13px"
        >Region
      </span>
      <v-radio-group v-model="regionColorSchemeModel" dense hide-details row>
        <v-radio
          v-for="option in currentRegionOptions"
          :key="option.value"
          :label="option.text"
          color="#7fbefa"
          :value="option.value"
          style="height: 32px"
        ></v-radio>
      </v-radio-group>
    </div>
    <!-- end region -->
    <div class="seperator accent-3"></div>
    <!--  begin neuron -->
    <div class="region d-flex flex-column">
      <span style="color: #ffffff; font-weight: 500; font-size: 13px"
        >Neuron
      </span>
      <v-radio-group v-model="neuronColorSchemeModel" dense hide-details row>
        <v-radio
          v-for="option in neuronOptions"
          :key="option.value"
          :label="option.text"
          color="#7fbefa"
          :value="option.value"
          style="height: 32px"
        ></v-radio>
      </v-radio-group>

      <div v-show="neuronColorSchemeModel === 'structure'">
        <div class="d-flex align-center" style="height: 32px">
          <div class="structure-color" style="background-color: #ffe040"></div>
          <span class="structure-text"> Dendrite</span>
        </div>
        <div class="d-flex align-center" style="height: 32px">
          <div class="structure-color" style="background-color: #ff4be2"></div>
          <span class="structure-text"> Soma</span>
        </div>
        <div class="d-flex align-center" style="height: 32px">
          <div class="structure-color" style="background-color: #00fe00"></div>
          <span class="structure-text"> Axon</span>
        </div>
      </div>
    </div>
    <!-- end neuron -->
  </div>
</template>

<script>
import { mapMutations, mapState } from "vuex";
import { hexToRgb } from "@/utils/utils.js";

export default {
  name: "ColorScheme",
  data() {
    return {
      regionOptions: [
        { text: "By CEBSIT scheme", value: "cebsit" },
        { text: "By Allen scheme", value: "allen" },
        { text: "By Random color", value: "random" }
      ],
      neuronOptions: [
        { text: "By random color", value: "random" },
        {
          text:
            process.env.VUE_APP_TARGET === "monkey"
              ? "By neuron types"
              : "By mouse line",
          value: "mouseLine"
        },
        { text: "By soma location area", value: "region" },
        { text: "By neuron structure", value: "structure" }
      ]
    };
  },
  computed: {
    ...mapState({
      functionMap: state => state.functionMap,
      theme: state => state.theme,
      target: state => state.target,
      regionColorScheme: state => state.region.colorScheme,
      neuronColorScheme: state => state.neuron.colorScheme,
      viewedNeurons: state => state.neuron.viewedNeurons,
      viewedRegions: state => state.region.viewedRegions,
      neuronRegionRelation: state => state.neuron.neuronRegionRelation,
      regionData: state => state.region.regionData,
      updateNeuronColor: state => state.neuron.updateNeuronColor
    }),

    currentRegionOptions() {
      return this.target === "monkey"
        ? this.regionOptions.filter(option => option.value !== "allen")
        : this.regionOptions;
    },

    headerStyle() {
      return {
        borderTop:
          "2px solid " +
          this.$vuetify.theme.themes[this.theme]["primary-light"],
        background: this.$vuetify.theme.themes[this.theme]["primary-bar"]
      };
    },

    regionColorSchemeModel: {
      get() {
        return this.regionColorScheme;
      },
      set(value) {
        this.setRegionColorFunc(value);
      }
    },
    neuronColorSchemeModel: {
      get() {
        return this.neuronColorScheme;
      },
      set(value) {
        this.setNeuronColorFunc(value);
      }
    }
  },

  watch: {
    updateNeuronColor() {
      if (this.updateNeuronColor.type === "region") {
        this.batchSetSomaAreaColor();
      }
    },

    "functionMap.set_brain_region_coloring_scheme": {
      handler(newVal) {
        this.setRegionColorFunc(newVal?.scheme);
      }
    },

    "functionMap.set_neuron_coloring_scheme": {
      handler(newVal) {
        this.setNeuronColorFunc(newVal?.scheme);
      }
    }
  },
  methods: {
    ...mapMutations({
      setRegionColorScheme: "region/setColorScheme",
      setNeuronColorScheme: "neuron/setColorScheme"
    }),

    onClose() {
      this.$emit("close");
    },

    setRegionColorFunc(value) {
      this.viewedRegions.forEach(item => {
        const hex =
          value === "random"
            ? item.randomColor
            : value === "cebsit"
            ? item.cebsitColor
            : item.allenColor;
        const rgb = hexToRgb(hex).map(el => el / 255.0);
        window.neuroViz.setColor(item.file, rgb);
        item.colorScheme = value;
        item.currentColor = hex;
      });

      this.setRegionColorScheme(value);
    },

    setNeuronColorFunc(value) {
      this.$store.commit("neuron/setIsBatchSetColor", false);
      if (value === "random") {
        this.batchSetIDColor();
      } else if (value === "mouseLine") {
        this.batchSetMouseLineColor();
      } else if (value === "structure") {
        this.batchSetStructureColor();
      } else {
        this.batchSetSomaAreaColor();
      }

      this.setNeuronColorScheme(value);
    },

    batchSetIDColor() {
      this.viewedNeurons.forEach(neuron => {
        neuron.colorScheme = "random";
        neuron.batchColor = null;
        neuron.currentColor = neuron.idColor;
        const rgb = hexToRgb(neuron.idColor).map(el => el / 255.0);
        window.neuroViz.setColor(neuron.file, rgb);
      });
    },

    batchSetMouseLineColor() {
      this.viewedNeurons.forEach(neuron => {
        neuron.colorScheme = "mouseLine";
        neuron.batchColor = null;
        neuron.currentColor = neuron.typeColor;
        const rgb = hexToRgb(neuron.typeColor).map(el => el / 255.0);
        window.neuroViz.setColor(neuron.file, rgb);
      });
    },

    batchSetStructureColor() {
      this.viewedNeurons.forEach(neuron => {
        neuron.batchColor = null;
        neuron.colorScheme = "structure";
        const { somaColor, axonColor, dentriteColor, undefinedColor } = {
          ...neuron.structureColor
        };
        window.neuroViz.setSWCPartColor(
          neuron.file,
          somaColor,
          axonColor,
          dentriteColor,
          undefinedColor
        );
      });
    },

    batchSetSomaAreaColor() {
      const getRegionSomaColor = neuron => {
        const projectName = neuron.projectFullName;
        const relationItem = this.neuronRegionRelation[projectName][neuron.id];
        const somaArray = relationItem.owner_region_array;
        if (somaArray.length === 0) {
          return "#ffffff";
        }

        return this.regionData[somaArray[somaArray.length - 1]].somaColor;
      };
      this.viewedNeurons.forEach(neuron => {
        const regionColor = getRegionSomaColor(neuron);
        neuron.regionColor = regionColor;
        neuron.batchColor = null;

        neuron.colorScheme = "region";
        neuron.currentColor = neuron.regionColor;
        const rgb = hexToRgb(neuron.regionColor).map(el => el / 255.0);

        window.neuroViz.setColor(neuron.file, rgb);
      });
    }
  }
};
</script>

<style scoped lang="scss">
* {
  font-family: Roboto;
}

.v-icon::after {
  display: none;
}
.color-scheme {
  position: absolute;
  width: 250px;
  background: rgba(33, 33, 33, 0.5);
  backdrop-filter: blur(20px);

  .color-scheme-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  :deep(.v-input) {
    margin: 4px 0 !important;

    .v-label {
      font-size: 13px !important;
      margin-left: 10px;
    }

    .v-input--selection-controls__ripple {
      display: none;
    }

    .v-input--selection-controls__input {
      width: 16px !important;
      height: 16px !important;
      margin-right: 4px !important;
    }
  }
}

.scheme-item {
  display: flex;
  align-items: center;
  height: 32px;
  span {
    transform: translateY(-1px);
    color: #ced4e4;
    font-size: 14px;
    margin-left: 10px;
  }
}

.color-title {
  padding: 4px 10px;
  // height: 24px;
}

.region {
  padding: 10px 10px 0 10px;
}

.seperator {
  height: 1px;
  margin: 14px 10px;
}
.neuron {
  padding: 0 10px 10px 10px;
}

.structure-color {
  width: 16px;
  height: 16px;
  border: 1px solid #868686;
  margin-right: 10px;
  margin-left: 24px;
}

.structure-text {
  font-size: 13px;
  font-weight: 400;
  color: #ced4e4;
}
</style>
