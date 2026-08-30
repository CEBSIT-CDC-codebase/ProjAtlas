<template>
  <div class="content-block" :style="blockStyle">
    <span class="block-title primary accent-4--text">{{ title }}</span>
    <slot></slot>
  </div>
</template>

<script>
import { mapState } from "vuex";
export default {
  name: "ContentBlock",
  props: {
    title: {
      type: String,
      default: "title"
    }
  },
  computed: {
    ...mapState({
      theme: state => state.theme
    }),

    blockStyle() {
      return {
        border:
          "1px solid " + this.$vuetify.theme.themes[this.theme]["accent-3"]
      };
    }
  }
};
</script>

<style lang="scss" scoped>
.content-block {
  position: relative;
  .block-title {
    position: absolute;
    top: -10px;
    left: 20px;
    padding: 0 5px;
    height: 16px;
    user-select: none;
  }
}
</style>
