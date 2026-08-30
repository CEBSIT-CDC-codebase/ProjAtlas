<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
  >
    <path
      fill-rule="evenodd"
      clip-rule="evenodd"
      d="M2.64624 10.3828C2.60718 10.3438 2.60718 10.2804 2.64624 10.2414L7.85837 5.02925C7.89742 4.9902 7.96074 4.9902 7.99979 5.02925L13.2119 10.2414C13.251 10.2804 13.251 10.3438 13.2119 10.3828L12.6462 10.9485C12.6072 10.9875 12.5439 10.9875 12.5048 10.9485L7.99979 6.44347C7.96074 6.40442 7.89742 6.40442 7.85837 6.44347L3.35334 10.9485C3.31429 10.9875 3.25097 10.9875 3.21192 10.9485L2.64624 10.3828Z"
      :fill="fill"
    />
  </svg>
</template>

<script>
export default {
  name: "Copy",
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
