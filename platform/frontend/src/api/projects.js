import axios from "axios";
import axiosSettings from "@/utils/axiosSetting";
axiosSettings(axios);

function getProjectsInfo() {
  return axios.get("/public/projects");
}

export { getProjectsInfo };
