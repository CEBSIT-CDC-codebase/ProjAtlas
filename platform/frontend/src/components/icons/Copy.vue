<template>
  <svg
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g id="icon_copy">
      <rect
        id="Rectangle 268"
        x="2.5"
        y="5.5"
        width="8"
        height="8"
        stroke="#CED4E4"
      />
      <path
        id="Vector 78"
        d="M5.5 4L5.5 2.5L13.5 2.5L13.5 10.5L12 10.5"
        stroke="#CED4E4"
      />
    </g>
  </svg>
</template>

<script>
export default {
  name: "Copy",
  props: {
    fill: {
      type: String,
      default: "#ffffff"
    },
    fillOpacity: {
      type: Number,
      default: 1
    }
  }
};
</script>

<style></style>
