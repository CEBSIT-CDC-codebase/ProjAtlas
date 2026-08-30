<template>
  <div class="menu-operation" :id="id" v-show="visible">
    <div
      class="menu-operation-item"
      @click="$emit('rename')"
      v-show="!lockStatus"
    >
      <v-icon size="16">$EditName</v-icon>
      <span class="item-text">Rename the group</span>
    </div>
    <div
      class="menu-operation-item"
      @click="$emit('edit')"
      v-show="!lockStatus"
    >
      <v-icon size="16">$Edit</v-icon>
      <span class="item-text">Edit the group</span>
    </div>
    <div class="menu-operation-item" @click="$emit('copy')">
      <v-icon size="16">$Copy</v-icon>
      <span class="item-text">Copy the group</span>
    </div>
    <div class="menu-operation-item" @click="$emit('delete')">
      <v-icon size="16">$Delete</v-icon>
      <span class="item-text">Delete the group</span>
    </div>
  </div>
</template>

<script>
import { v4 as uuidv4 } from "uuid";
export default {
  name: "MenuOperation",
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    lockStatus: {
      type: Boolean,
      default: false
    }
  },
  components: {},
  data() {
    return {
      id: `menu-${uuidv4()}`
    };
  },
  mounted() {
    window.addEventListener("click", this.onGlobalCLick, true);
  },
  beforeDestroy() {
    window.removeEventListener("click", this.onGlobalCLick, true);
  },
  methods: {
    onGlobalCLick(event) {
      const div = document.getElementById(this.id);
      if (!div) {
        return;
      }

      const rect = div.getBoundingClientRect();

      const clickedX = event.clientX;
      const clickedY = event.clientY;

      if (
        clickedX < rect.left ||
        clickedY < rect.top ||
        clickedX > rect.right ||
        clickedY > rect.bottom
      ) {
        this.$emit("clickOutside");
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.menu-operation {
  position: absolute;
  top: 30px;
  z-index: 9;
  display: flex;
  width: 220px;
  flex-direction: column;
  align-items: flex-start;
  border-radius: 2px;
  background: var(--BG-, #303c56);
  box-shadow: 0px 0px 10px 0px rgba(0, 0, 0, 0.5);

  .menu-operation-item {
    display: flex;
    height: 32px;
    padding: 10px;
    align-items: center;
    gap: 10px;
    align-self: stretch;

    .item-text {
      color: var(--dark, #ced4e4);
      /* Roboto/regular-14 */
      font-family: Roboto;
      font-size: 13px;
      font-style: normal;
      font-weight: 400;
      line-height: normal;
    }

    &:hover {
      cursor: pointer;
      background: rgba(255, 255, 255, 0.1);
    }
  }
}
</style>
