import { readFile } from "node:fs/promises";
import { extname } from "node:path";
import { adapters } from "./adapter-resolver.ts";
import { TransactionImportService } from "./transaction-import-service.ts";

export async function importFile(path: string) {
  const ext = extname(path).slice(1).toLowerCase();
  const adapter = adapters[ext];
  if (!adapter) {
    throw new Error(`Formato não suportado: .${ext}`);
  }
  const service = new TransactionImportService();
  return service.import(await readFile(path), adapter);
}
