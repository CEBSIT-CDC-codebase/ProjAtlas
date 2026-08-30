<template>
  <div class="scene-setting" v-draggable>
    <div
      class="scene-setting-header atlas-draggable-header"
      :style="headerStyle"
    >
      <span class="primary-light--text">More settings</span>
      <div>
        <v-icon size="16" @click="$emit('close')"> $Close </v-icon>
      </div>
    </div>
    <div class="scene-setting-body">
      <MouseControl></MouseControl>
      <div class="setting-line"></div>
      <NeuronDisplayMode></NeuronDisplayMode>
      <div class="setting-line"></div>
      <SomaRadius></SomaRadius>
      <div class="setting-line"></div>
      <DisplayControl></DisplayControl>
      <div class="setting-line"></div>
      <BackgroundColor></BackgroundColor>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
import BackgroundColor from "./components/BackgroundColor.vue";
import MouseControl from "./components/MouseControl.vue";
import SomaRadius from "./components/SomaRadius.vue";
import NeuronDisplayMode from "./components/NeuronDisplayMode.vue";
import DisplayControl from "./components/DisplayControl.vue";

export default {
  name: "SceneSetting",

  components: {
    NeuronDisplayMode,
    SomaRadius,
    MouseControl,
    BackgroundColor,
    DisplayControl
  },

  data() {
    return {};
  },

  watch: {},

  computed: {
    ...mapState({
      theme: state => state.theme,
      target: state => state.target,
      settingVisible: state => state.settingVisible
    }),

    headerStyle() {
      return {
        borderTop:
          "2px solid " +
          this.$vuetify.theme.themes[this.theme]["primary-light"],
        background: this.$vuetify.theme.themes[this.theme]["primary-bar"]
      };
    }
  },

  methods: {},

  mounted() {}
};
</script>

<style lang="scss">
.scene-setting {
  width: 250px;
  display: flex;
  flex-direction: column;
  user-select: none;
  position: absolute;
  z-index: 2;
  border-radius: 2px;
  box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.5);
  background: rgba(33, 33, 33, 0.5);
  backdrop-filter: blur(15px);
}

.scene-setting-header {
  display: flex;
  flex-direction: row;
  border-top-width: 1px;
  justify-content: space-between;
  align-items: center;
  padding: 4px 10px;
  font-size: 13px;
  font-weight: 500;

  :deep(.v-icon) {
    cursor: pointer;
  }
}

.scene-setting-body {
  padding: 14px;
  .setting-item {
    display: flex;
    align-items: flex-start;
    height: 32px;
    line-height: 32px;
    font-size: 13px;
  }
  .item-title {
    color: #7f8490;
  }
}

.setting-line {
  height: 1px;
  margin: 10px 0;
  background: #343f5c;
}

.v-input--switch {
  margin: 0;
  transform: scale(0.8);
  margin-right: -10px;
}
</style>
