<template>
  <div class="reference-main" id="reference" v-draggable>
    <div class="reference-header atlas-draggable-header" :style="headerStyle">
      <span>Reference</span>
      <v-icon size="16" style="cursor: pointer" @click="onClose">$Close</v-icon>
    </div>
    <div class="reference-content">
      <v-radio-group v-model="currentSlice" dense hide-details row>
        <v-radio
          label="Segmentation"
          color="#7fbefa"
          value="annotation"
          style="height: 32px"
        ></v-radio>

        <v-radio
          label="Average brain imaging map"
          color="#7fbefa"
          value="template"
          style="height: 32px"
        ></v-radio>
      </v-radio-group>

      <div style="background: #343f5c; margin: 14px 0; height: 1px"></div>

      <div
        class="d-flex flex-column"
        v-for="(sliceItem, index) in sliceItems"
        :key="index"
      >
        <div class="d-flex align-center height-32">
          <v-icon
            size="28"
            @click="
              () => {
                sliceItem.enabled = !sliceItem.enabled;
                onSwitchSlice(sliceItem);
              }
            "
          >
            {{ sliceItem.enabled ? "$SwitchOn" : "$SwitchOff" }}
          </v-icon>
          <div class="d-flex justify-space-between flex-grow-1">
            <span class="text">{{ sliceItem.name }}</span>
            <span v-show="sliceItem.enabled" class="text">
              Bregma(mm):{{ ((sliceItem.slice * sliceItem.spacing) / 1000.0).toFixed(2) }}
            </span>
          </div>
        </div>

        <div v-if="sliceItem.enabled" class="d-flex align-center height-32">
          <div
            class="d-flex align-center justify-center"
            style="
              width: 24px;
              height: 24px;
              border-radius: 2px;
              background: rgba(255, 255, 255, 0.1);
              margin-right: 10px;
            "
            @click="onChangeSliceByStep(sliceItem, -1)"
          >
            <v-icon>$SimpleArrowLeft</v-icon>
          </div>
          <v-slider
            hide-details
            :max="sliceItem.maxSlice"
            :value="sliceItem.slice"
            @input="debounceSliceChange(sliceItem, $event)"
          ></v-slider>
          <div
            class="d-flex align-center justify-center"
            style="
              width: 24px;
              height: 24px;
              border-radius: 2px;
              background: rgba(255, 255, 255, 0.1);
              margin-left: 10px;
            "
            @click="onChangeSliceByStep(sliceItem, 1)"
          >
            <v-icon>$SimpleArrowRight</v-icon>
          </div>
        </div>
        <div
          v-if="sliceItem.enabled"
          class="d-flex align-center justify-center height-32"
        >
          <span class="text" style="font-size: 13px; margin-left: 0"
            >Opacity</span
          >
          <v-slider
            hide-details
            v-model="sliceItem.opacity"
            style="flex-grow: 1"
            @change="onChangeOpacity(sliceItem)"
          ></v-slider>
          <div class="input-wrapper">
            <input
              style="width: 50px"
              type="number"
              max="100"
              min="0"
              v-model="sliceItem.opacity"
              @input="onChangeOpacity(sliceItem)"
            />
            <span class="text" style="font-size: 13px; margin-left: 0">%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { mapState } from "vuex";

export default {
  name: "Reference",
  data() {
    const names = [
      "Sagittal",
      "Horizontal",
      "Coronal",
    ];
    if (process.env.VUE_APP_TARGET === 'monkey') {
      names[0] = "Horizontal";
      names[1] = "Coronal";
      names[2] = "Sagittal";
    }
    return {
      mouseDown: false,
      mouseDownX: 0,
      mouseDownY: 0,
      currentSlice: "annotation",
      sliceItems: [
        {
          name: names[0],
          enabled: false,
          slice: 0,
          opacity: 100,
          maxSlice: 0,
          sizes: [],
          cachedTemplateSlices: {},
          cachedAnnotationSlices: {},
          spacing: 0,
          spaceDirections: [],
          axis: "z",
          currentAnnotationSlice: null,
          currentTemplateSlice: null,
          loadedTemplateSlices: [],
          loadedAnnotationSlices: []
        },
        {
          name: names[1],
          enabled: false,
          slice: 0,
          opacity: 100,
          maxSlice: 0,
          sizes: [],
          cachedTemplateSlices: {},
          cachedAnnotationSlices: {},
          spacing: 0,
          spaceDirections: {},
          axis: "y",
          currentAnnotationSlice: null,
          currentTemplateSlice: null,
          loadedTemplateSlices: [],
          loadedAnnotationSlices: []
        },
        {
          name: names[2],
          enabled: false,
          slice: 0,
          opacity: 100,
          maxSlice: 0,
          sizes: [],
          cachedTemplateSlices: {},
          cachedAnnotationSlices: {},
          spacing: 0,
          spaceDirections: [],
          axis: "x",
          currentAnnotationSlice: null,
          currentTemplateSlice: null,
          loadedTemplateSlices: [],
          loadedAnnotationSlices: []
        }
      ],
      debounceSliceChange: () => {},
      host: process.env.VUE_APP_SRV,
      species: process.env.VUE_APP_TARGET,
      project: process.env.VUE_APP_SUBTYPE,
      annotationHeader: null,
      templateHeader: null,
      setColorMapDone: false
    };
  },
  computed: {
    ...mapState({
      theme: state => state.theme,
      target: state => state.target,
      neuroVizReady: state => state.neuroVizReady,
      regionData: state => state.region.regionData,
      templateHeaderURL: state => state.templateHeaderURL,
      annotationHeaderURL: state => state.annotationHeaderURL,
      functionMap: state => state.functionMap,
      templateDataURL: state => state.templateDataURL,
      annotationDataURL: state => state.annotationDataURL
    }),

    enableSegmentationSlice() {
      return this.currentSlice === "annotation";
    },

    enableImageMapSlice() {
      return this.currentSlice === "template";
    },

    headerStyle() {
      return {
        borderTop:
          "2px solid " +
          this.$vuetify.theme.themes[this.theme]["primary-light"],
        background: this.$vuetify.theme.themes[this.theme]["primary-bar"]
      };
    }
  },

  watch: {
    neuroVizReady() {
      if (Object.keys(this.regionData).length > 0 && !this.setColorMapDone) {
        this.setColorMap();
      }
    },

    regionData() {
      if (this.neuroVizReady && !this.setColorMapDone) {
        this.setColorMap();
      }
    },

    "functionMap.set_reference_planes": {
      handler(newVal) {
        this.currentSlice =
          newVal?.type === "segmentation" ? "annotation" : "template";

        ["sagittal", "horizontal", "coronal"].forEach(axis => {
          if (Object.prototype.hasOwnProperty.call(newVal, axis)) {
            const item = this.sliceItems.find(
              i => i.name.toLowerCase() === axis
            );
            if (item?.enabled !== newVal[axis]) {
              item.enabled = newVal[axis];
              this.onSwitchSlice(item);
            }
          }
        });
      }
    },

    enableSegmentationSlice() {
      for (let i = 0; i < 3; i++) {
        const item = this.sliceItems[i];
        if (!this.enableSegmentationSlice) {
          window.neuroViz.unload(item.currentAnnotationSlice);
          item.currentAnnotationSlice = null;
        }

        if (item.enabled) {
          this.loadTargetSlice(item, item.slice);
        }
      }
    },

    enableImageMapSlice() {
      for (let i = 0; i < 3; i++) {
        const item = this.sliceItems[i];
        if (!this.enableImageMapSlice) {
          window.neuroViz.unload(item.currentTemplateSlice);
          item.currentTemplateSlice = null;
        }

        if (item.enabled) {
          this.loadTargetSlice(item, item.slice);
        }
      }
    }
  },
  mounted() {
    // get template header info
    axios.get(this.templateHeaderURL).then(response => {
      this.templateHeader = response.data.data;

      const sliceSize = response.data.data?.sizes;
      const sliceSpacing = response.data.data?.spaceDirections;

      for (let i = 0; i < 3; i += 1) {
        this.sliceItems[i].spaceDirections = sliceSpacing;
        this.sliceItems[i].sizes = sliceSize;
      }

      this.sliceItems[2].maxSlice = sliceSize[0] - 1; // coronal
      this.sliceItems[2].spacing = sliceSpacing[0];
      this.sliceItems[2].slice = (sliceSize[0] / 2).toFixed(0);

      this.sliceItems[1].maxSlice = sliceSize[1] - 1; // horizontal
      this.sliceItems[1].spacing = sliceSpacing[4];
      this.sliceItems[1].slice = (sliceSize[1] / 2).toFixed(0);

      this.sliceItems[0].maxSlice = sliceSize[2] - 1; // sagittal
      this.sliceItems[0].spacing = sliceSpacing[8];
      this.sliceItems[0].slice = (sliceSize[2] / 2).toFixed(0);
    });

    axios.get(this.annotationHeaderURL).then(resp => {
      this.annotationHeader = resp.data.data;
    });

    this.debounceSliceChange = this.debounce(this.onChangeSlice, 500, false);
  },
  methods: {
    onMouseDown(event) {
      event.preventDefault();
      this.mouseDownX = event.clientX;
      this.mouseDownY = event.clientY;
      this.mouseDown = true;
    },

    onMoveTable(event) {
      event.preventDefault();
      if (!this.mouseDown) {
        return;
      }

      let div = document.getElementById("reference");
      let offsetX = this.mouseDownX - event.clientX;
      let offsetY = this.mouseDownY - event.clientY;

      this.mouseDownX = event.clientX;
      this.mouseDownY = event.clientY;

      div.style.top = div.offsetTop - offsetY + "px";
      div.style.left = div.offsetLeft - offsetX + "px";
    },

    setColorMap() {
      const uids = Object.keys(this.regionData);
      const colorMap = new Map();
      for (let i = 0; i < uids.length; i += 1) {
        const hexColor = this.regionData[uids[i]].color_hex_triplet;
        const r = parseInt(hexColor.slice(0, 2), 16);
        const g = parseInt(hexColor.slice(2, 4), 16);
        const b = parseInt(hexColor.slice(4), 16);

        colorMap.set(Number(uids[i]), [r, g, b]);
      }
      window.neuroViz.setSliceColorMap(colorMap);
      this.setColorMapDone = true;
    },
    debounce(func, delay = 1000, immediate = false) {
      let timer = null;
      return function() {
        if (timer) {
          clearTimeout(timer);
        }
        if (immediate && !timer) {
          func.apply(this, arguments);
        }
        timer = setTimeout(() => {
          func.apply(this, arguments);
        }, delay);
      };
    },

    onClose() {
      this.$emit("close");
    },

    onSwitchSlice(sliceItem) {
      if (!sliceItem.enabled) {
        if (this.enableImageMapSlice) {
          window.neuroViz.unload(sliceItem.currentTemplateSlice);
          sliceItem.currentTemplateSlice = null;
        }

        if (this.enableSegmentationSlice) {
          window.neuroViz.unload(sliceItem.currentAnnotationSlice);
          sliceItem.currentAnnotationSlice = null;
        }
      } else {
        this.loadTargetSlice(sliceItem, sliceItem.slice);
      }
    },

    onChangeSlice(sliceItem, arg) {
      sliceItem.slice = arg;
      this.loadTargetSlice(sliceItem, arg);
    },

    onChangeSliceByStep(sliceItem, step) {
      const sliceValue = sliceItem.slice + step;
      if (sliceValue < 0) {
        sliceItem.slice = 0;
      } else if (sliceValue > sliceItem.maxSlice) {
        sliceItem.slice = sliceItem.maxSlice;
      } else {
        sliceItem.slice = sliceValue;
      }

      this.loadTargetSlice(sliceItem, sliceValue);
    },

    loadSliceFromCache(item, slice) {
      const target = this.enableSegmentationSlice ? "annotation" : "template";
      const cachedData = this.enableSegmentationSlice
        ? item.cachedAnnotationSlices
        : item.cachedTemplateSlices;

      const result = window.neuroViz.loadSlice(
        item.axis,
        slice,
        target,
        target === "annotation"
          ? this.annotationHeader.sizes
          : this.templateHeader.sizes,
        target === "annotation"
          ? this.annotationHeader.spaceDirections
          : this.templateHeader.spaceDirections,
        cachedData[slice]
      );

      if (target === "annotation") {
        item.loadedAnnotationSlices.push(result);
      } else {
        item.loadedTemplateSlices.push(result);
      }

      // unload other slices

      const name = `${item.axis}.${slice}.${
        target === "annotation" ? "annotation" : "template"
      }.slice`;

      if (item.slice !== slice) {
        window.neuroViz.unload(name);
      } else {
        let targetArray =
          target === "annotation"
            ? item.loadedAnnotationSlices
            : item.loadedTemplateSlices;
        const loopArray = [...targetArray];
        loopArray.forEach(el => {
          if (el !== name) {
            window.neuroViz.unload(el);
            const index = targetArray.indexOf(el);
            targetArray.splice(index, 1);
          }
        });

        if (target === "annotation") {
          item.currentAnnotationSlice = name;
        } else {
          item.currentTemplateSlice = name;
        }
      }

      this.onChangeOpacity(item);
    },

    loadSliceFromRemote(item, slice) {
      const target = this.enableSegmentationSlice ? "annotation" : "template";
      const prefix =
        target === "annotation" ? this.annotationDataURL : this.templateDataURL;
      const url = `${prefix}/${item.axis}/${slice}`;

      axios.get(url).then(resp => {
        const data = resp.data.data.slice;
        if (target === "annotation") {
          item.cachedAnnotationSlices[slice] = data;
        } else {
          item.cachedTemplateSlices[slice] = data;
        }

        if (item.slice !== slice) {
          return;
        }

        this.loadSliceFromCache(item, slice);

        this.onChangeOpacity(item);
      });
    },

    loadTargetSlice(sliceItem, slice) {
      const targetCache = this.enableSegmentationSlice
        ? sliceItem.cachedAnnotationSlices
        : sliceItem.cachedTemplateSlices;

      if (targetCache[slice]) {
        this.loadSliceFromCache(sliceItem, slice);
      } else {
        this.loadSliceFromRemote(sliceItem, slice);
      }
    },

    onChangeOpacity(sliceItem) {
      if (
        this.enableImageMapSlice &&
        sliceItem.enabled &&
        sliceItem.currentTemplateSlice
      ) {
        window.neuroViz.setSliceOpacity(
          sliceItem.currentTemplateSlice,
          sliceItem.opacity / 100.0
        );
      }

      if (
        this.enableSegmentationSlice &&
        sliceItem.enabled &&
        sliceItem.currentAnnotationSlice
      ) {
        window.neuroViz.setSliceOpacity(
          sliceItem.currentAnnotationSlice,
          sliceItem.opacity / 100.0
        );
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.reference-main {
  position: absolute;
  display: flex;
  flex-direction: column;
  width: 250px;
  z-index: 1000;
}
.reference-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 4px 10px;

  span {
    color: #7fbefa;
    font-size: 13px;
    font-style: normal;
    font-weight: 500;
    line-height: normal;
  }
}

.reference-content {
  display: flex;
  flex-direction: column;
  padding: 10px;
  background: rgba(33, 33, 33, 0.5);
  backdrop-filter: blur(20px);

  .input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;

    input {
      outline: none;
      border-radius: 2px;
      border: 1px solid #343f5c;
      margin-left: 10px;
      color: #eaf0ffde;
      font-size: 13px;
      padding: 8px 10px;
      height: 24px;
    }

    input::-webkit-outer-spin-button,
    input::-webkit-inner-spin-button {
      -webkit-appearance: none;
      margin: 0;
    }

    input[type="number"] {
      -moz-appearance: textfield;
      appearance: textfield;
    }

    span {
      position: absolute;
      right: 4px;
      top: 12px;
      transform: translateY(-50%);
    }
  }
}

.text {
  color: #ced4e4;
  font-size: 13px;
  font-weight: 400;
  margin-left: 10px;
}

.height-32 {
  height: 32px;
}

.reference-content {
  ::v-deep .v-slider__track-fill {
    background-color: #343f5c !important;
  }

  ::v-deep .v-slider .v-slider__track-background {
    background-color: #343f5c !important;
  }

  ::v-deep .v-slider .v-slider__thumb {
    background-color: #ffffff !important;
  }

  ::v-deep .v-slider .v-slider__thumb::before {
    display: none;
  }
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
</style>
