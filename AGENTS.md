# Site maintenance

This repository is a Jekyll site published through GitHub Pages. Edit source files
at the repository root; do not edit generated `_site/` output.

## Pages and images

- `results.html` is the Highlights page; `scidac.html` is Progress under SciDAC.
- Both use `table.highlights` and `img.results`, styled in `style.css`.
- Keep the image column at 36% on desktop, with images filling that column and
  preserving their aspect ratio. At widths up to 640px, stack images above text.
- A raw `file://` view of a Jekyll source page does not include the shared layout
  or stylesheet. Use a Jekyll-rendered preview or the deployed site for visual QA.
- Add new highlights in the requested order and match the surrounding markup.
  Prefer a faithful crop of a supplied talk or highlight PDF for the thumbnail.
- The 2026 meeting entry follows the Isotensor entry and links to
  `scidac_pi_2026.html`. Meeting assets live in `highlights/2026_SciDAC_PI/`.
  The meeting page has two-sentence descriptions for each talk and poster.
- Keep navigation pages at the repository root: shared layout links are relative.

## Publications

Use `generate_publications_v10.py` with the command in `README.md`. It needs
Python 3, network access to INSPIRE and paper PDFs, and Poppler's `pdftotext`.
Keep `--search-term SciDAC`, `authors.txt`, `include_ids.txt`, and
`exclude_ids.txt`; exclusions take precedence over forced inclusions.

Generate to a temporary output first, capture the run log, then review the result
before replacing `publications.html`. Check article counts, additions/removals,
override records, and download or extraction failures. A failed PDF download can
exclude a paper, so do not publish unexplained large removals.

## Verification and publishing

- Run `git diff --check` and verify that new local links and images exist.
- Review the exact diff and staged files before committing. Preserve unrelated
  user changes and staged work; do not commit `.DS_Store` or temporary files.
- When the user requests publication, commit the requested source changes and all
  linked new assets, then push the current branch (normally `main`). Do not claim
  that deployment finished based only on a successful push.
- Record meaningful maintenance work and any validation limitations in
  `MAINTENANCE.md`.
