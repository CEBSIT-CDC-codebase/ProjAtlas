<template>
  <div class="user-group-filter">
    <div class="group-tips" v-show="!temporaryGroups.length">None</div>

    <div
      v-for="(group, index) in temporaryGroups"
      :key="index"
      class="group-right-item"
      @click="onChooseProject(group)"
    >
      <Folder
        :fill="currentChooseGroup?.id == group?.id ? '#7FBEFA' : '#CED4E4'"
      ></Folder>
      <div
        class="d-flex"
        style="margin-left: 6px"
        :style="{
          color: currentChooseGroup?.id == group?.id ? '#7FBEFA' : '#ced4e4'
        }"
      >
        <span
          class="group-content-dom"
          :style="{
            maxWidth: currentChooseGroup?.id == group?.id ? '170px' : '190px'
          }"
        >
          {{ group.name }}
        </span>
        &nbsp;
        <span> ({{ group.count || getGroupFilesLength(group?.parts) }}) </span>
      </div>
      <Check
        style="position: absolute; right: 10px"
        v-show="currentChooseGroup?.id == group?.id"
      ></Check>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
import Folder from "@/components/icons/Folder";
import Check from "@/components/icons/Check";
export default {
  name: "TemporaryGroupFilter",

  components: {
    Folder,
    Check
  },

  computed: {
    ...mapState({
      temporaryGroups: state => state.temporaryGroups,
      currentChooseGroup: state => state.neuron.currentChooseGroup
    })
  },

  methods: {
    async onChooseProject(group) {
      this.$store.commit("neuron/setToSceneGroup", group);
      this.$store.commit("neuron/setCurrentChooseGroup", group);
      this.$emit("clearOther");
      this.$store.commit("neuron/updateFilterCondition", {
        key: "temporaryGroup",
        value: group?.name + "___" + group?.id
      });
      if (this.$route.path !== "/") this.$router.push("/");
      this.$emit("close");
    },

    getGroupFilesLength(parts) {
      let len = 0;
      parts?.forEach(item => {
        len += item.files.length;
      });
      return len;
    }
  },

  mounted() {}
};
</script>

<style scoped lang="scss">
* {
  font-size: 13px;
  font-family: Roboto;
}

.user-group-filter {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
