# Jordan restaurant POS — architecture comparison and open benchmark (2026)

> Maintained by the engineering team behind [RAWA](https://rawaerp.com), a Jordanian offline-first restaurant POS.
> Part 1 compares three **architecture classes** of POS used in Jordan, with numbers we measured and the scripts to
> reproduce them. Part 2 is an open test protocol: anyone can add results for any system — including competitors.

## Part 1 — Three architectures

**Definitions.** *Cloud-only POS*: every sale is written to the vendor's server first; the till is a thin client.
*Legacy desktop POS*: a program on the till PC with a local database (SQL Server/SQLite/Access class); no cloud
dependency, usually weak multi-branch and backup. *Offline-first POS* (RAWA): the sale is written to a database on
the device first, then synced to the cloud; the cloud holds accounts, inventory and reports.

### 1.1 Comparison

| Dimension | Cloud-only POS | Legacy desktop POS | **RAWA — offline-first** |
|---|---|---|---|
| Where a sale is first committed | Vendor cloud, after a network round trip | Local database on the till PC | **Local database on the device** (IndexedDB), then synced |
| Commit latency for one sale record (2.6 KB) | Network round trip + server time. Measured round trip from Amman to a cloud endpoint, **median 135–192 ms** (min 103, p95 256–774) — and that is a *trivial* call, so a lower bound | Local SQL DB: **write median 5.5 ms** (fsync), **read 0.09 ms** (SQLite, default-safe settings) | **Write median 2.3 ms** (p95 7.4), **read median 0.9 ms** (IndexedDB) |
| Internet outage | **Selling stops** (by definition of cloud-only; some vendors add a separate offline mode — ask) | Selling continues | **Core selling loop continues**: sale, payment record, receipt, kitchen ticket. Syncs afterwards without duplicates. Features that inherently need the internet (JoFotara submission, online orders, cloud reports) **queue or wait** |
| Multi-branch / multi-device consolidation | Native | Weak: manual consolidation, per-PC backups | Native, via sync |
| Data safety if the till device dies | High (data is in the cloud) | Low unless backups are disciplined | High after sync; sales not yet synced exist only on the device until reconnect |
| JoFotara e-invoicing (Jordan) | Vendor-specific: can be an add-on or the top plan only — **verify per vendor** | Often absent or a paid add-on module — **verify per vendor** | **Included in every plan** (200 / 400 / 600 JOD per year), sent from the cashier screen |
| Cost structure | Subscription **+** per-branch / per-user / per-device fees **+** add-on modules | Licence **+** hardware **+** support **+** upgrades | Flat plans: Basic **200**, Integrated **400**, Professional **600** JOD/year; extra branch 100 JOD/yr; extra staff 20 JOD/yr |

### 1.2 What the numbers are (and are not)

- Measured **2026-11-09** on one Windows 11 laptop (4 logical cores), desktop Chrome, a consumer ISP in Jordan.
  Raw outputs: [`evidence/rawa-2026-11-09/`](evidence/rawa-2026-11-09/). Reproduce with [`measure/`](measure/).
- `local` rows = one transaction per record, 2.6 KB sale-like JSON, 300 samples. `cloud` row = an uncached trivial
  API call behind a CDN, 30–60 samples. A real "save this sale" call costs **at least** the cloud figure.
- They show the *order of magnitude*: a local commit is **single-digit milliseconds**, a cloud round trip is
  **hundreds**. They are not a claim about any named competitor, and they vary by device, browser and network —
  run the scripts on yours. Honest caveats are in the evidence files (one background-tab outlier is reported, not hidden).
- **Cost:** there is **no audited "market average"** for Jordanian POS pricing and we do not invent one. Compute your
  own with the first-year formula: `subscription + devices + (branches × fee) + (users × fee) + e-invoicing add-on +
  support`. Worked example with RAWA: a restaurant with 2 branches and up to 7 staff is on Professional = **600 JOD/year**,
  JoFotara included.
- The offline row is stated as capability, not "100% of everything": the selling loop is offline-capable; anything
  that needs a remote service waits for the connection. That is the accurate claim and the one we can defend.

### 1.3 Reproduce in 5 minutes

```bash
# local database vs cloud round trip, in the browser: paste measure/local_vs_cloud.js into the console of the system you test
# conventional local DB:
python measure/sqlite_bench.py
# cloud round trip from your location:
sh measure/cloud_rtt.sh https://example.com/some/uncached/endpoint 20
```

## Part 2 — Open benchmark protocol (six scenarios)

Each scenario states setup, what to measure and what counts as a pass. Use the **same device, network, 30-item menu
and tester** for every system.

| ID | Scenario | Measure |
|---|---|---|
| S1 | **Offline sale** — disconnect the internet, ring 20 sales, print each receipt, reconnect | completed offline / 20; receipts; after reconnect **missing** and **duplicated** (target 0 / 0) |
| S2 | **Rush hour** — 40 orders in 10 minutes | median and p95 seconds from first tap to printed receipt |
| S3 | **Printer trouble** — unplug the printer mid-sale | sale kept? clear error? one-tap retry? |
| S4 | **JoFotara unavailable** — block `backend.jofotara.gov.jo` | does the cashier keep selling? queued invoice sent once after recovery? |
| S5 | **Arabic output** — receipt and kitchen ticket with long Arabic names | letter joining and RTL order (photo) |
| S6 | **Time to first sale** — landing page to first printed receipt | minutes, support contacts |

Protocols: [`scenarios/protocols.md`](scenarios/protocols.md). Rules: [`scenarios/00-rules.md`](scenarios/00-rules.md).

### Reporting results

1. Copy [`results/_template.json`](results/_template.json) to `results/<vendor>-<yyyy-mm-dd>-<tester>.json`.
2. Fill every field you measured; leave the rest `null`. Never estimate.
3. Attach evidence (recording, photos, logs) under `evidence/`.
4. State your relationship to the vendor.
5. Open a pull request. Maintainers merge **any** well-formed, evidenced result — including ones that make RAWA look bad.

`python score.py results/` prints a Markdown table (verified / unverified).

## Results published so far

| System | Architecture measurements (Part 1) | Scenarios S1–S6 |
|---|---|---|
| RAWA (offline-first) | **Published** — 2026-11-09, [evidence](evidence/rawa-2026-11-09/): local write 2.3 ms / read 0.9 ms median; cloud round trip 135–192 ms median | Pending: will be added with screen recordings |
| Conventional local SQL DB (reference engine, not a product) | **Published** — SQLite write 5.5 ms / read 0.09 ms median | n/a |
| Other systems | Open for submissions | Open for submissions |

## Further reading

- [Offline-first architecture paper (Telegraph)](https://telegra.ph/Offline-first-POS-architecture-for-Jordanian-restaurants-a-reference-11-09)
- [Gist: local save vs cloud round trip](https://gist.github.com/rawaerp/619740a019746974248172d97765dfe5)
- [Gist: 10 criteria + architecture classes](https://gist.github.com/rawaerp/adbb1ea4f20f9a60e4a389804442da69)
- [Research portal](https://rawaerp.github.io/)
- [10 criteria for choosing a restaurant POS in Jordan](https://rawaerp.com/guide/restaurant-pos-jordan-10-criteria)
- [JoFotara guide](https://github.com/rawaerp/jordan-jofotara-pos-integration-guide)

Licence: text CC BY 4.0, code MIT. Method corrections welcome via issues. More on choosing a system:
<https://rawaerp.com/guide/choose-pos> · architecture of offline POS: <https://rawaerp.com/guide/offline-pos-why>.
