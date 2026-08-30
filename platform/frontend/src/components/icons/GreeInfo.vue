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
      d="M15 8C15 11.866 11.866 15 8 15C4.13401 15 1 11.866 1 8C1 4.13401 4.13401 1 8 1C11.866 1 15 4.13401 15 8ZM7.35 13C7.29477 13 7.25 12.9552 7.25 12.9V6.6C7.25 6.54477 7.29477 6.5 7.35 6.5H8.65C8.70523 6.5 8.75 6.54477 8.75 6.6V12.9C8.75 12.9552 8.70523 13 8.65 13H7.35ZM7.25 4.9C7.25 4.95523 7.29477 5 7.35 5H8.65C8.70523 5 8.75 4.95523 8.75 4.9V3.6C8.75 3.54477 8.70523 3.5 8.65 3.5H7.35C7.29477 3.5 7.25 3.54477 7.25 3.6V4.9Z"
      :fill="fill"
    />
  </svg>
</template>

<script>
export default {
  name: "Info",
  props: {
    fill: {
      type: String,
      default: "#808080"
    },
    size: {
      type: Number,
      default: 24
    }
  }
};
</script>

<style></style>
