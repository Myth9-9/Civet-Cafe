import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { addPayment, generateBill, getReceipt, listBills } from "./api";
import type { PaymentMethod } from "./types";

export const billingKeys = {
  bills: ["billing", "bills"] as const,
  receipt: (billId: string) => ["billing", "receipt", billId] as const
};

export function useBills() {
  return useQuery({
    queryKey: billingKeys.bills,
    queryFn: listBills
  });
}

export function useReceipt(billId: string | null) {
  return useQuery({
    queryKey: billingKeys.receipt(billId ?? ""),
    queryFn: () => getReceipt(billId ?? ""),
    enabled: billId !== null
  });
}

export function useGenerateBill() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: generateBill,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: billingKeys.bills });
    }
  });
}

export function useAddPayment() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      billId,
      payload
    }: {
      billId: string;
      payload: { method: PaymentMethod; amount: string; referenceNumber?: string };
    }) => addPayment(billId, payload),
    onSuccess: async (_bill, variables) => {
      await queryClient.invalidateQueries({ queryKey: billingKeys.bills });
      await queryClient.invalidateQueries({ queryKey: billingKeys.receipt(variables.billId) });
    }
  });
}

