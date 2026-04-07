/**
 * Storage utilities — Token and user data in localStorage.
 */

const TOKEN_KEY = "ait_access_token";
const USER_KEY = "ait_user";

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (token) => localStorage.setItem(TOKEN_KEY, token);
export const removeToken = () => localStorage.removeItem(TOKEN_KEY);

export const getUser = () => {
  const data = localStorage.getItem(USER_KEY);
  return data ? JSON.parse(data) : null;
};
export const setUser = (user) => localStorage.setItem(USER_KEY, JSON.stringify(user));
export const removeUser = () => localStorage.removeItem(USER_KEY);

export const clearAuth = () => {
  removeToken();
  removeUser();
};
