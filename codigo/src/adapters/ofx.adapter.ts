import type { Transaction } from "../transaction.ts";
import type { TransactionFileAdapter } from "../transaction-file-adapter.ts";

export class OfxAdapter implements TransactionFileAdapter {
  async parse(content: Buffer): Promise<Transaction[]> {
    const blocks = content.toString().split("<STMTTRN>").slice(1);
    return blocks.map((block) => {
      const tag = (name: string) => block.match(new RegExp(`<${name}>([^<\\r\\n]+)`))![1].trim();
      const value = Number(tag("TRNAMT"));
      const d = tag("DTPOSTED");
      return {
        date: `${d.slice(0, 4)}-${d.slice(4, 6)}-${d.slice(6, 8)}`,
        description: tag("MEMO"),
        amount: Math.abs(value),
        type: value < 0 ? "DEBIT" : "CREDIT",
      };
    });
  }
}
