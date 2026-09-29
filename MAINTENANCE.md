# Maintenance record

## Near-threshold charm-meson highlight

- Added a three-sentence research highlight for `highlights/ddbar_26.pdf` before
  the 2026 SciDAC PI meeting entry, with a cropped top-left graphic in
  `img/ddbar_26.png`. Subsequently updated both title and image links to
  `highlights/ASCR_Highlight_DDbar_2026.pdf` at the user's request.
- The supplied slide mixes a 2024 PRL citation with arXiv:2602.09862. The user
  chose the matching publication, Phys. Rev. D 114, 054028 (2026), for the byline;
  verified DOI `10.1103/s3p2-552r` against INSPIRE and arXiv metadata.
- Used the paper's D–anti-D channel notation and qualified the summary to the
  energy region studied. Visually checked the crop and verified local assets,
  entry ordering, and whitespace; full Jekyll rendering was not checked locally.

## 2025 meeting archive

- Follow-up: the Romero preconditioner poster was replaced with a valid one-page
  PDF. Verified its extracted title and content, restored the linked title and
  standard Poster PDF link, and removed the obsolete source-only notice.

- Added the 2025 SciDAC PI meeting as the first entry on `scidac.html` and created
  `scidac_pi_2025.html` with two-sentence summaries of all five talks and four
  posters. Used a crop of the neutron-star image on slide 12 of Edwards's talk.
- Eight supplied presentation files are valid PDFs. The Romero preconditioner
  poster is LaTeX source with a `.pdf` suffix; preserved the original and labeled
  its link as a source download with a `.tex` download filename.
- Verified all nine presentation links, the thumbnail, and first-entry ordering;
  checked the crop visually and ran `git diff --check`. Full Jekyll rendering was
  not verified locally.

## Citation byline links

- Linked journal bylines on Highlights and SciDAC to publisher DOIs verified
  against INSPIRE metadata and Crossref. Kept all highlight-title links intact,
  including the hybrid-meson PDF link.
- Split the two baryon-spectrum citations into individual DOI links and corrected
  the volume 84 paper's year from 2012 to 2011 using its publication metadata.
- Linked news-source bylines to the published story URLs already used by their
  titles. Those existing news destinations were reused, not revalidated.
- Verified journal byline coverage, unchanged title destinations, absence of
  nested anchors, and `git diff --check`.

## 2026-09-29

- Added the Isotensor three-pion scattering highlight, linked PDF, and a crop of
  the bottom-left Dalitz plots. Shortened the description to omit the opening
  author attribution. Published in commit `2a9b2ff`.
- Added the 2026 SciDAC PI meeting highlight directly below it, with a graphic
  from Edwards's talk and a separate page linking three talks and two posters.
  Each presentation has a two-sentence description. Converted the Jinchen poster
  PNG into a PDF for the poster link. Published in commit `3bc8480`.
- Updated shared highlight CSS to reserve 36% of each desktop row for its image
  and stack images above text on screens up to 640px wide. This affects both the
  Highlights and SciDAC pages. `git diff --check` passed; rendered browser QA
  remains outstanding because the local Jekyll installation was unavailable and
  the attempted local preview could not be reached.
- Added `AGENTS.md` to preserve page conventions, publication generation steps,
  verification checks, and publishing practices.
- Ran `generate_publications_v10.py` with the README's SciDAC full-text filter,
  six author signatures, three forced includes, and one forced exclusion.
  Reviewed 425 candidates; the page increased from 237 to 240 unique records,
  adding INSPIRE IDs `3074723`, `3084385`, and `3118097`, with no removals or
  changes to existing entries. Verified all include/exclude overrides and
  uniqueness of the output IDs.
- Five candidates lacked accessible PDF URLs (`1343413`, `1853342`, `669330`,
  `2880206`, `1279092`). One candidate (`653762`) returned non-PDF content from
  a source URL; the generator attempted its alternative URL. These issues did
  not remove any previously listed publication.
