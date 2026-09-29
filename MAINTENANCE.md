# Maintenance record

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
