export type Category = {
  id: string;
  name: string;
  description: string | null;
  displayOrder: number;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
};

export type MenuItem = {
  id: string;
  categoryId: string;
  sku: string;
  name: string;
  description: string | null;
  price: string;
  taxRate: string;
  isAvailable: boolean;
  displayOrder: number;
  createdAt: string;
  updatedAt: string;
};

export type CategoryCreate = {
  name: string;
  description?: string;
  displayOrder: number;
  isActive: boolean;
};

export type MenuItemCreate = {
  categoryId: string;
  sku: string;
  name: string;
  description?: string;
  price: string;
  taxRate: string;
  isAvailable: boolean;
  displayOrder: number;
};

