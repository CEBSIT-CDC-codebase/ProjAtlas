<template>
  <svg
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g id="icon_play">
      <path
        id="Vector 129"
        d="M3 2.45755V13.0983C3 13.7177 3.67369 14.1021 4.20698 13.787L12.8772 8.66369C13.3912 8.35995 13.4034 7.62056 12.8997 7.30002L4.2295 1.78262C3.69692 1.4437 3 1.82628 3 2.45755Z"
        :fill="fill"
      />
    </g>
  </svg>
</template>
<script>
export default {
  name: "Close",
  props: {
    fill: {
      type: String,
      default: "#7FBEFA"
    },
    fillOpacity: {
      type: Number,
      default: 1
    }
  }
};
</script>

<style></style>
