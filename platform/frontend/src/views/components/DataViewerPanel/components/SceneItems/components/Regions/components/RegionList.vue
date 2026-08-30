<template>
  <div class="region-list" ref="regionList">
    <div class="d-flex align-center" style="height: 36px; padding: 0 10px">
      <v-checkbox
        hide-details
        dense
        :ripple="false"
        style="margin-right: 10px"
        color="#7fbefa"
        :indeterminate="selectAllIndeterminate"
        v-model="selectAll"
        @change="onSelectAllChanged"
      ></v-checkbox>
      <span style="flex-grow: 1; margin-left: 10px"
        >select {{ selectedRegions.length }} region</span
      >
      <span>{{ selectedRegions.length }}/{{ viewedRegions.length }}</span>
    </div>

    <v-virtual-scroll
      :items="viewedRegions"
      :height="scrollHeight"
      item-height="36"
      :bench="scrollHeight / 32 + 1"
    >
      <template v-slot:default="{ item }">
        <div
          class="d-flex align-center"
          style="height: 36px; padding: 0 10px; position: relative"
          @mouseenter="item.hovered = true"
          @mouseleave="item.hovered = false"
        >
          <div
            v-show="item.hovered || item.menuVisible"
            style="
              position: absolute;
              left: 0;
              top: 0;
              width: 100%;
              height: 100%;
              border: 1px solid #343f5c;
            "
          ></div>

          <v-checkbox
            hide-details
            dense
            :ripple="false"
            color="#7fbefa"
            v-model="item.operationSelected"
          ></v-checkbox>
          <v-icon
            size="24"
            style="margin-left: 10px; padding: 4px"
            @click="onChangeItemVisible(item)"
            >{{ item.visible ? "$Eye" : "$EyeHide" }}
          </v-icon>
          <v-menu
            v-model="item.colorPicker"
            offset-x
            :nudge-left="380"
            :close-on-content-click="false"
          >
            <template v-slot:activator="{ on, attrs }">
              <div
                v-bind="attrs"
                v-on="on"
                style="
                  width: 16px;
                  height: 16px;
                  margin: 10px;
                  border-radius: 2px;
                  cursor: pointer;
                  z-index: 10;
                  flex-basis: 16px;
                  flex-shrink: 0;
                "
                @click.stop="item.colorPicker = true"
                :style="computeRegionColor(item)"
              ></div>
            </template>

            <v-color-picker
              v-model="item.currentColor"
              width="285"
              height="152"
              hide-mode-switch
              mode="rgba"
              @input="onColorPickerChanged(item, $event)"
            ></v-color-picker>
          </v-menu>
          <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
              <span
                class="op-85"
                style="
                  flex: 1;
                  margin-left: 10px;
                  text-overflow: ellipsis;
                  white-space: nowrap;
                  overflow: hidden;
                "
                v-bind="attrs"
                v-on="on"
              >
                {{ item.name }}
              </span>
            </template>
            {{ item.name }}
          </v-tooltip>

          <SingleRegionOperations
            v-show="item.hovered || item.menuVisible"
            :region-item="item"
            @visibleChanged="
              visible => {
                item.menuVisible = visible;
              }
            "
          ></SingleRegionOperations>
          <v-icon
            size="24"
            style="padding: 4px; cursor: pointer"
            @click="onDeleteItem(item)"
          >
            $DeleteCross
          </v-icon>
        </div>
      </template>
    </v-virtual-scroll>

    <div class="resize-handle"></div>
  </div>
</template>

<script>
import { mapState } from "vuex";
import SingleRegionOperations from "./SingleRegionOperations.vue";
import { hexToRgb, debounce } from "@/utils/utils.js";
import interact from "interactjs";

export default {
  name: "RegionList",
  components: {
    SingleRegionOperations
  },
  data() {
    return {
      selectAll: false,
      windowHeight: window.innerHeight,
      scrollHeight: 36, // Initial height
      maxContentHeight: 0, // Added: stores the max content height
      listHeaderHeight: 50
    };
  },
  computed: {
    ...mapState({
      regionData: state => state.region.regionData,
      viewedRegions: state => state.region.viewedRegions,
      regionColorScheme: state => state.region.colorScheme
    }),

    selectedRegions() {
      return this.viewedRegions.filter(el => el.operationSelected);
    },

    selectAllIndeterminate() {
      return (
        this.selectedRegions.length > 0 &&
        this.selectedRegions.length !== this.viewedRegions.length
      );
    },

    maxAllowedHeight() {
      // Compute the max allowed height: the smaller of viewport height and content height
      return Math.min(this.windowHeight - 250, this.maxContentHeight);
    }
  },
  watch: {
    viewedRegions: {
      handler() {
        this.scrollHeight = Math.min(
          this.windowHeight - 250,
          this.viewedRegions.length * 36
        );
        this.updateMaxHeight();
      }
    },

    selectedRegions() {
      if (this.selectedRegions.length == 0) {
        this.selectAll = false;
      }

      if (this.selectedRegions.length == this.viewedRegions.length) {
        this.selectAll = this.viewedRegions.length > 0;
      }
    }
  },
  methods: {
    onSelectAllChanged() {
      this.viewedRegions.forEach(element => {
        element.operationSelected = this.selectAll;
      });
    },

    onChangeItemVisible(item) {
      const uid = item.regionObj.uid_array[0];
      const rawObj = this.regionData[parseInt(uid)];

      item.visible = !item.visible;
      if (item.visible) {
        window.neuroViz.load(rawObj.file);
      } else {
        window.neuroViz.unload(rawObj.file);
      }
    },

    onDeleteItem(item) {
      const uid = item.regionObj.uid_array[0];
      const rawObj = this.regionData[parseInt(uid)];

      window.neuroViz.unload(rawObj.file);
      this.$store.commit("region/removeViewedRegion", item);
    },

    computeRegionColor(item) {
      if (this.regionColorScheme === "random") {
        return { background: item.randomColor };
      } else if (this.regionColorScheme === "cebsit") {
        return { background: item.cebsitColor };
      } else {
        return { background: item.allenColor };
      }
    },
    onColorPickerChanged(item, value) {
      item.currentColor = value;

      const uid = item.regionObj.uid_array[0];
      const rawObj = this.regionData[parseInt(uid)];
      const rgb = hexToRgb(item.currentColor).map(el => el / 255.0);
      window.neuroViz.setColor(rawObj.file, rgb);

      if (this.regionColorScheme === "random") {
        item.randomColor = item.currentColor;
      } else if (this.regionColorScheme === "cebsit") {
        item.cebsitColor = item.currentColor;
      } else {
        item.allenColor = item.currentColor;
      }
    },

    initializeResizable() {
      const element = this.$refs.regionList;

      interact(element).resizable({
        edges: { bottom: true },
        listeners: {
          move: event => {
            let { y } = event.target.dataset;
            y = (parseFloat(y) || 0) + event.deltaRect.height;

            const newHeight = Math.max(85, Math.min(y, this.maxAllowedHeight));
            Object.assign(event.target.dataset, { y });
            this.scrollHeight = newHeight - this.listHeaderHeight; // this.listHeaderHeight is the header's height
          }
        },
        modifiers: [
          interact.modifiers.restrictSize({
            min: { height: 85 },
            max: { height: this.maxAllowedHeight }
          })
        ]
      });
    },

    updateMaxHeight: debounce(function() {
      this.windowHeight = window.innerHeight;
      this.maxContentHeight =
        this.viewedRegions.length * 36 + this.listHeaderHeight; // this.listHeaderHeight is the header's height
      this.scrollHeight = Math.min(
        this.windowHeight - 250,
        this.viewedRegions.length * 36
      );

      this.$nextTick(() => {
        this.initializeResizable();
        // Update the element's actual style
        if (this.$refs.regionList) {
          // this.$refs.regionList.style.height = `${
          //   this.scrollHeight
          // }px`;
          this.$refs.regionList.dataset.y = `${this.scrollHeight +
            this.listHeaderHeight}px`;
        }
      });
    }, 500)
  },
  mounted() {
    this.$nextTick(() => {
      this.updateMaxHeight();
    });
  },
  created() {
    window.addEventListener("resize", this.updateMaxHeight);
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.updateMaxHeight);
  }
};
</script>

<style lang="scss" scoped>
.region-list {
  position: relative;
  min-height: 85px;
  overflow-y: auto; // Changed to auto to show a scrollbar when content overflows
  overflow-x: hidden; // Hide the horizontal scrollbar
}

.resize-handle {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 10px;
  cursor: ns-resize;
  background: rgba(255, 255, 255, 0.1);
}

:deep(.v-input--selection-controls__input) {
  width: 16px !important;
  height: 16px !important;
  margin: 0 !important;
}
:deep {
  .v-input--checkbox.v-input--dense {
    margin-top: 0;
  }
}
:deep(.v-input) {
  padding: 0 !important;
  // margin: 0 !important;
}

:deep(.v-input__control) {
  padding: 0 !important;
}
:deep(.v-icon.v-icon::after) {
  display: none;
}
</style>
