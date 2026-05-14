const fs = require('fs');
const pdfjsLib = require('pdfjs-dist/legacy/build/pdf.js');

async function extract() {
  const data = new Uint8Array(fs.readFileSync('/Users/eduardosr/Documents/GitHub/ML63/Recursos/Gas Power/FE26137006909149.pdf'));
  const doc = await pdfjsLib.getDocument({data}).promise;
  let text = '';
  for (let i = 1; i <= doc.numPages; i++) {
    const page = await doc.getPage(i);
    const content = await page.getTextContent();
    text += content.items.map(item => item.str).join(' ') + ' ';
  }
  console.log("TEXT EXTRACTED:");
  const lines = text.split(' ');
  const kwIdx = lines.findIndex(l => l.includes('kWh'));
  console.log(text.substring(Math.max(0, text.indexOf('Consumo') - 200), text.indexOf('Consumo') + 500));
}
extract().catch(console.error);
