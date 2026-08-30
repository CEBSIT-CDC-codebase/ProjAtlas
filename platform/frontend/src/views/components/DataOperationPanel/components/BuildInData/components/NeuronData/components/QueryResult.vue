<template>
  <div class="main-div" style="padding-left: 10px">
    <div class="d-flex align-center" style="padding: 10px; height: 36px">
      <span class="accent-8--text">Query result:{{ filteredNeurons.length }}</span>
      <span style="padding: 10px; color: #586075">|</span>
      <span class="accent-8--text">Selected:{{ selectedCount }}</span>
    </div>

    <div class="query-header">
      <div class="d-flex align-center" style="height: 28px">
        <v-icon
          size="16"
          style="margin-right: 10px"
          :style="selectAllArrowStyle"
          @click="showFilteredNeurons = !showFilteredNeurons"
          >$ArrowDown</v-icon
        >
        <v-checkbox
          class="all-checkbox"
          hide-details
          dense
          :ripple="false"
          color="#7fbefa"
          :indeterminate="selectAllIndeterminate"
          v-model="selectAll"
          @change="onSelectAllChanged"
        ></v-checkbox>
        <span class="op-85" style="margin-left: 10px">All</span>
      </div>

      <v-virtual-scroll
        v-show="showFilteredNeurons"
        :items="filteredNeurons"
        :max-height="136"
        :item-height="28"
        :bench="136 / 28 + 1"
      >
        <template v-slot:default="{ item }">
          <div class="d-flex align-center" style="margin-left: 36px; height: 28px">
            <v-checkbox
              hide-details
              dense
              :ripple="false"
              color="#7fbefa"
              :input-value="isSelected(item)"
              @change="onToggle(item)"
            ></v-checkbox>
            <span class="op-85" style="margin-left: 10px">{{
              item.file.slice(0, -4)
            }}</span>
          </div>
        </template>
      </v-virtual-scroll>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
import { neuronSelectionKey } from "@/utils/neuronFilterTool";
export default {
  name: "QueryResult",
  data() {
    return {
      selectAll: false,
      showFilteredNeurons: false,
      windowHeight: 900
    };
  },
  computed: {
    ...mapState({
      filteredNeurons: state => state.neuron.filteredNeurons,
      filteredSelected: state => state.neuron.filteredSelected,
      selectionRevision: state => state.neuron.selectionRevision
    }),

    selectAllArrowStyle() {
      if (this.showFilteredNeurons) {
        return {};
      }

      return {
        transform: "rotate(-90deg)"
      };
    },

    selectedCount() {
      void this.selectionRevision;
      return this.filteredSelected?.size || 0;
    },

    selectAllIndeterminate() {
      const n = this.filteredNeurons.length;
      const s = this.selectedCount;
      return s > 0 && s !== n;
    }
  },

  watch: {
    filteredNeurons(newV) {
      if (newV.length === 0) {
        this.selectAll = false;
        this.$emit("hideAll");
        return;
      }

      if (newV.length > 0) {
        this.showFilteredNeurons = true;
        this.$emit("showAll");
      }

      this.selectAll = this.selectedCount === newV.length;
    },

    selectedCount(n) {
      if (n === 0) {
        this.selectAll = false;
      } else if (n === this.filteredNeurons.length) {
        this.selectAll = true;
      }
    },

    showFilteredNeurons() {
      if (this.showFilteredNeurons && this.filteredNeurons.length > 0) {
        this.$emit("showAll");
      } else {
        this.$emit("hideAll");
      }
    }
  },

  mounted() {
    this.windowHeight = window.innerHeight;
  },

  methods: {
    isSelected(item) {
      void this.selectionRevision;
      return this.filteredSelected.has(neuronSelectionKey(item));
    },

    onToggle(item) {
      this.$store.commit(
        "neuron/toggleFilteredSelection",
        neuronSelectionKey(item)
      );
    },

    onSelectAllChanged() {
      this.$store.commit("neuron/setFilteredSelection", this.selectAll);
    }
  }
};
</script>

<style lang="scss" scoped>
* {
  font-size: 13px;
  font-family: Roboto;
}

.main-div {
  border: 1px solid rgba(255, 196, 44, 0.2);
  background: rgba(255, 196, 44, 0.04);
}

:deep(.v-input--selection-controls__input) {
  width: 16px !important;
  height: 16px !important;
  margin: 0 !important;
}

:deep(.v-icon.v-icon::after) {
  display: none;
}

:deep(.v-virtual-scroll__item) {
  height: 28px !important;

  .v-input {
    margin: 0 !important;
    padding: 0 !important;
  }
}

.all-checkbox {
  margin: 0 !important;
  padding: 0 !important;
}
</style>
