<template>
  <div class="select-main">
    <div class="display-container" :id="displayID">
      <slot name="display-part"></slot>
    </div>
    <div
      class="options-container"
      :id="optionsID"
      v-show="showOptions"
      :style="{
        top: displayContainerBottom + 'px',
        left: displayContainerLeft + 'px',
        width: displayContainerWidth + 'px'
      }"
    >
      <slot name="options-part"></slot>
    </div>
  </div>
</template>

<script>
import { v4 as uuidv4 } from "uuid";
export default {
  name: "ASelect",
  props: {
    clearable: {
      type: Boolean,
      default: false
    },
    showOptions: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      displayID: "a-select-" + uuidv4(),
      optionsID: "a-select-" + uuidv4(),
      displayContainerBottom: 0,
      displayContainerLeft: 0,
      displayContainerWidth: 0
    };
  },

  watch: {
    showOptions() {
      if (this.showOptions) {
        this.calculateDisplayContainerGeometry();
      }
    }
  },

  mounted() {
    window.addEventListener("click", this.onGlobalClick);
    this.calculateDisplayContainerGeometry();
  },

  beforeDestroy() {
    window.removeEventListener("click", this.onGlobalClick);
  },

  methods: {
    calculateDisplayContainerGeometry() {
      const displayContainer = document.getElementById(this.displayID);
      const rect = displayContainer.getBoundingClientRect();
      this.displayContainerBottom = rect.bottom + 4;
      this.displayContainerLeft = rect.left;
      this.displayContainerWidth = rect.width;
    },

    onGlobalClick(event) {
      const clickOutsideTarget = id => {
        const clickedX = event.clientX;
        const clickedY = event.clientY;

        const element = document.getElementById(id);
        if (!element) {
          return;
        }
        const rect = element.getBoundingClientRect();
        if (
          clickedX < rect.left ||
          clickedY < rect.top ||
          clickedX > rect.right ||
          clickedY > rect.bottom
        ) {
          return true;
        }

        return false;
      };

      if (
        clickOutsideTarget(this.displayID) &&
        clickOutsideTarget(this.optionsID)
      ) {
        this.$emit("clickOutside");
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.select-main {
  position: relative;
}

.options-container {
  position: fixed;
  z-index: 12;
}
</style>
