const fs = require('fs');

const sql = fs.readFileSync('carga_inicial_movimientos.sql', 'utf8');
const lines = sql.split('\n');
const moves = [];
for (const line of lines) {
  const match = line.match(/\('([^']+)',\s*'([^']+)',\s*([^,]+),\s*([^,]+),\s*'([^']+)'\)/);
  if (match) {
    moves.push({
      _iso: match[1],
      concepto: match[2],
      importe: parseFloat(match[3]),
      saldo: parseFloat(match[4])
    });
  }
}

const isRecurring = (concepto) => {
  const c = (concepto || '').toUpperCase();
  const keywords = [
    'NATURGY', 'IBERDROLA', 'CURENERGIA', 'GAS POWER', 'MADRID DISTRIBUCION',
    'CANAL ISABEL', 'ISTA', 'TECHEM',
    'MJM', 'LIMPIEZA', 'PILAR', 'PREVENT', 'VANESSA',
    'ALFREDO SANCHEZ', 'FINCAS', 'HONORARIOS', 'ADMINISTRACION',
    'NOMINA', 'TGSS', 'SEGURIDAD SOCIAL', 'IRPF', 'MUTUA', 'QUIRON', 'PREVENCION',
    'COMISION', 'INTERES', 'IVA SOBRE', 'LIQUIDACION', 'MANTENIMIENTO DE CUENTA',
    'SEGURO', 'ALLIANZ', 'MAPFRE', 'CASER', 'OCASO',
    'LASSER', 'PRISMA', 'MULTISERVICIOS', 'EXTINTOR', 'IBEREXT', 'RIESGOS', 'LOPD', 'PROTECCION DATOS',
    'ASCENSOR', 'ORONA', 'THYSSEN', 'SCHINDLER', 'FAIN',
    'RECIBO', 'CUOTA', 'DEVOLUCION', 'REMESAS', 'TALONARIO', 'PROVISION'
  ];
  return keywords.some(k => c.includes(k));
};

let completedProjects = [];
moves.forEach(m => {
  if (m.importe >= 0) return;
  if (m.importe > -50) return;
  if (isRecurring(m.concepto)) return;
  let year = parseInt((m._iso || '').split('-')[0]);
  if (isNaN(year) || year >= 2025) return;
  
  completedProjects.push({
    year: year,
    nombre: m.concepto,
    pres: Math.abs(m.importe),
    _iso: m._iso
  });
});

const html = fs.readFileSync('ML63.html', 'utf8');
const dataMatch = html.match(/const DATA = (\{[\s\S]+?\});/);
let DATA = {};
if (dataMatch) {
  DATA = eval('(' + dataMatch[1] + ')');
}

Object.keys(DATA).forEach(year => {
  DATA[year].forEach(p => {
    if (p.progreso >= 1) {
      completedProjects.push({ ...p, year, pres: Math.abs(p.pres||0), _iso: year + '-01-01' });
    }
  });
});

let totalInversion = 0;
let totalPresidencia = 0;
const threshold = '2022-03-28';

completedProjects.forEach(p => {
  totalInversion += p.pres;
  if (p._iso >= threshold) {
    totalPresidencia += p.pres;
  }
});

console.log('Total:', totalInversion);
console.log('Desde presidencia:', totalPresidencia);

