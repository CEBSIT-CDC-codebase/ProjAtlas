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
      d="M13.2122 5.59497C13.2512 5.63403 13.2512 5.69734 13.2122 5.7364L8.00003 10.9485C7.96098 10.9876 7.89766 10.9876 7.85861 10.9485L2.64648 5.7364C2.60742 5.69734 2.60742 5.63403 2.64648 5.59497L3.21216 5.02929C3.25121 4.99024 3.31453 4.99024 3.35358 5.02929L7.85861 9.53432C7.89766 9.57337 7.96098 9.57337 8.00003 9.53432L12.5051 5.02929C12.5441 4.99024 12.6074 4.99024 12.6465 5.02929L13.2122 5.59497Z"
      :fill="fill"
    />
  </svg>
</template>
<script>
export default {
  name: "ArrowDown",
  props: {
    fill: {
      type: String,
      default: "#7F8491"
    },
    size: {
      type: Number,
      default: 24
    }
  }
};
</script>
