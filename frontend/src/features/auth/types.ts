export type AuthUser = {
  id: string;
  email: string;
  fullName: string;
  roleId: string;
  roleName: string;
  permissions: string[];
};

export type LoginRequest = {
  email: string;
  password: string;
};

export type TokenPairResponse = {
  accessToken: string;
  refreshToken: string;
  tokenType: "bearer";
  expiresAt: string;
  user: AuthUser;
};

