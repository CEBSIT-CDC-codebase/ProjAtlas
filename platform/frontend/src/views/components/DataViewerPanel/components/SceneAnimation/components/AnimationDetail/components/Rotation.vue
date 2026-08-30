<template>
  <div class="custom section">
    <div class="section-body">
      <div class="custom-header section-item">
        <span class="section-title">Section {{ value?.index + 1 }}</span>
        <div class="bg-icon" @click="$emit('deleteFunc', value?.index)">
          <delete fill="#C68DFF"></delete>
        </div>
      </div>

      <v-form :ref="refsName" v-model="formVaild">
        <div class="section-camera section-item">
          <span class="camera-title">Camera start:</span>
          <div class="d-flex">
            <frame :fill="iconStatusColor" v-if="!isSetStart"></frame>
            <add-frame
              class="bg-icon bg-section-icon"
              v-else
              @click.native="reviewStartEndFunc"
            ></add-frame>
            <span class="camera-set" @click="setStartEndFunc('start')"
              >Set</span
            >
          </div>
        </div>

        <div
          class="section-duration"
          v-for="item in rotationInputKeys"
          :key="item.label"
        >
          <span class="section-duration-text">{{ item.label }} Rotation</span>
          <v-text-field
            :rules="[confirmRotationRule(), rules.rotation]"
            :prefix="getPreFix(value[item.key])"
            suffix="°"
            v-model="value[item.key]"
            type="number"
          ></v-text-field>
        </div>

        <div class="section-duration">
          <span>Duration</span>
          <v-text-field
            :rules="[rules.duration]"
            v-model="durationVal"
            type="number"
          ></v-text-field>
          <!-- <input type="number" class="section-input" v-model="durationVal" /> -->
          <span> Second</span>
        </div></v-form
      >
    </div>

    <div
      class="section-operation active-preview"
      :class="disabledStyle"
      @click="previewFunc"
      @mouseenter="onMouseEnter"
      @mouseleave="onMouseLeave"
    >
      <play :fill="playFill"></play>
      <span>Preview</span>
    </div>
  </div>
</template>

<script>
import AddFrame from "@/components/icons/AddFrame";
import Delete from "@/components/icons/Delete";
import Frame from "@/components/icons/Frame";
import Play from "@/components/icons/Play";
export default {
  name: "Custom",

  props: {
    value: {
      type: Object,
      default: () => {}
    }
  },

  components: {
    AddFrame,
    Delete,
    Frame,
    Play
  },

  data() {
    return {
      playFill: "#C68DFF",
      errorFill: "#DC3737",
      iconStatusColor: "#7F8491",
      isSetStart: false,
      rules: {
        duration: value => {
          const pattern = /^[+]{0,1}(\d+)$/;
          return pattern.test(value) || "Required.";
        },
        rotation: value => {
          const pattern = /^(?:(-?(?:360(\.0+)?|3[0-5]\d(\.\d+)?|[0-2]?\d{1,2}(\.\d+)?))|null|undefined)?$/;
          return pattern.test(value) || "-360 ~ 360";
        }
      }
    };
  },

  computed: {
    rotationInputKeys() {
      const keyMap = {
        mouse: {
          ap: "x",
          dv: "y",
          lr: "z"
        },
        monkey: {
          ap: "y",
          dv: "z",
          lr: "x"
        }
      };
      return [
        {
          key: keyMap[process.env.VUE_APP_TARGET].ap,
          label: "AP"
        },
        {
          key: keyMap[process.env.VUE_APP_TARGET].dv,
          label: "DV"
        },
        {
          key: keyMap[process.env.VUE_APP_TARGET].lr,
          label: "LR"
        }
      ];
    },

    validStart() {
      return this.isSetStart;
    },

    disabledStyle() {
      if (this.playAble) {
        return "";
      }
      return "disabled-preview";
    },

    playAble() {
      return this.value?.valid && this.value?.cameraValid;
    },

    durationVal: {
      get() {
        return parseInt(this.value?.duration / 1000);
      },
      set(newV) {
        this.value.duration = +newV * 1000 || undefined;
      }
    },

    formVaild: {
      get() {
        return this.value?.valid;
      },
      set(newV) {
        this.value.valid = newV;
      }
    },

    refsName() {
      return this.value?.type + this.value?.index;
    }
  },

  watch: {
    validStart() {
      this.value.cameraValid = this.validStart;
      this.iconStatusColor = this.validStart ? "#7F8491" : this.errorFill;
    },

    playAble: {
      handler() {
        this.playFill = this.playAble ? "#C68DFF" : "#7F8490";
      }
    },

    formVaild() {
      if (this.$refs["form" + this.value?.index]?.validate()) {
        this.value.vaild = true;
      }
    }
  },

  methods: {
    getPreFix(num) {
      if (+num > 0) {
        return "+";
      } else if (num != 0 && !num) {
        return "0";
      }
      return "";
    },

    confirmRotationRule() {
      // At least one is within range
      const pattern = /^(-?([1-9]|[1-9]\d|1[0-9]\d|2[0-9]\d|3[0-5]\d|360|0))$/;
      const val = ["x", "y", "z"].some(key => pattern.test(this.value[key]));
      return val || "-360 ~ 360";
    },

    onMouseEnter() {
      this.playFill = this.playAble ? "#ffffff" : "#7F8490";
    },

    onMouseLeave() {
      this.playFill = this.playAble ? "#C68DFF" : "#7F8490";
    },

    setStartEndFunc(tag) {
      if (tag === "start") {
        !this.isSetStart && (this.isSetStart = true);
        this.value.start = window.neuroViz.serializeCamera();
        return;
      }
    },

    async reviewStartEndFunc() {
      window.neuroViz.deserializeCamera(this.value.start);
    },

    async previewFunc() {
      if (this.playAble) {
        this.$emit("rotationPlaying", this.value);
      }
    }
  },
  mounted() {
    if (this.value?.cameraValid) {
      this.isSetStart = true;
      return;
    }
    this.isSetStart = false;
    this.$refs[this.refsName].reset();
  }
};
</script>

<style lang="scss" scoped>
.custom {
  margin-bottom: 10px;
  .custom-header {
    display: flex;
    justify-content: space-between;
  }
}
.v-application .primary--text {
  color: #3b87fd !important;
  caret-color: #3b87fd !important;
}

:deep {
  .v-text-field.v-input--has-state > .v-input__control > .v-input__slot:before {
    border-color: #dc3737;
  }
  .v-text-field.v-input--is-focused > .v-input__control > .v-input__slot:after {
    transform: scaleX(0);
  }
}
</style>
