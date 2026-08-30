import store from "@/store";
export default function axiosSettings(axios) {
  axios.interceptors.request.use(
    config => {
      // Request interceptor
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
      return response;
    },
    error => {
      const statusCode = error.response?.status;
      let msg;
      if (statusCode === 401) {
        msg = "Please login first";
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
