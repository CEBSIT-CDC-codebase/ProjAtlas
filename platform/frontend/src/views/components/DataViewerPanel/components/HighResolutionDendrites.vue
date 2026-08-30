<template>
  <div
    v-show="highResDendritesVisible"
    ref="panel"
    class="high-resolution-dendrites"
    :style="panelStyle"
  >
    <div
      class="high-resolution-dendrites-header atlas-draggable-header"
      :style="headerStyle"
      @mousedown="onDragStart"
    >
      <span class="primary-light--text">High-Reselution Dendrites</span>
      <v-icon size="16" @click.stop="hidePanel">$Close</v-icon>
    </div>
    <div class="high-resolution-dendrites-body" :style="viewerStyle">
      <div
        ref="viewer"
        class="high-resolution-dendrites-canvas"
        style="position: relative;"
      >
        <div v-if="highResDendriticFiles.length > 0" class="orientation-icons">
          <v-icon
            size="32"
            style="cursor: pointer;"
            v-for="orientation in orientations"
            :key="orientation.value"
            @click="onSetCamera(orientation.value)"
            >{{ orientation.icon }}</v-icon
          >
          <v-icon
            size="32"
            style="cursor: pointer;"
            @click="changePlaneVisibility('z0')"
            >$Z0Plane</v-icon
          >
          <v-icon
            size="32"
            style="cursor: pointer;"
            @click="changePlaneVisibility('z50')"
            >$Z50Plane</v-icon
          >
        </div>
      </div>
      <div
        v-if="highResDendriticFiles.length === 0"
        class="high-resolution-dendrites-empty accent-1--text"
      >
        No dendritic files loaded
      </div>
    </div>
    <div class="resize-handle" @mousedown.stop.prevent="onResizeStart"></div>
  </div>
</template>

<script>
import { mapState } from "vuex";
const {
  collectSyncedDendriticFiles,
  createLatestAsyncRunner,
  partitionHighResDendriteColors
} = require("@/utils/highResDendrites");

export default {
  name: "HighResolutionDendrites",

  data() {
    return {
      neuroviz: null,
      initPromise: null,
      loadedFiles: [],
      hasTrackedMainView: false,
      runLatestSync: null,
      panelPosition: {
        left: 10,
        top: 71
      },
      panelSize: {
        width: 240,
        height: 240
      },
      minPanelSize: {
        width: 240,
        height: 240
      },
      headerHeight: 26,
      dragState: null,
      resizeState: null,
      orientations: [
        { icon: "$EyeSideX", value: "horizontal" },
        // { icon: "$EyeSideY", value: "coronal" },
        { icon: "$EyeSideTop", value: "sagittal" }
      ],
      zPlane0: null,
      zPlane0Visible: true,
      zPlane50: null,
      zPlane50Visible: true
    };
  },

  computed: {
    ...mapState({
      theme: state => state.theme,
      target: state => state.target,
      neuroVizReady: state => state.neuroVizReady,
      highResDendritesVisible: state => state.highResDendritesVisible,
      highResDendriticFiles: state => state.highResDendriticFiles,
      highResDendriticColors: state => state.highResDendriticColors,
      viewedNeurons: state => state.neuron.viewedNeurons
    }),

    headerStyle() {
      return {
        borderTop:
          "2px solid " +
          this.$vuetify.theme.themes[this.theme]["primary-light"],
        background: this.$vuetify.theme.themes[this.theme]["primary-bar"]
      };
    },

    panelStyle() {
      return {
        background: this.$vuetify.theme.themes[this.theme]["accent-5"] + "80",
        left: this.panelPosition.left + "px",
        top: this.panelPosition.top + "px",
        width: this.panelSize.width + "px",
        height: this.panelSize.height + "px"
      };
    },

    viewerStyle() {
      return {
        height: this.panelSize.height - this.headerHeight + "px"
      };
    }
  },

  watch: {
    highResDendritesVisible(newVal) {
      if (newVal) {
        this.syncView();
      }
    },

    highResDendriticFiles: {
      handler() {
        if (this.highResDendritesVisible) {
          this.syncView();
        }
      }
    },

    viewedNeurons: {
      handler() {
        if (this.highResDendritesVisible) {
          this.syncView();
        }
      }
    },

    highResDendriticColors: {
      handler() {
        if (
          this.highResDendritesVisible &&
          this.highResDendriticColors.length &&
          this.neuroviz
        ) {
          this.flushPendingColors();
        }
      }
    },

    neuroVizReady(newVal) {
      if (newVal && this.highResDendritesVisible) {
        this.syncView();
      }
    }
  },

  methods: {
    onSetCamera(newVal) {
      if (this.neuroviz) {
        this.neuroviz.setCamera(newVal);
      }
    },
    hidePanel() {
      this.$store.commit("setHighResDendritesVisible", false);
    },

    getViewerBounds() {
      const root = document.getElementById("scene-view");

      return {
        width: root?.clientWidth || window.innerWidth,
        height: root?.clientHeight || window.innerHeight
      };
    },

    clamp(value, min, max) {
      return Math.min(Math.max(value, min), max);
    },

    onDragStart(event) {
      if (["path", "svg", "g"].includes(event.target?.tagName)) return;

      this.dragState = {
        startX: event.clientX,
        startY: event.clientY,
        left: this.panelPosition.left,
        top: this.panelPosition.top
      };

      document.addEventListener("mousemove", this.onDragMove);
      document.addEventListener("mouseup", this.clearPointerState);
    },

    onDragMove(event) {
      if (!this.dragState) return;

      const bounds = this.getViewerBounds();
      const nextLeft =
        this.dragState.left + event.clientX - this.dragState.startX;
      const nextTop =
        this.dragState.top + event.clientY - this.dragState.startY;

      this.panelPosition = {
        left: this.clamp(
          nextLeft,
          0,
          Math.max(0, bounds.width - this.panelSize.width)
        ),
        top: this.clamp(
          nextTop,
          0,
          Math.max(0, bounds.height - this.panelSize.height)
        )
      };
    },

    onResizeStart(event) {
      this.resizeState = {
        startX: event.clientX,
        startY: event.clientY,
        width: this.panelSize.width,
        height: this.panelSize.height
      };

      document.addEventListener("mousemove", this.onResizeMove);
      document.addEventListener("mouseup", this.clearPointerState);
    },

    onResizeMove(event) {
      if (!this.resizeState) return;

      const bounds = this.getViewerBounds();
      const maxWidth = Math.max(
        this.minPanelSize.width,
        bounds.width - this.panelPosition.left
      );
      const maxHeight = Math.max(
        this.minPanelSize.height,
        bounds.height - this.panelPosition.top
      );
      const nextWidth =
        this.resizeState.width + event.clientX - this.resizeState.startX;
      const nextHeight =
        this.resizeState.height + event.clientY - this.resizeState.startY;

      this.panelSize = {
        width: this.clamp(nextWidth, this.minPanelSize.width, maxWidth),
        height: this.clamp(nextHeight, this.minPanelSize.height, maxHeight)
      };

      this.refreshViewerSize();
    },

    clearPointerState() {
      this.dragState = null;
      this.resizeState = null;
      document.removeEventListener("mousemove", this.onDragMove);
      document.removeEventListener("mousemove", this.onResizeMove);
      document.removeEventListener("mouseup", this.clearPointerState);
    },

    refreshViewerSize() {
      this.$nextTick(() => {
        const canvas = this.$refs.viewer?.querySelector("canvas");

        if (canvas) {
          canvas.style.width = "100%";
          canvas.style.height = "100%";
        }

        if (this.neuroviz && typeof this.neuroviz.resize === "function") {
          this.neuroviz.resize();
        } else if (
          this.neuroviz &&
          typeof this.neuroviz.throttledRender === "function"
        ) {
          this.neuroviz.throttledRender();
        }
      });
    },

    ensureView() {
      if (this.neuroviz) {
        return Promise.resolve(this.neuroviz);
      }

      if (this.initPromise) {
        return this.initPromise;
      }

      if (window.NeuroViz === undefined || !this.$refs.viewer) {
        return Promise.resolve(null);
      }

      this.neuroviz = new window.NeuroViz(
        process.env.VUE_APP_NEUROVIZ + "/experiments/lib/",
        process.env.VUE_APP_NEUROVIZ_SRV
      );

      this.initPromise = this.neuroviz
        .init({
          useTHREE: process.env.VUE_APP_NEUROVIZ_USE_THREE === "true",
          background: [17 / 255.0, 17 / 255.0, 17 / 255.0],
          rootContainer: this.$refs.viewer,
          parseUndefined: false
        })
        .then(() => {
          this.neuroviz.setSpecies(
            process.env.VUE_APP_TARGET === "monkey"
              ? "macaque"
              : process.env.VUE_APP_TARGET
          );

          if (process.env.VUE_APP_SUBTYPE === "lc") {
            this.neuroviz.setSomaSize(5);
          } else if (process.env.VUE_APP_TARGET === "monkey") {
            this.neuroviz.setSomaSize(200);
          }

          this.neuroviz.setCamera("sagittal");

          if (typeof this.neuroviz.setCubeAxesVisibility === "function") {
            this.neuroviz.setCubeAxesVisibility(false);
          }

          this.neuroviz.setSomaSizeScale(0.1);

          this.refreshViewerSize();

          return this.neuroviz;
        })
        .catch(error => {
          this.initPromise = null;
          throw error;
        });

      return this.initPromise;
    },

    clearLoadedFiles() {
      if (!this.neuroviz) {
        this.loadedFiles = [];
        return;
      }

      this.loadedFiles.forEach(file => {
        try {
          this.neuroviz.unload(file);
        } catch (error) {
          console.warn(error);
        }
      });

      this.loadedFiles = [];
      this.refreshViewerSize();
    },

    flushPendingColors() {
      if (!this.neuroviz || !this.highResDendriticColors.length) {
        return;
      }

      const { ready } = partitionHighResDendriteColors({
        colors: this.highResDendriticColors,
        loadedFiles: this.loadedFiles
      });

      ready.forEach(item => {
        if (!item?.file || !item?.color) {
          return;
        }

        this.neuroviz.setColor(item.file, item.color);
        this.$store.commit("removeHighResDendritesColor", item);
      });
    },

    getSyncedFiles() {
      const syncResult = collectSyncedDendriticFiles({
        requestedFiles: this.highResDendriticFiles,
        viewedNeurons: this.viewedNeurons,
        hasTrackedMainView: this.hasTrackedMainView
      });

      this.hasTrackedMainView = syncResult.hasTrackedMainView;

      return syncResult.files;
    },

    updatePlanes() {
      if (!this.neuroviz) return;

      if (this.zPlane0) {
        this.neuroviz.unload(this.zPlane0);
      }

      if (this.zPlane0Visible) {
        this.zPlane0 = this.neuroviz.addTransparentPlane("z", 0, {
          color: [1, 1, 1],
          opacity: 0.2,
          padding: 10
        });
      }

      if (this.zPlane50) {
        this.neuroviz.unload(this.zPlane50);
      }

      if (this.zPlane50Visible) {
        this.zPlane50 = this.neuroviz.addTransparentPlane("z", 50, {
          color: [1, 1, 1],
          opacity: 0.2,
          padding: 10
        });
      }
    },

    changePlaneVisibility(plane) {
      if (plane === "z0") {
        this.zPlane0Visible = !this.zPlane0Visible;
      } else if (plane === "z50") {
        this.zPlane50Visible = !this.zPlane50Visible;
      }
      this.updatePlanes();
    },

    async replaceLoadedFiles(files) {
      const previousFiles = this.loadedFiles.filter(
        file => !files.includes(file)
      );
      const nextFiles = files.filter(file => !this.loadedFiles.includes(file));

      previousFiles.forEach(file => {
        try {
          this.neuroviz.unload(file);
        } catch (error) {
          console.warn(error);
        }
      });

      await Promise.all(
        nextFiles.map(file => this.neuroviz.load(file).catch(() => null))
      );
      this.loadedFiles = [...files];
      this.flushPendingColors();
      this.refreshViewerSize();
      this.updatePlanes();
    },

    async syncView() {
      return this.runLatestSync(this.getSyncedFiles());
    },

    async syncFiles(files) {
      const latestFiles = [...files];

      if (!latestFiles.length) {
        this.clearLoadedFiles();
        return;
      }

      const neuroviz = await this.ensureView();
      if (!neuroviz) return;

      await this.replaceLoadedFiles(latestFiles);
    }
  },

  mounted() {
    this.runLatestSync = createLatestAsyncRunner(files =>
      this.syncFiles(files)
    );

    if (this.highResDendritesVisible) {
      this.syncView();
    }
  },

  beforeDestroy() {
    this.clearPointerState();
    this.clearLoadedFiles();
  }
};
</script>

<style lang="scss" scoped>
.high-resolution-dendrites {
  position: absolute;
  z-index: 3;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(15px);
  user-select: none;
  overflow: hidden;
}

.high-resolution-dendrites-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 10px;
  font-size: 13px;
  font-weight: 500;

  :deep(.v-icon) {
    cursor: pointer;
  }
}

.high-resolution-dendrites-body {
  position: relative;
  flex: 1;
  min-height: 0;
}

.high-resolution-dendrites-canvas {
  width: 100%;
  height: 100%;

  :deep(canvas) {
    width: 100% !important;
    height: 100% !important;
    display: block;
  }
}

.high-resolution-dendrites-empty {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 20px;
  background: rgba(0, 0, 0, 0.15);
  pointer-events: none;
}

.resize-handle {
  position: absolute;
  right: 0;
  bottom: 0;
  width: 16px;
  height: 16px;
  cursor: nwse-resize;
  background: linear-gradient(
    135deg,
    transparent 0%,
    transparent 45%,
    rgba(255, 255, 255, 0.45) 45%,
    rgba(255, 255, 255, 0.45) 55%,
    transparent 55%,
    transparent 100%
  );
}

:deep(.v-icon) {
  &::after {
    display: none !important;
  }
}

.orientation-icons {
  position: absolute;
  top: 0;
  left: 0;
  padding: 4px;
  display: flex;
  gap: 8px;
  flex-direction: column;
  z-index: 10;
}
</style>
