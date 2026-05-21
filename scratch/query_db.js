const supabaseUrl = 'https://byqtsuskdbgwpyvyiprc.supabase.co';
const supabaseKey = 'sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx';

async function queryDB() {
    const headers = {
        'apikey': supabaseKey,
        'Authorization': `Bearer ${supabaseKey}`,
        'Content-Type': 'application/json'
    };

    try {
        console.log("Fetching live MJM movements...");
        const mjmRes = await fetch(`${supabaseUrl}/rest/v1/movimientos?concepto=ilike.*mjm*&order=fecha.asc`, { headers });
        const mjmMoves = await mjmRes.json();
        console.log(`\nFound ${mjmMoves.length} MJM movements in live database:`);
        mjmMoves.forEach(m => {
            console.log(`  - Date: ${m.fecha} | Concept: ${m.concepto} | Amount: ${m.importe}€ | Balance: ${m.saldo}€`);
        });

        console.log("\nFetching live PEDRO / SIMON / NOMINA movements (from 2024-09-01 to 2025-04-30)...");
        const pedroRes = await fetch(`${supabaseUrl}/rest/v1/movimientos?fecha=gte.2024-09-01&fecha=lte.2025-04-30&or=(concepto.ilike.*simon*,concepto.ilike.*nomina*,concepto.ilike.*girones*)&order=fecha.asc`, { headers });
        const pedroMoves = await pedroRes.json();
        console.log(`\nFound ${pedroMoves.length} porter-related movements in live database:`);
        pedroMoves.forEach(m => {
            console.log(`  - Date: ${m.fecha} | Concept: ${m.concepto} | Amount: ${m.importe}€ | Balance: ${m.saldo}€`);
        });

    } catch (e) {
        console.error("Error querying Supabase REST API:", e);
    }
}

queryDB();
