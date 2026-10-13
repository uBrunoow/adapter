import { importFile } from "./import-file.ts";

const path = process.argv[2];
try {
  console.log(await importFile(path));
} catch (error) {
  console.error(`✗ ${(error as Error).message}`);
  process.exitCode = 1;
}
