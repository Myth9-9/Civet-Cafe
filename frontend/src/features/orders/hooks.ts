import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { addOrderItem, createOrder, listOrders, transitionOrder } from "./api";
import type { AddOrderItem, OrderCreate, OrderStatus } from "./types";

export const orderKeys = {
  orders: ["orders"] as const
};

export function useOrders() {
  return useQuery({
    queryKey: orderKeys.orders,
    queryFn: listOrders
  });
}

export function useCreateOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: OrderCreate) => createOrder(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: orderKeys.orders });
    }
  });
}

export function useAddOrderItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ orderId, payload }: { orderId: string; payload: AddOrderItem }) =>
      addOrderItem(orderId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: orderKeys.orders });
    }
  });
}

export function useTransitionOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ orderId, status }: { orderId: string; status: OrderStatus }) =>
      transitionOrder(orderId, status),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: orderKeys.orders });
    }
  });
}

