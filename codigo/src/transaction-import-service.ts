import type { Transaction } from "./transaction.ts";
import type { TransactionFileAdapter } from "./transaction-file-adapter.ts";

// Client: só conhece a interface, nunca o formato do arquivo
export class TransactionImportService {
  async import(content: Buffer, adapter: TransactionFileAdapter): Promise<Transaction[]> {
    const transactions = await adapter.parse(content);
    // validação, deduplicação e persistência ficariam aqui
    return transactions;
  }
}
