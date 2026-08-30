<template>
  <div>
    <ASelect
      :showOptions="displayOptions"
      @clickOutside="displayOptions = false"
    >
      <template slot="display-part">
        <div
          class="d-flex align-center secondary"
          style="
            height: 30px;
            padding: 10px;
            user-select: none;
            cursor: pointer;
            justify-content: space-between;
          "
          @click="displayOptions = true"
        >
          <span
            v-show="selectedGroup === ''"
            class="accent-7--text"
            style="flex-grow: 1"
          >
            Please select
          </span>
          <div
            v-show="selectedGroup !== ''"
            style="
              border-radius: 2px;
              padding: 2px;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
            "
          >
            <span style="padding: 0 4px">{{ selectedGroup }} </span>
          </div>
          <v-icon size="16" :style="arrowStyle">$ArrowDown</v-icon>
        </div>
      </template>

      <template slot="options-part">
        <div
          class="group-parent-dom accent-6"
          style="width: 116px; width: 100%"
        >
          <div class="group-left">
            <div
              class="group-item"
              v-for="(value, key) in groupValues"
              :key="key"
              :class="radioGroup === value ? 'active-group' : ''"
              @click="radioGroup = value"
            >
              <span>{{ key }}</span>
              <ArrowDown
                :style="groupArrowStyle"
                :fill="radioGroup === value ? '#7FBEFA' : '#7F8491'"
              ></ArrowDown>
            </div>
          </div>
          <div class="group-right">
            <div v-show="radioGroup === 'publicGroup'">
              <PublicGroupFilter
                @close="onChoosePublicGroup"
                @clearOther="clearOtherGroup('publicGroup')"
              ></PublicGroupFilter>
            </div>
            <div v-show="radioGroup === 'temporaryGroup'">
              <TemporaryGroupFilter
                @close="onChooseSelfGroup('temporaryGroup')"
                @clearOther="clearOtherGroup('temporaryGroup')"
              ></TemporaryGroupFilter>
            </div>
            <div v-show="radioGroup === 'customGroup'">
              <CustomGroupFilter
                @close="onChooseSelfGroup('customGroup')"
                @clearOther="clearOtherGroup('customGroup')"
              ></CustomGroupFilter>
            </div>
          </div>
        </div>
      </template>
    </ASelect>
    <div v-show="showSubtypeFilter">
      <SubtypeFilter
        ref="subtypeFilter"
        style="margin-top: 8px"
        @choose="onChooseSubtype"
      ></SubtypeFilter>
      <div
        class="subtypeInfo"
        v-if="currentPublicGroup === 'Mouse Hypothalamus'"
      >
        <v-icon size="16" color="#7FBEFA">$Info</v-icon>
        <span
          style="margin-left: 6px;color: #7FBEFA;text-decoration-line: underline;cursor: pointer;font-size: 13px;"
          @click="showHyLineSubtypeInfo = true"
          >Information of mouse line and type</span
        >
      </div>
    </div>
    <MouseLineSubtypeInfo
      :showHyLineSubtypeInfo="showHyLineSubtypeInfo"
      style="width: 900px;"
      @close="showHyLineSubtypeInfo = false"
    ></MouseLineSubtypeInfo>
  </div>
</template>

<script>
import ArrowDown from "@/components/icons/ArrowDown";
import ASelect from "@/components/ASelect.vue";
import CustomGroupFilter from "./CustomGroupFilter.vue";
import PublicGroupFilter from "./PublicGroupFilter.vue";
import TemporaryGroupFilter from "./TemporaryGroupFilter.vue";
import SubtypeFilter from "./SubtypeFilter.vue";
import MouseLineSubtypeInfo from "./MouseLineSubtypeInfo.vue";
import { mapState } from "vuex";
export default {
  name: "DataGroupFilter",
  components: {
    ASelect,
    PublicGroupFilter,
    TemporaryGroupFilter,
    CustomGroupFilter,
    SubtypeFilter,
    ArrowDown,
    MouseLineSubtypeInfo
  },
  data() {
    return {
      selectedGroup: "",
      displayOptions: false,
      radioGroup: "publicGroup",
      groupValues: {
        "Public Group": "publicGroup",
        "Custom Group": "customGroup",
        "Temporary Group": "temporaryGroup"
      },
      showHyLineSubtypeInfo: false
    };
  },
  computed: {
    ...mapState({
      filterCondition: state => state.neuron.filterCondition,
      groups: state => state.groups,
      temporaryGroups: state => state.temporaryGroups,
      toSceneGroup: state => state.neuron.toSceneGroup,
      currentChooseGroup: state => state.neuron.currentChooseGroup,
      groupsDetailData: state => state.groupsDetailData
    }),

    groupArrowStyle() {
      return {
        transform: "rotateZ(270deg)"
      };
    },

    arrowStyle() {
      if (this.displayOptions) {
        return {
          transform: "rotateZ(180deg)"
        };
      }

      return {};
    },

    currentPublicGroup() {
      return this.filterCondition.publicGroup;
    },

    showSubtypeFilter() {
      return (
        this.radioGroup === "publicGroup" &&
        this.currentPublicGroup &&
        this.currentPublicGroup !== "All public data" &&
        this.currentChooseGroup &&
        this.currentChooseGroup.customTypes.length > 0
      );
    }
  },

  watch: {
    radioGroup: {
      handler() {
        !this.selectedGroup &&
          (this.selectedGroup = this.filterCondition[this.radioGroup]);
      }
    },

    currentChooseGroup: {
      handler() {
        if (this.currentChooseGroup) {
          this.selectedGroup = this.currentChooseGroup?.name?.split("__")[0];
          // The view name must also be updated after a rename
          if (
            this.toSceneGroup?.id === this.currentChooseGroup?.id &&
            this.toSceneGroup?.name !== this.currentChooseGroup?.name
          ) {
            this.toSceneGroup.name = this.currentChooseGroup?.name;
          } else {
            this.$emit("onFilterClearCondition");
          }
        }
      },
      deep: true
    }
  },

  methods: {
    clearCondition() {
      this.selectedGroup = "";
    },

    clearOtherGroup(tag) {
      this.$store.commit("neuron/clearFilterCondition");

      Object.values(this.groupValues)
        .filter(item => item !== tag)
        .forEach(val => {
          this.filterCondition[val] = "";
        });
    },

    onChoosePublicGroup() {
      this.displayOptions = false;
      if (this.selectedGroup !== this.filterCondition.publicGroup) {
        this.$refs.subtypeFilter.reset();
        this.$emit("onFilterClearCondition");
      }
    },

    onChooseSelfGroup(tag) {
      this.displayOptions = false;
      if (this.selectedGroup !== this.filterCondition[tag]) {
        this.$refs.subtypeFilter.reset();
        this.$emit("onFilterClearCondition");
      }
    },

    onChooseSubtype(choice) {
      this.$store.commit("neuron/updateFilterCondition", {
        key: "class",
        value: choice
      });
    }
  }
};
</script>

<style lang="scss">
* {
  font-size: 13px;
  font-family: Roboto;
}

.group-parent-dom {
  display: flex;
  min-height: 276px;
  max-height: 276px;
  border-radius: 2px;
  font-size: 13px;
  background: #303c56;
  box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.5);
  .group-item {
    min-height: 28px;
    max-height: 32px;
    padding: 10px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: #a5abb9;
    &:hover {
      cursor: pointer;
      background-color: rgba(255, 255, 255, 0.1);
    }
  }

  .group-left {
    width: 150px;
    border-right: 1px solid #586075;
  }

  .group-right {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;

    .group-right-item {
      position: relative;
      // line-height: 16px;
      padding: 5px 10px;
      display: flex;
      align-items: center;
      &:hover {
        cursor: pointer;
        background-color: rgba(255, 255, 255, 0.1);
      }
    }
  }

  .active-group {
    color: #7fbefa;
  }

  .group-content-dom {
    font-size: 13px;
    font-weight: 400;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.group-container {
  :deep(.v-input) {
    margin: 4px 0 !important;

    .v-label {
      font-size: 13px !important;
    }

    .v-input--selection-controls__ripple {
      display: none;
    }

    .v-input--selection-controls__input {
      width: 16px !important;
      height: 16px !important;
      margin-right: 4px !important;
    }
  }
}

.subtypeInfo {
  display: flex;
  align-items: center;
  margin-top: 6px;

  path {
    fill: #7fbefa;
  }
}
</style>
