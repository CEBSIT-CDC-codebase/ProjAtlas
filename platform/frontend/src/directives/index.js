import draggable from "./draggable.js";

// Custom directives
const directives = {
  draggable
};

// This pattern allows batch-registering directives
export default {
  install(Vue) {
    Object.keys(directives).forEach(key => {
      Vue.directive(key, directives[key]);
    });
  }
};
