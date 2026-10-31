# ASV 1901 Historical Reader Beta v0.3

**Isolated additive beta** for `Stewards-of-the-Way/bible-foundation` at `demos/asv-1901-genesis-mobile-lab/`. No external dependencies and no data transfer.

## Scope
- Original scan derivatives of source PDF pages 17, 18 and 21. **These are not all the pages required to display Genesis 1–3 continuously**. Some text crosses intervening pages; do not interpret the demo as a complete facsimile transcription.
- Reuses the OpenBible.info comparison verse text for all 80 Genesis 1–3 verses; this is not independently scan-verified production text.
- Portable full-page images plus prepared cropped columns for phone; cropped columns deliberately omit center reference columns and many printed header elements. Some footnotes and historical features may be excluded by crop.
- Original, enhanced scan, custom ink-mask with independent background and ink colors, and modern digital comparison. Raw inversion was removed based on user feedback.
- Sticky chapter/verse/options toolbar; tap demonstration verse and select individual digital words in study panel. Only a few hotspot samples; verse-to-image positioning is not completely audited.
- Image crops are generated offline rather than zoom-decoded during scrolling. No duplicated color combinations are stored. Keep original untouched PDF separately.

## Installation
Unzip, upload the `demos/` directory at repository root preserving paths. Do not overwrite v0.1 or v0.2. The Pages URL is `https://stewards-of-the-way.github.io/bible-foundation/demos/asv-1901-genesis-mobile-lab/` once GitHub Pages deploys.

## Known limitations
Page jump for chapters is approximate, digitized comparisons are not transcription proof, and neither complete center-reference anchors nor reliable all-verse click maps exist. Enhanced imagery can change glyph morphology, and independent comparison against original is required. Layout/crop coverage and physical-device performance remain subject to review.
