import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createUser,
  deleteUser,
  listRoles,
  listSettings,
  listUsers,
  updateUser,
  upsertSetting
} from "./api";
import type { SettingUpsert, UserCreate } from "./types";

export const adminKeys = {
  roles: ["admin", "roles"] as const,
  users: ["admin", "users"] as const,
  settings: ["admin", "settings"] as const
};

export function useRoles() {
  return useQuery({ queryKey: adminKeys.roles, queryFn: listRoles });
}

export function useUsers() {
  return useQuery({ queryKey: adminKeys.users, queryFn: listUsers });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: UserCreate) => createUser(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: adminKeys.users });
    }
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<UserCreate> }) => updateUser(id, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: adminKeys.users });
    }
  });
}

export function useDeleteUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteUser,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: adminKeys.users });
    }
  });
}

export function useSettings() {
  return useQuery({ queryKey: adminKeys.settings, queryFn: listSettings });
}

export function useUpsertSetting() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: SettingUpsert) => upsertSetting(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: adminKeys.settings });
    }
  });
}

