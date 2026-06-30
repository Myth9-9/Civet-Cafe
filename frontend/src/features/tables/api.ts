import { apiClient } from "../../lib/apiClient";
import type { CafeTable, FloorSummary, TableCreate } from "./types";

type ApiTable = {
  id: string;
  table_number: string;
  floor: string;
  capacity: number;
  status: CafeTable["status"];
  created_at: string;
  updated_at: string;
};

type ApiFloorSummary = {
  floor: string;
  table_count: number;
  available_count: number;
  occupied_count: number;
  reserved_count: number;
  inactive_count: number;
};

function mapTable(table: ApiTable): CafeTable {
  return {
    id: table.id,
    tableNumber: table.table_number,
    floor: table.floor,
    capacity: table.capacity,
    status: table.status,
    createdAt: table.created_at,
    updatedAt: table.updated_at
  };
}

function mapFloor(summary: ApiFloorSummary): FloorSummary {
  return {
    floor: summary.floor,
    tableCount: summary.table_count,
    availableCount: summary.available_count,
    occupiedCount: summary.occupied_count,
    reservedCount: summary.reserved_count,
    inactiveCount: summary.inactive_count
  };
}

function tablePayload(payload: Partial<TableCreate>) {
  const body: Record<string, unknown> = {};
  if (payload.tableNumber !== undefined) body.table_number = payload.tableNumber;
  if (payload.floor !== undefined) body.floor = payload.floor;
  if (payload.capacity !== undefined) body.capacity = payload.capacity;
  if (payload.status !== undefined) body.status = payload.status;
  return body;
}

export async function listTables(): Promise<CafeTable[]> {
  const { data } = await apiClient.get<ApiTable[]>("/tables", {
    params: { include_inactive: true }
  });
  return data.map(mapTable);
}

export async function listFloors(): Promise<FloorSummary[]> {
  const { data } = await apiClient.get<ApiFloorSummary[]>("/tables/floors");
  return data.map(mapFloor);
}

export async function createTable(payload: TableCreate): Promise<CafeTable> {
  const { data } = await apiClient.post<ApiTable>("/tables", tablePayload(payload));
  return mapTable(data);
}

export async function updateTable(id: string, payload: Partial<TableCreate>): Promise<CafeTable> {
  const { data } = await apiClient.patch<ApiTable>(`/tables/${id}`, tablePayload(payload));
  return mapTable(data);
}

export async function deleteTable(id: string): Promise<void> {
  await apiClient.delete(`/tables/${id}`);
}

