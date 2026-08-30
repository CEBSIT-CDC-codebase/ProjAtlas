import Vue from "vue";
import Vuetify from "vuetify/lib/framework";
import { icons } from "./icons.js";

Vue.use(Vuetify);

export default new Vuetify({
  icons: {
    ...icons,
    iconFont: "md"
  },
  theme: {
    dark: true,
    light: true,
    themes: {
      dark: {
        primary: "#151c2d",
        secondary: "#0b101c",
        accent: "#1f283e",
        background: "#2d68c3",
        "primary-text": "#ced4e4",
        "primary-bar": "#283652",
        "primary-light": "#7fbefa",
        "primary-light-1": "#A5ABB9",
        "accent-1": "#ffffff",
        "accent-2": "#f5f8ff",
        "accent-3": "#343f5c",
        "accent-4": "#76e6ff",
        "accent-5": "#383838",
        "accent-6": "#303c56",
        "accent-7": "#7f8490",
        "accent-8": "#FFC42C",
        "accent-9": "#151a27",
        "border-light": "#4e5570"
      }
    }
  }
});
