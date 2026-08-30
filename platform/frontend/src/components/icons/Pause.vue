<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
  >
    <path
      d="M3.5 2C3.22386 2 3 2.22386 3 2.5V13.5C3 13.7761 3.22386 14 3.5 14H5.5C5.77614 14 6 13.7761 6 13.5V2.5C6 2.22386 5.77614 2 5.5 2H3.5Z"
      :fill="fill"
    />
    <path
      d="M10.5 2C10.2239 2 10 2.22386 10 2.5V13.5C10 13.7761 10.2239 14 10.5 14H12.5C12.7761 14 13 13.7761 13 13.5V2.5C13 2.22386 12.7761 2 12.5 2H10.5Z"
      :fill="fill"
    />
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
