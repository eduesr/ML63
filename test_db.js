const { createClient } = require('@supabase/supabase-js');
const db = createClient('https://byqtsuskdbgwpyvyiprc.supabase.co', 'sb_publishable_LVuLdmu3YUa0HhMZGdBKtg_VHPZUizx');
async function run() {
  const { data, error } = await db.from('proyectos').select('*').limit(1);
  console.log(data);
}
run();
