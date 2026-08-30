<template>
  <svg
    width="15"
    height="18"
    viewBox="0 0 15 18"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      id="Polygon 10"
      d="M-3.93421e-07 8.99958L15 -6.55671e-07L15 18L-3.93421e-07 8.99958Z"
      :fill="fill"
    />
  </svg>
</template>
<script>
export default {
  name: "Add",
  props: {
    fill: {
      type: String,
      default: "#303C56"
    },
    size: {
      type: Number,
      default: 24
    }
  }
};
</script>

<style></style>
