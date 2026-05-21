const fs = require('fs');
const html = fs.readFileSync('ML63.html', 'utf8');
const urlMatch = html.match(/supabase\.createClient\('([^']+)',\s*'([^']+)'\)/);
if (!urlMatch) { console.error("No url/key"); process.exit(1); }
const url = urlMatch[1];
const key = urlMatch[2];

fetch(`${url}/rest/v1/movimientos?select=fecha,concepto,importe,saldo&order=fecha.desc&limit=10`, {
  headers: { 'apikey': key, 'Authorization': `Bearer ${key}` }
}).then(r => r.json()).then(console.log).catch(console.error);
