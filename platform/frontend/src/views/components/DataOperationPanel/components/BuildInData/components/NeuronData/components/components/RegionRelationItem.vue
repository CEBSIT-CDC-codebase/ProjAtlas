<template>
  <div>
    <div class="d-flex align-center" style="width: 100%">
      <div
        class="d-flex align-center accent"
        style="padding: 10px 10px; flex-grow: 1; margin-left: 29px"
      >
        <ASelect
          :showOptions="showPartOptions"
          style="width: 68px; height: 32px"
          @clickOutside="showPartOptions = false"
        >
          <template slot="display-part">
            <div
              class="d-flex align-center secondary"
              style="
                height: 28px;
                padding: 8px 5px;
                user-select: none;
                cursor: pointer;
                justify-content: space-between;
                border-radius: 2px;
              "
              @click="showPartOptions = true"
            >
              <span
                class="primary-text--text"
                style="flex-grow: 1; font-size: 13px"
              >
                {{ neuronPart }}
              </span>
              <v-icon size="16" :style="partArrowStyle">$ArrowDown</v-icon>
            </div>
          </template>

          <template slot="options-part">
            <div
              class="d-flex flex-column accent-6"
              style="font-size: 13px; width: 100%"
            >
              <span class="part-option" @click="onChoosePart('Axon')"
                >Axon</span
              >
              <span class="part-option" @click="onChoosePart('Soma')"
                >Soma</span
              >
            </div>
          </template>
        </ASelect>
        <span class="op-85 accent-1--text" style="margin: 0 5px; width: 67px">{{
          neuronPart === "Soma" ? "locates in" : "projects to"
        }}</span>
        <RegionSearch
          ref="regionSearch"
          :neuronPart="neuronPart"
          @changeRegion="onChangeRegion"
        ></RegionSearch>
      </div>
      <div
        class="background d-flex align-center"
        style="width: 14px; height: 14px; border-radius: 7px; cursor: pointer"
        @click="onDelete"
      >
        <v-icon size="14">$Minus</v-icon>
      </div>
    </div>
    <MoreSetting
      ref="moreSetting"
      v-if="enableMoreSetting"
      :regiobObject="regiogObj"
      @changeMoreSetting="onChangeMoreSetting"
    ></MoreSetting>
  </div>
</template>

<script>
import { mapState } from "vuex";
import ASelect from "@/components/ASelect.vue";
import RegionSearch from "./RegionSearch.vue";
import MoreSetting from "./MoreSetting.vue";

export default {
  name: "RegionRelationItem",
  props: {
    neuronPart: {
      type: String,
      default: "Soma",
      event: "changePart"
    }
  },
  components: {
    ASelect,
    RegionSearch,
    MoreSetting
  },
  data() {
    return {
      partOptions: ["Soma", "Axon"],
      showPartOptions: false,
      regiogObj: undefined
    };
  },

  computed: {
    ...mapState({
      regionAxonTreeArray: state => state.region.regionAxonTreeArray,
      regionSomaTreeArray: state => state.region.regionSomaTreeArray,
      visualTarget: state => state.visualTarget,
      regionData: state => state.region.regionData
    }),

    partArrowStyle() {
      return {
        transform: this.showPartOptions ? "rotate(180deg)" : "rotate(0deg)"
      };
    },

    enableMoreSetting() {
      return this.neuronPart === "Axon" && this.visualTarget === "mouse";
    }
  },

  watch: {},

  methods: {
    onChangeRegion(target) {
      if (target && target.length > 0) {
        this.regiogObj = this.regionData[target];
      } else {
        this.regiogObj = undefined;

        if (this.enableMoreSetting) {
          this.$refs.moreSetting.clearParameters();
          this.$refs.moreSetting.hideMoreSetting();
        }
      }

      this.$emit("changeRegion", target);
    },
    onChoosePart(item) {
      this.$emit("changePart", item);
      this.showPartOptions = false;
    },

    onDelete() {
      this.$emit("delete");
    },

    onClearRegion() {
      this.$refs.regionSearch.onClearRegion();

      if (this.enableMoreSetting) {
        this.$refs.moreSetting.hideMoreSetting();
      }
    },

    onChangeMoreSetting(moreSetting) {
      this.$emit("changeMoreSetting", moreSetting);
    }
  }
};
</script>

<style scoped lang="scss">
* {
  font-size: 13px;
  font-family: Roboto;
}

.part-option {
  cursor: pointer;
  padding: 4px 10px;
}

::v-deep .v-icon::after {
  display: none;
}
.part-option:hover {
  background: #3d4a67;
  color: #ffffff;
}

svg {
  path {
    stroke: #ffffff !important;
    fill-opacity: 1;
  }
}

:deep(.v-treeview-node__toggle) {
  width: 32px;
  height: 40px;
}
</style>
