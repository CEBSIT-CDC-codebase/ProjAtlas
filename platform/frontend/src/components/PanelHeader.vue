<template>
  <div class="primary-bar d-flex flex-row align-center  panel-header">
    <span class="primary-light--text">{{ title }}</span>
    <v-spacer></v-spacer>
    <div
      class="icon-button"
      v-show="enableMinimize"
      style="margin-right: 10px; "
      @click="onMinimize"
    >
      <v-icon size="16">$Minus</v-icon>
    </div>

    <div
      class="icon-button"
      v-if="enableHorizental"
      style="margin-right: 10px;"
      @click="onHorizental"
    >
      <v-icon size="16">$WindowHorizental</v-icon>
    </div>

    <div
      class="icon-button"
      v-if="enableVertical"
      style="margin-right: 10px;"
      @click="onVertical"
    >
      <v-icon size="16">$WindowVertical</v-icon>
    </div>

    <div class="icon-button" v-if="enableFullScreen" @click="onFullScreen">
      <v-icon size="16">$FullScreen</v-icon>
    </div>
  </div>
</template>

<script>
export default {
  name: "PanelHeader",
  props: {
    title: {
      type: String,
      default: ""
    },
    enableMinimize: {
      type: Boolean,
      default: true
    },
    enableHorizental: {
      type: Boolean,
      default: false
    },
    enableVertical: {
      type: Boolean,
      default: false
    },
    enableFullScreen: {
      type: Boolean,
      default: true
    }
  },
  methods: {
    onMinimize() {
      this.$emit("minimize");
    },
    onHorizental() {
      this.$emit("horizental");
    },
    onVertical() {
      this.$emit("vertical");
    },
    onFullScreen() {
      this.$emit("fullScreen");
    }
  }
};
</script>

<style lang="scss" scoped>
.panel-header {
  padding: 4px 10px;
  font-family: Roboto;
  z-index: 1;

  .icon-button {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    width: 24px;
    height: 100%;
  }

  .v-icon::after {
    display: none;
  }
}
</style>
