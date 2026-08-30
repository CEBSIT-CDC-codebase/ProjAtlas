<template>
  <div class="d-flex flex-column">
    <div
      v-for="(project, index) in projectsData"
      :key="index"
      class="group-right-item"
      @click="onChooseProject(project)"
    >
      <Folder
        :fill="currentChooseGroup?.name == project?.name ? '#7FBEFA' : '#CED4E4'"
      ></Folder>
      <div class="d-flex flex-column" style="margin-left: 6px">
        <span
          class="group-content-dom"
          :style="{
            color: currentChooseGroup?.name == project?.name ? '#7FBEFA' : '#ced4e4',
            maxWidth: currentChooseGroup?.name == project?.name ? '170px' : '190px',
          }"
          >{{ project?.name }}</span
        >
        <span class="accent-7--text" style="font-size: 12px; font-weight: 400">
          {{ project?.author }}
        </span>
      </div>
      <Check
        style="position: absolute; right: 10px"
        v-show="currentChooseGroup?.name == project?.name"
      ></Check>
    </div>
  </div>
</template>

<script>
import { mapState } from "vuex";
import Folder from "@/components/icons/Folder";
import Check from "@/components/icons/Check";
export default {
  name: "PublicGroupFilter",

  components: {
    Folder,
    Check,
  },

  computed: {
    ...mapState({
      projects: (state) => state.projects,
      projectPath: (state) => state.projectPath,
      neuronClass: (state) => state.neuron.neuronClass,
      currentChooseGroup: (state) => state.neuron.currentChooseGroup,
      neuronDataSource: (state) => state.neuron.neuronDataSource,
    }),

    projectsData() {
      let projects = this.projects || [];
      if (!["trimodal", "rbm"].includes(process.env.VUE_APP_SUB_SPECIES)) {
        projects = projects.filter(
          (i) => i.acronym !== "rbm" && i.acronym !== "trimodal"
        );
      }
      return [{ name: "All public data" }].concat(projects);
    },
  },

  watch: {
    neuronDataSource() {
      this.currentChooseGroup?.name !== "All public data" &&
        this.onChooseProject(this.projectsData[0]);
    },

    projectsData() {
      if (
        process.env.VUE_APP_SUB_SPECIES === "rbm" ||
        process.env.VUE_APP_SUB_SPECIES === "trimodal"
      ) {
        const rbmProject = this.projectsData.filter(
          (i) => i.acronym === "rbm" || i.acronym === "trimodal"
        );
        this.onChooseProject(rbmProject[0]);
        return;
      }

      const routePath = this.$route.path.replace(/\/$/, "") || "/";
      if (this.projectPath.slice(1).includes(routePath)) {
        this.onChooseProject(this.projectsData[1]);
        return;
      }
      // Handle project sub-routes like /EI/line — already at the correct URL, skip navigation
      const projectBases = this.projectPath.filter((p) => p !== "/");
      const matchedBase = projectBases.find((base) =>
        routePath.toLowerCase().startsWith(base.toLowerCase() + "/")
      );
      if (matchedBase) {
        this.onChooseProject(this.projectsData[1], true);
        return;
      }
      if (this.$route.path === "/pvh_oxt") {
        this.onChooseProject(this.projectsData[1]);
        return;
      }
      if (this.$route.path === "/cea") {
        this.onChooseProject(this.projectsData[1]);
        return;
      }
      if (this.$route.path === "/rbm") {
        console.log("rbm project", this.projectsData);
        this.onChooseProject(this.projectsData[1]);
        return;
      }
      this.onChooseProject(this.projectsData[0]);
    },
  },

  methods: {
    onChooseProject(project, skipNavigation = false) {
      if (this.currentChooseGroup?.name === project?.name) {
        this.$emit("close");
        return;
      }
      this.$store.commit("neuron/setToSceneGroup", {});
      this.$store.commit("neuron/setCurrentChooseGroup", project);
      this.$emit("clearOther");

      this.$store.commit("neuron/updateFilterCondition", {
        key: "publicGroup",
        value: project.name,
      });
      if (!skipNavigation) {
        if (project?.acronym) {
          if (process.env.VUE_APP_SUB_SPECIES === project.acronym) {
            // Already at this acronym path; just push the root path to avoid a duplicated path like /rbm/rbm
            this.$router.push("/");
          } else {
            this.$router.push("/" + project?.acronym);
          }
        } else {
          this.$router.push("/");
        }
      }
      this.$emit("close");
    },

    chooseProjectFunc() {
      const fullPath = this.$route.path.replace(/\/$/, "") || "/";
      // Handle sub-routes like /EI/line by extracting the project base
      const projectBases = this.projectPath.filter((p) => p !== "/");
      const matchedBase = projectBases.find(
        (base) =>
          fullPath.toLowerCase() === base.toLowerCase() ||
          fullPath.toLowerCase().startsWith(base.toLowerCase() + "/")
      );
      const acronym = matchedBase ? matchedBase.slice(1) : fullPath.slice(1);

      let currentProject = this.projects.find(
        (item) => item?.acronym?.toLowerCase() === acronym.toLowerCase()
      );
      if (!currentProject && process.env.VUE_APP_SUB_SPECIES) {
        currentProject = this.projects.find(
          (item) => item?.acronym === process.env.VUE_APP_SUB_SPECIES
        );
      }
      currentProject = currentProject ? currentProject : this.projectsData[0];
      // Pass skipNavigation=true: the user is already at the correct URL
      this.onChooseProject(currentProject, true);
    },
  },

  mounted() {
    // Data may load faster than the component mounts (batched parallel loading), so call directly in that case
    // Otherwise wait for the chooseProjectByUrl event to trigger
    if (this.$store.state.neuron.getNeuronsDone) {
      this.chooseProjectFunc();
    } else {
      this.$root.$once("chooseProjectByUrl", this.chooseProjectFunc);
    }
  },
};
</script>

<style scoped lang="scss">
* {
  font-size: 13px;
  font-family: Roboto;
}
</style>
