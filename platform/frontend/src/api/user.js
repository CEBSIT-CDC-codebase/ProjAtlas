import axios from "axios";
import axiosSettings from "@/utils/axiosSetting";
axiosSettings(axios);

function validateUser() {
  return axios.get("/user/info");
}

export { validateUser };
