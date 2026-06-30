import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { createTable, deleteTable, listFloors, listTables, updateTable } from "./api";
import type { TableCreate } from "./types";

export const tableKeys = {
  tables: ["tables"] as const,
  floors: ["tables", "floors"] as const
};

export function useTables() {
  return useQuery({
    queryKey: tableKeys.tables,
    queryFn: listTables
  });
}

export function useFloors() {
  return useQuery({
    queryKey: tableKeys.floors,
    queryFn: listFloors
  });
}

export function useCreateTable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: TableCreate) => createTable(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: tableKeys.tables });
      await queryClient.invalidateQueries({ queryKey: tableKeys.floors });
    }
  });
}

export function useUpdateTable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<TableCreate> }) =>
      updateTable(id, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: tableKeys.tables });
      await queryClient.invalidateQueries({ queryKey: tableKeys.floors });
    }
  });
}

export function useDeleteTable() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteTable,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: tableKeys.tables });
      await queryClient.invalidateQueries({ queryKey: tableKeys.floors });
    }
  });
}

