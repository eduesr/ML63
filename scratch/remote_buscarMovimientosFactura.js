async function buscarMovimientosFactura(query) {
      const q = (query || '').trim();
      const el = document.getElementById('facturaSearchResults');
      if (!el) return;
      if (q.length < 2) { el.innerHTML = ''; return; }
      el.innerHTML = '<div style="color:var(--text-muted);font-size:13px">Buscando...</div>';
      const { data, error } = await db.from('movimientos')
        .select('id, fecha, concepto, importe, factura_ref')
        .ilike('concepto', `%${q}%`)
        .order('fecha', { ascending: false })
        .limit(30);
      if (error || !data?.length) {
        el.innerHTML = '<div style="color:var(--text-muted);font-size:13px">Sin resultados</div>';
        return;
      }
      el.innerHTML = `
        <table style="width:100%;border-collapse:collapse;font-size:13px">
          <thead><tr style="background:#F8FAFC">
            <th style="padding:8px 10px;text-align:left;border-bottom:2px solid #E2E8F0;color:var(--text-muted);font-weight:600">Fecha</th>
            <th style="padding:8px 10px;text-align:left;border-bottom:2px solid #E2E8F0;color:var(--text-muted);font-weight:600">Concepto</th>
            <th style="padding:8px 10px;text-align:right;border-bottom:2px solid #E2E8F0;color:var(--text-muted);font-weight:600">Importe</th>
            <th style="padding:8px 10px;text-align:left;border-bottom:2px solid #E2E8F0;color:var(--text-muted);font-weight:600">Nº Factura</th>
            <th style="padding:8px 10px;border-bottom:2px solid #E2E8F0"></th>
          </tr></thead>
          <tbody>${data.map(m => `
            <tr style="border-bottom:1px solid #F1F5F9" id="mrow_${m.id}">
              <td style="padding:8px 10px;white-space:nowrap">${m.fecha}</td>
              <td style="padding:8px 10px;color:var(--text-soft)">${m.concepto}</td>
              <td style="padding:8px 10px;text-align:right;font-weight:700;color:${m.importe < 0 ? '#EF4444' : '#10B981'}">${m.importe.toFixed(2).replace('.', ',')}€</td>
              <td style="padding:8px 10px">
                <input type="text" id="fref_${m.id}" value="${m.factura_ref || ''}"
                  placeholder="Ej: 7717"
                  style="width:100px;padding:5px 8px;border:1.5px solid #E2E8F0;border-radius:6px;font-size:13px;font-family:inherit;outline:none">
              </td>
              <td style="padding:8px 10px">
                <button onclick="guardarFacturaRef('${m.id}')"
                  style="background:#EEF2FF;color:var(--primary);border:none;padding:5px 12px;border-radius:6px;font-size:12px;font-weight:700;cursor:pointer;font-family:inherit">
                  Guardar
                </button>
              </td>
            </tr>`).join('')}
          </tbody>
        </table>`;
    }