import sqlite3, time, json, os, statistics, platform
db = os.path.join(os.environ.get("TEMP", "."), "sqlite_bench.db")
if os.path.exists(db): os.remove(db)
c = sqlite3.connect(db); c.execute("pragma journal_mode=delete"); c.execute("pragma synchronous=full")   # default-safe settings of a desktop POS
c.execute("create table sale(id text primary key, body text)"); c.commit()
body = json.dumps({"items": [{"item_code": f"ITEM-{i}", "name": "شاورما دجاج", "qty": 2} for i in range(8)], "blob": "y" * 900}, ensure_ascii=False)
def st(a):
    a = sorted(a); q = lambda p: a[min(len(a) - 1, int(p / 100 * len(a)))]
    return {"n": len(a), "min": round(a[0], 2), "median": round(q(50), 2), "p95": round(q(95), 2), "max": round(a[-1], 2)}
w, r = [], []
for i in range(300):
    t = time.perf_counter(); c.execute("insert into sale values (?,?)", (f"s{i}", body)); c.commit(); w.append((time.perf_counter() - t) * 1000)
for i in range(300):
    t = time.perf_counter(); c.execute("select body from sale where id=?", (f"s{i}",)).fetchone(); r.append((time.perf_counter() - t) * 1000)
c.close(); os.remove(db)
print(json.dumps({"engine": "SQLite " + sqlite3.sqlite_version + " (journal=delete, synchronous=full)", "os": platform.platform(), "write_ms": st(w), "read_ms": st(r)}))
