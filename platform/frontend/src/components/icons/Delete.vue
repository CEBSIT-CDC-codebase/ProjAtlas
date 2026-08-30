<template>
  <svg
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <path
      fill-rule="evenodd"
      clip-rule="evenodd"
      d="M10 2H6V4H10V2ZM11 4V2V1H10H6H5V2V4H4H3H2V5H3V14V15H4H12H13V14V5H14V4H13H12H11ZM12 5H11H10H6H5H4V14H12V5ZM6 7H7V12H6V7ZM10 7H9V12H10V7Z"
      :fill="fill"
      :fill-opacity="fillOpacity"
    />
  </svg>
</template>
<script>
export default {
  name: "Copy",
  props: {
    fill: {
      type: String,
      default: "#CED4E4"
    },
    fillOpacity: {
      type: Number,
      default: 1
    }
  }
};
</script>

<style></style>
