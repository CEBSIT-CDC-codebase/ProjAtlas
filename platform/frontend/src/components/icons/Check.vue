<template>
  <svg
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
  >
    <g id="check">
      <path
        id="Vector (Stroke)"
        fill-rule="evenodd"
        clip-rule="evenodd"
        d="M13.6868 3.64645C13.8821 3.84171 13.8821 4.15829 13.6868 4.35355L6.35351 11.6869C6.15825 11.8821 5.84167 11.8821 5.64641 11.6869L2.31307 8.35355C2.11781 8.15829 2.11781 7.84171 2.31307 7.64645C2.50833 7.45118 2.82492 7.45118 3.02018 7.64645L5.99996 10.6262L12.9797 3.64645C13.175 3.45118 13.4916 3.45118 13.6868 3.64645Z"
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
