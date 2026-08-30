<template>
  <div>
    <v-menu v-model="menuVisible" min-width="210">
      <template v-slot:activator="{ on, attrs }">
        <v-icon v-bind="attrs" v-on="on" size="24" class="bg-icon"
          >$More</v-icon
        >
      </template>

      <v-card class="menu-content" style="margin-top: 20px">
        <v-list class="accent-6" style="padding: 0; border-radius: 0">
          <v-list-item
            v-for="(item, index) in operations"
            :key="index"
            style="cursor: pointer"
            @click="item.callback ? item.callback() : ''"
          >
            <div class="d-flex align-center" v-if="!item.subItems">
              <v-list-item-icon>
                <v-icon size="16">{{ item.icon }}</v-icon>
              </v-list-item-icon>
              <v-list-item-title>{{ item.title }}</v-list-item-title>
            </div>

            <div v-else>
              <v-menu offset-x>
                <template v-slot:activator="{ on, attrs }">
                  <div v-bind="attrs" v-on="on" class="d-flex align-center">
                    <v-list-item-icon>
                      <v-icon size="16">{{ item.icon }}</v-icon>
                    </v-list-item-icon>
                    <v-list-item-title>{{ item.title }}</v-list-item-title>
                    <v-icon
                      size="16"
                      style="transform: rotateZ(90deg); margin-left: 10px"
                    >
                      $Arrow
                    </v-icon>
                  </div>
                </template>

                <v-list class="accent-6">
                  <v-list-item
                    v-for="(subItem, index) in item.subItems"
                    :key="index"
                    @click="subItem.callback ? subItem.callback() : ''"
                  >
                    <v-list-item-title>{{ subItem.title }}</v-list-item-title>
                  </v-list-item>
                </v-list>
              </v-menu>
            </div>
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>

    <NeuronLoadWarning
      title="Add Selected Neurons"
      :showDialog="showLoadWaring"
      :total="somaNeurons.length"
      :random="100"
      @close="showLoadWaring = false"
      @confirm="onApplyNeuronLoadWarning"
    ></NeuronLoadWarning>
  </div>
</template>

<script>
import { hexToRgb } from "@/utils/utils.js";
import { mapState } from "vuex";
import { formatNeuronData } from "@/utils/neuronFilterTool.js";
import NeuronLoadWarning from "@/components/NeuronLoadWarning.vue";
import { loadNeuron } from "@/utils/neuronLoader";

export default {
  name: "SingleRegionOperations",
  props: {
    regionItem: {
      required: true,
      Type: Object
    }
  },
  components: {
    NeuronLoadWarning
  },
  data() {
    return {
      menuVisible: false,
      showLoadWaring: false,
      somaNeurons: [],
      operations: [
        // {
        //   icon: "$Color",
        //   title: "Change coloring scheme",
        //   subItems: [
        //     {
        //       title: "Set by random color",
        //       callback: () => this.onChangeColorScheme("random")
        //     },
        //     {
        //       title: "Set by CEBSIT scheme",
        //       callback: () => this.onChangeColorScheme("cebsit")
        //     },
        //     {
        //       title: "Set by Allen theme",
        //       callback: () => this.onChangeColorScheme("allen")
        //     }
        //   ]
        // },
        {
          icon: "$Add",
          title: "Add neurons in this region...",
          callback: () => {
            this.addSomaNeurons();
          }
        }
      ]
    };
  },
  computed: {
    ...mapState({
      regionNeuronRelation: state => state.neuron.regionNeuronRelation,
      projects: state => state.projects,
      neuronData: state => state.neuron.neuronData,
      neuronTypeColors: state => state.neuron.typeColors
    })
  },
  methods: {
    onChangeColorScheme(scheme) {
      const hex =
        scheme === "random"
          ? this.regionItem.randomColor
          : scheme === "cebsit"
          ? this.regionItem.cebsitColor
          : this.regionItem.allenColor;
      const rgb = hexToRgb(hex).map(el => el / 255.0);
      window.neuroViz.setColor(this.regionItem.file, rgb);
      this.regionItem.colorScheme = scheme;
    },

    onApplyNeuronLoadWarning(payload) {
      this.showLoadWaring = false;
      if (payload.selectedOption === "random") {
        const count = payload.randomCount;
        const randomItems = this.somaNeurons
          .sort(() => Math.random() - 0.5)
          .slice(0, count);
        randomItems.forEach(el => {
          loadNeuron(el, false);
        });
      }
    },

    addSomaNeurons() {
      // find all the neurons which soma is in this region
      const projectNames = this.projects.map(el => el.name);
      this.somaNeurons = [];
      projectNames.forEach(name => {
        const projectData = this.regionNeuronRelation[name];
        if (!projectData) return;
        const relation = projectData[this.regionItem.uid];
        if (!relation) return;
        const neuronsUID = relation.owned_neuron_array;
        const neurons = formatNeuronData(
          neuronsUID,
          name,
          this.neuronData,
          this.neuronTypeColors
        );
        this.somaNeurons.push(...neurons);

        // neurons.forEach(neuron => {
        //   const rgb = hexToRgb(neuron.idColor).map(el => el / 255.0);
        //   window.neuroViz.loadOneWithColor(neuron.file, rgb);
        // });

        // this.$store.commit("neuron/addViewedNeurons", neurons);
      });

      if (this.somaNeurons.length > 500) {
        this.showLoadWaring = true;
      } else {
        this.somaNeurons.forEach(neuron => {
          loadNeuron(neuron, false);
        });
      }
    }
  }
};
</script>

<style scoped lang="scss">
:deep(.menu-content) {
  svg {
    path {
      fill: #ffffff !important;
      fill-opacity: 1;
    }
  }
}

:deep(.v-list-item) {
  padding: 10px;
  min-height: 32px !important;
  height: 32px !important;
  display: flex;
  align-items: center !important;
}

:deep(.v-list-item__icon) {
  margin: 0 !important;
}
</style>
