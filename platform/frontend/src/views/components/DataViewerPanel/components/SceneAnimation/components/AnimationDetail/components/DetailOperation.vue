<template>
  <div class="detail-operation">
    <div
      class="operation-btn"
      :class="disabledBtnClass"
      v-show="pauseFlag"
      @click="pauseFunc"
      @mouseenter="$emit('mainColorMouseEnter', 'pause')"
      @mouseleave="$emit('mainColorMouseLeave', 'pause')"
    >
      <Pause :fill="fillColors.pause"></Pause>
      <span>Pause</span>
    </div>
    <div
      class="operation-btn"
      :class="disabledBtnClass"
      v-show="playFlag"
      @click="playFunc"
      @mouseenter="$emit('mainColorMouseEnter', 'play')"
      @mouseleave="$emit('mainColorMouseLeave', 'play')"
    >
      <Play :fill="fillColors.play"></Play>
      <span>Play</span>
    </div>
    <div
      class="operation-btn"
      :class="stopDisabledBtnClass"
      @click="stopFunc"
      @mouseenter="extraMouseEnter('stop')"
      @mouseleave="extraMouseLeave('stop')"
    >
      <Stop :fill="fillColors.stop"></Stop>
      <span>Stop</span>
    </div>
    <div
      class="operation-btn"
      v-show="animationStatus != 'sample'"
      :class="saveDisabledBtnClass"
      @click="saveFunc"
      @mouseenter="extraMouseEnter('save')"
      @mouseleave="extraMouseLeave('save')"
    >
      <Save :fill="fillColors.save"></Save>
      <span>Save</span>
    </div>
    <div
      style="position: relative; flex: 1; height: 100%"
      @click="menuFunc"
      v-click-outside="menuClickOutSide"
    >
      <div
        class="operation-btn"
        :class="disabledBtnClass"
        @mouseenter="$emit('mainColorMouseEnter', 'menu')"
        @mouseleave="$emit('mainColorMouseLeave', 'menu')"
      >
        <Menu :fill="fillColors.menu"></Menu>
        <span>More</span>
      </div>
      <div class="more-items" v-show="moreVisible">
        <v-icon size="18" class="item-polygon">$Polygon</v-icon>
        <div class="more-item" @click="saveAsNewFunc">
          Save as a new animation
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Pause from "@/components/icons/Pause";
import Play from "@/components/icons/Play";
import Menu from "@/components/icons/Menu";
import Save from "@/components/icons/Save";
import Stop from "@/components/icons/Stop";
import { mapState } from "vuex";
export default {
  name: "DetailOperation",

  props: {
    fillColors: {
      type: Object,
      default: () => {}
    },
    currentData: {
      type: Object,
      default: () => {}
    },
    isAnimationWork: {
      type: Boolean,
      default: false
    }
  },

  components: {
    Play,
    Pause,
    Menu,
    Save,
    Stop
  },

  data() {
    return {
      moreVisible: false
    };
  },

  computed: {
    ...mapState(["animationStatus"]),

    pauseFlag() {
      return this.currentData?.onPlay && !this.currentData?.onPause;
    },

    playFlag() {
      return !this.currentData?.onPlay || this.currentData?.onPause;
    },

    stopFlag() {
      return this.currentData?.onPlay;
    },

    disabledBtnClass() {
      return this.isAnimationWork ? null : "diabled-operation-btn";
    },

    saveDisabledBtnClass() {
      return this.isAnimationWork && this.currentData?.name
        ? null
        : "diabled-operation-btn";
    },

    stopDisabledBtnClass() {
      // Enabled and currently playing
      return this.isAnimationWork && this.stopFlag
        ? null
        : "diabled-operation-btn";
    }
  },

  watch: {},

  methods: {
    extraMouseEnter(tag) {
      this.fillColors[tag] =
        this.isAnimationWork && this.extraJudge(tag) ? "#ffffff" : "#7F8490";
    },

    extraMouseLeave(tag) {
      this.fillColors[tag] =
        this.isAnimationWork && this.extraJudge(tag) ? "#7FBEFA" : "#7F8490";
    },

    extraJudge(tag) {
      if (tag === "stop") {
        return this.stopFlag;
      }
      if (tag === "save") {
        return this.currentData?.name !== "";
      }
    },

    menuClickOutSide() {
      if (this.moreVisible) this.moreVisible = false;
    },

    saveAsNewFunc() {
      this.$emit("saveFunc", "new");
    },

    pauseFunc() {
      if (this.isAnimationWork) {
        this.currentData.onPause = true;
        this.$emit("onPauseFunc");
      }
    },

    playFunc() {
      if (this.isAnimationWork) {
        this.currentData.onPlay = true;
        this.currentData.onPause = false;
        this.$emit("onPlayFunc");
      }
    },

    stopFunc() {
      if (this.isAnimationWork && this.stopFlag) {
        this.currentData.onPlay = false;
        this.currentData.onPause = false;
        this.$emit("onStopFunc");
      }
    },

    menuFunc() {
      if (this.isAnimationWork) {
        this.moreVisible = !this.moreVisible;
      }
    },

    saveFunc() {
      this.$emit("saveFunc");
    }
  }
};
</script>

<style lang="scss" scoped>
.detail-operation {
  height: 55px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-top: 1px solid #343f5c;
  .operation-btn {
    height: 100%;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding-top: 4px;
    color: #7fbefa;
    font-size: 13px;
    font-weight: 400;
    &:hover {
      cursor: pointer;
      background: #2d68c3;
      color: #ffffff;
      border: none;
    }
  }
  .diabled-operation-btn {
    color: #7f8490;
    &:hover {
      cursor: no-drop;
      color: #7f8490;
      background: transparent;
    }
  }
  .more-items {
    position: absolute;
    left: 90px;
    top: 0;
    color: #ced4e4;
    font-size: 13px;
    font-weight: 400;
    background: #303c56;
    border-radius: 2px;
    box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.5);
    .item-polygon {
      position: absolute;
      left: -13px;
      top: 7px;
    }
    .more-item {
      position: relative;
      padding: 0 10px;
      white-space: nowrap;
      line-height: 32px;
      height: 32px;
      &:hover {
        cursor: pointer;
        background: rgba(255, 255, 255, 0.1);
      }
    }
  }
}
</style>
