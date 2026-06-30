export type Role = {
  id: string;
  name: string;
  description: string | null;
  isSystem: boolean;
};

export type User = {
  id: string;
  supabaseUserId: string | null;
  roleId: string;
  email: string;
  fullName: string;
  phone: string | null;
  employeeCode: string | null;
  isActive: boolean;
};

export type Setting = {
  id: string;
  key: string;
  value: Record<string, unknown>;
  isPublic: boolean;
};

export type UserCreate = {
  email: string;
  fullName: string;
  roleId: string;
  phone?: string;
  employeeCode?: string;
  isActive: boolean;
};

export type SettingUpsert = {
  key: string;
  value: Record<string, unknown>;
  isPublic: boolean;
};

