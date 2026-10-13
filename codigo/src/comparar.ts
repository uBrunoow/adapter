import { isDeepStrictEqual } from "node:util";
import { importFile } from "./import-file.ts";

const [ofx] = await importFile("data/extrato.ofx");
const [excel] = await importFile("data/extrato.xlsx");
console.log("OFX:  ", ofx);
console.log("Excel:", excel);
console.log(isDeepStrictEqual(ofx, excel) ? "✓ mesmo objeto Transaction" : "✗ objetos diferentes");
