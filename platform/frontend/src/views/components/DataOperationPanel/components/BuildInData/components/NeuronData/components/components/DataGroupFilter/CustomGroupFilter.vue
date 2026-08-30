<template>
  <div class="user-group-filter">
    <div class="group-tips" v-show="!groups.length">
      {{ currentGroupTips }}
    </div>

    <div
      v-for="(group, index) in groups"
      :key="index"
      class="group-right-item"
      @click="onChooseProject(group)"
    >
      <FolderSaved
        :fill="currentChooseGroup?.id == group?.id ? '#7FBEFA' : '#CED4E4'"
      ></FolderSaved>
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
        <span> ({{ group.count }}) </span>
      </div>
      <Check
        style="position: absolute; right: 10px"
        v-show="currentChooseGroup?.id == group?.id"
      ></Check>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters } from "vuex";
import { getGroupDetailFunc } from "@/api/group";
import FolderSaved from "@/components/icons/FolderSaved";
import Check from "@/components/icons/Check";
export default {
  name: "CustomGroupFilter",
  components: {
    Check,
    FolderSaved
  },
  computed: {
    ...mapState({
      groups: state => state.groups || [],
      groupsDetailData: state => state.groupsDetailData,
      currentChooseGroup: state => state.neuron.currentChooseGroup
    }),

    ...mapGetters(["groupTips", "userInfo"]),

    currentGroupTips() {
      return this.userInfo ? "None" : this.groupTips;
    }
  },

  watch: {},

  methods: {
    async onChooseProject(group) {
      const id = group?.id;
      if (!this.groupsDetailData[id])
        this.groupsDetailData[id] = await getGroupDetailFunc(id);

      this.$store.commit("neuron/setToSceneGroup", {
        ...this.groupsDetailData[id]
      });
      this.$store.commit("neuron/setCurrentChooseGroup", group);
      this.$emit("clearOther");

      this.$store.commit("neuron/updateFilterCondition", {
        key: "customGroup",
        value: group?.name + "___" + id
      });
      if (this.$route.path !== "/") this.$router.push("/");
      this.$emit("close");
    }
  }
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
