<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="16"
    height="16"
    viewBox="0 0 16 16"
    fill="none"
  >
    <path
      d="M7.99999 2.5C5.78106 2.5 3.86798 3.81405 2.99846 5.70856L2.08961 5.29144C3.11611 3.05489 5.37594 1.5 7.99999 1.5C10.011 1.5 11.808 2.41321 13 3.84657V2L14 2V6L10 6L10 5L12.6106 5C11.6289 3.49427 9.93015 2.5 7.99999 2.5Z"
      :fill="fill"
    />
    <path
      d="M3 14V12.1534C4.19197 13.5868 5.98903 14.5 7.99999 14.5C10.624 14.5 12.8839 12.9451 13.9104 10.7086L13.0015 10.2914C12.132 12.186 10.2189 13.5 7.99999 13.5C6.06984 13.5 4.37111 12.5057 3.38935 11H6V10H2V14H3Z"
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
      default: "white"
    },
    fillOpacity: {
      type: Number,
      default: 1
    }
  }
};
</script>

<style></style>
