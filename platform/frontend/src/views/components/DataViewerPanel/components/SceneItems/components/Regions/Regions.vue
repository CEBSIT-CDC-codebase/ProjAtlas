<template>
  <div>
    <div
      v-if="viewedRegions.length === 0"
      class="d-flex align-center"
      style="padding: 20px 10px;"
    >
      <v-icon size="16" style="margin-right: 10px;">$LightBulb</v-icon>
      <span>Use the filter on the left side to add some brain regions.</span>
    </div>
    <div v-show="viewedRegions.length > 0">
      <BatchRegionOperations></BatchRegionOperations>
      <RegionList></RegionList>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
import RegionList from "./components/RegionList.vue";
import BatchRegionOperations from "./components/BatchRegionOperations.vue";

export default {
  name: "Regions",
  components: {
    RegionList,
    BatchRegionOperations
  },
  computed: {
    ...mapState({
      viewedRegions: state => state.region.viewedRegions
    })
  }
};
</script>

<style lang="scss" scoped></style>
