          onmouseover="this.style.borderColor='var(--primary)'" onmouseout="this.style.borderColor='var(--border)'">
          <div style="font-size:28px;margin-bottom:8px">📄</div>
          <div style="font-weight:700;font-size:14px">Factura proveedor</div>
          <div style="font-size:12px;color:var(--text-muted);margin-top:4px">Pirtac, Perón, etc.</div>
        </div>
      </div>
      <div id="docsList" style="margin-top:20px"></div>
    </div>

    <div class="card">
      <details>
        <summary style="list-style:none;display:flex;align-items:center;justify-content:space-between;cursor:pointer;padding:4px 0">
          <div class="card-title" style="margin-bottom:0">🔗 Vincular facturas a movimientos</div>
          <span style="font-size:13px;color:var(--text-muted)">▼ Abrir</span>
        </summary>
        <div style="margin-top:16px">
          <p class="card-desc" style="margin-bottom:12px">Busca un movimiento bancario por concepto y añade la referencia de factura correspondiente.</p>
          <div style="display:flex;gap:8px;margin-bottom:12px">
            <input type="text" id="facturaSearchInput" placeholder="Buscar por concepto, ej: MJM"
              style="flex:1;padding:10px 14px;border:1.5px solid var(--border);border-radius:8px;font-size:14px;outline:none;font-family:inherit"
              oninput="buscarMovimientosFactura(this.value)">
            <button onclick="buscarMovimientosFactura(document.getElementById('facturaSearchInput').value)"
              style="padding:10px 18px;background:var(--primary);color:white;border:none;border-radius:8px;font-size:14px;font-weight:700;cursor:pointer;font-family:inherit">Buscar</button>
          </div>
          <div id="facturaSearchResults"></div>
        </div>
      </details>
    </div>

    <div class="card">
      <details>
        <summary
          style="list-style:none;display:flex;align-items:center;justify-content:space-between;cursor:pointer;padding:4px 0">
          <div class="card-title" style="margin-bottom:0">📋 Log de sesiones</div>
          <span style="font-size:13px;color:var(--text-muted)">▼ Ver registro</span>
        </summary>
        <div style="margin-top:16px">
          <div style="display:flex;gap:8px;margin-bottom:12px;align-items:center">
            <button onclick="loadSessionLog(0)"
              style="background:var(--bg);border:1px solid var(--border);padding:6px 14px;border-radius:6px;font-size:13px;cursor:pointer;font-family:inherit">⟳
              Actualizar</button>
            <span id="sessionLogInfo" style="font-size:12px;color:var(--text-muted)"></span>
          </div>
          <div id="sessionLog">
            <div style="color:var(--text-muted);font-size:14px">Haz clic en "Actualizar" para cargar el log</div>
          </div>
          <div id="sessionLogPager" style="display:flex;gap:8px;margin-top:12px;align-items:center"></div>
        </div>
      </details>
    </div>

  </div>

  </div>

  <footer>
    <div style="text-align:center; line-height: 2;">
      <div>CP Modesto Lafuente 63 · Datos reales · 28/04/2026</div>
      <div>Administración · <strong>Susana Fernández Robleda</strong></div>
      <div>Presidente · <strong>Eduardo Sánchez Ruiz</strong></div>
    </div>
  </footer>

  <script>
    const DATA = {
      "2026": [],
      "2025": []
    };

    function setInner(id, html) {
      const el = document.getElementById(id);
      if (el) {
        el.innerHTML = html;
        return true;
      }
      return false;
    }

    function switchTab(e, name) {
      document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.getElementById(name).classList.add('active');
      e.target.classList.add('active');
      if (name === 'admin-panel' && _isAdmin) loadAdminPanel();
    }

    function fmtNum(n) {
      if (n === null || n === undefined) return '0';
      return Math.round(Math.abs(n)).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }
    function fmtSaldo(n) {
      const val = Math.round(n);
      const sign = val > 0 ? '+' : (val < 0 ? '-' : '');
      return sign + Math.abs(val).toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
    }
    function fmtPres(p) {
      if (p === null || p === undefined) return '<span style="color:var(--text-muted)">Sin presupuestar</span>';
      const sign = p < 0 ? 'Coste: ' : 'Ingreso: +';
      return sign + fmtNum(p) + '€';
    }

    function progClass(cat) {
      if (cat === 'completado') return 'green';
      if (cat === 'progreso') return 'amber';
      return 'gray';
    }

    function _baseProjectHTML(p) {
      const obs = p.obs && p.obs.length > 0 ? `<div class="project-obs">${p.obs}</div>` : '';
      const bancoRef = p.banco_ref
        ? `<div class="project-bank" style="background:#ECFDF5; border:1px solid #10B981; color:#065F46; padding:6px 10px; border-radius:6px; font-size:11px; margin-top:8px">✅ <strong>Asiento Bancario:</strong> ${p.banco_ref}</div>`
        : (p.pres !== null && p.cat !== 'pendiente'
          ? `<div class="project-bank" style="background:#FFF7ED; border:1px solid #F59E0B; color:#9A3412; padding:6px 10px; border-radius:6px; font-size:11px; margin-top:8px">⚠️ <strong>Pendiente de auditoría:</strong> Sin cruce bancario</div>`
          : '');

      const presBanner = (p.pres !== null && p.pres !== undefined)
        ? `<div class="project-pres" style="margin-top:6px">📋 <strong>Presupuesto:</strong> ${fmtPres(p.pres)}</div>`
        : `<div class="project-nopres" style="margin-top:6px">📋 Sin presupuestar</div>`;
      const progPct = Math.round(p.progreso * 100);
      const icon = p.cat === 'completado' ? '✅' : p.cat === 'progreso' ? '⏳' : '📋';
      const cardAccent = p.cat === 'completado' ? 'border-left: 3px solid var(--secondary);'
        : p.cat === 'progreso' ? 'border-left: 3px solid var(--accent);'
          : 'border-left: 3px solid var(--border);';

      let meatball = '';
      let dragAttr = '';
      if (typeof _isAdmin !== 'undefined' && _isAdmin) {
        const uid = (p._id || p.nombre).replace(/[^a-zA-Z0-9]/g, '_');
        const menuId = 'menu_' + uid;
        dragAttr = `draggable="true" ondragstart="handleDragStart(event, '${p._id}')" ondragend="handleDragEnd(event)"`;
        meatball = `<button class="card-menu-btn" onclick="event.stopPropagation();toggleMenu('${menuId}')">⋮</button>
      <div class="card-menu-dropdown" id="${menuId}">
        <button class="card-menu-item" onclick="event.stopPropagation();closeMenus();openModal('${p._id || ''}')">✏️ Editar</button>
        <button class="card-menu-item danger" onclick="event.stopPropagation();closeMenus();confirmDel('${p._id || ''}')">🗑️ Eliminar</button>
      </div>`;
      }

      return `<div class="project-card" data-id="${p._id}" ${dragAttr} style="position:relative;${cardAccent} ${_isAdmin ? 'cursor: grab;' : ''}">
    ${meatball}
    <div class="project-card-header">
      <span class="project-icon">${icon}</span>
      <span class="project-name">${p.nombre}</span>
    </div>
    <div class="progress-bar"><div class="progress-fill ${progClass(p.cat)}" style="width:${progPct}%"></div></div>
    ${obs}
    ${bancoRef}
    ${presBanner}
  </div>`;
    }

    function renderProjectsByState(year, elemId) {
      const projects = DATA[year] || [];
      const progreso = projects.filter(p => p.cat === 'progreso').sort((a, b) => a.orden !== b.orden ? a.orden - b.orden : b.progreso - a.progreso);
      const completados = projects.filter(p => p.cat === 'completado').sort((a, b) => a.orden - b.orden);
      const pendientes = projects.filter(p => p.cat === 'pendiente').sort((a, b) => a.orden - b.orden);
      let html = '';
      if (progreso.length) html += `<details class="project-section" open><summary>⏳ En curso <span class="count">${progreso.length}</span></summary><div class="project-list" data-cat="progreso" ondragover="allowDrop(event)" ondrop="handleDrop(event)">${progreso.map(_baseProjectHTML).join('')}</div></details>`;
      if (pendientes.length) html += `<details class="project-section" open><summary>📅 Gastos previstos · Resto de 2026 <span class="count">${pendientes.length}</span></summary><div class="project-list" data-cat="pendiente" ondragover="allowDrop(event)" ondrop="handleDrop(event)">${pendientes.map(_baseProjectHTML).join('')}</div></details>`;
      if (completados.length) html += `<details class="project-section" open><summary>✓ Completados <span class="count">${completados.length}</span></summary><div class="project-list" data-cat="completado" ondragover="allowDrop(event)" ondrop="handleDrop(event)">${completados.map(_baseProjectHTML).join('')}</div></details>`;
      setInner(elemId, html);
    }

    let draggedProjectId = null;
    let draggedItem = null;

    function handleDragStart(e, id) {
      if (!_isAdmin) return;
      draggedProjectId = id;
      draggedItem = e.target.closest('.project-card');
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', id);
      setTimeout(() => draggedItem.style.opacity = '0.5', 0);
    }

    function handleDragEnd(e) {
      if (draggedItem) {
        draggedItem.style.opacity = '1';
      }
      draggedItem = null;
      draggedProjectId = null;
    }

    function allowDrop(e) {
      if (!_isAdmin) return;
      e.preventDefault();
      const list = e.target.closest('.project-list');
      if (!list) return;
      const afterElement = getDragAfterElement(list, e.clientY);
      if (afterElement == null) {
        list.appendChild(draggedItem);
      } else {
        list.insertBefore(draggedItem, afterElement);
      }
    }

    function getDragAfterElement(container, y) {
      const draggableElements = [...container.querySelectorAll('.project-card:not([style*="opacity: 0.5"])')];
      return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        if (offset < 0 && offset > closest.offset) {
          return { offset: offset, element: child };
        } else {
          return closest;
        }
      }, { offset: Number.NEGATIVE_INFINITY }).element;
    }

    async function handleDrop(e) {
      if (!_isAdmin) return;
      e.preventDefault();
      const list = e.target.closest('.project-list');
      if (!list) return;
      
      const newCat = list.getAttribute('data-cat');
      const cards = Array.from(list.querySelectorAll('.project-card'));
      const updates = cards.map((card, index) => {
        return {
          id: card.getAttribute('data-id'),
          orden: index,