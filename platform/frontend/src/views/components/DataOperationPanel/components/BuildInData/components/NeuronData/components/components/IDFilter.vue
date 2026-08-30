<template>
  <div class="d-flex align-center">
    <ASelect
      style="margin-right: 10px"
      :showOptions="displayTypeOptions"
      @clickOutside="displayTypeOptions = false"
    >
      <template slot="display-part">
        <div
          class="d-flex align-center secondary id-display-container"
          @click="displayTypeOptions = true"
        >
          <span style="flex-grow: 1">{{ targetIDType }}</span>
          <v-icon size="16" style="margin-left: 5px" :style="arrowStyle">
            $ArrowDown
          </v-icon>
        </div>
      </template>
      <template slot="options-part">
        <div
          class="d-flex flex-column accent-6"
          style="width: 116px; font-size: 13px; font-family: Roboto"
        >
          <span
            v-for="(item, index) in IDTypes"
            :key="index"
            style="padding: 10px; cursor: pointer"
            @click="onChooseTargetType(item)"
            >{{ item }}</span
          >
        </div>
      </template>
    </ASelect>

    <ASelect
      style="flex-grow: 1"
      :showOptions="displayIDOptions"
      @clickOutside="displayIDOptions = false"
    >
      <template slot="display-part">
        <div>
          <div
            class="d-flex align-center secondary"
            style="height: 30px; border-radius: 2px"
          >
            <v-icon
              size="16"
              style="margin-left: 10px; margin-right: 5px"
              color="#7F8491"
            >
              $Search
            </v-icon>
            <div style="max-height: 30px; overflow-y: auto;flex-grow: 1;">
              <span
                v-show="enableMultiSelection"
                v-for="(item, index) in selectedItems"
                :key="index"
                class="accent-6"
                style="font-size: 13px; border-radius: 2px; margin-right: 2px; padding: 2px"
              >
                <span v-html="item.name"></span>
                <v-icon size="14" @click="item.selected = false"
                  >$DeleteCross
                </v-icon>
              </span>

              <input
                v-model="idSearch"
                class="id-input primary-text--text"
                :placeholder="selectedItems.length === 0 ? 'Search ID' : ''"
                style="flex-grow: 1"
                :disabled="disableInput"
                @click="displayIDOptions = true"
              />
            </div>

            <v-icon
              v-show="disableInput"
              size="16"
              style="margin-left: 10px; margin-right: 5px"
              color="#7F8491"
              @click="onDeleteChoice"
            >
              $DeleteCross
            </v-icon>
          </div>
        </div>
      </template>

      <template slot="options-part">
        <div
          class="d-flex flex-column accent-6"
          style="width: 116px; font-size: 13px; font-family: Roboto; width: 100%"
        >
          <v-virtual-scroll
            :items="options"
            item-height="24"
            :bench="200 / 24 + 1"
            style="width: 100%"
            max-height="200"
          >
            <template v-slot:default="{ item }">
              <div
                style="display: flex;align-items: center;padding-left: 10px; margin-top: 4px;"
              >
                <v-checkbox
                  v-show="enableMultiSelection"
                  hide-details
                  dense
                  :ripple="false"
                  v-model="item.selected"
                ></v-checkbox>
                <span
                  class="op-85"
                  style="display: flex; cursor: pointer; width: 100%"
                  @click="onChooseID(item)"
                  >{{ item.name }}</span
                >
              </div>
            </template>
          </v-virtual-scroll>
        </div>
      </template>
    </ASelect>
  </div>
</template>

<script>
import ASelect from "@/components/ASelect.vue";
import { mapState } from "vuex";

export default {
  name: "IDFilter",
  components: {
    ASelect
  },
  data() {
    return {
      targetIDType: "Neuron ID",
      IDTypes: ["Neuron ID", "Sample ID"],
      displayTypeOptions: false,
      displayIDOptions: false,
      idSearch: "",
      sampleIDResult: [],
      allSampleIDResult: [],
      neuronIDResult: [],
      allNeuronIDResult: [],
      disableInput: false
    };
  },

  computed: {
    ...mapState({
      neuronData: state => state.neuron.neuronData,
      projects: state => state.projects,
      targetSpecies: state => state.target
    }),
    arrowStyle() {
      if (this.displayTypeOptions) {
        return {
          transform: "rotateZ(180deg)"
        };
      }

      return {};
    },

    options() {
      if (this.targetIDType === "Neuron ID") {
        return this.neuronIDResult;
      }

      return this.sampleIDResult;
    },

    // Whether multi-selection is enabled
    enableMultiSelection() {
      return true; // All types support multi-selection
      // return (
      //   this.targetSpecies === "monkey" || this.$route.path === "/whole-cortex"
      // );
    },

    selectedItems() {
      if (this.targetIDType === "Neuron ID") {
        return this.allNeuronIDResult.filter(item => item.selected);
      }

      return this.allSampleIDResult.filter(item => item.selected);
    }
  },

  watch: {
    selectedItems() {
      if (this.targetIDType === "Neuron ID") {
        this.$store.commit("neuron/updateFilterIDCondition", {
          neuronID: [...this.selectedItems.map(item => item.name)],
          sampleID: []
        });
      } else {
        this.$store.commit("neuron/updateFilterIDCondition", {
          neuronID: [],
          sampleID: [...this.selectedItems.map(item => item.name)]
        });
      }
    },
    idSearch() {
      if (this.idSearch.length <= 1) {
        this.displayIDOptions = false;
        return;
      }

      this.displayIDOptions = true;

      if (this.targetIDType === "Neuron ID") {
        this.searchNeuronID();
      } else {
        this.searchSampleID();
      }
    },

    targetIDType() {
      if (this.disableInput) {
        this.onDeleteChoice();
        return;
      }

      if (this.idSearch.length <= 1) {
        return;
      }

      if (this.targetIDType === "Neuron ID") {
        this.searchNeuronID();
      } else {
        this.searchSampleID();
      }
    }
  },

  methods: {
    clearCondition() {
      this.targetIDType = "Neuron ID";
      this.idSearch = "";
      this.displayTypeOptions = false;
      this.displayIDOptions = false;
      this.disableInput = false;
      this.neuronIDResult = [];
      this.sampleIDResult = [];
      this.allNeuronIDResult = [];
      this.allSampleIDResult = [];
    },

    onChooseTargetType(choice) {
      this.targetIDType = choice;
      this.displayTypeOptions = false;
    },

    onChooseID(choice) {
      if (!this.enableMultiSelection) {
        this.idSearch = choice.name;
        if (this.targetIDType === "Neuron ID") {
          this.allNeuronIDResult.forEach(item => {
            item.selected = item.name === choice.name;
          });
        } else {
          this.allSampleIDResult.forEach(item => {
            item.selected = item.name === choice.name;
          });
        }
      } else {
        choice.selected = !choice.selected;
      }

      if (this.targetIDType === "Neuron ID") {
        this.$store.commit("neuron/updateFilterIDCondition", {
          neuronID: [...this.selectedItems.map(item => item.name)],
          sampleID: []
        });
      } else {
        this.$store.commit("neuron/updateFilterIDCondition", {
          neuronID: [],
          sampleID: [...this.selectedItems.map(item => item.name)]
        });
      }

      if (!this.enableMultiSelection) {
        setTimeout(() => {
          this.displayIDOptions = false;
          this.disableInput = true;
        }, 300);
      }
    },

    onDeleteChoice() {
      this.idSearch = "";
      this.displayIDOptions = false;

      this.$store.commit("neuron/updateFilterIDCondition", {
        neuronID: [],
        sampleID: []
      });

      this.allNeuronIDResult.forEach(item => {
        item.selected = false;
      });

      this.allSampleIDResult.forEach(item => {
        item.selected = false;
      });

      this.disableInput = false;
      this.neuronIDResult = [];
      this.sampleIDResult = [];
    },

    searchSampleID() {
      // Use Set and Map to speed up dedup and insertion
      this.sampleIDResult = [];
      const existingSampleIDs = new Set(
        this.allSampleIDResult.map(item => item.name)
      );
      const newSampleIDs = new Map();

      this.projects.forEach(project => {
        const neuronData = this.neuronData[project.name];
        if (!neuronData) return;
        Object.values(neuronData).forEach(({ file }) => {
          let id =
            this.targetSpecies !== "monkey"
              ? file.split("_")[0]
              : file.split("-")[0];
          if (!existingSampleIDs.has(id) && !newSampleIDs.has(id)) {
            newSampleIDs.set(id, { name: id, selected: false });
          }
        });
      });

      this.allSampleIDResult.push(...Array.from(newSampleIDs.values()));

      this.sampleIDResult = this.allSampleIDResult.filter(item =>
        item.name.includes(this.idSearch)
      );
    },

    searchNeuronID() {
      this.neuronIDResult = [];
      const existingNeuronIDs = new Set(
        this.allNeuronIDResult.map(item => item.name)
      );
      const newNeuronIDs = new Map();

      this.projects.forEach(project => {
        const neuronData = this.neuronData[project.name];
        if (!neuronData) return;
        Object.values(neuronData).forEach(({ file }) => {
          const id = file.split(".")[0];
          if (!existingNeuronIDs.has(id) && !newNeuronIDs.has(id)) {
            newNeuronIDs.set(id, { name: id, selected: false });
          }
        });
      });

      this.allNeuronIDResult.push(...Array.from(newNeuronIDs.values()));
      this.neuronIDResult = this.allNeuronIDResult.filter(item =>
        item.name.includes(this.idSearch)
      );
    }
  }
};
</script>

<style lang="scss" scoped>
* {
  font-size: 13px;
  font-family: Roboto;
}
.id-display-container {
  padding: 5px 10px;
  font-size: 13px;
  cursor: pointer;
  user-select: none;
  width: 116px;
  height: 30px;
  border-radius: 2px;
}

.id-input {
  outline: none;
  height: 16px;
  font-size: 13px;
}

:deep(.v-virtual-scroll__item) {
  height: 24px !important;
}

:deep(.v-input--selection-controls__input) {
  width: 16px !important;
  height: 16px !important;
  margin: 0 !important;
}
:deep(.v-input--checkbox) {
  padding: 0 !important;
  margin: 0 !important;
}

:deep(.v-input__control) {
  padding: 0 !important;
}

:deep(.v-icon.v-icon::after) {
  display: none;
}
</style>
