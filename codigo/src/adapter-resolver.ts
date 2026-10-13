import { OfxAdapter } from "./adapters/ofx.adapter.ts";
import { ExcelAdapter } from "./adapters/excel.adapter.ts";
import { CsvAdapter } from "./adapters/csv.adapter.ts";
import type { TransactionFileAdapter } from "./transaction-file-adapter.ts";

export const adapters: Record<string, TransactionFileAdapter> = {
  ofx: new OfxAdapter(),
  xlsx: new ExcelAdapter(),
  csv: new CsvAdapter(),
};
