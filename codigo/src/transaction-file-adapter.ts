import type { Transaction } from "./transaction.ts";

// Target: o contrato que todo adaptador cumpre
export interface TransactionFileAdapter {
  parse(content: Buffer): Promise<Transaction[]>;
}
