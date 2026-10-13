import * as XLSX from "xlsx";
import type { Transaction } from "../transaction.ts";
import type { TransactionFileAdapter } from "../transaction-file-adapter.ts";

export class ExcelAdapter implements TransactionFileAdapter {
  async parse(content: Buffer): Promise<Transaction[]> {
    const sheet = XLSX.read(content).Sheets["Extrato"];
    const rows = XLSX.utils.sheet_to_json<Record<string, string>>(sheet, { raw: false });
    return rows.map((row) => {
      const [day, month, year] = row["Data"].split("/");
      return {
        date: `${year}-${month}-${day}`,
        description: row["Histórico"],
        amount: Number(row["Valor"].replace(".", "").replace(",", ".")),
        type: row["Tipo"] === "Débito" ? "DEBIT" : "CREDIT",
      };
    });
  }
}
