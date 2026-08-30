<template>
  <div class="detail">
    <div style="margin: 10px">
      <div
        class="back"
        @click="$emit('back')"
        @mouseenter="mainColorMouseEnter('arrowLeft')"
        @mouseleave="mainColorMouseLeave('arrowLeft')"
      >
        <arrow-left :fill="fillColors.arrowLeft"></arrow-left>
        <span>Back</span>
      </div>

      <detail-create
        v-show="animationStatus !== 'sample'"
        :fill-colors="fillColors"
        @createNewFunc="createNewFunc"
        @mainColorMouseEnter="mainColorMouseEnter"
        @mainColorMouseLeave="mainColorMouseLeave"
      ></detail-create>

      <detail-header
        :name="currentAnimationData?.name"
        @changeNameFunc="changeNameFunc"
      ></detail-header>

      <div class="drag-list">
        <draggable
          v-model="animationList"
          @start.stop="onDragStart"
          @end.stop="onDragEnd"
          animation="200"
        >
          <transition-group>
            <div v-for="item in animationList" :key="item.uuid">
              <rotation
                @deleteFunc="deleteFunc"
                @rotationPlaying="rotationPlaying"
                v-show="item?.type === 'rotation'"
                :value="item"
              ></rotation>
              <custom
                @deleteFunc="deleteFunc"
                @customPlaying="customPlaying"
                v-show="item?.type === 'custom'"
                :value="item"
              ></custom>
            </div>
          </transition-group>
        </draggable>
      </div>
    </div>

    <detail-operation
      :currentData="currentAnimationData"
      :fillColors="fillColors"
      :isAnimationWork="isAnimationWork"
      @mainColorMouseEnter="mainColorMouseEnter"
      @mainColorMouseLeave="mainColorMouseLeave"
      @onPlayFunc="onPlayFunc"
      @onPauseFunc="onPauseFunc"
      @onStopFunc="onStopFunc"
      @saveFunc="saveFunc"
    ></detail-operation>
  </div>
</template>

<script>
import { mapState } from "vuex";
import Custom from "./components/Custom.vue";
import Rotation from "./components/Rotation.vue";
import ArrowLeft from "@/components/icons/ArrowLeft";
import draggable from "vuedraggable";
import DetailHeader from "./components/DetailHeader.vue";
import DetailCreate from "./components/DetailCreate.vue";
import DetailOperation from "./components/DetailOperation.vue";
import { deepClone } from "@/utils/utils";
import { createAnimationsFunc, updateAnimationsFunc } from "@/api/animation";
export default {
  name: "AnimationDetail",

  components: {
    ArrowLeft,
    Custom,
    Rotation,
    draggable,
    DetailHeader,
    DetailCreate,
    DetailOperation
  },

  data() {
    return {
      animationList: [],
      mainColorFill: "#7FBEFA",
      fillColors: {
        pause: "#7F8490",
        play: "#7F8490",
        stop: "#7F8490",
        save: "#7F8490",
        menu: "#7F8490",
        addRotation: "#7FBEFA",
        addCustom: "#7FBEFA",
        arrowLeft: "#7FBEFA"
      },
      operationArr: ["pause", "play", "stop", "save", "menu"],
      currentAnimationData: null,
      animationIndexs: {},
      currentAnimationResult: {},
      pauseStatus: false,
      stopStatus: false
    };
  },

  watch: {
    animationStatus() {
      this.resetData();
    }
  },

  computed: {
    ...mapState({
      theme: state => state.theme,
      target: state => state.target,
      userInfo: state => state.userInfo,
      animations: state => state.animations,
      animationStatus: state => state.animationStatus,
      currentAnimation: state => state.currentAnimation
    }),

    isAnimationWork() {
      const val =
        this.animationList.length &&
        this.animationList.every(item => item?.valid && item?.cameraValid);
      const color = val ? "#7FBEFA" : "#7F8490";
      this.operationArr.forEach(item => {
        // Enabled and currently playing
        const judgeVal = ["stop", "save"].includes(item);
        if (judgeVal && val) {
          let primaryVal;
          item === "stop" && (primaryVal = this.currentAnimationData?.onPlay);
          item === "save" &&
            (primaryVal = this.currentAnimationData?.name !== "");
          this.fillColors[item] = primaryVal ? color : "#7F8490";
          return;
        }
        this.fillColors[item] = color;
      });
      return val || false;
    }
  },

  methods: {
    changeNameFunc(newV) {
      this.currentAnimationData.name = newV;
    },

    resetData() {
      if (this.animationStatus.includes("create")) {
        this.currentAnimationData = {
          name: "",
          onPause: false,
          onPlay: false,
          onStop: false
        };
        this.animationList = [];
      } else {
        this.currentAnimationData = deepClone(this.currentAnimation);
        this.setCameraData();
      }
    },

    setCameraData() {
      let start = Date.now();
      this.currentAnimationData?.cameraInterpolations?.forEach(item => {
        this.$set(item, "type", "custom");
        this.$set(item, "valid", true);
        this.$set(item, "onPlay", false);
        this.$set(item, "cameraValid", true);
        this.$set(item, "uuid", start++);
      });
      this.currentAnimationData?.cameraRotations?.forEach(item => {
        this.$set(item, "type", "rotation");
        this.$set(item, "valid", true);
        this.$set(item, "onPlay", false);
        this.$set(item, "cameraValid", true);
        this.$set(item, "uuid", start++);
      });
      this.animationList = [
        this.currentAnimationData?.cameraInterpolations,
        this.currentAnimationData?.cameraRotations
      ]
        .flat(1)
        .filter(Boolean)
        .sort((a, b) => a.index - b.index);
    },

    mainColorMouseEnter(tag) {
      if (this.operationArr.includes(tag)) {
        this.fillColors[tag] = this.isAnimationWork ? "#7FBEFA" : "#7F8490";
        return;
      }
      this.fillColors[tag] = "#7FBEFA";
    },

    mainColorMouseLeave(tag) {
      if (this.operationArr.includes(tag)) {
        this.fillColors[tag] = this.isAnimationWork ? "#7FBEFA" : "#7F8490";
        return;
      }
      this.fillColors[tag] = "#7FBEFA";
    },

    createNewFunc(type) {
      this.animationList.push({
        type,
        valid: false,
        cameraValid: false,
        index: this.animationList.length,
        uuid: Date.now()
      });
    },

    onDragStart(event) {
      event.stopPropagation();
    },

    onDragEnd(event) {
      event.stopPropagation();
      this.animationList.forEach((item, index) => {
        item.index = index;
      });
    },

    deleteFunc(index) {
      this.animationList.splice(index, 1);
      this.animationList.forEach((item, index) => {
        item.index = index;
      });
    },

    async saveFunc(tab) {
      if (!this.userInfo) {
        this.$store.commit("setLoginFlag", true);
        return;
      }
      if (this.isAnimationWork && this.currentAnimationData?.name) {
        this.currentAnimationData.cameraInterpolations = this.animationList.filter(
          item => item.type === "custom"
        );
        this.currentAnimationData.cameraRotations = this.animationList.filter(
          item => item.type === "rotation"
        );

        this.currentAnimationData.cameraRotations?.forEach(rotation => {
          ["x", "y", "z"].forEach(
            v => (rotation[v] = rotation[v] ? +rotation[v] : 0)
          );
        });

        if (this.animationStatus.includes("create") || tab === "new") {
          await createAnimationsFunc({
            name: this.currentAnimationData?.name,
            cameraInterpolations: this.currentAnimationData
              ?.cameraInterpolations,
            cameraRotations: this.currentAnimationData?.cameraRotations
          });
        } else {
          await updateAnimationsFunc(this.currentAnimation?.id, {
            name: this.currentAnimationData?.name,
            cameraInterpolations: this.currentAnimationData
              ?.cameraInterpolations,
            cameraRotations: this.currentAnimationData?.cameraRotations
          });
        }
        this.$store.dispatch("getAnimations");
        this.$store.commit("setCurrentAnimation", this.currentAnimationData);
        this.$emit("setCurrentTab", "menu");
        this.$store.commit("setToolTipType", "success");
        this.$store.commit("setToolTipMessage", "Saved successfully");
        this.$store.commit("setToolTipVisible", true);
      }

      this.currentAnimationData = {
        name: "",
        onPause: false,
        onPlay: false,
        onStop: false
      };
      this.animationList = [];
    },

    onPauseFunc() {
      this.pauseStatus = true;
      this.currentAnimationResult?.setPause(true);
    },

    onStopFunc() {
      this.pauseStatus = false;
      this.stopStatus = true;
      this.currentAnimationResult?.stop();
    },

    async onPlayFunc() {
      if (this.pauseStatus) {
        this.pauseStatus = false;
        this.currentAnimationResult?.setPause(false);
        return;
      }
      for (let i = 0; i < this.animationList.length; i++) {
        const item = this.animationList[i];
        if (this.stopStatus) {
          this.stopStatus = false;
          break;
        }
        if (item?.type === "custom") await this.customPlaying(item);
        if (item?.type === "rotation") await this.rotationPlaying(item);
      }
      this.currentAnimationData.onPlay = false;
    },

    async customPlaying(item) {
      this.currentAnimationResult?.stop && this.currentAnimationResult?.stop();
      this.currentAnimationResult = await window.neuroViz.interpolateCamera(
        item?.start,
        item?.end,
        item?.duration
      );
      return this.currentAnimationResult?.animation;
    },

    async rotationPlaying(item) {
      await window.neuroViz.deserializeCamera(item?.start);
      let xMul = 1;
      let yMul = 1;
      let zMul = 1;
      if (process.env.VUE_APP_TARGET === "monkey") {
        xMul = 1;
        yMul = -1;
        zMul = -1;
      }
      this.currentAnimationResult = await window.neuroViz.rotateCamera(
        +item?.x * xMul + "",
        +item?.y * yMul + "",
        +item?.z * zMul + "",
        item?.duration
      );
      return this.currentAnimationResult?.animation;
    }
  },

  mounted() {
    this.pauseStatus = false;
    this.stopStatus = false;
  }
};
</script>

<style lang="scss">
.detail {
  .back {
    color: #7fbefa;
    font-size: 13px;
    font-weight: 400;
    height: 32px;
    line-height: 32px;
    max-width: 55px;
    &:hover {
      cursor: pointer;
      color: #ffffff;
    }
    svg {
      transform: translateY(3px);
      margin-right: 4px;
    }
  }
  .drag-list {
    max-height: calc(100vh - 380px);
    @include hide-scrollbar();
    overflow-x: hidden;
    overflow-y: auto;
  }
}

.section {
  width: 100%;
  border: 1px solid #926dcd;
  .section-body {
    padding: 10px;
  }
  .section-title {
    font-weight: 400;
    color: #c68dff;
    font-size: 13px;
    font-weight: 400;
  }
  .section-item {
    display: flex;
    height: 24px;
    line-height: 24px;
    font-size: 13px;
    font-weight: 400;
    color: #ced4e4;
    &:not(:last-of-type) {
      margin-bottom: 10px;
    }
  }
  .bg-section-icon {
    width: 24px;
    height: 24px;
    transform: translateY(0) !important;
  }
  .section-camera {
    svg {
      transform: translateY(3px);
    }
    .camera-title {
      width: 90px;
      margin-right: 20px;
    }
    .camera-set {
      cursor: pointer;
      margin-left: 5px;
      color: #c68dff;
      text-decoration-line: underline;
    }
  }
  .section-duration {
    display: flex;
    align-items: center;
    color: #ced4e4;
    height: 32px;
    line-height: 32px;
    .section-duration-text {
      display: inline-block;
      width: 80px;
    }

    .v-input {
      flex: 0;
      width: 60px;
      color: #ffffff;
    }
    .v-input__slot {
      width: 60px;
      font-size: 13px;
    }
    .v-text-field {
      margin: 0 10px;
      padding: 0;
    }
    .v-input__slot {
      margin: 0;
    }
    .v-text-field__details {
      display: none;
    }
    // .v-text-field__slot input {
    //   border-bottom: 1px solid #7f8490;
    //   &:focus {
    //     border-color: #3b87fd !important;
    //   }
    // }
    // .theme--dark.v-text-field > .v-input__control > .v-input__slot:before {
    //   border: none;
    // }
  }
  .section-input {
    width: 60px;
    height: 21px;
    margin: 0 10px;
    color: #ced4e4;
    border-bottom: 1px solid #ced4e4;
    &::after {
      content: "°";
    }
  }
  .section-operation {
    width: 100%;
    line-height: 28px;
    height: 28px;
    text-align: center;
    font-size: 13px;
    font-weight: 400;
    svg {
      transform: translateY(3px);
      margin-right: 10px;
    }
  }
  .active-preview {
    border-top: 1px solid #926dcd;
    color: #c68dff;
    &:hover {
      cursor: pointer;
      color: #ffffff;
      background: rgba(146, 109, 205, 0.1);
    }
  }
  .disabled-preview {
    // border-top: 1px solid rgba(255, 255, 255, 0.1);
    // background: rgba(255, 255, 255, 0.1);
    color: #7f8490;
    background: transparent;
    &:hover {
      cursor: no-drop;
      color: #7f8490;
    }
  }
}

.v-text-field__prefix,
.v-text-field__suffix {
  color: #ffffff;
  padding: 0 !important;
}
</style>
