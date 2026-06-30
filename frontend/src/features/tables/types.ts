export type TableStatus = "available" | "occupied" | "reserved" | "inactive";

export type CafeTable = {
  id: string;
  tableNumber: string;
  floor: string;
  capacity: number;
  status: TableStatus;
  createdAt: string;
  updatedAt: string;
};

export type FloorSummary = {
  floor: string;
  tableCount: number;
  availableCount: number;
  occupiedCount: number;
  reservedCount: number;
  inactiveCount: number;
};

export type TableCreate = {
  tableNumber: string;
  floor: string;
  capacity: number;
  status: TableStatus;
};

