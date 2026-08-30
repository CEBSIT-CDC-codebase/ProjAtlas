<template>
  <svg
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g id="icon_arrow">
      <path
        id="Vector 85"
        d="M7.80371 13.3037L2.50041 8.00041M2.50041 8.00041L7.80371 2.69711M2.50041 8.00041L13.107 8.00041"
        :stroke="fill"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </g>
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
