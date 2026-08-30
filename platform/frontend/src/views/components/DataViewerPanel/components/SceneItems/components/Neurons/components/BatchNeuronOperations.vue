<template>
  <div
    class="d-flex align-center justify-end"
    style="height: 24px; padding: 0 10px; z-index: 5"
  >
    <div
      id="neuron-batch-operations-trigger"
      class="d-flex align-center button"
      :class="disabledBtnTag"
      style="
        position: relative;
        padding: 6px 14px;
        border-radius: 18px;
        height: 24px;
        margin-right: 10px;
        width: auto;
      "
      @click.self="showMainOperations = !showMainOperations"
    >
      <span
        style="margin-right: 4px; font-size: 13px"
        @click.self="showMainOperations = !showMainOperations"
      >
        Edit
      </span>
      <Arrow
        :fill="arrowFill"
        :style="menuArrowStyle"
        @click.native="showMainOperations = !showMainOperations"
      ></Arrow>

      <div
        id="neuron-batch-operations"
        v-if="showMainOperations"
        class="menu-items d-flex flex-column accent-6"
        :style="{
          right: dataAnalyzingLayout === 'minimize' ? '0' : 'auto',
          left: dataAnalyzingLayout === 'minimize' ? 'auto' : '0'
        }"
      >
        <div
          class="operations-item"
          v-for="(operation, index) in operations"
          :key="index"
          @click="operation.callback ? operation.callback() : ''"
          @mouseenter="
            operation.optionHovered !== undefined
              ? ((operation.optionHovered = true),
                (operation.showSubmenu = true))
              : ''
          "
          @mouseleave="optionMouseLeave(operation)"
        >
          <v-menu
            v-if="operation.name === 'Set color'"
            v-model="setColorVisible"
            offset-x
            :nudge-left="510"
            :close-on-content-click="false"
            content-class="neuron-color-picker-menu"
          >
            <template v-slot:activator="{ on, attrs }">
              <div
                v-bind="attrs"
                v-on="on"
                @click.stop="openBatchColorPicker()"
                style="width: 100%; text-align: left"
              >
                <v-icon size="16" style="margin-right: 10px">
                  {{ operation.icon }}
                </v-icon>
                <span style="font-size: 13px">{{ operation.name }}</span>
              </div>
            </template>

            <v-color-picker
              :value="hexToRgbaObj(colorValue)"
              width="285"
              flat
              dark
              mode="rgba"
              canvas-height="190"
              @input="onColorPickerInput($event)"
            ></v-color-picker>
          </v-menu>

          <v-icon
            v-if="operation.name !== 'Set color'"
            size="16"
            :class="
              operation.icon === '$Copy' || operation.icon === '$MoveTo'
                ? 'explore-icon'
                : ''
            "
            style="margin-right: 10px"
          >
            {{ operation.icon }}
          </v-icon>
          <span v-if="operation.name !== 'Set color'" style="font-size: 13px">
            {{ operation.name }}
          </span>

          <v-icon
            v-if="operation.submenu"
            size="16"
            style="transform: rotateZ(90deg)"
          >
            $Arrow
          </v-icon>
          <div
            v-if="operation.showSubmenu"
            class="operation-submenu accent-6"
            @mouseenter="operation.submenuHovered = true"
            @mouseleave="operation.submenuHovered = false"
          >
            <div
              v-for="(subItem, subIndex) in operation.submenu"
              :key="subIndex"
              style="padding: 10px"
              @click="
                subItem.callback
                  ? (subItem.callback(), (operation.showSubmenu = false))
                  : ''
              "
            >
              {{ subItem.name }}
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- <div
      class="d-flex align-center button"
      :class="disabledBtnTag"
      style="padding: 6px 14px; border-radius: 18px; height: 24px; width: auto"
    >
      Analyze
    </div> -->
    <StructureVisibleDialog
      :showStructureDialog="showStructureDialog"
      :somaVisible.sync="batchStructure.somaVisible"
      :dendriteVisible.sync="batchStructure.dendriteVisible"
      :axonVisible.sync="batchStructure.axonVisible"
      :undefinedVisible.sync="batchStructure.undefinedVisible"
      @close="showStructureDialog = false"
      @apply="batchSetStructureVisible"
    ></StructureVisibleDialog>
    <ColorSchema
      class="color-schema-dialog"
      :show="showColorSchemaDialog"
      @close="showColorSchemaDialog = false"
    ></ColorSchema>
  </div>
</template>

<script>
import { mapState } from "vuex";
import { debounce } from "@/utils/utils";
import StructureVisibleDialog from "./StructureVisibleDialog.vue";
import ColorSchema from "./ColorSchema.vue";
import Arrow from "@/components/icons/Arrow";

export default {
  name: "BatchNeuronOperations",
  components: {
    StructureVisibleDialog,
    ColorSchema,
    Arrow
  },
  data() {
    return {
      operations: [],
      primaryOperations: [
        {
          icon: "$Eye",
          name: "Show",
          callback: this.batchShow
        },
        {
          icon: "$EyeHide",
          name: "Hide",
          callback: this.batchHide
        },
        {
          icon: "$DeleteCross",
          name: "Remove from scene...",
          callback: this.batchDelete
        },
        {
          icon: "$Color",
          name: "Set color",
          callback: null
        },
        {
          icon: "$Structure",
          name: "Set structure",
          callback: () => {
            this.showStructureDialog = true;
          }
        },
        {
          icon: "$MoveTo",
          name: "Move to...",
          callback: () => {
            if (this.selectedNeuron.length) {
              this.$store.commit("neuron/setNeuronListOperation", {
                visible: true,
                tag: "Move"
              });
              this.$store.commit(
                "neuron/setCurrentNeuronData",
                this.selectedNeuron
              );
            }
          }
        },
        {
          icon: "$Copy",
          name: "Copy to...",
          callback: () => {
            if (this.selectedNeuron.length) {
              this.$store.commit("neuron/setNeuronListOperation", {
                visible: true,
                tag: "Copy"
              });
              this.$store.commit(
                "neuron/setCurrentNeuronData",
                this.selectedNeuron
              );
            }
          }
        },
        {
          icon: "$Delete",
          name: "Delete from group...",
          callback: () => {
            this.$store.commit("neuron/setDelDialogVisible", true);
            this.$store.commit(
              "neuron/setCurrentNeuronData",
              this.selectedNeuron
            );
          }
        },
        {
          icon: "mdi-poll",
          name: "Analyze",
          callback: () => {
            this.$store.commit(
              "neuron/setTobeAnalyzedNeurons",
              this.selectedNeuron
            );
          }
        }
        // {
        //   icon: "$Download",
        //   name: "Download as swc file"
        // }
      ],
      showMainOperations: false,
      colorValue: "",
      setColorVisible: false,
      showStructureDialog: false,
      showColorSchemaDialog: false,
      batchStructure: {
        somaVisible: true,
        dendriteVisible: true,
        axonVisible: true,
        undefinedVisible: true
      }
    };
  },

  watch: {
    sceneCurrentGroup: debounce(function() {
      const isAll = this.sceneCurrentGroup?.id == "all";
      const filterArr = ["$MoveTo", "$Delete"];
      this.operations = this.primaryOperations.filter(item => {
        // "all" should not have move or delete
        if (isAll && filterArr.includes(item.icon)) {
          return false;
        }
        return true;
      });
    }, 200)
  },

  computed: {
    ...mapState({
      sceneCurrentGroup: state => state.sceneCurrentGroup,
      settingValues: state => state.settingValues,
      viewedNeurons: state => state.neuron.viewedNeurons,
      dataAnalyzingLayout: state => state.layout.dataAnalyzing,
      batchCurrentColor: state => state.neuron.batchCurrentColor
    }),

    selectedNeuron() {
      return this.viewedNeuronsData.filter(el => el.selected);
    },

    viewedNeuronsData() {
      if (this.sceneCurrentGroup?.id === "all") {
        return this.viewedNeurons;
      }
      return this.viewedNeurons.filter(item =>
        item?.groups?.find(g => g.id === this.sceneCurrentGroup?.id)
      );
    },

    disabledBtnTag() {
      return this.selectedNeuron.length === 0 ? "disabled-button" : "";
    },

    arrowFill() {
      return this.selectedNeuron.length === 0 ? "#7F8490" : "#ffffff";
    },

    menuArrowStyle() {
      if (this.showMainOperations) {
        return { transform: "rotate(0deg)" };
      }

      return {
        transform: "rotate(180deg)"
      };
    }
  },

  mounted() {
    window.addEventListener("click", this.onGlobalClick);
  },

  beforeDestroy() {
    window.removeEventListener("click", this.onGlobalClick);
  },

  methods: {
    onGlobalClick(event) {
      // Color picker popup is teleported to <body> — ignore clicks inside it
      if (event.target?.closest(".neuron-color-picker-menu")) return;

      const clickOutsideTarget = id => {
        const clickedX = event.clientX;
        const clickedY = event.clientY;

        const element = document.getElementById(id);
        if (!element) {
          return true;
        }
        const rect = element.getBoundingClientRect();
        if (
          clickedX < rect.left ||
          clickedY < rect.top ||
          clickedX > rect.right ||
          clickedY > rect.bottom
        ) {
          return true;
        }

        return false;
      };

      if (
        clickOutsideTarget("neuron-batch-operations-trigger") &&
        clickOutsideTarget("neuron-batch-operations")
      ) {
        this.showMainOperations = false;
        this.setColorVisible = false;
      }
    },

    batchHide() {
      const selectedNeurons = this.viewedNeurons.filter(el => el.selected);
      selectedNeurons.forEach(el => {
        el.visible = false;
        window.neuroViz.unload(el.file);
      });

      if (process.env.VUE_APP_SUB_SPECIES === "rbm") {
        selectedNeurons.forEach(item => {
          if (item.dendritic) {
            this.$store.commit("removeHighResDendrites", item.dendritic);
          }
        });
      }
    },

    batchShow() {
      const selectedNeurons = this.viewedNeurons.filter(el => el.selected);
      selectedNeurons.forEach(el => {
        this.settingValues.mode &&
          window.neuroViz.setSWCPartVisibility(
            el.file,
            true,
            true,
            true,
            true,
            true
          );

        el.visible = true;
        window.neuroViz.load(el.file);
      });

      if (process.env.VUE_APP_SUB_SPECIES === "rbm") {
        selectedNeurons.forEach(item => {
          if (item.dendritic) {
            this.$store.commit("addHighResDendrites", item.dendritic);
          }
        });
      }
    },

    hexToRgbaObj(hex) {
      const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})/i.exec(hex || "");
      if (!m) return { r: 255, g: 255, b: 255, a: 1 };
      return {
        r: parseInt(m[1], 16),
        g: parseInt(m[2], 16),
        b: parseInt(m[3], 16),
        a: 1
      };
    },

    openBatchColorPicker() {
      this.colorValue = this.batchCurrentColor || "#ffffff";
      this.setColorVisible = true;
    },

    onColorPickerInput(val) {
      let hex;
      if (val && typeof val === "object") {
        const r = Math.round(val.r || 0);
        const g = Math.round(val.g || 0);
        const b = Math.round(val.b || 0);
        hex =
          "#" +
          r.toString(16).padStart(2, "0") +
          g.toString(16).padStart(2, "0") +
          b.toString(16).padStart(2, "0");
      } else {
        hex = val;
      }
      this.colorValue = hex;
      this.onColorChanged(hex);
    },

    onColorChanged(val) {
      this.$store.commit("neuron/setBatchCurrentColor", val);
      this.$store.commit("neuron/setIsBatchSetColor", true);
    },

    batchDelete() {
      const selectedNeurons = this.viewedNeurons.filter(el => el.selected);
      selectedNeurons.forEach(el => {
        window.neuroViz.unload(el.file);
      });
      this.$store.commit("neuron/setIsBatchSetColor", false);
      this.$store.commit("neuron/setIsRemoveSwc", true);
      this.$store.commit("neuron/removeViewedNeurons", selectedNeurons);
      if (process.env.VUE_APP_SUB_SPECIES === "rbm") {
        selectedNeurons.forEach(item => {
          if (item.dendritic) {
            this.$store.commit("removeHighResDendrites", item.dendritic);
          }
        });
      }
    },

    optionMouseLeave(option) {
      if (option.submenu === undefined) {
        return;
      }
      option.optionHovered = false;

      setTimeout(() => {
        if (option.submenuHovered) {
          option.showSubmenu = true;
          return;
        }

        if (!option.optionHovered) {
          option.showSubmenu = false;
        }
      }, 300);
    },

    batchSetStructureVisible(
      somaVisible,
      dendriteVisible,
      axonVisible,
      undefinedVisible
    ) {
      this.batchStructure.somaVisible = somaVisible;
      this.batchStructure.dendriteVisible = dendriteVisible;
      this.batchStructure.axonVisible = axonVisible;
      this.batchStructure.undefinedVisible = undefinedVisible;

      const selectedNeurons = this.viewedNeurons.filter(el => el.selected);
      selectedNeurons.forEach(el => {
        el.somaVisible = this.batchStructure.somaVisible;
        el.dendriteVisible = this.batchStructure.dendriteVisible;
        el.axonVisible = this.batchStructure.axonVisible;
        el.undefinedVisible = this.batchStructure.undefinedVisible;
        window.neuroViz.setSWCPartVisibility(
          el.file,
          this.batchStructure.somaVisible,
          this.batchStructure.axonVisible,
          this.batchStructure.dendriteVisible,
          this.settingValues.mode,
          this.batchStructure.undefinedVisible
        );
      });
      this.showStructureDialog = false;
    }
  }
};
</script>

<style lang="scss" scoped>
.menu-items {
  position: absolute;
  width: 230px;
  bottom: -10px;
  left: 0;
  transform: translateY(100%);
  z-index: 100;
  border-radius: 2px;
  box-shadow: 0 0 10px 0 rgba(#000000, 0.5);
}

:deep(.menu-items) {
  svg {
    path {
      fill: #ced4e4 !important;
      caret-color: #ced4e4 !important;
      fill-opacity: 1;
    }
  }
}

:deep {
  .explore-icon {
    svg {
      path {
        fill: none !important;
        caret-color: none !important;
        fill-opacity: 1;
      }
    }
  }
}

.operation-submenu {
  position: absolute;
  right: -2px;
  top: 0;
  width: 229px;
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  font-size: 13px;
  border-radius: 2px;
  box-shadow: 0 0 10 0 rgba($color: #000000, $alpha: 0.5);
}

.operations-item {
  display: flex;
  align-items: center;
  padding: 0 10px;
  height: 32px;
  cursor: pointer;
  position: relative;
  color: #ced4e4;
  font-size: 13px;
  &:hover {
    background: rgba(255, 255, 255, 0.1);
  }
}
</style>
