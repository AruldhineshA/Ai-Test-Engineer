/**
 * Auth Context — Global authentication state.
 * Provides user, login, register, logout to all components.
 */

import { createContext, useState, useEffect } from "react";
import api from "../utils/api";
import { getToken, setToken, getUser, setUser, clearAuth } from "../utils/storage";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUserState] = useState(getUser());
  const [loading, setLoading] = useState(true);

  // On mount — verify token is still valid
  useEffect(() => {
    const token = getToken();
    if (token) {
      api.get("/auth/me")
        .then((res) => {
          setUserState(res.data);
          setUser(res.data);
        })
        .catch(() => {
          clearAuth();
          setUserState(null);
        })
        .finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (email, password) => {
    const res = await api.post("/auth/login", { email, password });
    setToken(res.data.access_token);
    setUser(res.data.user);
    setUserState(res.data.user);
    return res.data;
  };

  const register = async (email, fullName, password) => {
    const res = await api.post("/auth/register", {
      email,
      full_name: fullName,
      password,
    });
    setToken(res.data.access_token);
    setUser(res.data.user);
    setUserState(res.data.user);
    return res.data;
  };

  const logout = () => {
    clearAuth();
    setUserState(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
