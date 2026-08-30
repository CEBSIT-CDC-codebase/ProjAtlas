<template>
  <svg
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g id="icon_save">
      <path
        id="Union"
        fill-rule="evenodd"
        clip-rule="evenodd"
        d="M2 3V2H3H4.5H5.5H11L14 5V13V14H13H3H2V13V3ZM3 3H4.5V5.5V6H5H10V5H5.5V3H10.5858L13 5.41421V13H11.5V9.5V9H11H5H4.5V9.5V13H3V3ZM5.5 13H10.5V10H5.5V13Z"
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
