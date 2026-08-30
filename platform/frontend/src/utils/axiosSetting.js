import store from "@/store";
export default function axiosSettings(axios) {
  axios.defaults.baseURL = process.env.VUE_APP_USER_API;
  // axios.defaults.timeout = 5000;

  axios.interceptors.request.use(
    config => {
      // Request interceptor
      config.headers["Authorization"] = `Bearer ${localStorage.getItem(
        "access_token"
      )}`;
      return config;
    },
    error => {
      // Propagate the error to business code
      error.data = {};
      error.data.msg = "The server is abnormal. Please contact the administrator!";
      return Promise.resolve(error);
    }
  );

  axios.interceptors.response.use(
    response => {
      // Response interceptor
      const oldDate = localStorage.getItem("initial_time") || Date.now();
      if (oldDate - Date.now() > 12 * 60 * 60 * 1000) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("vuex");
        store.commit("setUserInfo", null);
        location.replace("/");
        // store.commit("setLoginFlag", true);
      }
      return response;
    },
    error => {
      const statusCode = error.response?.status;
      let msg;
      if (statusCode === 401) {
        msg = "Please log in first";
        store.commit("setLoginFlag", true);
      } else {
        msg = "Request timeout or server exception. Check the network or contact the administrator";
      }

      // Propagate the error to business code
      error.data = {};
      error.data.msg = msg;
      return Promise.resolve(error);
    }
  );
}
