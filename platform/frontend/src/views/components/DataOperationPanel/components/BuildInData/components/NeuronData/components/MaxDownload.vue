<template>
  <div class="load_warning_div">
    <div class="warning_div">
      <div class="warning_header">
        <span>Warning</span>
        <v-icon small style="margin-right: 11px" @click="onClose"
          >$Close</v-icon
        >
      </div>
      <p style="margin: 0 10px;">
        Please select 10000 or fewer neurons to download. Or you may go to the
        <a style="color: #007afc;" @click="toDownloadPage">Data Download</a>
        page to download full data.
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: "MaxDownload",

  methods: {
    toDownloadPage() {
      this.$router.push("./download");
    },

    onClose() {
      this.$emit("close");
    }
  }
};
</script>

<style lang="scss" scoped>
.load_warning_div {
  position: fixed;
  z-index: 10;
  background-color: rgba(0, 0, 0, 0.5);
  top: 0px;
  left: 0px;
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.warning_div {
  width: 340px;
  height: 138px;
  display: flex;
  flex-direction: column;
  border-radius: 4px;
  background: #313237;
  border: 1px solid #353539;
}

.warning_div p {
  font-size: 13px;
  color: #c4c4c4;
  margin: 0 20px;
}

.warning_header {
  display: flex;
  height: 46px;
  justify-content: space-between;
  align-items: center;
}

.warning_header span {
  margin-left: 20px;
  font-size: 13px;
  line-height: 16px;
  text-align: left;
  color: #ffffff;
}

.warning_footer {
  height: 24px;
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}

.warning_footer span {
  height: 24px;
  width: 40px;
  font-size: 12px;
  color: #ffffff;
  text-align: center;
  line-height: 24px;
  border-radius: 2px;
  cursor: pointer;
}
</style>
