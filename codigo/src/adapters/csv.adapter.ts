import type { Transaction } from "../transaction.ts";
import type { TransactionFileAdapter } from "../transaction-file-adapter.ts";

export class CsvAdapter implements TransactionFileAdapter {
  async parse(content: Buffer): Promise<Transaction[]> {
    const [, ...lines] = content.toString().trim().split("\n");
    return lines.map((line) => {
      const [date, description, value] = line.split(";");
      const amount = Number(value);
      return {
        date,
        description,
        amount: Math.abs(amount),
        type: amount < 0 ? "DEBIT" : "CREDIT",
      };
    });
  }
}
