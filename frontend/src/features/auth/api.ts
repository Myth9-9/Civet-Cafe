import { apiClient } from "../../lib/apiClient";
import type { LoginRequest, TokenPairResponse } from "./types";

type ApiAuthUser = {
  id: string;
  email: string;
  full_name: string;
  role_id: string;
  role_name: string;
  permissions: string[];
};

type ApiTokenPairResponse = {
  access_token: string;
  refresh_token: string;
  token_type: "bearer";
  expires_at: string;
  user: ApiAuthUser;
};

function mapTokenPair(response: ApiTokenPairResponse): TokenPairResponse {
  return {
    accessToken: response.access_token,
    refreshToken: response.refresh_token,
    tokenType: response.token_type,
    expiresAt: response.expires_at,
    user: {
      id: response.user.id,
      email: response.user.email,
      fullName: response.user.full_name,
      roleId: response.user.role_id,
      roleName: response.user.role_name,
      permissions: response.user.permissions
    }
  };
}

export async function login(payload: LoginRequest): Promise<TokenPairResponse> {
  const { data } = await apiClient.post<ApiTokenPairResponse>("/auth/login", payload);
  return mapTokenPair(data);
}

export async function logout(refreshToken: string): Promise<void> {
  await apiClient.post("/auth/logout", { refresh_token: refreshToken });
}

