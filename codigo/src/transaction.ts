export type TransactionType = "CREDIT" | "DEBIT";

export interface Transaction {
  date: string;
  description: string;
  amount: number;
  type: TransactionType;
}
