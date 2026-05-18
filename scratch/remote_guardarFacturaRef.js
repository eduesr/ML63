async function guardarFacturaRef(id) {
      const val = document.getElementById('fref_' + id)?.value.trim() || null;
      const { error } = await db.from('movimientos').update({ factura_ref: val }).eq('id', id);
      if (error) { toast('Error al guardar: ' + error.message, 'err'); return; }
      const row = document.getElementById('mrow_' + id);
      if (row) row.style.background = '#ECFDF5';
      setTimeout(() => { if (row) row.style.background = ''; }, 1500);
      toast('Referencia guardada ✓', 'ok');
    }