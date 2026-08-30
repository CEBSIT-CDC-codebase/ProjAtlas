<template>
  <v-app>
    <v-app-bar
      app
      color="primary"
      dark
      elevation="0"
      height="32"
      class="app-bar"
    >
      <span>
        <v-icon
          size="30"
          style="margin-left: 10px; cursor: pointer"
          @click="toDigital"
          >$DigitalBrain</v-icon
        >
        <span
          @click="toDigital"
          style="margin-left: 5px; font-family: 'Open Sans'; cursor: pointer"
        >
          Digital Brain
        </span>
        <span style="margin-left: 5px; font-family: 'Open Sans'">
          | Projectome Atlas
        </span>
      </span>
      <v-spacer></v-spacer>
      <v-btn text color="primary-text" @click="$router.push('/')"
        >Data Viewer</v-btn
      >
      <v-btn text color="primary-text" @click="$router.push('/download')">
        Data Download
      </v-btn>
      <v-btn
        text
        color="primary-text"
        v-show="userGuideVisible"
        @click="toDigitalHelp"
      >
        User Guide
      </v-btn>
      <v-btn text color="primary-text" @click="toDigitalTools"
        >More Tools</v-btn
      >
      <v-btn text color="primary-text" @click="toDigital('contact')"
        >Contact Us</v-btn
      >
      <div class="user-unlogin" v-if="!$store.getters.userInfo">
        <v-btn
          text
          class="ml-5"
          color="primary-text"
          @click="userLogic('login')"
          >Log In</v-btn
        >
        <v-btn color="background" tile @click="userLogic('register')"
          >Sign Up</v-btn
        >
      </div>
      <div class="user-login" v-else>
        <v-btn
          text
          @click="userDialog = !userDialog"
          ref="userBtn"
          v-click-outside="loginClickOutside"
        >
          <v-icon dark> $BrainUser </v-icon>
          &nbsp;
          <span style="color: #fff">{{
            $store.getters.userInfo?.nickname
          }}</span>
        </v-btn>
        <ul class="user-login-menu" v-show="userDialog" @click="userInfoClick">
          <li>
            <v-icon size="16">$BrainUser</v-icon>
            User Profile
          </li>
          <li>
            <v-icon size="16">$Exit</v-icon>
            Log out
          </li>
        </ul>
      </div>
    </v-app-bar>

    <v-main>
      <keep-alive>
        <router-view />
      </keep-alive>
    </v-main>

    <tool-tips
      :type="toolTipType"
      :visible="toolTipVisible"
      :message="toolTipMessage"
      :visibleDuration="toolTipDuration"
      @close="$store.commit('setToolTipVisible', false)"
    ></tool-tips>

    <v-dialog
      persistent
      transition="dialog-bottom-transition"
      max-width="460"
      v-model="unLoginVisible"
    >
      <v-card class="login-dialog-card" style="background-color: #151c2d">
        <div class="un-login-close">
          <span
            class="bg-icon"
            style="cursor: pointer"
            @click="unLoginVisible = false"
          >
            <close fill="#A5ABB9"></close>
          </span>
        </div>
        <div class="un-login-main">
          <p>Please login first.</p>
          <v-btn
            elevation="0"
            height="50"
            width="300"
            class="login-btn"
            color="#2D68C3"
            @click="userLogic('login')"
          >
            Login
          </v-btn>
          <p class="register-account">
            Don't have an account?
            <span @click="userLogic('register')" style="font-size: 13px">
              Register here.
            </span>
          </p>
        </div>
      </v-card>
    </v-dialog>

    <a-dialog
      :visible.sync="expirationDialogVisible"
      width="320"
      @confirm="confirmExpirationGroup"
      title="System information"
      surebtnText="log in again"
      :footerVisible="true"
    >
      <div class="expiration-dialog">
        <span class=""> The session has expired. Please log in again </span>
      </div>
    </a-dialog>

    <welcome-dialog
      v-if="welcomeDialogVisible"
      @close="welcomeDialogVisible = false"
    ></welcome-dialog>
  </v-app>
</template>

<script>
import { getUrlParam } from "@/utils/utils";
import ADialog from "@/components/ADialog";
import { mapState } from "vuex";
import ToolTips from "@/components/ToolTips";
import Close from "@/components/icons/Close";
import { getShareGroup } from "@/api/group";
import { fetchGetUser, fetchAddUser } from "@/api/ai-interface";
import WelcomeDialog from "./components/WelcomeDialog";
import { getMoreSettingData } from "./utils/moreSetting";
import { computeRegionSomaTree } from "./utils/neuronFilterTool";

export default {
  name: "App",
  components: {
    ToolTips,
    Close,
    ADialog,
    WelcomeDialog
  },
  data: () => ({
    userDialog: false,
    welcomeDialogVisible: true,
    loginPollingTimer: null
  }),

  computed: {
    ...mapState({
      addGroupFlag: state => state.addGroupFlag,
      projects: state => state.projects,
      loginFlag: state => state.loginFlag,
      expirationFlag: state => state.expirationFlag,
      toolTipType: state => state.toolTipType,
      toolTipDuration: state => state.toolTipDuration,
      toolTipMessage: state => state.toolTipMessage,
      toolTipVisible: state => state.toolTipVisible,
      sceneCurrentGroup: state => state.sceneCurrentGroup,
      projectPath: state => state.projectPath,
      userInfo: state => state.userInfo,
      viewedNeurons: state => state.neuron.viewedNeurons,
      visualTarget: state => state.visualTarget
    }),

    userGuideVisible() {
      return process.env.VUE_APP_TARGET !== "monkey";
    },

    unLoginVisible: {
      get() {
        return this.loginFlag;
      },
      set(newV) {
        this.$store.commit("setLoginFlag", newV);
      }
    },

    expirationDialogVisible: {
      get() {
        return this.expirationFlag;
      },
      set(newV) {
        this.$store.commit("setExpirationFlag", newV);
      }
    }
  },

  watch: {
    async projects(newV) {
      if (!newV) return;
      await this.dispatchNeuronData(newV);
      computeRegionSomaTree();
      this.$store.commit("neuron/setGetNeuronsDone", true);
      if (this.visualTarget === "mouse") {
        getMoreSettingData();
      }
    },

    async $route() {
      const projects = this.$store.state.projects;
      if (!projects) return;
      await this.dispatchNeuronData(projects);
      computeRegionSomaTree();
      this.$store.commit("neuron/setGetNeuronsDone", true);
    },

    async userInfo() {
      if (!this.userInfo) {
        this.$store.commit("setGroups", []);
        this.viewedNeurons?.forEach(item => {
          item.groups = item?.groups?.filter(g => g?.save !== "save");
        });
        if (this.sceneCurrentGroup?.save === "save") {
          this.$store.commit("setSceneCurrentGroup", {
            name: "All neurons",
            id: "all"
          });
        }
      } else {
        this.$store.commit("setLoginFlag", false);
        if (["mouse", "monkey"].includes(process.env.VUE_APP_TARGET)) {
          let res = await fetchAddUser({
            ...this.userInfo,
            name: this.userInfo?.realname || this.userInfo?.nickname
          });
          if (!res.data?.user) {
            res = await fetchGetUser(this.userInfo?.email);
          }
          this.$store.commit("session/setUserInfo", res.data?.user);
          this.$store.dispatch("session/getSessions");
        }
      }
    }
  },

  methods: {
    /**
     * Unified entry point: decides between batch loading (root route /)
     * or on-demand loading (specific project route) based on the route.
     */
    async dispatchNeuronData(projects) {
      let path = this.$route.path.replace(/\/$/, "") || "/";
      // Root route / -> load all projects in parallel; other routes -> load a single project on demand
      if (path === "/") {
        await this.loadAllProjectsData(projects);
      } else {
        await this.loadProjectNeuronData(projects);
      }
    },

    /**
     * Root route only: load neuron data + region relations for all projects in parallel
     * - Neuron data: batch fetch + write to Vuex once
     * - Region relations: parallel dispatch (each project writes to a different state key, no conflicts)
     * - All shared computation (sort/merge) runs only once
     */
    async loadAllProjectsData(projects) {
      const singleDataset = ["trimodal", "rbm"];

      // Filter projects (same logic as the original for loop)
      const projectsToLoad = projects.filter(project => {
        if (!singleDataset.includes(process.env.VUE_APP_SUB_SPECIES)) {
          return !singleDataset.includes(project.acronym);
        }
        return true;
      });

      if (projectsToLoad.length === 0) return;

      // ===== Phase 1: fetch + parse neuron data for all projects in parallel (built-in cache check) =====
      await this.$store.dispatch("neuron/loadBatchNeuronData", {
        projects: projectsToLoad
      });

      // ===== Phase 2: fetch region relations in parallel (skip already-cached ones) =====
      const needRegion = projectsToLoad.filter(
        p => !this.$store.state.neuron.regionNeuronRelation[p.name]
      );
      if (needRegion.length > 0) {
        await Promise.all(
          needRegion.map(project =>
            this.$store.dispatch("neuron/getNeuronRegionRelation", {
              projects: projectsToLoad,
              name: project.name,
              acronym: project.acronym
            })
          )
        );
      }

      // ===== Phase 3: platform-specific data =====
      if (process.env.VUE_APP_SUB_SPECIES === "SC") {
        const needOrder = projectsToLoad.filter(
          p => !this.$store.state.neuron.neuronTypeOrder[p.name]
        );
        if (needOrder.length > 0) {
          await Promise.all(
            needOrder.map(project =>
              this.$store.dispatch("neuron/getNeuronTypeOrder", {
                projects: projectsToLoad,
                name: project.name,
                acronym: project.acronym
              })
            )
          );
        }
      }

      this.$root.$emit("chooseProjectByUrl");
    },

    /**
     * Load neuron data on demand for the project matching the current route.
     * Loads only a single project instead of iterating over all 18 projects,
     * avoiding memory overflow from loading the full dataset into Vuex.
     */
    async loadProjectNeuronData(projects) {
      let path = this.$route.path.replace(/\/$/, "") || "/";
      // projectPath: ['/', '/pfc', '/hipp', '/hy', '/lha', '/pvh_oxt', '/cea', '/EI', '/spcd', '/whole-cortex']

      // Handle project sub-routes like /EI/line
      if (!this.projectPath.slice(1).includes(path)) {
        const matchedBase = this.projectPath.find(
          pp => pp !== "/" && path.startsWith(pp + "/")
        );
        if (matchedBase) {
          path = matchedBase;
        }
      }

      const projectAcronym = path.slice(1).toLowerCase();
      const targetProject = projects.find(
        item => item?.acronym?.toLowerCase() === projectAcronym
      );

      if (!targetProject) return;

      // Skip the duplicate request if the current project's data is already loaded
      if (this.$store.state.neuron.neuronData[targetProject.name]) return;

      const singleDataset = ["trimodal", "rbm"];
      const shouldSkip =
        !singleDataset.includes(process.env.VUE_APP_SUB_SPECIES) &&
        singleDataset.includes(targetProject.acronym);

      if (shouldSkip) return;

      // Swap the current project into the first slot (preserves original logic: lets other components access the current project via index 0)
      const currIndex = projects.findIndex(
        item => item?.acronym?.toLowerCase() === projectAcronym
      );
      if (currIndex > 0) {
        const one = projects[currIndex];
        projects[currIndex] = projects[0];
        projects[0] = one;
      }

      // Parallel requests: neuronInfo + regionRelation write to different state keys, no conflicts
      // SC-specific data is fetched in parallel too, reducing sequential waiting
      const tasks = [
        this.$store.dispatch("neuron/getNeuronInfo", {
          projects,
          name: targetProject.name,
          acronym: targetProject.acronym
        }),
        this.$store.dispatch("neuron/getNeuronRegionRelation", {
          projects,
          name: targetProject.name,
          acronym: targetProject.acronym
        })
      ];
      if (process.env.VUE_APP_SUB_SPECIES === "SC") {
        tasks.push(
          this.$store.dispatch("neuron/getNeuronTypeOrder", {
            projects,
            name: targetProject.name,
            acronym: targetProject.acronym
          })
        );
      }
      await Promise.all(tasks);
      this.$root.$emit("chooseProjectByUrl");
    },

    loginClickOutside() {
      if (this.userDialog) this.userDialog = false;
    },

    confirmExpirationGroup() {
      this.$store.commit("setExpirationFlag", false);
      this.userLogic("login");
    },

    userInfoClick(e) {
      const text = e.target.innerText;
      if (text.includes("Log out")) {
        this.$store.commit("setUserInfo", null);
        this.$store.commit("session/setUserInfo", null);
        this.$store.commit("setGroups", []);
        localStorage.removeItem("access_token");
        localStorage.removeItem("vuex");
        this.$router.push("/");
      }
      if (text.includes("User Profile")) {
        this.$router.push("/userinfo");
      }
      this.userDialog = !this.userDialog;
    },

    userLogic(tag) {
      const redirectURL = encodeURIComponent(process.env.VUE_APP_WWW_HOST);
      if (this.loginPollingTimer) clearInterval(this.loginPollingTimer);
      this.loginPollingTimer = setInterval(async () => {
        const token = localStorage.getItem("access_token");
        if (token) {
          clearInterval(this.loginPollingTimer);
          this.loginPollingTimer = null;
          await this.$store.dispatch("getUserInfo");
          this.$store.dispatch("getGroups");
          this.$store.dispatch("getAnimations");
        }
      }, 1000);
      window.open(
        `${process.env.VUE_APP_USER_URL}/iam/admin/#/${tag}?redirect=${redirectURL}`
      );
    },

    toDigital(tag = "") {
      let val = "?from=projectome_atlas";
      if (tag === "contact") {
        val = "contact" + val;
      }
      const link = process.env.VUE_APP_DIGITAL_HOST + val;
      const token =
        getUrlParam("token") || localStorage.getItem("access_token");
      const str = token && token !== "null" ? `&token=${token}` : "";
      window.open(link + str, "_blank");
    },

    toDigitalHelp() {
      // Set VUE_APP_HELP_URL in your .env to point to your own docs; defaults to "#" (no-op)
      // so the open-source build never links to any internal host.
      const url = process.env.VUE_APP_HELP_URL || "#";
      window.open(url, "_blank");
    },

    async toDigitalTools() {
      const token =
        getUrlParam("token") || localStorage.getItem("access_token");
      const str = token && token !== "null" ? `?token=${token}` : "";
      window.open(process.env.VUE_APP_TOOLS_URL + str, "_blank");
    },

    async getRequireTokenData() {
      let token = getUrlParam("token");
      if (!token) {
        token = localStorage.getItem("access_token");
      } else {
        localStorage.setItem("access_token", token);
      }
      if (token) {
        await this.$store.dispatch("getUserInfo");
        this.$store.dispatch("getGroups");
        this.$store.dispatch("getAnimations");
      }
    },

    closeLoginNewPageFunc() {
      const token = getUrlParam("token"),
        loginTimeout = localStorage.getItem("login_timeout");

      if (token && loginTimeout) {
        localStorage.setItem("access_token", token);
        localStorage.removeItem("login_timeout");
        window.close();
      }
    },

    async getSharedGroups() {
      const shareId = getUrlParam("shareID");
      if (shareId) {
        const shareVal = await getShareGroup(shareId);
        if (shareVal) {
          this.$store.commit("setTemporaryGroups", [
            { ...shareVal, count: null, selected: false, operation: false }
          ]);
          this.$store.commit("setAddGroupFlag", !this.addGroupFlag);
        } else {
          this.$store.commit("setToolTipType", "error");
          this.$store.commit("setToolTipMessage", "No shared data");
          this.$store.commit("setToolTipVisible", true);
        }
      }
    }
  },

  mounted() {
    document.title = process.env.VUE_APP_META_TITLE;
    // if want to use light theme, just set the dark to be false
    // this.$vuetify.theme.dark = false;
    const previousChoice = localStorage.getItem("show_welcome");
    const isVisible =
      process.env.VUE_APP_TARGET === "mouse" &&
      (previousChoice === null || previousChoice === "true");
    if (isVisible) {
      this.welcomeDialogVisible = true;
    } else {
      this.welcomeDialogVisible = false;
    }
  },

  beforeDestroy() {
    if (this.loginPollingTimer) {
      clearInterval(this.loginPollingTimer);
      this.loginPollingTimer = null;
    }
  },

  async created() {
    this.closeLoginNewPageFunc();
    this.getRequireTokenData();
    this.getSharedGroups();

    // download region data
    this.$store.dispatch("region/getRegionData");

    let currentRouterPath = this.$route.path.replace(/\/$/, "") || "/";

    // Handle project sub-routes like /EI/line
    if (!this.projectPath.includes(currentRouterPath)) {
      const matchedBase = this.projectPath.find(
        pp => pp !== "/" && currentRouterPath.startsWith(pp + "/")
      );
      if (matchedBase) {
        currentRouterPath = matchedBase;
      }
    }

    if (this.projectPath.includes(currentRouterPath)) {
      this.$store.dispatch("getProjects");
    }

    if (process.env.VUE_APP_SUB_SPECIES === "rbm") {
      this.$store.dispatch("neuron/getDendritesIPLInfo");
    }
  }
};
</script>

<style lang="scss">
html {
  font-size: 13px;
}


.message-content :has(> ul:only-child, > ol:only-child) > ul,
.message-content :has(> ul:only-child, > ol:only-child) > ol,
.message-content > ul,
.message-content > ol {
  padding-left: 0px;
}

.v-application p {
  margin-bottom: 0;
  user-select: text !important;
  /* Force-enable text selection */
  -webkit-user-select: text !important;
  /* Safari */
  -moz-user-select: text !important;
  /* Firefox */
  -ms-user-select: text !important;
}


.app-bar {
  .v-toolbar__content {
    .v-btn {
      padding: 0 14px !important;
      font-size: 13px !important;
      font-family: Open Sans;
      font-weight: 400;
      font-style: normal;
      letter-spacing: 0;
      height: 32px;
      border-radius: 0;
    }

    .v-btn:nth-last-child(2),
    .v-btn:last-child {
      color: white;
      padding: 0 16px !important;
    }
  }
}

.login-btn {
  border-radius: 2px;
  margin: 30px 0 10px;

  .v-btn__content {
    font-size: 16px;
  }
}

.login-dialog-card {
  min-height: 300px;
  padding: 100px 30px;
  display: flex;
  justify-content: center;
  border-radius: 4px;
  box-shadow: 0px 0px 12px 0px rgba(0, 0, 0, 0.1) !important;

  .un-login-close {
    position: absolute;
    right: 5px;
    top: 5px;
  }

  .un-login-main {
    text-align: center;

    p:first-of-type {
      color: #ced4e4;
      text-align: center;
      font-size: 20px;
      margin: 0;
    }

    .register-account {
      margin: 0;
      color: #ced4e4;
      font-size: 13px;
      text-align: left;

      span {
        cursor: pointer;
        color: #7fbefa;
      }
    }

    .v-btn {
      font-size: 16px;
      margin: 10px 0;
      width: 100%;
    }
  }
}

.user-login {
  position: relative;
  line-height: 32px;

  .user-login-menu {
    position: absolute;
    width: 140px;
    right: 0;
    top: 36px;
    z-index: 9;
    padding-left: 0;
    transition: all 0.5s;

    li {
      font-size: 13px;
      padding-left: 15px;
      height: 40px;
      line-height: 40px;
      white-space: nowrap;
      border-top: 1px solid var(--10, rgba(223, 232, 255, 0.07));
      background: rgba(21, 28, 45, 0.3);
      backdrop-filter: blur(8px);
      color: #fff;
      opacity: 0.87;
      cursor: pointer;

      &:hover {
        opacity: 0.5;
      }
    }
  }
}

::-webkit-scrollbar {
  width: 6px;
  height: 4px;
  border-radius: 0;
}

::-webkit-scrollbar-track {
  background-color: rgba(241, 241, 241, 0.1);
}

::-webkit-scrollbar-thumb {
  border-radius: 0;
  background: #2d68c3;
}

::-webkit-scrollbar-button {
  display: none;
}

// ::-webkit-scrollbar-corner {
//   background: #d4d1d1;
// }

// ::-webkit-scrollbar-track-piece {
//   background-color: #d4d1d1;
//   border-radius: 3px;
// }
.v-dialog__content {
  z-index: 1000 !important;
}
</style>
