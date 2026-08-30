<template>
  <div class="detail-create">
    <div
      class="create-btn"
      @click="$emit('createNewFunc', 'rotation')"
      @mouseenter="$emit('mainColorMouseEnter', 'addRotation')"
      @mouseleave="$emit('mainColorMouseLeave', 'addRotation')"
    >
      <add :fill="fillColors?.addRotation"></add>
      <span>New rotation animation section</span>
    </div>
    <div
      class="create-btn"
      @click="$emit('createNewFunc', 'custom')"
      @mouseenter="$emit('mainColorMouseEnter', 'addCustom')"
      @mouseleave="$emit('mainColorMouseLeave', 'addCustom')"
    >
      <add :fill="fillColors?.addCustom"></add>
      <span>New custom animation section</span>
    </div>
  </div>
</template>

<script>
import Add from "@/components/icons/Add";
export default {
  name: "DetailCreate",

  props: {
    fillColors: {
      type: Object,
      default: () => {}
    }
  },
  // °
  components: { Add },

  data() {
    return {};
  },

  computed: {},

  watch: {},

  methods: {}
};
</script>

<style lang="scss" scoped>
.create-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 28px;
  margin-bottom: 10px;
  padding: 6px 10px;
  border-radius: 2px;
  border: 1px solid #343f5c;
  // transition: all .5s;
  span {
    color: #7fbefa;
    text-align: center;
    font-size: 13px;
    font-weight: 400;
  }
  svg {
    transform: translate(-4px, 1px);
  }
  &:hover {
    border: none;
    background-color: #2d68c3;
    cursor: pointer;
    span {
      color: #ffffff;
    }
  }
}
</style>
