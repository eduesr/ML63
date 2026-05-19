import re

print("--- STARTING SURGICAL MERGE OF FEATURES ---")

# 1. Read stable HTML
with open('scratch/ML63_stable.html', 'r', encoding='utf-8') as f:
    stable_content = f.read()

# 2. Read current HTML to get the exact Coeficientes block
with open('ML63.html', 'r', encoding='utf-8') as f:
    current_content = f.read()

# Extract Coeficientes HTML block
coef_html_match = re.search(r'<!-- Coeficientes de Participación -->.*?<!-- Resumen de totales al pie -->.*?</div>\s*</div>', current_content, re.DOTALL)
if coef_html_match:
    coef_html = coef_html_match.group(0)
    # The last </div> belongs to the card, so let's keep only the inner content and add back a closing div for the Coeficientes block
    # Let's verify by checking the exact end
    print("✓ Successfully extracted Coeficientes HTML block.")
else:
    # Fallback to hardcoded HTML if regex fails
    print("✕ Coeficientes HTML match failed. Using fallback HTML.")
    coef_html = """
        <!-- Coeficientes de Participación -->
        <div style="margin-top: 24px; border-top: 1px solid var(--border); padding-top: 20px; width: 100%;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; width: 100%;">
            <div style="font-size: 14px; font-weight: 700; color: var(--text-soft); text-transform: uppercase; letter-spacing: 0.5px; display: flex; align-items: center; gap: 6px;">
              <span>🏠 Reparto de Coeficientes</span>
            </div>
            <!-- Buscador y Controles -->
            <div style="display: flex; gap: 8px; align-items: center;">
              <input type="text" id="coefSearch" placeholder="Buscar propiedad..." style="padding: 6px 12px; font-size: 12px; border: 1px solid var(--border); border-radius: 6px; outline: none; width: 140px; transition: border-color 0.2s;" oninput="filterCoeficientes()">
              <select id="coefSort" style="padding: 6px 10px; font-size: 12px; border: 1px solid var(--border); border-radius: 6px; outline: none; cursor: pointer; background: white;" onchange="filterCoeficientes()">
                <option value="planta">Por Planta</option>
                <option value="coef-desc">Mayor Coef.</option>
                <option value="coef-asc">Menor Coef.</option>
              </select>
            </div>
          </div>
          
          <!-- Flex Wrap Grid Container (100% width) -->
          <div id="coefFlexContainer" style="display: flex; flex-wrap: wrap; gap: 10px; width: 100%;">
            <div style="text-align: center; color: var(--text-muted); font-size: 13px; padding: 20px; width: 100%;">Cargando coeficientes...</div>
          </div>

          <!-- Resumen de totales al pie -->
          <div style="margin-top: 16px; display: flex; justify-content: space-between; font-size: 12px; font-weight: 700; color: var(--text-muted); border-top: 1px solid var(--border); padding-top: 10px; width: 100%;">
            <span id="coefCountLabel">0 propiedades</span>
            <span id="coefSumLabel">Total: 0.00%</span>
          </div>
        </div>
"""

# Extract Coeficientes JS code
coef_js_match = re.search(r'// Guardar propiedades globalmente para poder filtrar reactivamente en el cliente.*?// 5\. Tesorería 2025', current_content, re.DOTALL)
if coef_js_match:
    coef_js = coef_js_match.group(0)
    # Remove the trailing '// 5. Tesorería 2025' so we don't duplicate it
    coef_js = coef_js.replace('// 5. Tesorería 2025', '').strip()
    print("✓ Successfully extracted Coeficientes JS block.")
else:
    print("✕ Coeficientes JS match failed. Using fallback JS.")
    coef_js = """
        // Guardar propiedades globalmente para poder filtrar reactivamente en el cliente
        window._allPropiedades = propsData || [];

        // Definir la función de filtrado y renderizado reactivo
        window.filterCoeficientes = function() {
          const q = (document.getElementById('coefSearch')?.value || '').toLowerCase().trim();
          const sort = document.getElementById('coefSort')?.value || 'planta';
          const data = window._allPropiedades || [];
          
          let filtered = data.filter(p => {
            const nom = (p.nombre || '').toLowerCase();
            const cod = (p.codigo || '').toLowerCase();
            const not = (p.notas || '').toLowerCase();
            return nom.includes(q) || cod.includes(q) || not.includes(q);
          });

          if (sort === 'planta') {
            const orderMap = { 'sotano': 0, 'local': 1, 'vivienda': 2 };
            filtered.sort((a, b) => {
              const typeA = a.tipo || 'vivienda';
              const typeB = b.tipo || 'vivienda';
              const oA = orderMap[typeA] ?? 2;
              const oB = orderMap[typeB] ?? 2;
              if (oA !== oB) return oA - oB;
              return (a.codigo || '').localeCompare(b.codigo || '', 'es', { numeric: true });
            });
          } else if (sort === 'coef-desc') {
            filtered.sort((a, b) => (parseFloat(b.coeficiente) || 0) - (parseFloat(a.coeficiente) || 0));
          } else if (sort === 'coef-asc') {
            filtered.sort((a, b) => (parseFloat(a.coeficiente) || 0) - (parseFloat(b.coeficiente) || 0));
          }

          let cardsHtml = '';
          let sumCoef = 0;
          
          filtered.forEach(p => {
            const val = parseFloat(p.coeficiente) || 0;
            sumCoef += val;
            
            let label = p.nombre || p.codigo;
            
            // Determinar el índice de planta/nivel
            let levelIndex = 0;
            if (p.tipo !== 'sotano' && p.tipo !== 'local') {
              const match = label.match(/^([1-8])/);
              if (match) {
                levelIndex = parseInt(match[1], 10);
              }
            }

            // Mapear el nivel al color correspondiente en la paleta global (secuencia del 1 al 7)
            const levelColors = [
              { bg: 'var(--c1-light)', text: 'var(--c1)', border: 'rgba(239, 68, 68, 0.25)' },   // Nivel 0 (Sótano y Locales) -> Rojo (c1)
              { bg: 'var(--c2-light)', text: 'var(--c2)', border: 'rgba(245, 158, 11, 0.25)' },  // Planta 1 -> Naranja/Ocre (c2)
              { bg: 'var(--c3-light)', text: 'var(--c3)', border: 'rgba(16, 185, 129, 0.25)' },  // Planta 2 -> Verde (c3)
              { bg: 'var(--c4-light)', text: 'var(--c4)', border: 'rgba(14, 165, 233, 0.25)' },  // Planta 3 -> Azul Cielo (c4)
              { bg: 'var(--c5-light)', text: 'var(--c5)', border: 'rgba(139, 92, 246, 0.25)' },  // Planta 4 -> Violeta (c5)
              { bg: 'var(--c6-light)', text: 'var(--c6)', border: 'rgba(99, 102, 241, 0.25)' },  // Planta 5 -> Indigo (c6)
              { bg: 'var(--c7-light)', text: 'var(--c7)', border: 'rgba(20, 184, 166, 0.25)' }   // Planta 6 -> Teal (c7)
            ];

            // Selección cíclica para plantas superiores (Plantas 7 y 8)
            const colorObj = levelColors[levelIndex % levelColors.length];
            const bg = colorObj.bg;
            const titleColor = colorObj.text;
            const coefColor = colorObj.text;
            const borderStyle = `1px solid ${colorObj.border}`;

            const coefText = val > 0 ? `${val.toFixed(2)}%` : 'Comun.';
            
            cardsHtml += `
              <div style="flex: 1 1 calc(10% - 10px); min-width: 105px; max-width: 140px; background: ${bg}; border: ${borderStyle}; border-radius: 8px; padding: 12px 10px; display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; box-shadow: 0 1px 2px rgba(0,0,0,0.02); transition: all 0.2s;" onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.05)';" onmouseout="this.style.transform='none'; this.style.boxShadow='0 1px 2px rgba(0,0,0,0.02)';">
                <div style="font-size: 16px; font-weight: 800; color: ${titleColor}; margin-bottom: 4px; letter-spacing: -0.2px;">
                  ${label}
                </div>
                <div style="font-size: 16px; font-weight: 700; color: ${coefColor}; font-family: monospace;">
                  ${coefText}
                </div>
              </div>
            `;
          });

          const flexEl = document.getElementById('coefFlexContainer');
          if (flexEl) {
            flexEl.innerHTML = cardsHtml || '<div style="text-align: center; padding: 24px; color: var(--text-muted); font-style: italic; width: 100%;">Ninguna propiedad coincide con la búsqueda.</div>';
          }
          
          const countLabel = document.getElementById('coefCountLabel');
          if (countLabel) countLabel.innerText = `${filtered.length} propiedades`;
          
          const sumLabel = document.getElementById('coefSumLabel');
          if (sumLabel) sumLabel.innerText = `Total: ${sumCoef.toFixed(2)}%`;
        };

        // Renderizado inicial
        window.filterCoeficientes();
"""

# Extract properties database fetch call
props_db_fetch = """        console.log('Cargando propiedades...');
        const { data: propsData, error: propsError } = await db.from('propiedades').select('*');
        if (propsError) console.error('Error fetching propiedades:', propsError);
"""

# 3. Perform surgical replacements on stable content

# A. Insert database fetch right at the start of loadDashboardData()
load_dash_str = "async function loadDashboardData() {\n      try {"
if load_dash_str in stable_content:
    stable_content = stable_content.replace(
        load_dash_str,
        f"{load_dash_str}\n{props_db_fetch}"
    )
    print("✓ Successfully inserted properties database fetch call.")
else:
    print("✕ Could not locate loadDashboardData in stable HTML.")

# B. Insert HTML block right inside the first Tesorería card (after the kpi-grid-split closing div)
target_html_place = """          <div class="kpi kpi-mejora">
            <div class="kpi-label">🔨 Mejoras del Edificio (proyectos)</div>
            <div class="kpi-value" id="gastoMejora2026">---€</div>
            <div class="kpi-sub">proyectos de la hoja de ruta</div>
          </div>
        </div>"""

if target_html_place in stable_content:
    stable_content = stable_content.replace(
        target_html_place,
        f"{target_html_place}\n        {coef_html}"
    )
    print("✓ Successfully inserted Coeficientes HTML block.")
else:
    print("✕ Could not locate target HTML place for Coeficientes.")

# C. Insert JS filtering logic right before // 5. Tesorería 2025
target_js_place = "        // 5. Tesorería 2025"
if target_js_place in stable_content:
    stable_content = stable_content.replace(
        target_js_place,
        f"{coef_js}\n\n        {target_js_place}"
    )
    print("✓ Successfully inserted Coeficientes JS block.")
else:
    print("✕ Could not locate target JS place.")

# D. Upgrade version numbers in titles and headers from (v11) to (v12)
stable_content = stable_content.replace('(v11)', '(v12)')
print("✓ Successfully bumped version to v12 in titles and header.")

# E. Write the merged result to ML63.html and ML63_V12.html
with open('ML63.html', 'w', encoding='utf-8') as f:
    f.write(stable_content)
print("✓ Successfully wrote merged content to ML63.html (overwriting).")

with open('ML63_V12.html', 'w', encoding='utf-8') as f:
    f.write(stable_content)
print("✓ Successfully saved versioned copy to ML63_V12.html.")

print("--- MERGE PROCESS COMPLETED SUCCESSFULLY! ---")
