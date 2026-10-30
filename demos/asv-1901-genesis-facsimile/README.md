# Stewards of the Way · Genesis 1–3 interactive facsimile demonstration

## Open locally
Open `index.html` in a browser. No server, package manager, external CDN, or internet connection required.

## Repository installation (manual)
This ZIP contains an additive isolated demo. Copy the `demos/asv-1901-genesis-facsimile/` folder to the root of `Stewards-of-the-Way/bible-foundation`. Existing files need not be replaced. For GitHub Pages, ensure Pages serves this folder or link to it from the published website. GitHub repository file browsing does **not** execute HTML directly. If Pages is configured for root main, the route is `/bible-foundation/demos/asv-1901-genesis-facsimile/`.

## Scope and evidence
Original 1901 PDF source: `Bible_(1901_American_Standard_Version).pdf`, Genesis pages 17, 18 and 21 (PDF page numbers, one-indexed). Rendered derivative `.webp` files keep the historical image appearance, with separate left/right column crops for portrait. The source PDF was not modified and is not included.

Verse detail text is separately obtained from OpenBible.info `usx-english-only/01-GEN.usx`, clearly marked as **comparison text**; it is not independently scan-verified. Selected example hotspots are approximate, human-review pending, and are not a complete verse- or word-coordinate inventory. The 1901 center-column destinations have not been reverified in this demo. Use the verse selector for all of Genesis 1–3.

To move to production: verify each hotspot word/verse boundary and anchor against the printed page, add original reference group records and note links, match page/column boundaries, audit responsive display and accessibility, and add a fallback page navigation method for image load errors.

All tooling is demonstrative and isolated. No existing site, schemas, content, or production interfaces are modified.

## Source fingerprints
Original PDF SHA-256: `e5a19756c441024c056a5f2e11eba4e1213c9a3c42e5d22c33147520bbbd3f7d`
OpenBible ZIP SHA-256: `9c0c15c70a490583ae1f2bd8e617ef6ca692ade1e528c7df08175777412dd247`
