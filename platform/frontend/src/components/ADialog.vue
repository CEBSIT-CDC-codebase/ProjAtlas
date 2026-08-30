<template>
  <v-dialog
    v-model="visibleDialog"
    v-bind="$attrs"
    v-on="$listeners"
    persistent
  >
    <div
      class="dialog-header"
      :class="{ 'draggable-header': draggable }"
      @mousedown="onHeaderMouseDown"
    >
      <span>{{ title }}</span>
      <v-icon
        style="cursor: pointer"
        :color="$store.getters.iconThemeColor"
        :size="iconSize"
        v-show="closeIcon"
        @click="$_handleCancel"
        >$Close</v-icon
      >
    </div>
    <v-card elevation="0" class="dialog-card">
      <!--Default slot for content area-->
      <div class="card-main">
        <slot />
      </div>
      <!--Use the dialog's footer slot to add buttons-->

      <div class="card-footer" v-show="footerVisible">
        <template v-if="$slots.footer">
          <slot name="footer" />
        </template>

        <div v-else class="d-flex justify-end">
          <span @click="$_handleCancel" class="dialog-button cancel-button">
            {{ cancelbtnText }}
          </span>
          &nbsp;
          <span @click="$_handleConfirm" class="dialog-button confirm-button">
            {{ surebtnText }}
          </span>
        </div>
      </div>
    </v-card>
  </v-dialog>
</template>
<script>
export default {
  name: "ADialog",
  // By default, attribute bindings from the parent scope that are not
  // recognized as props will "fall through" and be applied as plain
  // HTML attributes on the child component's root element.
  props: {
    // Expose the visible prop to show/hide the dialog
    visible: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: ""
    },
    cancelbtnText: {
      type: String,
      default: "Cancel"
    },
    surebtnText: {
      type: String,
      default: "Save"
    },
    closeIcon: {
      type: Boolean,
      default: true
    },
    iconSize: {
      type: String,
      default: "18"
    },
    footerVisible: {
      type: Boolean,
      default: false
    },
    // Allow dragging the dialog via its header
    draggable: {
      type: Boolean,
      default: false
    }
  },

  components: {},

  data() {
    return {
      dragEl: null,
      dragOffset: { x: 0, y: 0 },
      dragStartX: 0,
      dragStartY: 0
    };
  },

  watch: {
    visible(val) {
      // Reset on close so it re-centers next time it opens
      if (!val) {
        this.dragOffset = { x: 0, y: 0 };
        if (this.dragEl) this.dragEl.style.transform = "";
        this.dragEl = null;
      }
    }
  },

  computed: {
    // Convert .sync via a computed property; external callers can also use visible.sync directly
    visibleDialog: {
      get() {
        return this.visible;
      },
      set(val) {
        this.$emit("update:visible", val);
      }
    }
  },

  methods: {
    // Emit the cancel event
    $_handleCancel() {
      this.$emit("update:visible", false);
    },

    // Emit the confirm event
    $_handleConfirm() {
      this.$emit("confirm");
    },

    onHeaderMouseDown(e) {
      if (!this.draggable) return;
      // Don't trigger dragging when clicking the close icon
      if (["path", "svg", "g"].includes(e.target?.tagName)) return;
      const dialogEl = e.currentTarget.closest(".v-dialog");
      if (!dialogEl) return;
      this.dragEl = dialogEl;
      this.dragStartX = e.clientX - this.dragOffset.x;
      this.dragStartY = e.clientY - this.dragOffset.y;
      document.addEventListener("mousemove", this.onHeaderMouseMove);
      document.addEventListener("mouseup", this.onHeaderMouseUp);
      e.preventDefault();
    },

    onHeaderMouseMove(e) {
      if (!this.dragEl) return;
      this.dragOffset.x = e.clientX - this.dragStartX;
      this.dragOffset.y = e.clientY - this.dragStartY;
      this.dragEl.style.transform = `translate(${this.dragOffset.x}px, ${this.dragOffset.y}px)`;
    },

    onHeaderMouseUp() {
      document.removeEventListener("mousemove", this.onHeaderMouseMove);
      document.removeEventListener("mouseup", this.onHeaderMouseUp);
    }
  }
};
</script>

<style lang="scss" scoped>
.dialog-header {
  border-top: 2px solid #7fbefa;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 28px;
  line-height: 28px;
  padding: 0 10px;
  background: #283652;

  span {
    color: var(--dark-2, #7fbefa);
    font-size: 13px;
    font-weight: 400;
  }

  &.draggable-header {
    cursor: move;
  }
}

.dialog-card {
  // padding: 14px;
  border-radius: 0;
  background: var(--dark-bg, #151c2d);

  .card-footer {
    padding-bottom: 10px;
    margin-right: 10px;
    text-align: right;
  }
}

.card-main {
  padding: 10px;
  :deep {
    .theme--light.v-data-table
      .v-data-table-header
      th.sortable
      .v-data-table-header__icon {
      // @include text-subheader();
    }
  }
}

:deep {
  .v-dialog {
    border-radius: 0;
  }

  .theme--light.v-data-table.v-data-table--fixed-header thead th {
    box-shadow: none;
  }
}
</style>
