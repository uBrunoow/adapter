import * as XLSX from "xlsx";

// Gera data/extrato.xlsx com a mesma movimentação do OFX
const sheet = XLSX.utils.aoa_to_sheet([
  ["Data", "Histórico", "Valor", "Tipo"],
  ["05/10/2026", "Pagamento fornecedor", "150,00", "Débito"],
]);
const book = XLSX.utils.book_new();
XLSX.utils.book_append_sheet(book, sheet, "Extrato");
XLSX.writeFile(book, "data/extrato.xlsx");
