<template>
  <div>
    <div class="animation-body">
      <div class="animation-body-main">
        <span class="animation-body-title">Sample Animation</span>
        <div class="animation-body-items">
          <div
            class="animation-body-item"
            v-for="item in sampleAnimations"
            :key="item?.name"
            @click="toDetail(item, 'sample')"
          >
            <div class="item-left d-flex">
              <div style="transform: translateY(2px); padding-right: 10px">
                <animation :size="16" fill="#CED4E4"></animation>
              </div>
              <span>{{ item?.name }}</span>
            </div>
            <div class="item-right d-flex">
              <div
                class="bg-icon"
                v-show="item?.onPlay && !item?.onPause"
                @click.stop="pauseFunc(item)"
              >
                <Pause></Pause>
              </div>
              <div
                class="bg-icon"
                v-show="!item?.onPlay || item?.onPause"
                @click.stop="playFunc(item)"
              >
                <Play></Play>
              </div>
              <div
                class="bg-icon"
                v-show="item?.onPlay"
                @click.stop="stopFunc(item)"
              >
                <Stop></Stop>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="animation-body-main">
        <span class="animation-body-title">Saved Animation</span>
        <div v-if="!userInfo" class="animation-login-tip">
          <span>{{ groupTips }}</span>
        </div>
        <div class="animation-body-items" v-else>
          <div
            class="animation-body-item"
            v-for="item in animations"
            :key="item.id"
            @click="toDetail(item, 'saved')"
          >
            <div class="item-left d-flex">
              <div style="transform: translateY(2px); padding-right: 10px">
                <animation :size="16" fill="#CED4E4"></animation>
              </div>
              <span>{{ item.name }}</span>
            </div>
            <div class="item-right d-flex">
              <!-- Playing && not paused -->
              <div
                class="bg-icon"
                v-show="!item?.onPlay"
                @click.stop="deleteFunc(item)"
              >
                <Delete fill="#7FBEFA"></Delete>
              </div>
              <div
                class="bg-icon"
                v-show="item?.onPlay && !item?.onPause"
                @click.stop="pauseFunc(item)"
              >
                <Pause></Pause>
              </div>
              <!-- Not playing || paused -->
              <div
                class="bg-icon"
                v-show="!item?.onPlay || item?.onPause"
                @click.stop="playFunc(item)"
              >
                <Play></Play>
              </div>
              <!-- Playing -->
              <div
                class="bg-icon"
                v-show="item?.onPlay"
                @click.stop="stopFunc(item)"
              >
                <Stop></Stop>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="animation-line"></div>

    <div
      class="create-animation"
      @click="$emit('toCreate')"
      @mouseenter="createMouseEnter"
      @mouseleave="createMouseLeave"
    >
      <add :fill="addFill"></add>
      <span>Create New</span>
    </div>

    <a-dialog
      :visible.sync="deleteDialogVisible"
      width="320"
      @confirm="confirmDeleteAnimation"
      title="Delete Confirmation"
      cancelbtnText="Cancel"
      surebtnText="Yes,delete!"
      :footerVisible="true"
    >
      <div class="delete-dialog">
        <v-icon>$Alert</v-icon>
        <span
          >Are you sure you want to delete the '{{ operationItem?.name }}'
          animation?</span
        >
      </div>
    </a-dialog>
  </div>
</template>

<script>
import { mapState, mapGetters } from "vuex";
import Add from "@/components/icons/Add";
import Animation from "@/components/icons/Animation";
import Pause from "@/components/icons/Pause";
import Stop from "@/components/icons/Stop";
import Play from "@/components/icons/Play";
import Delete from "@/components/icons/Delete";
import ADialog from "@/components/ADialog";
import { deleteAnimationsFunc } from "@/api/animation";

export default {
  name: "AnimationMenu",

  components: {
    Add,
    ADialog,
    Animation,
    Pause,
    Stop,
    Play,
    Delete
  },

  data() {
    const sampleAnimations = [];
    if (process.env.VUE_APP_TARGET === "mouse") {
      sampleAnimations.push({
        onPlay: false,
        onPause: false,
        id: "6656d1c74a343cfb9270f6f6",
        userID: "6653f4547a1b84f5a203c907",
        name: "Example Animation",
        cameraInterpolations: [
          {
            index: 0,
            start: {
              focal: [6587.835, 3618.2725, 6502.2173],
              position: [-10144.849, 3618.2725, 6502.2173],
              up: [0, -1, 0]
            },
            end: {
              focal: [6587.835, 3847.6426, 5686.8623],
              position: [6290.3564, 3847.6426, 41194.93],
              up: [0, -1, 0]
            },
            duration: 4000
          }
        ],
        cameraRotations: [
          {
            index: 1,
            start: {
              focal: [6587.835, 3848.0095, 5685.558],
              position: [6316.653, 3848.0095, 41250.438],
              up: [0, -1, 0]
            },
            x: 360,
            y: 0,
            z: 0,
            duration: 5000
          }
        ],
        timeCreate: "2024-05-29T06:57:11.347Z",
        timeUpdate: "0001-01-01T00:00:00Z",
        timeDelete: "0001-01-01T00:00:00Z"
      });
    }
    if (process.env.VUE_APP_TARGET === "monkey") {
      sampleAnimations.push({
        id: "67c90203db5f4dea199a0e58",
        userID: "656ee04b41090af33b4da540",
        name: "example Macaque",
        cameraInterpolations: [
          {
            index: 0,
            start: {
              focal: [
                30685.470613449812,
                37545.16201969981,
                23785.436323404312
              ],
              position: [
                30685.470613449856,
                167941.80742672697,
                23785.436323404225
              ],
              up: [-4.4408920985006257e-16, 4.440892098500626e-16, 1]
            },
            end: {
              focal: [
                30685.470613449812,
                37545.16201969981,
                23785.436323404312
              ],
              position: [
                161082.11602047697,
                37545.16201969978,
                23785.43632340434
              ],
              up: [-4.4408920985006257e-16, 4.440892098500626e-16, 1]
            },
            duration: 3000
          }
        ],
        cameraRotations: [
          {
            index: 1,
            start: {
              focal: [
                30685.470613449812,
                37545.16201969981,
                23785.436323404312
              ],
              position: [
                161082.11602047697,
                37545.16201969978,
                23785.43632340434
              ],
              up: [-4.4408920985006257e-16, 4.440892098500626e-16, 1]
            },
            x: 0,
            y: 360,
            z: 0,
            duration: 3000
          }
        ],
        timeCreate: "2025-03-06T02:01:39.984Z",
        timeUpdate: "2025-03-06T02:04:10.748Z",
        timeDelete: "0001-01-01T00:00:00Z"
      });
    }
    return {
      targetTab: "neurons",
      panelPosition: [10, 66],
      addFill: "#7FBEFA",
      operationItem: null,
      currentAnimationResult: null,
      stopStatus: false,
      deleteDialogVisible: false,
      lastPlayingItem: null,
      sampleAnimations
    };
  },

  watch: {
    "functionMap.play_example_animation": {
      handler(newVal) {
        if (newVal?.do_it) this.playFunc(this.sampleAnimations[0]);
      }
    }
  },

  computed: {
    ...mapState({
      theme: state => state.theme,
      target: state => state.target,
      animations: state => state.animations,
      currentAnimation: state => state.currentAnimation,
      functionMap: state => state.functionMap
    }),

    ...mapGetters(["groupTips", "userInfo"]),

    headerStyle() {
      return {
        borderTop:
          "2px solid " +
          this.$vuetify.theme.themes[this.theme]["primary-light"],
        background: this.$vuetify.theme.themes[this.theme]["primary-bar"]
      };
    },

    totalStyle() {
      return {
        background: this.$vuetify.theme.themes[this.theme]["accent-5"] + "80",
        top: this.panelPosition[1] + "px",
        left: this.panelPosition[0] + "px"
      };
    }
  },

  methods: {
    toDetail(item, tag) {
      this.$store.commit("setCurrentAnimation", { ...item });
      this.$emit("setCurrentTab", "detail");
      this.$store.commit("setAnimationStatus", tag);
    },

    createMouseEnter() {
      this.addFill = "#ffffff";
    },

    createMouseLeave() {
      this.addFill = "#7FBEFA";
    },

    deleteFunc(item) {
      this.operationItem = item;
      this.deleteDialogVisible = true;
    },

    pauseFunc(item) {
      item.onPause = true;
      this.currentAnimationResult?.setPause(true);
    },

    async playFunc(item) {
      // If it was paused before
      if (item.onPause) {
        item.onPause = false;
        this.currentAnimationResult?.setPause(false);
        return;
      }
      // If the previous item is still playing
      if (this.lastPlayingItem && this.lastPlayingItem?.id !== item?.id) {
        if (this.lastPlayingItem?.onPlay) {
          // If it's a rotation, restore it first
          this.currentAnimationResult?.stop();
          this.stopStatus = true;
          this.lastPlayingItem.onPlay = false;
        }
        this.lastPlayingItem.onPause = false;
      }
      // Record && set state
      item.onPlay = true;
      item.onPause = false;
      this.stopStatus = false;
      this.lastPlayingItem = item;
      const list = [item?.cameraInterpolations, item?.cameraRotations]
        .flat(1)
        .filter(Boolean)
        .sort((a, b) => a.index - b.index);
      for (let i = 0; i < list.length; i++) {
        const item = list[i];
        if (this.stopStatus) {
          this.stopStatus = false;
          break;
        }
        item?.end
          ? await this.customPlaying(item)
          : await this.rotationPlaying(item);
      }
      item.onPlay = false;
    },

    stopFunc(item) {
      item.onPlay = false;
      item.onPause = false;
      this.stopStatus = true;
      this.currentAnimationResult?.stop();
    },

    async confirmDeleteAnimation() {
      await deleteAnimationsFunc(this.operationItem?.id);
      this.deleteDialogVisible = false;
      this.$store.dispatch("getAnimations");
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
      this.currentAnimationResult = await window.neuroViz.rotateCamera(
        item?.x,
        item?.y,
        item?.z,
        item?.duration
      );
      return this.currentAnimationResult?.animation;
    }
  },

  mounted() {}
};
</script>

<style lang="scss" scoped>
.animation-body {
  // display: flex;
  color: #ced4e4;
  font-size: 13px;
  font-weight: 400;
  .animation-body-title {
    padding-left: 10px;
    color: #f5f8ff;
    font-weight: 500;
  }
  .animation-body-main {
    width: 100%;
    padding: 10px;

    .animation-login-tip {
      height: 32px;
      line-height: 32px;
      padding-left: 10px;
      color: #7f8490;
      font-size: 13px;
    }

    .animation-body-items {
      max-height: 145px;
      overflow-x: hidden;
      overflow-y: auto;
    }
    .animation-body-item {
      display: flex;
      align-items: center;
      justify-content: space-between;

      .item-right {
      }
      .item-left {
        flex-grow: 1;
        padding: 5px 10px;
        cursor: pointer;
        &:hover {
          background: rgba(255, 255, 255, 0.1);
        }
      }
    }
  }

  .bg-icon {
    padding: 10px;
  }
}

.create-animation {
  width: 100%;
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-top: 1px solid #343f5c;

  span {
    color: #7fbefa;
    text-align: center;
    padding-left: 4px;
    font-size: 13px;
  }
  &:hover {
    cursor: pointer;
    background: #2d68c3;
    span {
      color: #ffffff;
    }
  }
}
</style>
