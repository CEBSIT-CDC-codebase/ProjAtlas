<template>
  <ADialog
    :visible="showStructureDialog"
    title="Set Structure"
    width="320"
    persistent
    @update:visible="onVisible"
  >
    <template>
      <div class="d-flex flex-column" style="font-size: 13px;">
        <div class="d-flex align-center" style="height: 32px;margin-top: 4px;">
          <v-checkbox
            dense
            hide-details
            :ripple="false"
            color="#7fbefa"
            v-model="structure.somaVisible"
          ></v-checkbox>
          <span style="margin-left: 5px;">Show soma</span>
        </div>
        <div class="d-flex align-center" style="height: 32px;">
          <v-checkbox
            dense
            hide-details
            :ripple="false"
            color="#7fbefa"
            v-model="structure.dendriteVisible"
          ></v-checkbox>
          <span style="margin-left: 5px;">Show dendrite</span>
        </div>
        <div class="d-flex align-center" style="height:32px;">
          <v-checkbox
            dense
            hide-details
            :ripple="false"
            color="#7fbefa"
            v-model="structure.axonVisible"
          ></v-checkbox>
          <span style="margin-left: 5px;">Show axon</span>
        </div>
        <div
          class="d-flex"
          style="justify-content: right;margin-top: 10px;margin-bottom: 4px;"
        >
          <div class="cancel-button primary-text--text" @click="onCancel">
            Cancel
          </div>
          <div class="confirm-button" @click="onApply">Apply</div>
        </div>
      </div>
    </template>
  </ADialog>
</template>

<script>
import ADialog from "@/components/ADialog";

export default {
  name: "StructureVisibleDialog",
  components: {
    ADialog
  },
  props: {
    somaVisible: {
      type: Boolean,
      default: true
    },
    dendriteVisible: {
      type: Boolean,
      default: true
    },
    axonVisible: {
      type: Boolean,
      default: true
    },
    undefinedVisible: {
      type: Boolean,
      default: true
    },
    showStructureDialog: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      structure: {
        somaVisible: true,
        dendriteVisible: true,
        axonVisible: true
      }
    };
  },
  mounted() {
    this.structure = {
      somaVisible: this.somaVisible,
      dendriteVisible: this.dendriteVisible,
      axonVisible: this.axonVisible,
      undefinedVisible: this.undefinedVisible
    };
  },

  methods: {
    onApply() {
      this.$emit(
        "apply",
        this.structure.somaVisible,
        this.structure.dendriteVisible,
        this.structure.axonVisible,
        this.structure.undefinedVisible
      );
    },
    onCancel() {
      this.$emit("close");
    },

    onVisible() {
      this.$emit("close");
    }
  }
};
</script>

<style scoped lang="scss">
:deep(.v-input--selection-controls__input) {
  width: 16px !important;
  height: 16px !important;
  margin: 0 !important;
}
:deep(.v-input) {
  padding: 0 !important;
  margin: 0 !important;
}

:deep(.v-input__control) {
  padding: 0 !important;
}
:deep(.v-icon.v-icon::after) {
  display: none;
}

.cancel-button {
  padding: 6px 14px;
  border-radius: 21px;
  border: 1px solid #343f5c;
  height: 24px;
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-right: 10px;
}

.confirm-button {
  padding: 6px 14px;
  border-radius: 21px;
  height: 24px;
  display: flex;
  align-items: center;
  cursor: pointer;
}
</style>
