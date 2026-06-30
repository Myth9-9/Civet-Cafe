import type { AuthUser } from "./types";

const ACCESS_TOKEN_KEY = "civet.accessToken";
const REFRESH_TOKEN_KEY = "civet.refreshToken";
const USER_KEY = "civet.user";

export const authTokenStorage = {
  getAccessToken(): string | null {
    return window.localStorage.getItem(ACCESS_TOKEN_KEY);
  },
  getRefreshToken(): string | null {
    return window.localStorage.getItem(REFRESH_TOKEN_KEY);
  },
  getUser(): AuthUser | null {
    const rawUser = window.localStorage.getItem(USER_KEY);
    return rawUser ? (JSON.parse(rawUser) as AuthUser) : null;
  },
  setSession(accessToken: string, refreshToken: string, user: AuthUser): void {
    window.localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    window.localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    window.localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  clear(): void {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
    window.localStorage.removeItem(REFRESH_TOKEN_KEY);
    window.localStorage.removeItem(USER_KEY);
  }
};

