import { useQuery } from "@tanstack/react-query";

import { getDailyReport, getMonthlyReport } from "./api";

export const reportKeys = {
  daily: (date: string) => ["reports", "daily", date] as const,
  monthly: (year: number, month: number) => ["reports", "monthly", year, month] as const
};

export function useDailyReport(reportDate: string) {
  return useQuery({
    queryKey: reportKeys.daily(reportDate),
    queryFn: () => getDailyReport(reportDate)
  });
}

export function useMonthlyReport(year: number, month: number) {
  return useQuery({
    queryKey: reportKeys.monthly(year, month),
    queryFn: () => getMonthlyReport(year, month)
  });
}

