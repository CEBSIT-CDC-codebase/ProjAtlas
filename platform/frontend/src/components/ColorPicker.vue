<template>
  <div class="color-picker">
    <div class="color-picker-type">
      <div
        class="type-item"
        :class="{ 'type-active': currentHexColor === val }"
        v-for="(val, key) in colorDetailMap"
        :key="key"
        @click="chooseColorFunc(val)"
      >
        <div class="type-color-item" :style="getTypeItemStyle(val)"></div>
      </div>
    </div>
    <div class="color-picker-gradient">
      <div class="btn-reset" @click="$emit('gradientResetFunc', colorValues)">
        <v-icon size="14" color="#7FBEFA" style="transform: translateY(-1px)">
          $Refresh
        </v-icon>
        Reset
      </div>
      <div class="gradient-items">
        <div
          class="gradient-item"
          v-for="i in 10"
          :key="i + 'gradient'"
          :class="{
            'active-gradient-item':
              currentGradientValue === gradientValues[(i - 1) * 2]
          }"
        >
          <div
            class="item-word"
            :style="getGradientColorFunc(i)"
            @click="chooseGradientColor(i)"
          ></div>
          <span class="item-arrow"></span>
        </div>
      </div>
      <div
        class="gradient-bar"
        :style="getTypeItemStyle(currentHexColor)"
      ></div>
      <div class="color-picker-opacity">
        <span>Gradient</span>
        <v-slider
          step="10"
          v-model="opacityOfSlice"
          dense
          class="align-center layers-slider"
          @end="setOpacityFunc"
        >
        </v-slider>
        <v-text-field
          v-model="opacityOfSlice"
          disabled
          outlined
          dense
          color="primary"
          style="max-width: 56px"
          hide-details
        ></v-text-field>
        <span class="opacity-percent">%</span>
      </div>
    </div>
  </div>
</template>

<script>
import { gradient } from "@/utils/uColor";

export default {
  props: {
    colorDetailMap: {
      type: Object,
      default: () => {}
    },
    colorValues: {
      type: Object,
      default: () => {}
    }
  },
  data() {
    return {
      gradientValues: [],
      currentGradientValue: "",
      opacityOfSlice: 0,
      currentGradientIndex: 0
    };
  },
  computed: {
    currentHexColor() {
      return this.colorDetailMap[this.colorValues?.colorString];
    }
  },
  watch: {
    currentHexColor() {
      this.getGradientValues();
    },
    currentGradientIndex() {
      this.getCurrentOpacityValue();
    },
    "colorValues.opacityValues"() {
      this.getCurrentOpacityValue();
    }
  },
  methods: {
    // Get the current gradient color values
    getGradientValues() {
      const vals = gradient(this.currentHexColor, "#ffffff", 18) || [];
      this.currentGradientValue = vals[0];
      this.gradientValues = [...vals, "#ffffff"];
    },
    getCurrentOpacityValue() {
      this.opacityOfSlice = parseInt(
        this.colorValues.opacityValues[this.currentGradientIndex] * 100
      );
    },
    getTypeItemStyle(color) {
      return {
        background: `linear-gradient(to right, ${color}, #ffffff)`
      };
    },
    getGradientColorFunc(index) {
      return {
        background: `${this.gradientValues[(index - 1) * 2]}`
      };
    },
    setOpacityFunc() {
      this.$emit(
        "changeColorOpacityValues",
        this.colorValues,
        this.currentGradientIndex,
        this.opacityOfSlice / 100
      );
    },
    chooseGradientColor(index) {
      this.currentGradientValue = this.gradientValues[(index - 1) * 2];
      this.currentGradientIndex = index - 1;
    },
    chooseColorFunc(color) {
      for (const key in this.colorDetailMap) {
        if (this.colorDetailMap[key] === color)
          this.$emit("changeColorValues", this.colorValues, key);
      }
    }
  },
  mounted() {
    this.getGradientValues();
    this.opacityOfSlice = parseInt(
      this.colorValues.opacityValues[this.currentGradientIndex] * 100
    );
  }
};
</script>
<style lang="scss" scoped>
.color-picker {
  width: 340px;
}

.color-picker-type {
  display: flex;
  flex-wrap: wrap;
  line-height: 34px;
  background-color: #26272b;

  .type-item {
    width: 34px;
    height: 34px;
    line-height: 34px;
    text-align: center;

    &:hover {
      cursor: pointer;
      background-color: #313237;
    }

    .type-color-item {
      width: 14px;
      height: 14px;
      margin: 10px;
      border-radius: 2px;
    }
  }

  .type-active {
    background-color: #313237;

    .type-color-item {
      border: 1px solid #01d1ff;
    }
  }
}

.color-picker-gradient {
  // height: 126px;
  padding: 10px 20px 8px;
  background: #313237;

  .btn-reset {
    text-align: right;
    color: #7fbefa;
    font-size: 12px;
    cursor: pointer;
    margin-bottom: 5px;
  }

  .gradient-items {
    display: flex;
    transform: translateX(-7px);

    .gradient-item {
      display: inline-block;
      text-align: center;

      &:not(:last-child) {
        margin-right: 19px;
      }

      > .item-arrow {
        display: block;
        position: relative;
        width: 0;
        height: 0;
        top: 0px;
        left: 4px;
        border-width: 4px 3px 0;
        border-color: white transparent transparent;
        border-style: solid;
      }

      > .item-word {
        width: 14px;
        height: 14px;
        border: 1px solid white;
        cursor: pointer;
      }
    }

    .active-gradient-item {
      > .item-arrow {
        left: 3px;
        border-width: 5px 5px 0;
        border-top-color: #01d1ff;
      }

      > .item-word {
        outline: 2px solid #01d1ff;
      }
    }
  }

  .gradient-bar {
    margin: 5px 0;
    height: 20px;
  }

  .color-picker-opacity {
    display: flex;
    font-size: 12px;
    color: rgba($color: #fff, $alpha: 0.85);

    .opacity-percent {
      position: absolute;
      right: 30px;
      //bottom: 23px;
      color: rgba(255, 255, 255, 0.5);
    }
  }
}

::v-deep {
  .v-input__slot {
    height: 24px;
    min-height: 24px !important;
  }

  .v-text-field__slot {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.85);
  }

  .v-text-field--outlined fieldset {
    border-radius: 2px;
  }

  .v-messages {
    display: none;
  }
}
</style>
