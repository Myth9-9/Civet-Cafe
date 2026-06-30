import { apiClient } from "../../lib/apiClient";
import type { Category, CategoryCreate, MenuItem, MenuItemCreate } from "./types";

type ApiCategory = {
  id: string;
  name: string;
  description: string | null;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

type ApiMenuItem = {
  id: string;
  category_id: string;
  sku: string;
  name: string;
  description: string | null;
  price: string;
  tax_rate: string;
  is_available: boolean;
  display_order: number;
  created_at: string;
  updated_at: string;
};

function mapCategory(category: ApiCategory): Category {
  return {
    id: category.id,
    name: category.name,
    description: category.description,
    displayOrder: category.display_order,
    isActive: category.is_active,
    createdAt: category.created_at,
    updatedAt: category.updated_at
  };
}

function mapMenuItem(item: ApiMenuItem): MenuItem {
  return {
    id: item.id,
    categoryId: item.category_id,
    sku: item.sku,
    name: item.name,
    description: item.description,
    price: item.price,
    taxRate: item.tax_rate,
    isAvailable: item.is_available,
    displayOrder: item.display_order,
    createdAt: item.created_at,
    updatedAt: item.updated_at
  };
}

function categoryPayload(payload: CategoryCreate) {
  return {
    name: payload.name,
    description: payload.description || null,
    display_order: payload.displayOrder,
    is_active: payload.isActive
  };
}

function menuItemPayload(payload: MenuItemCreate) {
  return {
    category_id: payload.categoryId,
    sku: payload.sku,
    name: payload.name,
    description: payload.description || null,
    price: payload.price,
    tax_rate: payload.taxRate,
    is_available: payload.isAvailable,
    display_order: payload.displayOrder
  };
}

export async function listCategories(): Promise<Category[]> {
  const { data } = await apiClient.get<ApiCategory[]>("/menu/categories", {
    params: { include_inactive: true }
  });
  return data.map(mapCategory);
}

export async function createCategory(payload: CategoryCreate): Promise<Category> {
  const { data } = await apiClient.post<ApiCategory>("/menu/categories", categoryPayload(payload));
  return mapCategory(data);
}

export async function updateCategory(
  categoryId: string,
  payload: Partial<CategoryCreate>,
): Promise<Category> {
  const body: Record<string, unknown> = {};
  if (payload.name !== undefined) body.name = payload.name;
  if (payload.description !== undefined) body.description = payload.description || null;
  if (payload.displayOrder !== undefined) body.display_order = payload.displayOrder;
  if (payload.isActive !== undefined) body.is_active = payload.isActive;
  const { data } = await apiClient.patch<ApiCategory>(
    `/menu/categories/${categoryId}`,
    body,
  );
  return mapCategory(data);
}

export async function deleteCategory(categoryId: string): Promise<void> {
  await apiClient.delete(`/menu/categories/${categoryId}`);
}

export async function listMenuItems(): Promise<MenuItem[]> {
  const { data } = await apiClient.get<ApiMenuItem[]>("/menu/items", {
    params: { include_unavailable: true }
  });
  return data.map(mapMenuItem);
}

export async function createMenuItem(payload: MenuItemCreate): Promise<MenuItem> {
  const { data } = await apiClient.post<ApiMenuItem>("/menu/items", menuItemPayload(payload));
  return mapMenuItem(data);
}

export async function updateMenuItem(
  itemId: string,
  payload: Partial<MenuItemCreate>,
): Promise<MenuItem> {
  const body: Record<string, unknown> = {};
  if (payload.categoryId !== undefined) body.category_id = payload.categoryId;
  if (payload.sku !== undefined) body.sku = payload.sku;
  if (payload.name !== undefined) body.name = payload.name;
  if (payload.description !== undefined) body.description = payload.description || null;
  if (payload.price !== undefined) body.price = payload.price;
  if (payload.taxRate !== undefined) body.tax_rate = payload.taxRate;
  if (payload.isAvailable !== undefined) body.is_available = payload.isAvailable;
  if (payload.displayOrder !== undefined) body.display_order = payload.displayOrder;
  const { data } = await apiClient.patch<ApiMenuItem>(`/menu/items/${itemId}`, body);
  return mapMenuItem(data);
}

export async function deleteMenuItem(itemId: string): Promise<void> {
  await apiClient.delete(`/menu/items/${itemId}`);
}
