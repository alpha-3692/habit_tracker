"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User } from "@/types";
import { authApi, LoginPayload, RegisterPayload } from "@/lib/api/auth";

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  isLoading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  signup: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // Restore session from localStorage if present
    const storedToken = localStorage.getItem("habitforge_access_token");
    if (storedToken) {
      setAccessToken(storedToken);
      authApi
        .getMe(storedToken)
        .then((userData) => setUser(userData))
        .catch(() => {
          localStorage.removeItem("habitforge_access_token");
          localStorage.removeItem("habitforge_refresh_token");
          setAccessToken(null);
          setUser(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (payload: LoginPayload) => {
    const data = await authApi.login(payload);
    setAccessToken(data.access_token);
    setUser(data.user);
    localStorage.setItem("habitforge_access_token", data.access_token);
    localStorage.setItem("habitforge_refresh_token", data.refresh_token);
  };

  const signup = async (payload: RegisterPayload) => {
    const data = await authApi.register(payload);
    setAccessToken(data.access_token);
    setUser(data.user);
    localStorage.setItem("habitforge_access_token", data.access_token);
    localStorage.setItem("habitforge_refresh_token", data.refresh_token);
  };

  const logout = () => {
    setAccessToken(null);
    setUser(null);
    localStorage.removeItem("habitforge_access_token");
    localStorage.removeItem("habitforge_refresh_token");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        accessToken,
        isLoading,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
