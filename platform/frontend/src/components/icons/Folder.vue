<template>
  <svg
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g id="icon_folder">
      <path
        id="Rectangle 230"
        d="M6.55279 4.22361L6.69098 4.5H7H14.5V13.5H1.5V2.5H5.69098L6.55279 4.22361Z"
        :stroke="fill"
      />
    </g>
  </svg>
</template>
<script>
export default {
  name: "Folder",
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
