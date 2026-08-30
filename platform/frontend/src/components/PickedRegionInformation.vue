<template>
  <div class="region-infor-main">
    <span>Region: {{ regionItem ? regionItem.name : "" }}</span>
    <span>x: {{ worldPosition[0].toFixed(1) }}</span>
    <span>y: {{ worldPosition[1].toFixed(1) }}</span>
    <span>z: {{ worldPosition[2].toFixed(1) }}</span>
  </div>
</template>

<script>
import { mapState } from "vuex";

export default {
  name: "PickedRegionInformation",

  computed: {
    ...mapState({
      worldPosition: state => state.PickedInformation.pickedRegionWorldPosition,
      regionItem: state => state.PickedInformation.regionItem
    })
  }
};
</script>

<style scoped>
.region-infor-main {
  padding: 20px 20px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 25px;
  color: black;
  display: flex;
  flex-direction: column;
}
</style>
