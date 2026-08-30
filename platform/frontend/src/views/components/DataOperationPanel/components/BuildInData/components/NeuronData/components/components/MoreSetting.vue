<template>
  <div class="main" :style="{ paddingBottom: expandOptions ? '' : '0' }">
    <div class="content" :style="{ border: expandOptions ? '' : 'none' }">
      <div
        class="options"
        v-if="expandOptions"
        :style="{ padding: expandOptions ? '' : '0' }"
      >
        <div class="type-selection" v-if="hasPathway">
          <div
            class="current-selection"
            @click="showTypeOptions = !showTypeOptions"
            :id="currentTypeID"
          >
            <span class="current-span">{{ currentSelection }}</span>
            <v-icon
              size="14"
              :style="{
                transform: showTypeOptions ? 'rotate(180deg)' : 'rotate(0deg)'
              }"
              >$ArrowDown</v-icon
            >

            <div
              class="type-options"
              :id="typeOptionsID"
              v-if="showTypeOptions"
              @click.stop="onChooseType('Projection Mode')"
            >
              <div class="type-option-item">
                <span
                  :style="{
                    color:
                      currentSelection === 'Projection Mode' ? '#7FBEFA' : ''
                  }"
                  >Projection Mode</span
                >
                <v-icon
                  size="16"
                  v-show="currentSelection === 'Projection Mode'"
                  >$Check</v-icon
                >
              </div>
              <div
                class="type-option-item"
                style="margin-top: 10px;"
                @click.stop="onChooseType('Projection Pathway')"
              >
                <span
                  :style="{
                    color:
                      currentSelection === 'Projection Pathway' ? '#7FBEFA' : ''
                  }"
                  >Projection Pathway</span
                >
                <v-icon
                  size="16"
                  v-show="currentSelection === 'Projection Pathway'"
                  >$Check</v-icon
                >
              </div>
            </div>
          </div>
        </div>

        <span v-if="!hasPathway" style="color: #ced4e4;font-size: 12px;"
          >Projection Mode</span
        >
        <div
          class="mode-selection"
          v-if="currentSelection === 'Projection Mode'"
          style="margin-top: 10px;"
        >
          <ASelect
            :showOptions="showModeOptions"
            @clickOutside="showModeOptions = false"
          >
            <template slot="display-part">
              <div
                class="d-flex align-center secondary"
                style="height: 28px; padding: 5px 10px;user-select: none;cursor: pointer;justify-content: space-between;border-radius:2px ;"
                @click="showModeOptions = true"
              >
                <input
                  v-model="mode"
                  class="primary-text--text"
                  placeholder="Select ipsilateral or contralateral"
                  readonly
                  style="flex-grow: 1;cursor: pointer; "
                />
                <v-icon
                  size="16"
                  v-if="mode === ''"
                  :style="{
                    transform: showModeOptions
                      ? 'rotate(180deg)'
                      : 'rotate(0deg)'
                  }"
                  >$ArrowDown</v-icon
                >
                <v-icon
                  size="16"
                  v-if="mode !== ''"
                  @click="(mode = ''), clearParameters(), updateMoreSetting()"
                >
                  $DeleteCross</v-icon
                >
              </div>
            </template>
            <template slot="options-part">
              <div
                class="d-flex flex-column accent-6"
                style="font-size: 12px;width: 100%;padding: 10px;"
              >
                <div
                  class="part-option"
                  :style="{ color: mode === 'ipsilateral' ? '#7FBEFA' : '' }"
                  style="margin-bottom: 8px;"
                  @click="
                    (mode = 'ipsilateral'),
                      (showModeOptions = false),
                      updateMoreSetting()
                  "
                >
                  <span>ipsilateral</span>
                  <v-icon size="16" v-show="mode === 'ipsilateral'"
                    >$Check</v-icon
                  >
                </div>

                <div
                  class="part-option"
                  :style="{ color: mode === 'contralateral' ? '#7FBEFA' : '' }"
                  @click="
                    (mode = 'contralateral'),
                      (showModeOptions = false),
                      updateMoreSetting()
                  "
                >
                  <span>contralateral</span>
                  <v-icon size="16" v-show="mode === 'contralateral'"
                    >$Check</v-icon
                  >
                </div>
              </div>
            </template>
          </ASelect>
        </div>

        <div
          class="pathway-selection"
          v-if="currentSelection === 'Projection Pathway'"
          style="margin-top: 10px;display: flex;align-items: center;"
        >
          <v-icon
            size="16"
            style="margin-right: 4px;cursor: pointer;"
            @click="(pathway = 'All'), updateMoreSetting()"
            >{{ pathway === "All" ? "$RadioOn" : "$RadioOff" }}</v-icon
          >
          <span style="margin-right: 10px;">All</span>

          <v-icon
            size="16"
            style="margin-right: 4px;cursor: pointer;"
            @click="(pathway = 'Caudal'), updateMoreSetting()"
            >{{ pathway === "Caudal" ? "$RadioOn" : "$RadioOff" }}</v-icon
          >
          <span style="margin-right: 10px;">Caudal</span>

          <v-icon
            size="16"
            style="margin-right: 4px;cursor: pointer;"
            @click="(pathway = 'Rostral'), updateMoreSetting()"
            >{{ pathway === "Rostral" ? "$RadioOn" : "$RadioOff" }}</v-icon
          >
          <span>Rostral</span>
        </div>

        <div class="para-header">
          <span>Axon parameters</span>
          <!-- <v-icon size="16" style="margin-left: 4px;cursor: pointer;"
            >$HelpCircle</v-icon
          > -->
        </div>

        <div class="para-item" style="margin-bottom: 5px;">
          <span>Axon terminal points:</span>
          <span>[</span>
          <input
            type="number"
            placeholder="input number"
            v-model="terminalPointsMin"
            @input="updateMoreSetting()"
          />
          <span>,</span>
          <input
            type="number"
            placeholder="input number"
            v-model="terminalPointsMax"
            @input="updateMoreSetting()"
          />
          <span>]</span>
        </div>

        <div class="para-item" style="margin-bottom: 5px;">
          <span>Axon cable length(μm):</span>
          <span>{{ mode !== "" ? "(" : "[" }}</span>
          <input
            type="number"
            placeholder="input number"
            v-model="cableLengthMin"
            @input="updateMoreSetting()"
          />
          <span>,</span>
          <input
            type="number"
            placeholder="input number"
            v-model="cableLengthMax"
            @input="updateMoreSetting()"
          />
          <span>]</span>
        </div>

        <div class="para-item">
          <span>Axon branch points:</span>
          <span>[</span>
          <input
            type="number"
            placeholder="input number"
            v-model="branchPointsMin"
            @input="updateMoreSetting()"
          />
          <span>,</span>
          <input
            type="number"
            placeholder="input number"
            v-model="branchPointsMax"
            @input="updateMoreSetting()"
          />
          <span>]</span>
        </div>
      </div>

      <div
        class="visible-header"
        @click="
          moreSettingDataReady && regiobObject
            ? (expandOptions = !expandOptions)
            : ''
        "
        :style="{
          paddingBottom: expandOptions ? '' : '0',
          opacity: moreSettingDataReady && regiobObject ? 1 : 0.5
        }"
      >
        <span>More setting</span>
        <v-icon
          v-if="moreSettingDataReady"
          size="14"
          color="#7fbefa"
          :style="{
            transform: expandOptions ? 'rotate(180deg)' : 'rotate(0deg)'
          }"
          >$ArrowDown</v-icon
        >
        <div v-if="!moreSettingDataReady" class="loading-ellipsis"></div>
      </div>
    </div>
  </div>
</template>

<script>
import ASelect from "@/components/ASelect.vue";
import { mapState } from "vuex/dist/vuex.common.js";

export default {
  name: "MoreSetting",
  props: {
    regiobObject: {
      type: Object,
      default: () => {
        return undefined;
      }
    }
  },
  components: {
    ASelect
  },
  data() {
    return {
      expandOptions: false,
      currentSelection: "Projection Mode",
      showTypeOptions: false,
      currentTypeID: "currentTypeID_" + (Math.random() * 100000).toFixed(1),
      typeOptionsID: "typeOptionsID_" + (Math.random() * 100000).toFixed(1),
      pathway: "All",
      mode: "",
      showModeOptions: false,
      terminalPointsMin: null,
      terminalPointsMax: null,
      cableLengthMin: null,
      cableLengthMax: null,
      branchPointsMin: null,
      branchPointsMax: null
    };
  },

  computed: {
    ...mapState({
      moreSettingDataReady: state => state.moreSettingDataReady
    }),

    hasPathway() {
      if (this.regiobObject) {
        return this.regiobObject.pathway;
      }
      return false;
    }
  },

  watch: {
    hasPathway() {
      if (!this.hasPathway) {
        this.currentSelection = "Projection Mode";
      }
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
      const clickOutsideTarget = id => {
        const clickedX = event.clientX;
        const clickedY = event.clientY;

        const element = document.getElementById(id);
        if (!element) {
          return;
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
        clickOutsideTarget(this.currentTypeID) &&
        clickOutsideTarget(this.typeOptionsID)
      ) {
        this.showTypeOptions = false;
      }
    },

    onChooseType(type) {
      this.currentSelection = type;
      this.showTypeOptions = false;

      this.terminalPointsMin = null;
      this.terminalPointsMax = null;
      this.cableLengthMin = null;
      this.cableLengthMax = null;
      this.branchPointsMin = null;
      this.branchPointsMax = null;

      this.updateMoreSetting();
    },

    clearParameters() {
      this.terminalPointsMin = null;
      this.terminalPointsMax = null;
      this.cableLengthMin = null;
      this.cableLengthMax = null;
      this.branchPointsMin = null;
      this.branchPointsMax = null;
      this.mode = "";
      this.pathway = "All";
      this.updateMoreSetting();
    },

    hideMoreSetting() {
      this.expandOptions = false;
    },

    updateMoreSetting() {
      this.$emit("changeMoreSetting", {
        projectionTarget: this.currentSelection,
        projectionMode: this.mode,
        projectionPathway: this.pathway.toLocaleLowerCase(),
        terminalPointsMin: this.terminalPointsMin,
        terminalPointsMax: this.terminalPointsMax,
        cableLengthMin: this.cableLengthMin,
        cableLengthMax: this.cableLengthMax,
        branchPointsMin: this.branchPointsMin,
        branchPointsMax: this.branchPointsMax
      });
    }
  }
};
</script>

<style lang="scss" scoped>
.main {
  display: flex;
  flex-direction: column;
  background: #1f283e;
  margin-left: 29px;
  padding: 0 10px 10px 10px;
  margin-right: 14px;
}

.content {
  border: 1px solid #343f5c;
  display: flex;
  flex-direction: column;
}

.options {
  display: flex;
  flex-direction: column;
  padding: 10px 10px;
}

.visible-header {
  align-self: flex-end;
  width: 100px;
  display: flex;
  align-items: center;
  height: 16px;
  padding: 10px 0;
  justify-content: flex-end;
  margin-bottom: 10px;
  cursor: pointer;

  span {
    color: #7fbefa;
    margin-right: 5px;
    font-size: 12px;
  }

  :deep(.v-icon) {
    margin-right: 0;
    path {
      fill: #7fbefa;
    }
  }
}

.type--selection {
  display: flex;
}

.current-span {
  color: #ffc42c;
  font-size: 12px;
  margin-right: 4px;
}

.current-selection {
  cursor: pointer;
  position: relative;
  width: 130px;

  :deep(.v-icon) {
    path {
      fill: #ffc42c;
    }
  }
}

.type-options {
  position: absolute;
  top: 20px;
  left: 0;
  width: 150px;
  height: 60px;
  z-index: 100;
  background: #303c56;
  display: flex;
  flex-direction: column;
  padding: 10px;

  .type-option-item {
    display: flex;
    align-items: center;
    justify-content: space-between;

    span {
      font-size: 12px;
    }

    :deep(.v-icon) {
      path {
        fill: #7fbefa;
      }
    }
  }
}

.para-header {
  display: flex;
  align-items: center;
  margin-top: 10px;
  margin-bottom: 4px;

  span {
    font-size: 12;
    color: #a5abb9;
  }

  :deep(.v-icon) {
    path {
      stroke: #a5abb9;
    }
  }
}

.para-item {
  height: 32px;
  align-items: center;
  display: grid;
  grid-template-columns: 145px 3px 80px 3px 80px auto;
  grid-column-gap: 3px;
  font-size: 14px;
  color: #ced4e4;

  input {
    height: 32px;
    border-radius: 2px;
    background: #0b101c;
    padding: 0 2px;
    color: #ced4e4;
  }

  input::placeholder {
    font-size: 12px;
  }
}

.part-option {
  cursor: pointer;
  font-size: 12px;
  color: #ced4e4;
  height: 16px;
  display: flex;
  align-items: center;

  span {
    margin-right: 8px;
  }
}

.loading-ellipsis {
  position: relative;
  width: 14px;
  color: #7fbefa;
}

.loading-ellipsis::after {
  content: ".";
  animation: ellipsis 1.5s infinite;
}

@keyframes ellipsis {
  0% {
    content: "";
  }
  20% {
    content: ".";
  }
  40% {
    content: "..";
  }

  80% {
    content: "...";
  }
  100% {
    content: "";
  }
}
</style>
