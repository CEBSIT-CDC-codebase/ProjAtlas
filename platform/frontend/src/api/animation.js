import axios from "axios";
import axiosSettings from "@/utils/axiosSetting";
axiosSettings(axios);

async function getAnimationsFunc() {
  return await axios.get("user/animations");
}

async function createAnimationsFunc(body) {
  return await axios.post("user/animations", body);
}

async function updateAnimationsFunc(id, body) {
  return await axios.put("user/animations/" + id, body);
}

async function deleteAnimationsFunc(id) {
  return await axios.delete("user/animations/" + id);
}

export {
  getAnimationsFunc,
  createAnimationsFunc,
  updateAnimationsFunc,
  deleteAnimationsFunc
};
