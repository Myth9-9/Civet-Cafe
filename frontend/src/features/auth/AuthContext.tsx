import { useMutation } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { useMemo, useState } from "react";

import { login as loginRequest, logout as logoutRequest } from "./api";
import { AuthContext, type AuthContextValue } from "./authContextValue";
import { authTokenStorage } from "./tokenStorage";
import type { AuthUser } from "./types";

type AuthProviderProps = {
  children: ReactNode;
};

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<AuthUser | null>(() => authTokenStorage.getUser());

  const loginMutation = useMutation({
    mutationFn: loginRequest,
    onSuccess: (session) => {
      authTokenStorage.setSession(session.accessToken, session.refreshToken, session.user);
      setUser(session.user);
    }
  });

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: user !== null,
      isLoggingIn: loginMutation.isPending,
      login: async (payload) => {
        await loginMutation.mutateAsync(payload);
      },
      logout: async () => {
        const refreshToken = authTokenStorage.getRefreshToken();
        authTokenStorage.clear();
        setUser(null);
        if (refreshToken) {
          await logoutRequest(refreshToken);
        }
      }
    }),
    [loginMutation, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
