# Stewards of the Way | Genesis 1901 ASV Visual Laboratory v0.2

**Status:** Isolated visual beta. Does not alter the first Genesis demo, the core Bible Foundation files, or the source PDF. Not production Scripture or a completed cross-reference audit.

## Installation in the existing `bible-foundation` repository

Upload the *contents of this package* to the repository root while **preserving their paths**. All beta files live under:

`demos/asv-1901-genesis-visual-lab/`

There is no overwrite of `demos/asv-1901-genesis-facsimile/` (v0.1).

If GitHub Pages is publishing the default `main` branch from `/ (root)`, browse:

`https://stewards-of-the-way.github.io/bible-foundation/demos/asv-1901-genesis-visual-lab/`

URL is an expected route only until the owner installs this ZIP. The `index.html` also works with local file:// URLs; no CDNs or network services are needed.

## Five reading appearances

1. **Original 1901:** original-color WebP derivatives already present in beta v0.1, copied byte-for-byte. The original 1901 source PDF remains archival and unmodified. These are reduced-resolution, compressed screen images, not identical file bytes to the PDF's underlying JPEG2000.
2. **Direct inversion:** CSS `filter: invert(1)` applied to the original-color images, including their paper background. No new asset.
3. **Clean dark:** independent **pre-generated transparent ink** WebP, with white-on-dark display filter. Background is chosen using CSS (graphite, midnight, forest, plum) with no duplicate images.
4. **Enhanced scan:** independent **pre-generated sharpened/normalized** WebP derived from the scanned page. No text retypes, paraphrases, or replacements in the image. May alter fine image features and is for viewing only.
5. **Digital reader:** all 80 verses from Genesis chapters 1–3 are in an OpenBible.info USX-derived comparison transcription. **Not** a finished independent scan-first verified transcription.

Original and prepared modes reuse the **same three full-page images per variant** in both full-page and cropped portrait views. The portrait view uses CSS clipping of full images; it does not store separate left and right image crops. Images beyond the first page use lazy loading.

## Available interactions

- Auto/continuous-column/full-page layout, independent of visual appearance.
- Continuous normal browser scrolling. No forced page-turn controls.
- Interface theme is separate from the paper treatment.
- Optional A/B comparison with original page beside the chosen appearance.
- Sample, approximate original-image verse hotspots **not fully audited**.
- Verse picker, 80 verse targets in the digital reader, word selection in the verse-study panel, explicit Clear Selection and selection toggles.
- Closing the study panel clears the active verse. Escape also clears it.
- Example 1901 Genesis 1:1 cross-references, separately labelled as an earlier visually checked example. All other references remain awaiting audit.

## Authenticity, audit and safety

**Original source:** `Bible_(1901_American_Standard_Version).pdf`, PDF pages 17, 18, 21. Historically faithful visible page images are derivatives, not a substitution for the archived original PDF.

**Text:** `assets/comparison-text.js` from the v0.1 digital fixture. From OpenBible.info `usx-english-only` and retained with its source limitation.

**Hotspots:** `assets/hotspots.js` from v0.1; six approximate sample rectangles, *not* claims of 80 verified facsimile verse mappings. Full 1901 reference tagging and bookwide transcription audit are outstanding.

**No CGBC player integration:** this is an isolated Bible Foundation test. No production, schema, player or GitHub changes made by the assistant.

**Accessibility:** buttons, controls, individual digital verses and their study panels are keyboard accessible. Image-derived text itself is not a replacement for the digital accessible transcription.

## Processing technique

- `page-N-original.webp`: reused v0.1 screen derivatives, no re-encoding.
- `page-N-enhanced.webp`: local luminance normalization and gentle unsharp mask on each source RGB image. This output **must not** be treated as facsimile evidence for ambiguous letters.
- `page-N-ink.webp`: grayscale local closing and Gaussian smoothing to estimate paper background, alpha derived from difference to recover printed ink; background is transparent. CSS renders extracted dark ink in light color over any chosen page color. Fine marks may not reproduce perfectly, especially near faint paper detail; preserve the original view for checking.
- Raw inversion is performed with the browser CSS filter directly on the original source image.

## Testing

Tested headlessly in Chromium, at 1440×900 desktop and 390×844 phone-sized viewports: image decoding, five appearance modes, 80 digital verses, verse open/reselect-to-clear, Clear Selection button, portrait crops and A/B comparison. Tests reported zero JavaScript exceptions. This is **not** a claim that all physical devices, scroll speeds, screen readers or browser engines have been tested.

To reproduce functional tests using an ordinary web server or by opening `index.html`, select each mode and test **full page** / **one column** / **auto**, change Clean dark's paper, compare with original, open a verse and click it again, and switch interface theme. Review actual small reference typography separately in the original view.
