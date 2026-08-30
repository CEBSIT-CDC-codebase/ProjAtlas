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
              @click.native="reviewStartEndFunc('start')"
            ></add-frame>
            <span class="camera-set" @click="setStartEndFunc('start')"
              >Set</span
            >
          </div>
        </div>

        <div class="section-camera section-item">
          <span class="camera-title">Camera end:</span>
          <div class="d-flex">
            <frame :fill="iconStatusColor" v-if="!isSetEnd"></frame>
            <add-frame
              class="bg-icon bg-section-icon"
              v-else
              @click.native="reviewStartEndFunc('end')"
            ></add-frame>
            <span class="camera-set" @click="setStartEndFunc('end')">Set</span>
          </div>
        </div>

        <div class="section-duration">
          <span>Duration</span>
          <v-text-field
            :rules="[rules.duration]"
            v-model="durationVal"
            type="number"
          ></v-text-field>
          <span> Second</span>
        </div>
      </v-form>
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
  // °
  components: {
    AddFrame,
    Delete,
    Frame,
    Play
  },

  data() {
    return {
      playFill: "#C68DFF",
      iconStatusColor: "#7F8491",
      rules: {
        duration: value => {
          const pattern = /^[+]{0,1}(\d+)$/;
          return pattern.test(value) || "Required.";
        }
      },
      isSetStart: false,
      isSetEnd: false,
      errorFill: "#DC3737"
    };
  },

  computed: {
    refsName() {
      return this.value?.type + this.value?.index;
    },

    durationVal: {
      get() {
        return parseInt(this.value?.duration / 1000);
      },
      set(newV) {
        this.value.duration = +newV * 1000 || undefined;
      }
    },

    disabledStyle() {
      if (this.playAble) {
        return "";
      }
      return "disabled-preview";
    },

    formVaild: {
      get() {
        return this.value?.valid;
      },
      set(newV) {
        this.value.valid = newV;
      }
    },

    playAble() {
      return this.value?.valid && this.value?.cameraValid;
    },

    validStartEnd() {
      return this.isSetStart && this.isSetEnd;
    }
  },

  watch: {
    playAble: {
      handler() {
        this.playFill = this.playAble ? "#C68DFF" : "#7F8490";
      }
      // immediate: true,
    },

    validStartEnd() {
      this.value.cameraValid = this.validStartEnd;
      this.iconStatusColor = this.validStartEnd ? "#7F8491" : this.errorFill;
    },

    formVaild() {
      if (this.$refs[this.refsName]?.validate()) {
        this.value.valid = true;
      }
    }
  },

  methods: {
    setStartEndFunc(tag) {
      if (tag === "start") {
        !this.isSetStart && (this.isSetStart = true);
        this.value.start = window.neuroViz.serializeCamera();
        return;
      }

      if (tag === "end") {
        !this.isSetEnd && (this.isSetEnd = true);
        this.value.end = window.neuroViz.serializeCamera();
      }
    },

    async reviewStartEndFunc(tag) {
      const currentTo = tag === "start" ? this.value.start : this.value.end;
      window.neuroViz.deserializeCamera(currentTo);
    },

    onMouseEnter() {
      this.playFill = this.playAble ? "#ffffff" : "#7F8490";
    },

    onMouseLeave() {
      this.playFill = this.playAble ? "#C68DFF" : "#7F8490";
    },

    previewFunc() {
      if (this.playAble) {
        this.$emit("customPlaying", this.value);
      }
    }
  },

  mounted() {
    if (this.value?.cameraValid) {
      this.isSetStart = true;
      this.isSetEnd = true;
      return;
    }
    this.isSetStart = false;
    this.isSetEnd = false;
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
