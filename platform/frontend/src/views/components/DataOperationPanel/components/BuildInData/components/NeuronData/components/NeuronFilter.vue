<template>
  <div class="d-flex flex-column neuron-filter">
    <ContentBlock title="Structure" class="block-item">
      <template>
        <div class="d-flex flex-column op-85" style="flex: 1">
          <div class="d-flex align-center" style="margin-bottom: 4px">
            <span class="mr-2 op-85" style="width: 128px"
              >Reconstruction Type
            </span>
            <div class="d-flex align-center" style="flex: 1">
              <v-checkbox
                hide-details
                dense
                :ripple="false"
                color="#7fbefa"
                v-model="axonAndDentrite"
                @change="updateReconstructionChoice('axonAndDentrite')"
              ></v-checkbox>
              <span class="op-85" style="margin-left: 4px">
                Axon and Dendrite
              </span>
            </div>
            <div class="d-flex align-center" style="flex: 1">
              <v-checkbox
                hide-details
                :ripple="false"
                color="#7fbefa"
                v-model="axonOnly"
                @change="updateReconstructionChoice('axonOnly')"
              ></v-checkbox>
              <span class="op-85" style="margin-left: 4px">
                Axon Only
              </span>
            </div>
          </div>
          <!-- <div v-if="visualTarget === 'mouse'" class="d-flex align-center">
            <span class="mr-2 op-85" style="width: 128px"></span>
            <div class="d-flex align-center" style="flex: 1">
              <v-checkbox
                hide-details
                :ripple="false"
                color="#7fbefa"
                v-model="dendriteOnly"
                @change="updateReconstructionChoice('dendriteOnly')"
              ></v-checkbox>
              <span class="op-85" style="margin-left: 4px">Dendrite Only</span>
            </div>
            <div class="d-flex align-center" style="flex: 1">
            </div>
          </div> -->
        </div>
      </template>
    </ContentBlock>

    <ContentBlock title="Anatomical Region" style="z-index: 1" class="block-item">
      <template>
        <RelationFilter ref="relationFilter"></RelationFilter>
      </template>
    </ContentBlock>

    <ContentBlock
      :title="visualTarget === 'mouse' ? 'Mouse Line' : 'Neuron Types'"
      class="block-item"
    >
      <template>
        <LineFilter ref="lineFilter"></LineFilter>
      </template>
    </ContentBlock>

    <ContentBlock title="ID" class="block-item">
      <template>
        <IDFilter ref="idFilter"></IDFilter>
      </template>
    </ContentBlock>
  </div>
</template>

<script>
import RelationFilter from "./components/RelationFilter.vue";
import LineFilter from "./components/LineFilter.vue";
import IDFilter from "./components/IDFilter.vue";
import ContentBlock from "@/components/ContentBlock.vue";
import { mapState } from "vuex";
export default {
  name: "NeuronFilter",
  components: {
    ContentBlock,
    RelationFilter,
    LineFilter,
    IDFilter,
  },
  data() {
    return {
      axonAndDentrite: true,
      axonOnly: true,
      dendriteOnly: true,
      undefinedRecon: true,
      visualTarget: process.env.VUE_APP_TARGET,
    };
  },
  computed: {
    ...mapState({
      functionMap: (state) => state.functionMap,
    }),
  },
  watch: {
    "functionMap.query_neurons_by_structure": {
      handler(newVal) {
        // axon_only and axon_and_dendrite false
        // if(newVal?.axon_only === false && newVal?.axon_and_dendrite === false) {
        //  this.dendriteOnly = newVal?.dendrite_only;
        //   this.$store.commit("neuron/updateFilterCondition", {
        //     key: "dendriteOnly",
        //     value: this.dendriteOnly,
        //   });
        // }
        if (Object.prototype.hasOwnProperty.call(newVal, "axon_only")) {
          this.axonOnly = newVal?.axon_only;
          this.$store.commit("neuron/updateFilterCondition", {
            key: "axonOnly",
            value: this.axonOnly,
          });
        }
        if (Object.prototype.hasOwnProperty.call(newVal, "axon_and_dendrite")) {
          this.axonAndDentrite = newVal?.axon_and_dendrite;
          this.$store.commit("neuron/updateFilterCondition", {
            key: "axonAndDentrite",
            value: this.axonAndDentrite,
          });
        }
        if (Object.prototype.hasOwnProperty.call(newVal, "dendrite_only")) {
          this.dendriteOnly = newVal?.dendrite_only;
          this.$store.commit("neuron/updateFilterCondition", {
            key: "dendriteOnly",
            value: this.dendriteOnly,
          });
        }
        if (Object.prototype.hasOwnProperty.call(newVal, "undefined")) {
          this.undefinedRecon = newVal?.undefined;
          this.$store.commit("neuron/updateFilterCondition", {
            key: "undefinedRecon",
            value: this.undefinedRecon,
          });
        }
      },
    },
  },
  methods: {
    clearCondition() {
      this.axonAndDentrite = true;
      this.axonOnly = true;
      this.dendriteOnly = true;
      this.undefinedRecon = true;
      this.updateReconstructionChoice("axonAndDentrite");
      this.updateReconstructionChoice("axonOnly");
      this.updateReconstructionChoice("dendriteOnly");
      this.updateReconstructionChoice("undefinedRecon");

      this.$refs.relationFilter.clearCondition();
      this.$refs.lineFilter.clearCondition();
      this.$refs.idFilter.clearCondition();
      this.$emit("clearCondition");
    },
    updateReconstructionChoice(target) {
      if (target === "axonAndDentrite") {
        this.$store.commit("neuron/updateFilterCondition", {
          key: target,
          value: this.axonAndDentrite,
        });
      } else if (target === "axonOnly") {
        this.$store.commit("neuron/updateFilterCondition", {
          key: target,
          value: this.axonOnly,
        });
      } else if (target === "dendriteOnly") {
        this.$store.commit("neuron/updateFilterCondition", {
          key: target,
          value: this.dendriteOnly,
        });
      } else if (target === "undefinedRecon") {
        this.$store.commit("neuron/updateFilterCondition", {
          key: target,
          value: this.undefinedRecon,
        });
      }
    },
  },
};
</script>

<style lang="scss" scoped>
* {
  font-size: 13px;
  font-family: Roboto;
}

/* For Chrome and Safari */
.neuron-filter::-webkit-scrollbar {
  width: 4px;
}

/* For Firefox */
.neuron-filter {
  scrollbar-width: 4px;
}

:deep(.v-input--checkbox) {
  margin: 0 !important;
  padding: 0 !important;

  .v-input__control {
    width: 20px !important;
    height: 20px !important;
  }

  .v-input__slot {
    width: 20px !important;
    height: 20px !important;
  }
}

:deep(.v-input--selection-controls__input) {
  margin: 0 !important;

  input {
    width: 20px !important;
    height: 20px !important;
  }
}

:deep(.v-icon) {
  font-size: 20px !important;
}
</style>
