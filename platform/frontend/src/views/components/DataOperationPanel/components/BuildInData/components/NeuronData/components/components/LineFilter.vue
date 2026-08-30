<template>
  <div>
    <ASelect :showOptions="displayOptions" @clickOutside="displayOptions = false">
      <template slot="display-part">
        <div
          class="d-flex align-center secondary"
          style="height: 30px; padding: 10px; user-select: none; cursor: pointer"
          @click="displayOptions = true"
        >
          <span
            v-show="selectedLine.length === 0"
            class="accent-7--text"
            style="flex-grow: 1; font-size: 13px"
          >
            Please select
          </span>
          <div
            v-if="selectedLine.length > 0"
            style="flex-grow: 1"
            class="d-flex align-center"
          >
            <div
              v-for="(mouseLine, index) in selectedLine"
              :key="index"
              class="accent-6"
              style="font-size: 13px; border-radius: 2px; margin-right: 2px; padding: 2px"
            >
              <span v-html="mouseLine"></span>
              <v-icon size="14" @click="onRemoveLine(mouseLine)"
                >$DeleteCross
              </v-icon>
            </div>
          </div>

          <v-icon size="16" :style="arrowStyle">$ArrowDown</v-icon>
        </div>
      </template>

      <template slot="options-part">
        <div>
          <div
            class="d-flex flex-column accent-6"
            style="font-size: 13px; width: 100%; max-height: 300px; overflow: auto"
          >
            <div
              v-for="(line, index) in filteredMouseLines"
              :key="index"
              class="line-item"
            >
              <v-checkbox
                v-model="line.selected"
                hide-details
                dense
                :ripple="false"
                style="margin-right: 10px"
                color="#7fbefa"
                @change="onChooseLine(line)"
              ></v-checkbox>
              <span
                class="op-85 primary-text--text"
                style="margin-left: 10px; cursor: pointer; flex-grow: 1"
                @click="(line.selected = !line.selected), onChooseLine(line)"
                v-html="line.name"
              >
              </span>
            </div>
          </div>
        </div>
      </template>
    </ASelect>
  </div>
</template>

<script>
import ASelect from "@/components/ASelect.vue";
import { mapState } from "vuex";

export default {
  name: "LineFilter",
  components: {
    ASelect,
  },
  data() {
    return {
      selectedLine: [],
      displayOptions: false,
    };
  },

  computed: {
    ...mapState({
      mouseLines: (state) => state.neuron.mouseLines,
      functionMap: (state) => state.functionMap,
      currentChooseGroup: (state) => state.neuron.currentChooseGroup,
    }),
    arrowStyle() {
      if (this.displayOptions) {
        return {
          transform: "rotateZ(180deg)",
        };
      }

      return {};
    },
    // Filter by project; only lines from the current project are shown,
    // unless the selection is "all" or another non-public project
    filteredMouseLines() {
      if (!this.currentChooseGroup || !this.currentChooseGroup.acronym) {
        // Deduplicate by name
        return Array.from(
          new Map(this.mouseLines.map((line) => [line.name, line])).values()
        );
      }

      const acronym = this.currentChooseGroup.acronym;
      const lines = this.mouseLines.filter((line) => line.project === acronym);
      // Deduplicate by name
      return Array.from(new Map(lines.map((line) => [line.name, line])).values());
    },
  },

  watch: {
    selectedLine(val) {
      this.$store.commit("neuron/updateFilterCondition", {
        key: "mouseLine",
        value: [...val],
      });
    },

    "functionMap.set_mouse_line": {
      handler(newVal) {
        if (Object.prototype.hasOwnProperty.call(newVal, "mouse_line")) {
          const cleanedUserInput = newVal.mouse_line
            .replace(/<[^>]*>/g, "")
            .replace(/[^a-zA-Z0-9]/g, "")
            .toLowerCase();
          const cur = this.mouseLines.find(
            (item) =>
              item.name
                .replace(/<[^>]*>/g, "")
                .replace(/[^a-zA-Z0-9]/g, "")
                .toLowerCase() == cleanedUserInput
          );
          if (cur) {
            cur.selected = true;
            this.onChooseLine(cur);
          }
        }
      },
    },

    "functionMap.set_neuron_type": {
      handler(newVal) {
        if (Object.prototype.hasOwnProperty.call(newVal, "neuron_type")) {
          const cleanedUserInput = newVal.neuron_type
            .replace(/<[^>]*>/g, "")
            .replace(/[^a-zA-Z0-9]/g, "")
            .toLowerCase();
          const cur = this.filteredMouseLines.find(
            (item) =>
              item.name
                .replace(/<[^>]*>/g, "")
                .replace(/[^a-zA-Z0-9]/g, "")
                .toLowerCase() == cleanedUserInput
          );
          if (cur) {
            cur.selected = true;
            this.onChooseLine(cur);
          }
        }
      },
    },
  },

  methods: {
    clearCondition() {
      this.selectedLine = [];
      this.mouseLines.forEach((item) => {
        item.selected = false;
      });
    },
    onChooseLine(line) {
      // avoid already selected
      if (line.selected && !this.selectedLine.some((item) => item === line.name)) {
        this.selectedLine.push(line.name);
      } else {
        this.selectedLine = this.selectedLine.filter((item) => item !== line.name);
      }
    },

    onRemoveLine(line) {
      this.mouseLines.forEach((item) => {
        if (item.name === line) {
          item.selected = false;
        }
      });

      this.selectedLine = this.mouseLines
        .filter((item) => item.selected)
        .map((item) => item.name);
    },
  },
};
</script>

<style lang="scss" scoped>
* {
  font-size: 13px;
  font-family: Roboto;
}

.line-item {
  display: flex;
  align-items: center;
  padding: 10px;
  height: 32px;

  &:hover {
    cursor: pointer;
    background-color: rgba(255, 255, 255, 0.1);
  }
}
</style>
