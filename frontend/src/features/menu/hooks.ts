import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createCategory,
  createMenuItem,
  deleteCategory,
  deleteMenuItem,
  listCategories,
  listMenuItems,
  updateCategory,
  updateMenuItem
} from "./api";
import type { CategoryCreate, MenuItemCreate } from "./types";

export const menuKeys = {
  categories: ["menu", "categories"] as const,
  items: ["menu", "items"] as const
};

export function useCategories() {
  return useQuery({
    queryKey: menuKeys.categories,
    queryFn: listCategories
  });
}

export function useMenuItems() {
  return useQuery({
    queryKey: menuKeys.items,
    queryFn: listMenuItems
  });
}

export function useCreateCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CategoryCreate) => createCategory(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: menuKeys.categories });
    }
  });
}

export function useUpdateCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<CategoryCreate> }) =>
      updateCategory(id, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: menuKeys.categories });
    }
  });
}

export function useDeleteCategory() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteCategory,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: menuKeys.categories });
      await queryClient.invalidateQueries({ queryKey: menuKeys.items });
    }
  });
}

export function useCreateMenuItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: MenuItemCreate) => createMenuItem(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: menuKeys.items });
    }
  });
}

export function useUpdateMenuItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<MenuItemCreate> }) =>
      updateMenuItem(id, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: menuKeys.items });
    }
  });
}

export function useDeleteMenuItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteMenuItem,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: menuKeys.items });
    }
  });
}

