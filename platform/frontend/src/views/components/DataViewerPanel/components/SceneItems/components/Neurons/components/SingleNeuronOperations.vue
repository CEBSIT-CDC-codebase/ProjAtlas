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
            <v-list-item-icon>
              <v-icon
                size="16"
                :class="
                  item.icon === '$Copy' || item.icon === '$MoveTo'
                    ? 'explore-icon'
                    : ''
                "
                style="transform: translateY(-1px)"
              >
                {{ item.icon }}
              </v-icon>
            </v-list-item-icon>

            <v-list-item-title>{{ item.title }}</v-list-item-title>

            <!-- Submenu -->
            <!-- <v-menu offset-y>
              <template v-slot:activator="{ on, attrs }">
                <v-icon
                  v-bind="attrs"
                  v-on="on"
                  size="24"
                  style="padding: 4px;"
                >
                  $More
                </v-icon>
              </template>

              <v-list>
                <v-list-item
                  v-for="(subItem, index) in item.subItems"
                  :key="index"
                  @click="handleSubItemClick(subItem)"
                >
                  <v-list-item-title>{{ subItem.title }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu> -->
            <!-- End of submenu -->
          </v-list-item>
        </v-list>
      </v-card>
    </v-menu>
    <StructureVisibleDialog
      :showStructureDialog="showStructureDialog"
      :somaVisible.sync="neuronItem.somaVisible"
      :dendriteVisible.sync="neuronItem.dendriteVisible"
      :axonVisible.sync="neuronItem.axonVisible"
      :undefinedVisible.sync="neuronItem.undefinedVisible"
      @close="showStructureDialog = false"
      @apply="setStructureVisible"
    ></StructureVisibleDialog>
  </div>
</template>

<script>
import { mapState } from "vuex";
import StructureVisibleDialog from "./StructureVisibleDialog.vue";
export default {
  name: "SingleNeuronOperations",
  components: {
    StructureVisibleDialog
  },
  props: {
    neuronItem: {
      required: true,
      Type: Object
    }
  },
  data() {
    return {
      menuVisible: false,
      primaryOperations: [
        // {
        //   icon: "$Color",
        //   title: "Change coloring scheme",
        //   subItems: [
        //     { title: "Set by random color" },
        //     { title: "Set by mouse line" },
        //     { title: "Set by soma location area" },
        //     { title: "Set by neuron structure" }
        //   ]
        // },
        {
          icon: "$Structure",
          title: "Set structure",
          callback: () => {
            this.showStructureDialog = true;
          }
        },
        {
          icon: "$MoveTo",
          title: "Move to...",
          callback: () => {
            this.$store.commit("neuron/setNeuronListOperation", {
              visible: true,
              tag: "Move"
            });
            this.$store.commit("neuron/setCurrentNeuronData", this.neuronItem);
          }
        },
        {
          icon: "$Copy",
          title: "Copy to...",
          callback: () => {
            this.$store.commit("neuron/setNeuronListOperation", {
              visible: true,
              tag: "Copy"
            });
            this.$store.commit("neuron/setCurrentNeuronData", this.neuronItem);
          }
        },
        {
          icon: "$Delete",
          title: "Delete from group...",
          callback: () => {
            this.$store.commit("neuron/setDelDialogVisible", true);
            this.$store.commit("neuron/setCurrentNeuronData", this.neuronItem);
          }
        },
        {
          icon: "$Info",
          title: "View infomation",
          callback: () => {
            this.$store.commit("neuron/setCurrentNeuronData", this.neuronItem);
            this.$emit("viewInfo");
          }
        }
      ],
      showStructureDialog: false
    };
  },
  // Your component's computed properties go here
  computed: {
    ...mapState({
      sceneCurrentGroup: state => state.sceneCurrentGroup,
      viewedNeurons: state => state.neuron.viewedNeurons,
      settingValues: state => state.settingValues
    }),

    operations() {
      const isAll = this.sceneCurrentGroup?.id == "all";
      const filterArr = ["$MoveTo", "$Delete"];
      return this.primaryOperations.filter(item => {
        // "all" should not have move or delete
        if (isAll && filterArr.includes(item.icon)) {
          return false;
        }
        return true;
      });
    }
  },
  watch: {
    menuVisible() {
      this.$emit("visibleChanged", this.menuVisible);
    }
  },
  // Your component's lifecycle hooks go here
  mounted() {},
  methods: {
    setStructureVisible(
      somaVisible,
      dendriteVisible,
      axonVisible,
      undefinedVisible
    ) {
      this.neuronItem.somaVisible = somaVisible;
      this.neuronItem.dendriteVisible = dendriteVisible;
      this.neuronItem.axonVisible = axonVisible;
      this.neuronItem.undefinedVisible = undefinedVisible;
      window.neuroViz.setSWCPartVisibility(
        this.neuronItem.file,
        this.neuronItem.somaVisible,
        this.neuronItem.axonVisible,
        this.neuronItem.dendriteVisible,
        this.settingValues.mode,
        this.neuronItem.undefinedVisible
      );

      this.showStructureDialog = false;
    }
  }
};
</script>

<style scoped lang="scss">
:deep(.menu-content) {
  svg {
    path {
      fill: #ced4e4 !important;
      fill-opacity: 1;
    }
  }
}

:deep {
  .explore-icon {
    svg {
      path {
        fill: none !important;
        caret-color: none !important;
        fill-opacity: 1;
      }
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
