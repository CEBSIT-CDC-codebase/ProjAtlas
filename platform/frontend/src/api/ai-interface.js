import axios from "axios";
import axiosSettings from "@/utils/aiAxiosSetting";

const instance = axios.create({
  baseURL: process.env.VUE_APP_AI_API
});
axiosSettings(instance);

function fetchGetUser(email) {
  return instance.get(`/get-user/${email}`);
}

function fetchAddUser(user) {
  return instance.post(`/add-user`, user);
}

function fetchUpdateUser(userId, user) {
  return instance.put(`/update-user/${userId}`, user);
}

function fetchDeleteUser(userId) {
  return instance.delete(`/delete-user/${userId}`);
}

function fetchGetMessages(sessionId) {
  return instance.get(`/get-messages/${sessionId}`);
}

function fetchGetMessage(messageId) {
  return instance.get(`/get-message/${messageId}`);
}

function fetchAddMessage(message) {
  return instance.post(`/add-message`, message);
}

function fetchUpdateMessage(messageId, message) {
  return instance.put(`/update-message/${messageId}`, message);
}

function fetchDeleteMessage(messageId) {
  return instance.delete(`/delete-message/${messageId}`);
}

function fetchGetSessions(userId) {
  return instance.get(`/get-sessions/${userId}`);
}

function fetchGetSession(sessionId) {
  return instance.get(`/get-session/${sessionId}`);
}

function fetchAddSession(session) {
  return instance.post(`/add-session`, session);
}

function fetchUpdateSession(sessionId, session) {
  return instance.put(`/update-session/${sessionId}`, session);
}

function fetchDeleteSession(sessionId) {
  return instance.delete(`/delete-session/${sessionId}`);
}

export {
  fetchGetUser,
  fetchAddUser,
  fetchUpdateUser,
  fetchDeleteUser,
  fetchGetMessages,
  fetchGetMessage,
  fetchAddMessage,
  fetchUpdateMessage,
  fetchDeleteMessage,
  fetchGetSessions,
  fetchGetSession,
  fetchAddSession,
  fetchUpdateSession,
  fetchDeleteSession
};
