import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import vuetify from "./plugins/vuetify";
import "@fontsource/open-sans";
import "./styles/font.css";
import "@mdi/font/css/materialdesignicons.css";
import directives from "./directives";

if (process.env["VUE_APP_MODE"] === "production") {
  // Optional analytics (Matomo). Enable only by setting VUE_APP_ANALYTICS_URL in your
  // own .env; leave it unset to disable tracking entirely (recommended for public/forked
  // deployments so no data is sent to any third-party host).
  if (process.env.VUE_APP_ANALYTICS_URL && ["mouse", "monkey"].indexOf(process.env.VUE_APP_TARGET) !== -1) {
    var _paq = (window._paq = window._paq || []);
    /* tracker methods like "setCustomDimension" should be called before "trackPageView" */
    _paq.push(["trackPageView"]);
    _paq.push(["enableLinkTracking"]);
    (function() {
      var u = process.env.VUE_APP_ANALYTICS_URL;
      _paq.push(["setTrackerUrl", u + "matomo.php"]);
      if (process.env.VUE_APP_TARGET === "mouse") {
        _paq.push(["setSiteId", "1"]);
      } else if (process.env.VUE_APP_TARGET === "monkey") {
        _paq.push(["setSiteId", "11"]);
      }
      var d = document,
        g = d.createElement("script"),
        s = d.getElementsByTagName("script")[0];
      g.async = true;
      g.src = u + "matomo.js";
      s.parentNode.insertBefore(g, s);
    })();
  }
}

Vue.config.productionTip = false;
Vue.use(directives);

new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount("#app");
