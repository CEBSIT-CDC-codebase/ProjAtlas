import axios from "axios";
import axiosSettings from "@/utils/axiosSetting";
axiosSettings(axios);

async function getGroupsFunc() {
  return await axios.get("user/groups");
}

async function getShareGroup(shareId) {
  return await axios.get(`public/share/${shareId}`).then(res => res.data.data);
}

async function getGroupDetailFunc(id) {
  return await axios.get("user/groups/" + id).then(res => res.data.data);
}

async function createOrCopyGroupFunc(body) {
  return await axios.post("user/groups", body);
}

async function updateGroupShareFunc(id, body) {
  return await axios.post("user/groups/" + id + "/share", body);
}

async function updateGroupFunc(id, body) {
  return await axios.put("user/groups/" + id, body);
}

async function deleteGroupFunc(id) {
  return await axios.delete("user/groups/" + id);
}

export {
  createOrCopyGroupFunc,
  deleteGroupFunc,
  getGroupsFunc,
  getGroupDetailFunc,
  getShareGroup,
  updateGroupShareFunc,
  updateGroupFunc
};
