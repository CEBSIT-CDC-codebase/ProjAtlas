import Vue from "vue";
import VueRouter from "vue-router";
import HomePage from "@/views/Index.vue";
import neuroVizTool from "../utils/neuroVizTool";
import store from "@/store";

Vue.use(VueRouter);

// Get the prototype's push function
const originalPush = VueRouter.prototype.push;
// Get the prototype's replace function
const originalReplace = VueRouter.prototype.replace;
// Override the prototype's push function
VueRouter.prototype.push = function push(location) {
  return originalPush.call(this, location).catch(err => err);
};
// Override the prototype's replace function
VueRouter.prototype.replace = function replace(location) {
  return originalReplace.call(this, location).catch(err => err);
};

const routes = [
  // 1. Base pages (fixed paths)
  {
    path: "/",
    name: "HomePage",
    component: HomePage
  },
  {
    path: "/userinfo",
    name: "userInfo",
    component: () => import("@/views/userInfo")
  },
  {
    path: "/download",
    name: "Download",
    component: () => import("@/views/DataDownload/DataDownload")
  },

  // 2. Special region/business paths (fixed paths)
  { path: "/pfc", name: "HomePage pfc", component: HomePage },
  { path: "/hy", name: "HomePage hy", component: HomePage },
  { path: "/lha", name: "HomePage LHA", component: HomePage },
  { path: "/hipp", name: "HomePage hipp", component: HomePage },
  { path: "/pvh_oxt", name: "HomePage pvh_oxt", component: HomePage },
  { path: "/cea", name: "HomePage cea", component: HomePage },
  
  { path: "/bla", name: "HomePage bla", component: HomePage },
  { path: "/cea2", name: "HomePage cea2", component: HomePage },
  { path: "/cm", name: "HomePage cm", component: HomePage },
  { path: "/md", name: "HomePage md", component: HomePage },
  { path: "/nac", name: "HomePage nac", component: HomePage },
  { path: "/pf", name: "HomePage pf", component: HomePage },
  { path: "/pvt", name: "HomePage pvt", component: HomePage },
  { path: "/rt", name: "HomePage rt", component: HomePage },
  { path: "/vpl", name: "HomePage vpl", component: HomePage },
  { path: "/vta", name: "HomePage vta", component: HomePage },

  { path: "/spcd", name: "HomePage spcd", component: HomePage },
  { path: "/EI", name: "HomePage ei", component: HomePage },
  { path: "/EI/line", name: "HomePage ei line", component: HomePage },
  { path: "/EI/neuron", name: "HomePage ei neuron", component: HomePage },
  { path: "/EI/region", name: "HomePage ei region", component: HomePage },
  {
    path: "/EI/cytoarchitecture",
    name: "HomePage ei cytoarchitecture",
    component: HomePage
  },
  { path: "/whole-cortex", name: "HomePage whole-cortex", component: HomePage },
  { path: "/rbm", name: "HomePage rbm", component: HomePage },
  { path: "/trimodal", name: "HomePage Trimodal", component: HomePage },

  // 3. Dynamic parameter path (placed last as a fallback)
  // Only reached when none of the above match
  {
    path: "/:dataType",
    name: "HomePage dataType",
    component: HomePage
  },
  // 4. Global 404 (optional)
  {
    path: "*",
    redirect: "/"
  }
];

const router = new VueRouter({
  mode: "history",
  base: process.env.VUE_APP_PUBLIC_PATH || "/",
  routes
});

const pathArr = [...store.state.projectPath];

function isActivePath(path) {
  if (pathArr.includes(path)) return true;
  // Match project sub-routes like /EI/line, /EI/neuron
  const projectBases = store.state.projectPath.filter(p => p !== "/");
  return projectBases.some(base => path.startsWith(base + "/"));
}

router.beforeEach((to, from, next) => {
  const path = to?.path;
  store.dispatch("checkAndLogout");
  if (!window.neuroViz && isActivePath(path)) {
    neuroVizTool.init(() => {
      store.commit("setNeuroVizReady", true);
    });
  } else if (window.neuroViz && !isActivePath(path)) {
    window.neuroViz.setVisibility(false);
  } else if (window.neuroViz && isActivePath(path)) {
    window.neuroViz.setVisibility(true);
  }
  next();
});

export default router;
