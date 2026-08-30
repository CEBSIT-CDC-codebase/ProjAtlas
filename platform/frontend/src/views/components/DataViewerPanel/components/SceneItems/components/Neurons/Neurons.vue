<template>
  <div>
    <div
      v-if="viewedNeurons.length === 0"
      class="d-flex align-center"
      style="padding: 20px 10px;"
    >
      <v-icon size="16" style="margin-right: 10px;">$LightBulb</v-icon>
      <span>Use the fliter on the left side to add some neurons.</span>
    </div>
    <div v-show="viewedNeurons.length > 0">
      <NeuronGroup></NeuronGroup>
      <BatchNeuronOperations></BatchNeuronOperations>
      <NeuronList></NeuronList>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";

import NeuronGroup from "./components/NeuronGroup.vue";
import NeuronList from "./components/NeuronList.vue";
import BatchNeuronOperations from "./components/BatchNeuronOperations.vue";

export default {
  name: "Neurons",
  components: {
    NeuronList,
    NeuronGroup,
    BatchNeuronOperations
  },
  computed: {
    ...mapState({
      viewedNeurons: state => state.neuron.viewedNeurons
    })
  }
};
</script>

<style lang="scss" scoped></style>
