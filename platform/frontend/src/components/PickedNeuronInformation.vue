<template>
  <div class="neuron-infor-main" v-show="showInformation">
    <div class="top-div">
      <v-icon @click="showInformation = false" small>$DeleteCircle</v-icon>
    </div>
    <div class="information-item">
      <span class="head-span">Neuron: </span>
      <span>{{ neuronItem ? neuronItem.file : "" }}</span>
    </div>

    <div class="information-item">
      <span class="head-span">Soma brain area: </span>
      <span>{{ somaBrain }}</span>
    </div>

    <div class="information-item">
      <span class="head-span"> x: </span>
      <span class="right-span">{{ worldPosition[0].toFixed(1) }}</span>
    </div>

    <div class="information-item">
      <span class="head-span">y:</span>
      <span class="right-span"> {{ worldPosition[1].toFixed(1) }}</span>
    </div>

    <div class="information-item">
      <span class="head-span"> z: </span>
      <span class="right-span"> {{ worldPosition[2].toFixed(1) }}</span>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";

export default {
  name: "PickedNeuronInformation",
  data() {
    return {
      showInformation: true
    };
  },

  computed: {
    ...mapState({
      worldPosition: state => state.PickedInformation.pickedNeuronWorldPosition,
      neuronItem: state => state.PickedInformation.neuronItem,
      neuronRegionRelation: state => state.neuron.neuronRegionRelation,
      regionData: state => state.region.regionData
    }),

    somaBrain() {
      if (!this.neuronItem) {
        return "";
      }

      const projectName = this.neuronItem.projectFullName;
      const relationItem = this.neuronRegionRelation[projectName][
        this.neuronItem.id
      ];
      const ownerRegions = relationItem.owner_region_array || [];
      if (ownerRegions && ownerRegions.length > 0) {
        return this.regionData[ownerRegions[ownerRegions.length - 1]].acronym;
      } else {
        return "";
      }
    }
  },

  watch: {
    worldPosition() {
      this.showInformation = true;
    }
  }
};
</script>

<style scoped>
.neuron-infor-main {
  padding: 4px 4px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 4px;
  color: black;
  display: flex;
  flex-direction: column;
  max-width: 300px;
}

.top-div {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 2px;
  margin-top: 2px;
}
.information-item {
  display: flex;
}

.head-span {
  font-weight: bolder;
}
</style>
