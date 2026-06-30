import { apiClient } from "../../lib/apiClient";
import type { Role, Setting, SettingUpsert, User, UserCreate } from "./types";

type ApiRole = {
  id: string;
  name: string;
  description: string | null;
  is_system: boolean;
};

type ApiUser = {
  id: string;
  supabase_user_id: string | null;
  role_id: string;
  email: string;
  full_name: string;
  phone: string | null;
  employee_code: string | null;
  is_active: boolean;
};

type ApiSetting = {
  id: string;
  key: string;
  value: Record<string, unknown>;
  is_public: boolean;
};

function mapRole(role: ApiRole): Role {
  return {
    id: role.id,
    name: role.name,
    description: role.description,
    isSystem: role.is_system
  };
}

function mapUser(user: ApiUser): User {
  return {
    id: user.id,
    supabaseUserId: user.supabase_user_id,
    roleId: user.role_id,
    email: user.email,
    fullName: user.full_name,
    phone: user.phone,
    employeeCode: user.employee_code,
    isActive: user.is_active
  };
}

function mapSetting(setting: ApiSetting): Setting {
  return {
    id: setting.id,
    key: setting.key,
    value: setting.value,
    isPublic: setting.is_public
  };
}

export async function listRoles(): Promise<Role[]> {
  const { data } = await apiClient.get<ApiRole[]>("/roles");
  return data.map(mapRole);
}

export async function listUsers(): Promise<User[]> {
  const { data } = await apiClient.get<ApiUser[]>("/users", {
    params: { include_inactive: true }
  });
  return data.map(mapUser);
}

export async function createUser(payload: UserCreate): Promise<User> {
  const { data } = await apiClient.post<ApiUser>("/users", {
    email: payload.email,
    full_name: payload.fullName,
    role_id: payload.roleId,
    phone: payload.phone || null,
    employee_code: payload.employeeCode || null,
    is_active: payload.isActive
  });
  return mapUser(data);
}

export async function updateUser(id: string, payload: Partial<UserCreate>): Promise<User> {
  const body: Record<string, unknown> = {};
  if (payload.fullName !== undefined) body.full_name = payload.fullName;
  if (payload.roleId !== undefined) body.role_id = payload.roleId;
  if (payload.phone !== undefined) body.phone = payload.phone || null;
  if (payload.employeeCode !== undefined) body.employee_code = payload.employeeCode || null;
  if (payload.isActive !== undefined) body.is_active = payload.isActive;
  const { data } = await apiClient.patch<ApiUser>(`/users/${id}`, body);
  return mapUser(data);
}

export async function deleteUser(id: string): Promise<void> {
  await apiClient.delete(`/users/${id}`);
}

export async function listSettings(): Promise<Setting[]> {
  const { data } = await apiClient.get<ApiSetting[]>("/settings");
  return data.map(mapSetting);
}

export async function upsertSetting(payload: SettingUpsert): Promise<Setting> {
  const { data } = await apiClient.put<ApiSetting>("/settings", {
    key: payload.key,
    value: payload.value,
    is_public: payload.isPublic
  });
  return mapSetting(data);
}

