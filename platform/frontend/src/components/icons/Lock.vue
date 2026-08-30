<template>
  <svg
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g id="icon_lock">
      <path
        id="Union"
        fill-rule="evenodd"
        clip-rule="evenodd"
        d="M10 4C10 2.89543 9.10457 2 8 2C6.89543 2 6 2.89543 6 4V5H10V4ZM14 5H11V4C11 2.34315 9.65685 1 8 1C6.34315 1 5 2.34315 5 4V5H2V14H14V5ZM3 13V6H13V13H3ZM9 9C9 9.37014 8.7989 9.69331 8.5 9.86622V11.5H7.5V9.86622C7.2011 9.69331 7 9.37014 7 9C7 8.44771 7.44772 8 8 8C8.55229 8 9 8.44771 9 9Z"
        :fill="fill"
      />
    </g>
  </svg>
</template>

<script>
export default {
  name: "Lock",
  props: {
    fill: {
      type: String,
      default: "#FFC42C"
    },
    fillOpacity: {
      type: Number,
      default: 1
    }
  }
};
</script>

<style></style>
