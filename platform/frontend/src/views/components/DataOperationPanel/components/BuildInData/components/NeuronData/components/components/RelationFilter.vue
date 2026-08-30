<template>
  <div>
    <div style="margin-bottom: 10px" v-show="targetSpecies === 'monkey' || isRBM">
      <div class="d-flex align-center op-85">
        <span class="op-85" style="margin-right: 20px; width: 128px">{{
          isRBM ? "Soma EyeSide" : "Soma Hemisphere"
        }}</span>
        <v-checkbox
          hide-details
          dense
          :ripple="false"
          color="#7fbefa"
          v-model="left"
          @change="updateSideChoice"
        ></v-checkbox>
        <span class="op-85" style="margin: 0 10px">Left</span>
        <v-checkbox
          hide-details
          dense
          :ripple="false"
          color="#7fbefa"
          v-model="right"
          @change="updateSideChoice"
        ></v-checkbox>
        <span class="op-85" style="margin: 0 10px; flex-grow: 1">Right</span>
      </div>
    </div>
    <div style="position: relative; z-index: 10">
      <div v-for="(relationItem, index) in filterCondition.relationItems" :key="index">
        <RegionRelationItem
          :ref="getRefID(index)"
          :neuron-part="relationItem.type"
          @delete="onDeleteRelationItem(index)"
          @changeRegion="onUpdateRelationRegion(index, $event)"
          @changePart="onUpdateRelationPart(index, $event)"
          @changeMoreSetting="onUpdateMoreSetting(index, $event)"
        ></RegionRelationItem>
        <RelationLogic
          v-model="relationItem.relation"
          @change="onUpdateRelationItem(index, $event)"
          @create="onCreateRelationItem"
        ></RelationLogic>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex/dist/vuex.common.js";
import RegionRelationItem from "./RegionRelationItem.vue";
import RelationLogic from "./RelationLogic.vue";
export default {
  name: "RelationFilter",
  components: {
    RegionRelationItem,
    RelationLogic,
  },
  data() {
    return {
      left: true,
      right: true,
    };
  },
  computed: {
    ...mapState({
      targetSpecies: (state) => state.target,
      functionMap: (state) => state.functionMap,
    }),
    filterCondition() {
      return this.$store.state.neuron.filterCondition;
    },

    isRBM() {
      return process.env.VUE_APP_SUB_SPECIES === "rbm";
    },
  },

  watch: {
    "functionMap.filter_neurons_by_hemisphere": {
      handler(newVal) {
        this.left = newVal.left;
        this.right = newVal.right;
        this.updateSideChoice();
      },
    },

    // "functionMap.set_soma_location": {
    //   handler(newVal) {
    //     console.log(newVal?.region);
    //   },
    // },
  },

  methods: {
    getRefID(index) {
      return `item_${index}`;
    },

    clearCondition() {
      this.left = true;
      this.right = true;
      this.filterCondition.relationItems.forEach((_, index) => {
        const id = `item_${index}`;
        this.$refs[id][0].onClearRegion();
      });
    },
    updateSideChoice() {
      this.$store.commit("neuron/updateFilterCondition", {
        key: "left",
        value: this.left,
      });
      this.$store.commit("neuron/updateFilterCondition", {
        key: "right",
        value: this.right,
      });
    },
    onUpdateRelationItem(index, relation) {
      this.$store.commit("neuron/updateFilterRelationItem", {
        index,
        key: "relation",
        value: relation,
      });
    },

    onUpdateRelationRegion(index, regionUID) {
      this.$store.commit("neuron/updateFilterRelationItem", {
        index,
        key: "region",
        value: regionUID,
      });
    },

    onUpdateRelationPart(index, part) {
      this.$store.commit("neuron/updateFilterRelationItem", {
        index,
        key: "type",
        value: part,
      });
    },

    onUpdateMoreSetting(index, moreSetting) {
      this.$store.commit("neuron/updateFilterRelationItem", {
        index,
        key: "moreSetting",
        value: moreSetting,
      });
    },

    onCreateRelationItem() {
      this.$store.commit("neuron/addFilterRelationItem");
    },

    onDeleteRelationItem(index) {
      this.$store.commit("neuron/deleteFilterRelationItem", index);
    },
  },
};
</script>

<style lang="scss" scoped>
* {
  font-size: 13px;
  font-family: Roboto;
}
:deep(.v-input--checkbox) {
  margin: 0 !important;
  padding: 0 !important;
}

:deep(.v-input--selection-controls__input) {
  margin: 0 !important;
}

:deep(.v-input__control) {
  width: 16px !important;
  height: 16px !important;
}

:deep(.v-input__slot) {
  width: 16px !important;
  height: 16px !important;
}

:deep(.v-icon) {
  font-size: 16px !important;
}
</style>
