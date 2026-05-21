const fs = require('fs');
(async () => {
  const XLSX = await import('https://cdn.jsdelivr.net/npm/xlsx@0.18.5/xlsx.mjs');
  const buffer = fs.readFileSync('Recursos/Banco/Hasta 19 Mayo.xls');
  const wb = XLSX.read(buffer, { type: 'array', cellDates: true });
  const ws = wb.Sheets[wb.SheetNames[0]];
  const rows = XLSX.utils.sheet_to_json(ws, { header: 1 });
  console.log(rows[9]);
})();
