<template>
  <svg
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g id="icon_arrow2">
      <path
        id="vector"
        fill-rule="evenodd"
        clip-rule="evenodd"
        d="M7.44975 2.34371C7.64501 2.14845 7.96159 2.14845 8.15685 2.34371L13.4602 7.64701C13.6554 7.84227 13.6554 8.15886 13.4602 8.35412L8.15685 13.6574C7.96159 13.8527 7.64501 13.8527 7.44975 13.6574C7.25448 13.4622 7.25448 13.1456 7.44975 12.9503L11.8995 8.50057L2.5 8.50057C2.22386 8.50057 2 8.27671 2 8.00057C2 7.72442 2.22386 7.50057 2.5 7.50057L11.8995 7.50057L7.44975 3.05082C7.25448 2.85556 7.25448 2.53897 7.44975 2.34371Z"
        :fill="fill"
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
