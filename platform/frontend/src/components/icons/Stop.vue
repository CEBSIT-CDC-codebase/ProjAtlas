<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
  >
    <path
      d="M2 3C2 2.44772 2.44772 2 3 2H13C13.5523 2 14 2.44772 14 3V13C14 13.5523 13.5523 14 13 14H3C2.44772 14 2 13.5523 2 13V3Z"
      :fill="fill"
    />
  </svg>
</template>
<script>
export default {
  name: "AddFrame",
  props: {
    fill: {
      type: String,
      default: "#7FBEFA"
    },
    size: {
      type: Number,
      default: 24
    }
  }
};
</script>

<style></style>
