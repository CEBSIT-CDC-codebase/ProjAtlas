<template>
  <div class="d-flex justify-center align-center view-header">
    <v-tooltip top v-for="(item, index) in icons" :key="index">
      <template v-slot:activator="{ on, attrs }">
        <v-icon
          size="32"
          class="pa-1"
          v-bind="attrs"
          v-on="on"
          @click="setViewCamera(item.value)"
        >
          {{ item.icon }}
        </v-icon>
      </template>
      <span>{{ item.tooltip }}</span>
    </v-tooltip>

    <div class="ml-1 mr-1 accent-3" style="width: 1px; height: 20px"></div>

    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-icon
          size="32"
          class="pa-1"
          v-bind="attrs"
          v-on="on"
          @click="visibleFunc('color')"
        >
          $ColorScheme
        </v-icon>
      </template>
      <span>Coloring Scheme</span>
    </v-tooltip>

    <div class="ml-1 mr-1 accent-3" style="width: 1px; height: 20px"></div>

    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-icon
          size="32"
          class="pa-1"
          v-bind="attrs"
          v-on="on"
          @click="visibleFunc('reference')"
        >
          $Reference
        </v-icon>
      </template>
      <span>Reference</span>
    </v-tooltip>

    <div class="ml-1 mr-1 accent-3" style="width: 1px; height: 20px"></div>

    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-icon
          size="32"
          class="pa-1"
          v-bind="attrs"
          v-on="on"
          @click="cameraFunc"
        >
          $Camera
        </v-icon>
      </template>
      <span>Screenshot</span>
    </v-tooltip>

    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-icon
          size="32"
          class="pa-1"
          v-bind="attrs"
          v-on="on"
          @click="visibleFunc('animation')"
        >
          $Animation
        </v-icon>
      </template>
      <span>Animation</span>
    </v-tooltip>

    <div class="ml-1 mr-1 accent-3" style="width: 1px; height: 20px"></div>

    <v-tooltip top>
      <template v-slot:activator="{ on, attrs }">
        <v-icon
          size="32"
          class="pa-1"
          v-bind="attrs"
          v-on="on"
          @click="visibleFunc('setting')"
        >
          $Setting
        </v-icon>
      </template>
      <span>More Setting</span>
    </v-tooltip>

    <div
      v-show="sceneVisible.color"
      style="position: absolute; left: 10px; bottom: -10px; transform: translateY(100%)"
    >
      <ColorScheme @close="sceneVisible.color = false"></ColorScheme>
    </div>

    <div
      v-show="sceneVisible.reference"
      style="position: absolute; left: 10px; bottom: -10px; transform: translateY(100%)"
    >
      <SceneReference
        class="SceneReference"
        @close="sceneVisible.reference = false"
      ></SceneReference>
    </div>
    <div
      v-show="sceneVisible.setting"
      style="position: absolute; left: 10px; bottom: -10px; transform: translateY(100%)"
    >
      <SceneSetting @close="sceneVisible.setting = false"></SceneSetting>
    </div>
    <div
      v-show="sceneVisible.animation"
      style="position: absolute; left: 10px; bottom: -10px; transform: translateY(100%)"
    >
      <SceneAnimation @close="sceneVisible.animation = false"></SceneAnimation>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
import { downloadBase64Img } from "@/utils/utils";
import ColorScheme from "@/components/ColorScheme.vue";
import SceneAnimation from "./SceneAnimation/SceneAnimation.vue";
import SceneSetting from "./SceneSetting/SceneSetting.vue";
import SceneReference from "./SceneReference/SceneReference.vue";
export default {
  name: "ViewHeader",
  components: {
    ColorScheme,
    SceneAnimation,
    SceneReference,
    SceneSetting
  },
  data() {
    return {
      icons: [
        {
          icon: ["mouse", "monkey"].includes(process.env.VUE_APP_TARGET)
            ? "$MBrainHorizental"
            : "$ZBrainHorizental",
          value: "horizontal",
          tooltip: "Horizontal"
        },
        {
          icon: ["mouse", "monkey"].includes(process.env.VUE_APP_TARGET)
            ? "$MBrainSagittal"
            : "$ZBrainSagittal",
          value: "sagittal",
          tooltip: "Sagittal"
        },
        {
          icon: ["mouse", "monkey"].includes(process.env.VUE_APP_TARGET)
            ? "$MBrainCoronal"
            : "$ZBrainCoronal",
          value: "coronal",
          tooltip: "Coronal"
        },
        {
          icon: "$Rotate90Down",
          value: "pitch-90",
          tooltip: "Pitch-90"
        },
        {
          icon: "$Rotate90Up",
          value: "pitch+90",
          tooltip: "Pitch+90"
        },
        {
          icon: "$Rotate90Right",
          value: "yaw+90",
          tooltip: "Yaw+90"
        },
        {
          icon: "$Rotate90Left",
          value: "yaw-90",
          tooltip: "Yaw-90"
        },
        {
          icon: "$Rotate90Clockwise",
          value: "+90",
          tooltip: "Rotate Clockwise"
        },
        {
          icon: "$Rotate90Anticlockwise",
          value: "-90",
          tooltip: "Rotate Anticlockwise"
        },
        {
          icon: "$FlipToRight",
          value: "right",
          tooltip: "Flip from Left to Right"
        },
        {
          icon: "$FlipToLeft",
          value: "left",
          tooltip: "Flip from Right to Left"
        },
        {
          icon: "$Refresh",
          value: null,
          tooltip: "Reset"
        }
      ],
      sceneVisible: {
        color: false,
        reference: false,
        animation: false,
        setting: false
      }
    };
  },

  watch: {
    "functionMap.set_camera": {
      handler(newVal) {
        if (Object.prototype.hasOwnProperty.call(newVal, "camera")) {
          window.neuroViz.setCamera(newVal?.camera);
        }
      }
    },
    "functionMap.set_neuron_mirror_state": {
      handler(newVal) {
        if (Object.prototype.hasOwnProperty.call(newVal, "state")) {
          this.setViewCamera(newVal?.state);
        }
      }
    },
    "functionMap.take_screenshot": {
      handler(newVal) {
        if (Object.prototype.hasOwnProperty.call(newVal, "do_it")) {
          newVal?.do_it && this.cameraFunc();
        }
      }
    }
  },

  computed: {
    ...mapState({
      animationVisible: state => state.animationVisible,
      functionMap: state => state.functionMap,
      settingVisible: state => state.settingVisible,
      viewedNeurons: state => state.neuron.viewedNeurons
    })
  },

  methods: {
    setViewCamera(value) {
      if (value !== null) {
        if (value === "fullScreen") {
          window.neuroViz.toggleFullScreen();
        } else if (value === "reference") {
          this.showReference = true;
        } else if (value === "left" || value === "right") {
          this.viewedNeurons.forEach(element => {
            window.neuroViz.mirrorSWCToSide(element.file, value);
          });
        } else {
          window.neuroViz.setCamera(value);
        }
      } else {
        window.neuroViz.setCamera();

        // reset mirror
        this.viewedNeurons.forEach(element => {
          window.neuroViz.resetSWCMirror(element.file);
        });
      }
    },

    visibleFunc(tag) {
      for (const key in this.sceneVisible) {
        this.sceneVisible[key] = false;
      }
      this.sceneVisible[tag] = true;

      if (tag === "animation") {
        this.$store.commit("layout/setDataAnalyzing", "minimize");
      }
    },

    async cameraFunc() {
      const val = await window.neuroViz.captureImage();
      downloadBase64Img(val);
    }
  }
};
</script>

<style lang="scss" scoped>
.view-header {
  background: rgba(74, 96, 150, 0.3);
  backdrop-filter: blur(10px);
  height: 32px;
  z-index: 1;
  position: relative;
}

.v-icon {
  &:hover {
    background-color: rgba(74, 96, 150, 0.3);
  }
}

.v-icon::after {
  display: none;
}

.reference {
  position: absolute;
  left: 10px;
  bottom: -10px;
  transform: translateY(100%);
}
</style>
