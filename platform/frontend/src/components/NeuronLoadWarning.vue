<template>
  <ADialog
    width="320"
    persistent
    :title="title"
    :visible="showDialog"
    @update:visible="onVisible"
  >
    <template>
      <div class="d-flex flex-column" style="padding: 14px;">
        <div
          class="primary-text--text"
          style="margin-bottom: 10px;font-size: 13px;font-weight: 400;"
        >
          {{ total }} neurons ara selected to display. It will take some time.
          Are you sure you want to proceed?
        </div>
        <div class="select-group">
          <v-radio-group v-model="selectedOption" dense hide-details row>
            <div
              class="d-flex align-center primary-text--text"
              style="margin-bottom: 6px;font-size: 13px;font-weight: 400;"
            >
              <v-radio color="#7fbefa" label="" value="all"></v-radio>
              <span>All {{ total }} neurons</span>
            </div>
            <div class="d-flex align-center" style="margin-bottom: 10px;">
              <v-radio color="#7fbefa" label="" value="random"></v-radio>
              <div
                style="flex-grow: 1;font-size: 13px;font-weight: 400;"
                class="primary-text--text"
              >
                <span style="width: 90px;flex-basis: 90px;flex-shrink: 0;"
                  >Randomly add</span
                >
                <input
                  v-model="randomCount"
                  class="random-input primary-text--text"
                  style="width: 60px;flex-grow: 0;font-size: 13px;font-weight: 400;"
                />
                <span style="width: 54px;flex-basis:54px;flex-shrink: 0;">
                  neurons</span
                >
              </div>
            </div>
          </v-radio-group>
        </div>
        <div class="d-flex" style="justify-content: right;">
          <div class="cancel-button primary-text--text" @click="onCancel">
            Cancel
          </div>
          <div class="confirm-button" @click="onConfirm">Yes</div>
        </div>
      </div>
    </template>
  </ADialog>
</template>

<script>
import ADialog from "@/components/ADialog";

export default {
  name: "NeuronLoadWarning",
  components: {
    ADialog
  },
  props: {
    title: {
      type: String,
      default: ""
    },
    total: {
      type: Number,
      default: 0
    },
    random: {
      type: Number,
      default: 0
    },
    showDialog: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      selectedOption: "random",
      randomCount: 100
    };
  },
  mounted() {
    this.randomCount = this.random;
  },
  methods: {
    onVisible() {
      this.$emit("close");
    },

    onCancel() {
      this.$emit("close");
      this.$emit("cancel");
    },

    onConfirm() {
      const n = parseInt(this.randomCount, 10);
      this.$emit("confirm", {
        selectedOption: this.selectedOption,
        randomCount: Number.isFinite(n) && n > 0 ? n : this.random
      });
      this.$emit("close");
    }
  }
};
</script>

<style scoped lang="scss">
* {
  font-family: Roboto;
}

.random-input {
  padding: 5px 10px;
  border: 1px solid #343f5c;
  border-radius: 2px;
  margin: 0 10px;
  height: 24px;
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

.select-group {
  :deep(.v-input) {
    margin: 4px 0 !important;

    .v-label {
      font-size: 13px !important;
    }

    .v-input--selection-controls__ripple {
      display: none;
    }

    .v-input--selection-controls__input {
      width: 16px !important;
      height: 16px !important;
      margin-right: 4px !important;
    }
  }

  .v-input--radio-group.v-input--radio-group--row .v-radio {
    margin-right: 10px;
  }
}
</style>
