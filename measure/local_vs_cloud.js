// Paste into the browser console on any page of the origin you want to test (a throw-away IndexedDB is used and
// deleted afterwards - nothing of the site's own data is touched). Measures, on THIS device:
//   1) local store: one IndexedDB transaction per record (what an offline-first POS does per sale), 2.6 KB sale-like record
//   2) a network round trip to an uncached endpoint of the same origin (what a cloud-only POS pays per call)
// Keep the tab visible while it runs: background tabs are throttled and distort the numbers.
(async () => {
  const CLOUD_URL = '/api/method/ping';           // change to an uncached endpoint of the system you are testing
  const N = 300, CLOUD_N = 30;
  const items = Array.from({length: 8}, (_, i) => ({item_code: 'ITEM-' + i, item_name: 'شاورما دجاج ' + i, qty: 2, rate: 2.5, amount: 5, modifiers: ['بدون بصل', 'زيادة ثوم'], note: 'x'.repeat(60)}));
  const sale = {id: '', created: Date.now(), items, payments: [{mode: 'Cash', amount: 40}], totals: {net: 34.48, tax: 5.52, grand: 40}, blob: 'y'.repeat(900)};
  const stats = a => { a = [...a].sort((x, y) => x - y); const q = p => a[Math.min(a.length - 1, Math.floor(p / 100 * a.length))]; return {n: a.length, min: +a[0].toFixed(2), median: +q(50).toFixed(2), p95: +q(95).toFixed(2), max: +a[a.length - 1].toFixed(2)}; };
  const db = await new Promise((res, rej) => { const r = indexedDB.open('pos_bench_tmp', 1); r.onupgradeneeded = () => r.result.createObjectStore('sale_queue', {keyPath: 'id'}); r.onsuccess = () => res(r.result); r.onerror = () => rej(r.error); });
  const run = (mode, fn) => new Promise((res, rej) => { const t = db.transaction('sale_queue', mode); const s = t.objectStore('sale_queue'); const rq = fn(s); t.oncomplete = () => res(rq && rq.result); t.onerror = () => rej(t.error); });
  await run('readwrite', s => s.put({...sale, id: 'warm'}));
  const w = [], r = [], c = [];
  for (let i = 0; i < N; i++) { const t0 = performance.now(); await run('readwrite', s => s.put({...sale, id: 's' + i})); w.push(performance.now() - t0); }
  for (let i = 0; i < N; i++) { const t0 = performance.now(); await run('readonly', s => s.get('s' + i)); r.push(performance.now() - t0); }
  db.close(); indexedDB.deleteDatabase('pos_bench_tmp');
  for (let i = 0; i < CLOUD_N; i++) { const t0 = performance.now(); const x = await fetch(CLOUD_URL + '?_=' + Date.now() + '_' + i, {cache: 'no-store'}); await x.text(); c.push(performance.now() - t0); await new Promise(z => setTimeout(z, 150)); }
  const out = {origin: location.origin, visible: document.visibilityState, cores: navigator.hardwareConcurrency, ua: navigator.userAgent, record_bytes: JSON.stringify(sale).length,
               local_write_ms: stats(w), local_read_ms: stats(r), cloud_roundtrip_ms: stats(c)};
  console.log(JSON.stringify(out, null, 2));
  return out;
})();
