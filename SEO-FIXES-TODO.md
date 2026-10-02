# SEO fixes — owner to-do

Items from the 2 Oct 2026 SEO crawl that need a value, a decision or an account only the owner has.
Everything else in `SEO-FIXES.md` has been done in the repo (see "What was changed" at the end).

> **Important — how this repo works.** This repository holds the *built* HTML of the site (an export
> from a Next.js project), not the source. There is no build step here, so the fixes were made
> directly in the HTML files, with small scripts in `tools/`. **If the site is ever rebuilt from the
> original Next.js source and re-uploaded, these fixes will be overwritten** unless the same changes
> are made in that source too.
>
> Before every commit run: `python3 tools/apply-partials.py` then `python3 tools/check-site.py`.

---

## 1. Owner actions (accounts and settings)

| # | Action | Where |
|---|---|---|
| 1.1 | ~~Confirm the non-www → www redirect is 308.~~ **Already 308** (checked 2 Oct 2026: `https://adarshprojects.co.in/` → 308 → `https://www.adarshprojects.co.in/`). Nothing to do. | Vercel → Domains |
| 1.2 | Verify the site in Google Search Console. Use a **Domain property** for `adarshprojects.co.in` (DNS TXT record) — it covers www and non-www and needs no code. If you prefer an HTML-tag property instead, send the `google-site-verification` code and it will be added to every page `<head>`. | Search Console + DNS |
| 1.3 | After deploy, submit `https://www.adarshprojects.co.in/sitemap.xml` in Search Console, and request indexing for the home page and the five project pages. | Search Console |
| 1.4 | Supply analytics IDs (see §3). | — |
| 1.5 | After deploy, check that `https://www.adarshprojects.co.in/projects/adarsh-savana-phase-3` (no slash) and `https://www.adarshprojects.co.in/index.html` now 308 to the slash / root URL (`vercel.json` sets `cleanUrls` and `trailingSlash`). | Browser |

## 2. RERA number conflict (Task 2) — confirm before anything else

`PRM/KA/RERA/1251/446/PR/311224/007335` is shown **both** as the site's *K-RERA agent registration*
and as the *project* RERA number of **Adarsh Rosewood**. The `/PR/` pattern is a project registration,
so the footer use is probably wrong. Please confirm:

- [ ] The K-RERA **agent** registration number of Adarsh Projects / IamHere Software Labs (format usually `PRM/KA/RERA/1251/…/AG/…`).
- [ ] The Adarsh Rosewood **project** RERA number.

Where it appears (each fix is a find-and-replace of the number in these files):

| Use | File(s) |
|---|---|
| Agent number, sitewide footer | `partials/footer.html` (one line) → then run `python3 tools/apply-partials.py` to stamp all pages |
| Agent number, contact page body | `contact/index.html` ("K-RERA registration" section) |
| Rosewood project number (visible copy, FAQ and JSON-LD `additionalProperty` "RERA Number") | `projects/adarsh-rosewood/index.html` (4 places) |
| Rosewood project number (review post) | `blog/adarsh-rosewood-bellandur-review/index.html` (3 places) |

The About page no longer prints the number; it points to the footer.

## 3. Analytics and conversion tracking (Task 3)

Support is in `assets/js/site.js` → `CONFIG` block. Each tag loads only when its ID is filled in,
after the first scroll/tap (or 8 s), so nothing blocks rendering. Fill in:

| Variable | Example | Note |
|---|---|---|
| `GA4_ID` | `G-XXXXXXXXXX` | Use this **or** `GTM_ID`, not both (double counting). |
| `GTM_ID` | `GTM-XXXXXXX` | If you use GTM, add GA4 and the Pixel inside GTM instead. |
| `META_PIXEL_ID` | `123456789012345` | |
| `CLARITY_ID` | `abcd123xyz` | Optional. |
| `GSC_VERIFICATION` | — | Not needed if you verify by DNS (§1.2). |

Events sent: `lead_form_submit` (GA4/GTM) and `LeadFormSubmit` (Pixel, custom) when a lead form posts
successfully; `generate_lead` (GA4/GTM) and `Lead` (Pixel standard event) on `/thank-you/`.
Mark `generate_lead` as a key event in GA4 and use `Lead` for Meta optimisation.
After editing `site.js`, run `python3 tools/apply-partials.py` so pages get the new `?v=` hash.

> These are not Vercel environment variables: a static site with no build step cannot read them,
> so the IDs live in `site.js`. They are public by nature (they ship to every browser anyway).

## 4. Unconfirmed project data (Task 9)

The values below show as "To be confirmed", "Confirm on K-RERA", "On request" or "Not published" on
the project pages. They were **not** filled in. Supply any you can confirm (with the source) and they
will be updated. Placeholder values are now **left out of the JSON-LD** (e.g. `Possession: To be
confirmed` no longer appears in structured data); they still show on the page.

| Project (file) | Unconfirmed fields |
|---|---|
| Adarsh Parkland Phase 2 — `projects/adarsh-parkland-phase-2/index.html` (27 placeholders) | Starting price; per-config price (2.5 BHK, 3 BHK); rate per sq ft; possession / completion date; Phase 2 land and units; towers and floors; kitchen spec; electrical and fitting brands; booking amount; stage-wise payment schedule; khata type; land conversion / plan approval; encumbrance certificate; rental yield |
| Adarsh Rosewood — `projects/adarsh-rosewood/index.html` (31) | Starting price; price range and per-config prices (2 & 3 BHK, east/west facing); rate per sq ft; possession; land area; launch date; fitting brands; booking amount; stage-wise schedule; khata type; land conversion / plan approval; encumbrance certificate; rental yield; **RERA number (see §2)** |
| Adarsh Savana Phase 3 — `projects/adarsh-savana-phase-3/index.html` (62) | Possession; Phase 3 land area; Phase 3 plot count; **Phase 3 RERA number** (only Phase I `…/201001/003613` is listed); prices for Ruby, Diamond and Premium plots; water supply; power; sewage; permitted construction (FAR, height); compound wall and gate; sale agreement; infrastructure milestones; registration; DC conversion; encumbrance certificate; bank approvals; locality price trend; resale rates in earlier Savana phases |
| Adarsh Tropica Phase 2 — `projects/adarsh-tropica-phase-2/index.html` (33) | Starting price; per-config prices (2.5 & 3 BHK); rate per sq ft; possession; exact address; Phase 2 land area; units; towers and floors; launch date; fitting brands; booking amount; stage-wise schedule; khata type; land conversion / plan approval; encumbrance certificate; bank approvals; rental yield |
| Adarsh Welkin Park — `projects/adarsh-welkin-park/index.html` (40) | Starting price / project price (flats and villas, east/west facing); possession; land area; units; tower count; fitting brands; booking amount; stage-wise schedule; khata type; land conversion / plan approval; encumbrance certificate; rental yield |

Also needed for structured data:
- [ ] Map pin coordinates for **Adarsh Rosewood** and **Adarsh Savana Phase 3** (their Google Maps embeds are zoomed out, so the embed centre is not the site). The other three project pages now carry `geo` from their street-level map embeds.

## 5. Authors and legal pages (Task 10)

- [ ] Blog author: all 12 posts now credit the **Organization** "Adarsh Projects" in JSON-LD (the visible byline "Adarsh Projects Research Desk" is unchanged). If you want a named author for E-E-A-T, send the name, a 2–3 line bio, a photo and a profile URL (LinkedIn) and it will be added as a `Person` with an author box.
- [ ] `/terms/` (83 words) and `/privacy-policy/` (126 words) are too short. Supply full legal text from your lawyer; it was deliberately not written here. The privacy policy should cover the lead form, MSG91 OTP, Google Apps Script/Sheets storage, analytics cookies (once §3 is live) and WhatsApp contact.

## 6. Dates (Task 14)

- `/new-launches/` title and description no longer carry a month.
- The "*Indicative prices as of September 2026*" notes on the home page and project pages were **kept**. They record when the prices were last checked; replacing them with an automatic "current month" would claim a check that did not happen. When you re-confirm prices with Adarsh, update the month on those lines (search the repo for `as of September 2026`) and the `lastmod` of those pages in `sitemap.xml`.

## 7. Sitemap upkeep (Task 13)

`<changefreq>` and `<priority>` were removed. `lastmod` now reflects the last real content change per
page. When you change a page's content, update its `<lastmod>` in `sitemap.xml` to that date (styling
or header/footer changes don't count).

## 8. Outbound-link policy (owner instruction, 2 Oct 2026)

- Links to news sites and other non-government sources were removed (the "Sources" lists keep only
  government entries; inline mentions such as "per Deccan Herald" remain as plain text). The JSON-LD
  `citation` lists follow the same rule.
- Government links (`*.gov.in`, `*.nic.in`, `rbi.org.in`) remain on blog, location and category pages.
- The five project pages and `/projects/` have **no** outbound links at all.
- WhatsApp chat links (`wa.me`) are contact buttons, not source links, and were kept.
- `tools/check-site.py` now fails if a non-government or project-page outbound link comes back.

## 9. Facts the new copy could not include (supply if you want them on the site)

- [ ] Savana Phase I RERA number appears both as `EX/PRM/KA/RERA/1250/303/PR/201001/003613` and without the `EX/` prefix — confirm which is correct.
- [ ] Savana Phase 3 RERA number (only Phase I is published).
- [ ] Possession dates for every project; prices for every flat project and for Savana plots above 1,200 sq ft.
- [ ] Tropica Phase 2: distances / drive times and carpet areas.
- [ ] Drive times in minutes (most pages only have km from brochures); airport distance per project; walking distance from Rosewood to Bellandur metro and from Parkland to the nearest ORR Blue Line station.
- [ ] Banks that have approved each project; rental yields and locality price trends.
- [ ] A Welkin Park review post (none exists; the location pages link only to the project page).

## 10. Content checks for the owner

- The expanded hub pages (`/locations/*`, `/plots-in-bangalore/`, `/apartments-in-bangalore/`, `/new-launches/`, `/projects/`, `/about/`, `/contact/`) were written only from facts already on the site. Please read them once for tone and accuracy.

---

## What was changed (summary)

See the commit message and `git diff` for full detail.

## Lead forms (2 Oct 2026)

- OTP verification is **off** on all forms (`OTP: false` in `assets/js/site.js`); leads go straight to the Apps Script webhook. Set it to `true` to bring MSG91 OTP back (the widget IDs are still in the config).
- A lead popup opens once per browser session after 35% scroll + 15 s on the page. It never opens on `/thank-you/`, `/site-visit/` or `/contact/`, over an on-screen lead form, or after the visitor has started any form. Markup: `partials/sticky-cta.html`; logic: `initPopup()` in `site.js`. Leads from it arrive with `intent: "popup"`; analytics event `lead_popup_open` / `LeadPopupOpen`.
