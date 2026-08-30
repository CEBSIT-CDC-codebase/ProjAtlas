<template>
  <div class="main">
    <div class="primary-main content">
      <DownloadTable></DownloadTable>
      <DataDescription style="margin-top: 50px"></DataDescription>
    </div>
    <Footer></Footer>
  </div>
</template>

<script>
import Footer from "@/views/DataDownload/components/Footer";
import DownloadTable from "@/views/DataDownload/components/DownloadTable";
import DataDescription from "@/views/DataDownload/components/DataDescription";

export default {
  name: "DataDownload",
  components: {
    Footer,
    DownloadTable,
    DataDescription
  },
  mounted() {
    // this.$store.commit("setVisualType", "mouse");
  }
};
</script>

<style scoped lang="scss">
.main {
  width: 100vw;
  max-width: 100vw;
  height: 100%;
  background: #0b101c;
  display: flex;
  flex-direction: column;
  overflow-x: auto;
  overflow-y: auto;
  max-height: 100vh;

  .content {
    width: 100%;
    flex-grow: 1;
    margin-top: 48px;
    margin-bottom: 200px;
    display: flex;
    flex-direction: column;
  }
}

::-webkit-scrollbar {
  width: 0 !important;
}
</style>
