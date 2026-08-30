<template>
  <div class="container-btns">
    <div
      class="btn-item"
      v-for="item in functionValues"
      :key="item.id"
      :class="{
        'active-btn-item': currentFunction?.id === item?.id,
        'disable-btn-item': isLoading
      }"
      @click="chooseFunction(item)"
    >
      {{ item.text }} 
    </div>

    <v-dialog v-model="analyzeNavVisible" max-width="1200px">
      <v-stepper v-model="e1" style="background-color: #262e4a">
        <v-stepper-header style="background-color: #3b4e8e">
          <v-stepper-step :complete="e1 > 1" step="1">
            Analyze of step 1
          </v-stepper-step>

          <v-divider></v-divider>

          <v-stepper-step :complete="e1 > 2" step="2">
            Analyze of step 2
          </v-stepper-step>
        </v-stepper-header>

        <v-stepper-items>
          <v-stepper-content step="1">
            <v-card class="mb-4" color="#262e4a" height="620">
              <img
                style="height: 100%; width: 100%; object-fit: contain"
                src="@/assets/analyze-nav1.jpg"
              />
            </v-card>

            <v-btn
              text
              @click="analyzeNavVisible = false"
              class="ml-2"
              style="float: right"
            >
              Cancel
            </v-btn>
            <v-btn color="#2d68c3" @click="e1 = 2" style="float: right">
              Next
            </v-btn>
          </v-stepper-content>

          <v-stepper-content step="2">
            <v-card class="mb-4" color="#262e4a" height="620">
              <img
                style="height: 100%; width: 100%; object-fit: contain"
                src="@/assets/analyze-nav2.jpg"
              />
            </v-card>

            <v-btn
              text
              @click="analyzeNavVisible = false"
              class="ml-2"
              style="float: right"
            >
              Cancel
            </v-btn>
            <v-btn color="#2d68c3" @click="e1 = 1" style="float: right">
              Last
            </v-btn>
          </v-stepper-content>
        </v-stepper-items>
      </v-stepper>
    </v-dialog>
  </div>
</template>
<script>
import { mapState } from "vuex";

export default {
  props: {
    currentFunction: {
      type: Object,
      default: () => {}
    },
    functionValues: {
      type: Array,
      default: () => []
    }
  },
  data: () => ({
    analyzeNavVisible: false,
    e1: 1
  }),

  computed: {
    ...mapState({
      isLoading: state => state.session.isLoading
    })
  },

  methods: {
    chooseFunction(item) {
      if (this.isLoading) return;

      if (item?.text === "Analyzing") {
        this.analyzeNavVisible = true;
        this.e1 = 1;
        return;
      }

      if (item?.type === "summarization") {
        // Trigger NeuronData's onAnalyze
        this.$store.commit("setFunctionMap", {
          name: "analyze_neurons",
          args: Date.now()
        });
      }

      // if (item?.type === "summarization") {
      //   this.$store.commit("setToolTipType", "warning");
      //   this.$store.commit(
      //     "setToolTipMessage",
      //     "This function is only supported for analyzing results page triggers"
      //   );
      //   this.$store.commit("setToolTipVisible", true);
      //   return;
      // }
      this.$emit("setCurrentFunction", item);
    }
  }
};
</script>
<style scoped lang="scss">
.container-btns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, auto));
  justify-content: left;
  margin: 20px 0;
  gap: 10px;
  .btn-item {
    display: flex;
    height: 24px;
    padding: 6px;
    font-size: 14px;
    align-items: center;
    gap: 10px;
    border-radius: 4px;
    border: 1px solid #586b9c;
    transition: all 0.3s;
    &:hover {
      cursor: pointer;
      opacity: 0.7;
    }
  }

  .active-btn-item {
    background-color: #2d68c3;
  }

  .disable-btn-item {
    pointer-events: none;
    opacity: 0.4;
  }
}
</style>
