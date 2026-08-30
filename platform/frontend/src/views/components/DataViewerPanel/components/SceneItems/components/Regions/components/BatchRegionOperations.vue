<template>
  <div class="d-flex align-center" style="margin: 16px 10px 6px 0">
    <div style="flex-grow: 1; order: -1"></div>
    <v-menu
      v-model="menuVisible"
      min-width="210"
      :disabled="selectedRegions.length === 0"
    >
      <template v-slot:activator="{ on, attrs }">
        <div
          :class="disabledBtnTag"
          class="d-flex align-center button"
          v-bind="attrs"
          v-on="on"
          style="padding: 6px 14px; width: auto; border-radius: 18px; height: 24px"
        >
          <span style="font-size: 13px">Edit</span>&nbsp;
          <Arrow
            :fill="arrowFill"
            :style="menuArrowStyle"
            style="height: 16px"
          ></Arrow>
        </div>
      </template>

      <v-card class="menu-content" style="margin-top: 30px">
        <v-list class="accent-6" style="padding: 0; border-radius: 0">
          <v-list-item
            v-for="(item, index) in operations"
            :key="index"
            style="cursor: pointer"
            @click="item.callback ? item.callback() : ''"
          >
            <div class="d-flex align-center" v-if="!item.subItems">
              <v-list-item-icon>
                <v-icon size="16">{{ item.icon }}</v-icon>
              </v-list-item-icon>
              <v-list-item-title>{{ item.title }}</v-list-item-title>
            </div>

            <div v-else>
              <v-menu offset-x>
                <template v-slot:activator="{ on, attrs }">
                  <div v-bind="attrs" v-on="on" class="d-flex align-center">
                    <v-list-item-icon>
                      <v-icon size="16">{{ item.icon }}</v-icon>
                    </v-list-item-icon>
                    <v-list-item-title>{{ item.title }}</v-list-item-title>
                    <v-icon
                      size="16"
                      style="transform: rotateZ(90deg); margin-left: 10px"
                    >
                      $Arrow
                    </v-icon>
                  </div>
                </template>

                <v-list class="accent-6">
                  <v-list-item
                    v-for="(subItem, index) in item.subItems"
                    :key="index"
                    @click="subItem.callback ? subItem.callback() : ''"
                  >
                    <v-list-item-title>{{ subItem.title }}</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </div>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
  </div>
</template>

<script>
import Arrow from "@/components/icons/Arrow";
import { mapState } from "vuex";
import { hexToRgb } from "@/utils/utils.js";

export default {
  name: "BatchRegionOperations",
  components: {
    Arrow
  },
  data() {
    return {
      menuVisible: false,
      operations: [
        {
          icon: "$Eye",
          title: "Show",
          callback: this.onShowRegions
        },
        {
          icon: "$EyeHide",
          title: "Hide",
          callback: this.onHideRegions
        },
        // {
        //   icon: "$Color",
        //   title: "Change coloring scheme",
        //   subItems: [
        //     {
        //       title: "Set by random color",
        //       callback: () => this.onChangeColorScheme("random")
        //     },
        //     {
        //       title: "Set by CEBSIT scheme",
        //       callback: () => this.onChangeColorScheme("cebsit")
        //     },
        //     {
        //       title: "Set by Allen theme",
        //       callback: () => this.onChangeColorScheme("allen")
        //     }
        //   ]
        // },
        {
          icon: "$DeleteCross",
          title: "Remove from scene...",
          callback: this.onDeleteRegions
        }
      ]
    };
  },

  computed: {
    ...mapState({
      regionData: state => state.region.regionData,
      viewedRegions: state => state.region.viewedRegions
    }),

    disabledBtnTag() {
      return this.selectedRegions.length === 0 ? "disabled-button" : "";
    },

    selectedRegions() {
      return this.viewedRegions.filter(el => el.operationSelected);
    },

    arrowFill() {
      return this.selectedRegions.length === 0 ? "#7F8490" : "#ffffff";
    },

    buttonStyle() {
      if (this.selectedRegions.length === 0) {
        return {
          background: "#1f283e",
          color: "#7F8490",
          cursor: "unset"
        };
      }

      return {
        background: "#2d68c3",
        color: "#ffffff",
        cursor: "pointer"
      };
    },

    menuArrowStyle() {
      if (this.menuVisible) {
        return { transform: "rotate(0deg)" };
      }

      return {
        transform: "rotate(180deg) "
      };
    }
  },
  methods: {
    onShowRegions() {
      this.selectedRegions.forEach(item => {
        const uid = item.regionObj.uid_array[0];
        const rawObj = this.regionData[parseInt(uid)];

        item.visible = true;
        window.neuroViz.load(rawObj.file);
      });
    },

    onHideRegions() {
      this.selectedRegions.forEach(item => {
        const uid = item.regionObj.uid_array[0];
        const rawObj = this.regionData[parseInt(uid)];

        item.visible = false;
        window.neuroViz.unload(rawObj.file);
      });
    },

    onDeleteRegions() {
      this.selectedRegions.forEach(item => {
        const uid = item.regionObj.uid_array[0];
        const rawObj = this.regionData[parseInt(uid)];

        window.neuroViz.unload(rawObj.file);
        this.$store.commit("region/removeViewedRegion", item);
      });
    },

    onChangeColorScheme(scheme) {
      this.selectedRegions.forEach(item => {
        const hex =
          scheme === "random"
            ? item.randomColor
            : scheme === "cebsit"
            ? item.cebsitColor
            : item.allenColor;
        const rgb = hexToRgb(hex).map(el => el / 255.0);
        window.neuroViz.setColor(item.file, rgb);
        item.colorScheme = scheme;
      });
    }
  }
};
</script>

<style scoped lang="scss">
:deep(.menu-content) {
  svg {
    path {
      fill: #ffffff !important;
      fill-opacity: 1;
    }
  }
}

:deep(.v-list-item) {
  padding: 10px;
  min-height: 32px !important;
  height: 32px !important;
  display: flex;
  align-items: center !important;
}

:deep(.v-list-item__icon) {
  margin: 0 !important;
}
</style>
