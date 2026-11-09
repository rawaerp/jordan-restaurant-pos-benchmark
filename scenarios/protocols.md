# Protocols

Read [`00-rules.md`](00-rules.md) first. Every scenario uses the same 30-item test menu: 10 items with a modifier
(size, "no onions", extra), 5 combos, 15 plain items, prices between 0.5 and 12 JOD, Arabic names of 8–30 characters.

## S1 — Offline sale

1. Log in, open a shift, confirm the system is online (note how it shows this).
2. Disconnect the internet (unplug the router's WAN cable; keep the local network so the printer still works).
3. Ring 20 sales: 12 cash, 8 card, 6 of them with a modifier, 2 with a discount, 1 split payment. Note the time.
4. Print every receipt. Count printed vs expected.
5. Reconnect. Wait up to 5 minutes. Open the day report.
6. Record: `offline_completed`, `receipts_printed`, `missing_after_sync`, `duplicates_after_sync`, `sync_minutes`.

**Pass:** 20/20 completed, 20 receipts, 0 missing, 0 duplicates.

## S2 — Rush hour

1. Pre-write 40 orders (3–6 items each) on paper.
2. Record the screen (phone video of the tablet is fine, with a visible clock).
3. Start a 10-minute timer; ring the orders one after another as fast as is realistic.
4. For each order note the frame count from first tap to the receipt starting to print.
5. Record: `orders_completed`, `median_seconds`, `p95_seconds`, `stalls` (any freeze > 2 s), `errors`.

## S3 — Printer trouble

1. Start a sale, unplug the printer power, press pay.
2. Observe: is the sale saved? what does the screen say? is there a one-tap reprint?
3. Plug the printer in, retry. Check no duplicate sale was created.
4. Record: `sale_kept`, `clear_error`, `one_tap_retry`, `duplicate_created`.

## S4 — JoFotara unavailable

1. Enable JoFotara for a test taxpayer or the vendor's sandbox/demo (state which).
2. On the router, block `backend.jofotara.gov.jo`.
3. Ring 5 sales. Does the cashier wait? Note the extra seconds per sale vs normal.
4. Remove the block. Wait up to 15 minutes. Check all 5 invoices reached JoFotara **once each**.
5. Record: `cashier_blocked`, `extra_seconds_per_sale`, `invoices_sent_after_recovery`, `duplicate_invoices`.

## S5 — Arabic output

1. Print a receipt with the longest Arabic item name, a quantity of 12, a price 12.500 and a modifier line.
2. Print a kitchen ticket for an order containing that item with "بدون بصل".
3. Photograph both. Judge: letters joined, words in correct right-to-left order, numbers readable.
4. Record: `receipt_arabic_ok`, `kitchen_arabic_ok`, plus the photos as evidence.

## S6 — Time to first sale

1. Start the clock on the vendor's landing page.
2. Register, add 10 items, connect a printer, ring and print one sale.
3. Stop the clock. Count support contacts (chat, call, WhatsApp) needed.
4. Record: `minutes_to_first_sale`, `support_contacts`.
