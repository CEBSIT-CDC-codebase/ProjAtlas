<template>
  <div class="scene-animation" v-draggable>
    <div
      class="scene-animation-header atlas-draggable-header"
      :style="headerStyle"
    >
      <span class="primary-light--text">Animation</span>
      <div>
        <v-icon
          size="16"
          @click="bodyVisible = !bodyVisible"
          :style="arrowStyle"
        >
          $Arrow
        </v-icon>
        &nbsp;
        <v-icon size="16" @click="$emit('close')">$Close</v-icon>
      </div>
    </div>

    <animation-menu
      @toCreate="createAnimation"
      @setCurrentTab="setCurrentTab"
      v-show="currentTab === 'menu' && bodyVisible"
    ></animation-menu>
    <animation-detail
      @back="backFunc"
      @setCurrentTab="setCurrentTab"
      v-show="currentTab === 'detail' && bodyVisible"
    ></animation-detail>
  </div>
</template>

<script>
import { mapState } from "vuex";
import AnimationMenu from "./components/AnimationMenu/AnimationMenu.vue";
import AnimationDetail from "./components/AnimationDetail/AnimationDetail.vue";
export default {
  name: "SceneAnimation",

  components: {
    AnimationDetail,
    AnimationMenu
  },

  data() {
    return {
      currentTab: "menu",
      bodyVisible: true
    };
  },

  // watch: {
  //   currentAnimation() {
  //     this.currentTab = "detail";
  //   },
  // },

  computed: {
    ...mapState({
      theme: state => state.theme,
      target: state => state.target,
      currentAnimation: state => state.currentAnimation
    }),

    arrowStyle() {
      return this.bodyVisible
        ? "transform: rotate(0);"
        : "transform: rotate(180deg);";
    },

    headerStyle() {
      return {
        borderTop:
          "2px solid " +
          this.$vuetify.theme.themes[this.theme]["primary-light"],
        background: this.$vuetify.theme.themes[this.theme]["primary-bar"]
      };
    }
  },

  methods: {
    createAnimation() {
      this.currentTab = "detail";
      this.$store.commit("setAnimationStatus", "create");
    },

    setCurrentTab(tab) {
      this.currentTab = tab;
    },

    backFunc() {
      this.currentTab = "menu";
      this.$store.commit("setAnimationStatus", "");
    }
  },

  mounted() {}
};
</script>

<style lang="scss" scoped>
.scene-animation {
  width: 300px;
  display: flex;
  flex-direction: column;
  backdrop-filter: blur(15px);
  background: rgba(33, 33, 33, 0.5);
  position: absolute;
  z-index: 2;
}

.scene-animation-header {
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

.animation-line {
  height: 1px;
  background: #343f5c;
}
</style>
