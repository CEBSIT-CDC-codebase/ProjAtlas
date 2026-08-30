<template>
  <div
    class="d-flex flex-row accent-9"
    style="width: 300px; padding: 14px; border-radius: 4px; backdrop-filter: blur(5px)"
  >
    <div class="d-flex flex-column" style="flex-grow: 1">
      <div
        class="d-flex align-center primary-text--text"
        style="justify-content: space-between; margin-bottom: 11px; font-size: 13px"
      >
        <span>Processing: {{ loadedCount }}/{{ totalLoadingCount }}</span>
        <span> {{ progress }}% </span>
      </div>

      <div class="d-flex align-center">
        <div
          style="
            flex-grow: 1;
            height: 6px;
            display: flex;
            align-items: center;
            background: #ffffff33;
            height: 100%;
            border-radius: 3px; ;
          "
        >
          <div
            :style="{ width: progress + '%' }"
            style="
              background: linear-gradient(to right, #20f2ff, #0066ff);
              height: 100%;
              border-radius: 3px;
              height: 6px;
            "
          ></div>
        </div>
      </div>
    </div>

    <div
      class="d-flex align-center"
      style="
        padding: 6px 14px;
        flex-basis: 84px;
        border-radius: 4px;
        width: 84px;
        border: 2px solid #343f5c;
        margin-left: 8px;
        cursor: pointer;
      "
      @click="onStop"
    >
      <div
        style="width: 16px; height: 16px; background: #7fbefa; margin-right: 4px"
      ></div>
      <span style="font-size: 13px; color: #7fbefa"> Stop </span>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
import { stopTasks } from "@/utils/neuronLoader.js";

export default {
  name: "LoadProgress",
  data() {
    return {
      gradientColor: "linear-gradient(to #20F2FF, #0066FF)",
      progress: 0
    };
  },
  computed: {
    ...mapState({
      loadedCount: state => state.loadedCount,
      totalLoadingCount: state => state.totalLoadingCount
    })
  },

  watch: {
    loadedCount() {
      if (this.totalLoadingCount === 0) {
        this.progress = 0;
        return;
      }

      const v = ((this.loadedCount * 1.0) / this.totalLoadingCount) * 100;
      this.progress = Math.round(v * 10) / 10; // round to 1 decimal place
    }
  },

  methods: {
    onStop() {
      stopTasks();
      this.$store.commit("resetLoadingState");
    }
  }
};
</script>

<style scoped lang="scss">
.v-progress-linear__bar {
  background: inherit !important;
}

.gradient-progress .v-progress-linear__bar {
  background: linear-gradient(to right, #20f2ff, #0066ff) !important;
}
</style>
