<template>
  <div class="a-select">
    <div class="select-title" v-show="title.length">
      {{ title }}
      <span class="title-required" v-show="required">*</span>
    </div>
    <v-select
      ref="selectDom"
      v-model="selectValue"
      :disabled="disabled"
      v-bind="$attrs"
      v-on="$listeners"
      clear-icon="$Delete"
    >
      <template
        #[slotName]="slotProps"
        v-for="(slot, slotName) in $scopedSlots"
      >
        <slot :name="slotName" v-bind="slotProps" />
      </template>
    </v-select>
  </div>
</template>
<script>
export default {
  // By default, attribute bindings from the parent scope that are not
  // recognized as props will "fall through" and be applied as plain
  // HTML attributes on the child component's root element.
  // Setting inheritAttrs to false disables this default behavior.
  inheritAttrs: false,
  model: {
    prop: "selected",
    event: "change"
  },
  props: {
    // Expose the visible prop to show/hide the dialog
    selected: {
      type: [String, Number],
      default: undefined
    },
    title: {
      type: String,
      default: ""
    },
    required: {
      type: Boolean,
      default: true
    },
    disabled: {
      type: Boolean,
      default: false
    }
  },
  data: () => ({
    selectValue: ""
  }),
  watch: {
    selected: {
      handler(nv) {
        this.selectValue = this.selected;
        this.$emit("change", nv);
      },
      immediate: true
    }
  }
};
</script>

<style lang="scss" scoped>
.a-select {
  font-size: 13px;

  .select-title {
    color: #2d3341;
    margin-bottom: 5px;
    opacity: 0.87;

    .title-required {
      font-weight: bold;
      color: red;
    }
  }
}

.theme--dark .v-list {
  background: #303c56 !important;
}

:deep {
  .v-icon__component {
    width: 16px;
    height: 16px;
  }

  .v-input {
    color: #343f5c;
  }

  .v-select__slot {
    border: 1px solid currentColor;
    // border-radius: 2px;
    padding-left: 10px;
    font-size: 13px;
    // background: var(--selectDisable) or #f9f9f9;
  }

  .v-text-field__details {
    display: none;
  }

  .v-subheader {
    font-size: 13px;
    height: 32px;
    font-weight: 400;
    color: #86a3e1;
    padding-left: 10px;
    // margin: 2px 0 10px;
    // padding-top: 10px;
  }

  .v-list-item {
    color: #343f5c;
    opacity: 0.87;
    height: 30px;
    min-height: 30px;
    padding: 0 20px;

    .v-list-item__content {
      padding: 0;
    }

    .v-list-item__title {
      font-size: 13px;
      color: #ffffff;
    }
  }

  .v-list-item--link:before {
    // background: transparent;
  }
}

.v-text-field {
  padding-top: 0;
}

.v-list {
  padding: 0;
}
.v-application .info--text {
  color: #343f5c !important;
  caret-color: #343f5c !important;
}
</style>
