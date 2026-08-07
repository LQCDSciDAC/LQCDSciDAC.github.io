#!/usr/bin/env python3
"""
Generate publications.html for LQCDSciDAC.github.io from INSPIRE-HEP.

Examples
--------
    python3 generate_publications.py R.G.Edwards.1 K.N.Orginos.1

    python3 generate_publications.py \
        --authors-file authors.txt \
        --output publications.html

authors.txt is one INSPIRE author signature per line, e.g.
    R.G.Edwards.1
    K.N.Orginos.1

Only published, refereed journal articles are selected. Records are
de-duplicated by INSPIRE literature record ID and sorted by publication date.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any, Iterable


GENERATOR_VERSION = "2026-08-07.5"
DEFAULT_SINCE_YEAR = 2002  # include publications from 2002 onward

API_URL = "https://inspirehep.net/api/literature"
INSPIRE_LITERATURE_URL = "https://inspirehep.net/literature/{}"

# INSPIRE documents a rate limit of 15 requests / 5 seconds.
# 0.4 s between successful requests stays comfortably below that.
REQUEST_DELAY = 0.40
PAGE_SIZE = 1000

FIELDS = ",".join(
    [
        "titles",
        "authors.full_name",
        "collaborations",
        "publication_info",
        "imprints",
        "document_type",
        "refereed",
        "earliest_date",
        "control_number",
    ]
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the LQCD SciDAC publications.html page from "
            "published INSPIRE-HEP articles by selected authors."
        )
    )
    parser.add_argument(
        "authors",
        nargs="*",
        help='INSPIRE author signatures, e.g. "R.G.Edwards.1"',
    )
    parser.add_argument(
        "--authors-file",
        type=Path,
        help="Text file containing one INSPIRE author signature per line.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("publications.html"),
        help="Output file (default: publications.html).",
    )
    parser.add_argument(
        "--since-year",
        type=int,
        default=DEFAULT_SINCE_YEAR,
        help=(
            "Keep only publications with journal publication year >= this value "
            f"(default: {DEFAULT_SINCE_YEAR})."
        ),
    )
    parser.add_argument(
        "--max-authors",
        type=int,
        default=20,
        help=(
            "Maximum number of authors printed before using 'et al.' "
            "(default: 20; use 0 to print every author)."
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print INSPIRE queries and retrieval counts.",
    )
    return parser.parse_args()


def load_authors(args: argparse.Namespace) -> list[str]:
    authors: list[str] = []

    for author in args.authors:
        author = author.strip()
        if author:
            authors.append(author)

    if args.authors_file:
        for line in args.authors_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                authors.append(line)

    # Preserve input order while removing duplicates.
    authors = list(dict.fromkeys(authors))

    if not authors:
        raise SystemExit(
            "No authors supplied. Pass INSPIRE signatures on the command line "
            "or use --authors-file."
        )
    return authors


def get_json(url: str, max_attempts: int = 6) -> dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "User-Agent": "LQCDSciDAC-publications-generator/1.0",
    }
    request = urllib.request.Request(url, headers=headers)

    for attempt in range(1, max_attempts + 1):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                payload = json.load(response)
            time.sleep(REQUEST_DELAY)
            return payload

        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                retry_after = exc.headers.get("Retry-After")
                try:
                    wait = max(float(retry_after), 5.0) if retry_after else 5.0
                except ValueError:
                    wait = 5.0
            elif 500 <= exc.code < 600:
                wait = min(2 ** attempt, 20)
            else:
                detail = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(
                    f"INSPIRE returned HTTP {exc.code} for {url}\n{detail}"
                ) from exc

            if attempt == max_attempts:
                raise RuntimeError(
                    f"INSPIRE request failed after {max_attempts} attempts: {url}"
                ) from exc
            print(
                f"INSPIRE HTTP {exc.code}; retrying in {wait:g} s...",
                file=sys.stderr,
            )
            time.sleep(wait)

        except (urllib.error.URLError, TimeoutError) as exc:
            if attempt == max_attempts:
                raise RuntimeError(
                    f"INSPIRE request failed after {max_attempts} attempts: {url}"
                ) from exc
            wait = min(2 ** attempt, 20)
            print(
                f"Network error ({exc}); retrying in {wait:g} s...",
                file=sys.stderr,
            )
            time.sleep(wait)

    raise AssertionError("unreachable")


def query_for_author(author: str) -> str:
    # tc p = "Published (in a refereed journal)" in INSPIRE's search syntax.
    # document_type:article excludes books, theses, proceedings, etc.
    return f"a {author} and tc p and document_type:article"


def fetch_author_records(author: str, verbose: bool = False) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    page = 1

    while True:
        params = {
            "q": query_for_author(author),
            "size": PAGE_SIZE,
            "page": page,
            "fields": FIELDS,
        }
        url = f"{API_URL}?{urllib.parse.urlencode(params)}"

        if verbose:
            print(f"[INSPIRE] {author}: page {page}", file=sys.stderr)

        data = get_json(url)
        page_hits = data.get("hits", {}).get("hits", [])
        records.extend(page_hits)

        total_obj = data.get("hits", {}).get("total", 0)
        if isinstance(total_obj, dict):
            total = int(total_obj.get("value", 0))
        else:
            total = int(total_obj or 0)

        if not page_hits or len(records) >= total or len(page_hits) < PAGE_SIZE:
            break
        page += 1

    if verbose:
        print(
            f"[INSPIRE] {author}: retrieved {len(records)} published article(s)",
            file=sys.stderr,
        )

    return records


def choose_publication_info(metadata: dict[str, Any]) -> dict[str, Any]:
    infos = metadata.get("publication_info") or []

    # Prefer the main publication over errata/addenda when INSPIRE labels it.
    for info in infos:
        if (
            info.get("journal_title")
            and not info.get("hidden", False)
            and info.get("material") == "publication"
        ):
            return info

    # Otherwise use the first visible journal entry.
    for info in infos:
        if info.get("journal_title") and not info.get("hidden", False):
            return info

    return infos[0] if infos else {}


_DATE_RE = re.compile(r"^(\d{4})(?:-(\d{1,2}))?(?:-(\d{1,2}))?")


def normalized_date(value: Any) -> date | None:
    if value is None:
        return None
    match = _DATE_RE.match(str(value))
    if not match:
        return None
    year = int(match.group(1))
    month = int(match.group(2) or 1)
    day = int(match.group(3) or 1)
    try:
        return date(year, month, day)
    except ValueError:
        return None


def publication_date(metadata: dict[str, Any]) -> date:
    """
    INSPIRE's schema defines imprints[].date as the publication date.

    If several imprint dates exist, use the earliest one (first publication).
    Fall back to publication_info.year, then earliest_date.
    """
    imprint_dates = [
        d
        for imprint in (metadata.get("imprints") or [])
        if (d := normalized_date(imprint.get("date"))) is not None
    ]
    if imprint_dates:
        return min(imprint_dates)

    pub = choose_publication_info(metadata)
    if pub.get("year"):
        return date(int(pub["year"]), 1, 1)

    fallback = normalized_date(metadata.get("earliest_date"))
    if fallback:
        return fallback

    return date.min


def publication_year(metadata: dict[str, Any]) -> int:
    """
    Use the journal's publication year for the year heading when available.
    """
    pub = choose_publication_info(metadata)
    if pub.get("year"):
        return int(pub["year"])

    d = publication_date(metadata)
    return d.year if d != date.min else 0


def record_id(hit: dict[str, Any]) -> str:
    rid = hit.get("id")
    if rid is None:
        rid = hit.get("metadata", {}).get("control_number")
    if rid is None:
        raise ValueError("INSPIRE hit has no record ID/control_number")
    return str(rid)


MATHML_TAGS = (
    "math|mrow|mi|mo|mn|msub|msup|mover|munder|munderover|"
    "mtext|mfrac|msqrt|mroot|mtable|mtr|mtd|mfenced|mspace|"
    "semantics|annotation|annotation-xml"
)

_MATHML_ESCAPED_TAG_RE = re.compile(
    rf"""\\(?=</?(?:{MATHML_TAGS})\b)""",
    re.IGNORECASE,
)


def title_for(metadata: dict[str, Any]) -> str:
    """
    Return an INSPIRE title with MathML preserved as real HTML/MathML markup.

    INSPIRE titles can arrive with MathML either directly:
        <math>...</math>

    or HTML-escaped:
        &lt;math&gt;...&lt;/math&gt;

    Some serialized forms may also contain a literal backslash immediately
    before a MathML tag:
        \\<math>...\\</math>

    Normalize those cases so the generated page contains actual MathML tags.
    """
    titles = metadata.get("titles") or []
    if not titles:
        return "(untitled)"

    title = str(titles[0].get("title") or "(untitled)")

    # Decode HTML entities such as &lt;math&gt; and &amp;.
    title = html.unescape(title)

    # Remove only backslashes that immediately precede known MathML tags.
    # This deliberately leaves ordinary LaTeX/backslashes elsewhere untouched.
    title = _MATHML_ESCAPED_TAG_RE.sub("", title)

    return title

def initials(given: str) -> str:
    """
    Convert given names to compact initials without spelling ordinary
    names letter-by-letter.

    Examples:
        "Robert G."   -> "R.G."
        "Joe"         -> "J."
        "Yong"        -> "Y."
        "H.-T."       -> "H.-T."
        "Jean-Pierre" -> "J.-P."
    """
    pieces: list[str] = []

    for token in re.split(r"\s+", given.strip()):
        if not token:
            continue

        # Preserve already-initialized forms such as R., R.G., or H.-T.
        compact = token.replace(" ", "")
        if "." in compact and all(
            ch.isalpha() or ch in ".-" for ch in compact
        ):
            if not compact.endswith("."):
                compact += "."
            pieces.append(compact)
            continue

        # Hyphenated full names: Jean-Pierre -> J.-P.
        if "-" in token:
            subparts = token.split("-")
            initial_parts: list[str] = []
            for part in subparts:
                first = next((ch for ch in part if ch.isalpha()), None)
                if first:
                    initial_parts.append(first.upper() + ".")
            if initial_parts:
                pieces.append("-".join(initial_parts))
            continue

        # Ordinary full given name: Joe -> J., Yong -> Y.
        first = next((ch for ch in token if ch.isalpha()), None)
        if first:
            pieces.append(first.upper() + ".")

    return "".join(pieces)

def display_author(full_name: str) -> str:
    """
    Convert INSPIRE's usual 'Surname, Given Middle' form to 'G.M. Surname'.
    If the name is in some other form, leave it alone.
    """
    if "," not in full_name:
        return full_name.strip()

    surname, given = full_name.split(",", 1)
    short = initials(given)
    return f"{short} {surname.strip()}".strip()


def format_authors(metadata: dict[str, Any], max_authors: int) -> str:
    raw = [
        a.get("full_name", "").strip()
        for a in (metadata.get("authors") or [])
        if a.get("full_name")
    ]
    authors = [display_author(a) for a in raw]

    collaborations = [
        c.get("value", "").strip()
        for c in (metadata.get("collaborations") or [])
        if c.get("value")
    ]

    if not authors:
        return ", ".join(collaborations) if collaborations else "(authors unavailable)"

    if max_authors > 0 and len(authors) > max_authors:
        text = f"{authors[0]} et al."
        if collaborations:
            text += " [" + ", ".join(collaborations) + "]"
        return text

    return ", ".join(authors)


def article_locator(pub: dict[str, Any]) -> str:
    artid = pub.get("artid")
    page_start = pub.get("page_start")
    page_end = pub.get("page_end")

    if artid:
        return str(artid)
    if page_start and page_end and str(page_end) != str(page_start):
        return f"{page_start}-{page_end}"
    if page_start:
        return str(page_start)
    return ""


def format_journal_citation(metadata: dict[str, Any]) -> str:
    pub = choose_publication_info(metadata)

    journal = str(pub.get("journal_title") or "").strip()
    volume = str(pub.get("journal_volume") or "").strip()
    issue = str(pub.get("journal_issue") or "").strip()
    year = str(pub.get("year") or "").strip()
    locator = article_locator(pub)

    if not journal:
        freetext = str(pub.get("pubinfo_freetext") or "").strip()
        return freetext or "Published article"

    parts = [journal]
    if volume:
        parts.append(volume)
    if year:
        parts.append(f"({year})")

    citation = " ".join(parts)

    if issue:
        citation += f" {issue}"
    if locator:
        citation += f", {locator}"

    return citation


def deduplicate(records: Iterable[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    unique: dict[str, dict[str, Any]] = {}
    for hit in records:
        unique[record_id(hit)] = hit
    return unique


def render_html(
    records: Iterable[dict[str, Any]],
    max_authors: int,
) -> str:
    records = list(records)

    # Latest publication date first; INSPIRE recid is a stable tie-breaker.
    records.sort(
        key=lambda hit: (
            publication_date(hit.get("metadata", {})),
            int(record_id(hit)) if record_id(hit).isdigit() else 0,
        ),
        reverse=True,
    )

    lines = [
        "---",
        "layout: default",
        "---",
        "",
        '<a id="publications"></a><h1>Journal Publications</h1>',
        "",
        "<!-- This file is generated by generate_publications.py. -->",
        '<table class="publications">',
        "",
    ]

    current_year: int | None = None

    for hit in records:
        metadata = hit.get("metadata", {})
        year = publication_year(metadata)

        if year != current_year:
            current_year = year
            year_label = str(year) if year else "Unknown year"
            anchor = f"year{year}" if year else "year-unknown"
            lines.extend(
                [
                    "<!-- ================================================================================ -->",
                    f"  <!-- {year_label} -->",
                    f'  <tr class="year"><td colspan="2">'
                    f'<a id="{anchor}"></a><h2>{html.escape(year_label)}</h2>'
                    f"</td></tr>",
                    "",
                ]
            )

        rid = record_id(hit)
        title = title_for(metadata)
        authors = html.escape(format_authors(metadata, max_authors), quote=False)
        citation = html.escape(format_journal_citation(metadata), quote=False)
        url = INSPIRE_LITERATURE_URL.format(urllib.parse.quote(rid, safe=""))

        lines.extend(
            [
                "<!-- ******* row  ******* -->",
                '  <tr class="publications">',
                '    <td class="publications">',
                f"      <b>{title}</b><br/>",
                f"      {authors}",
                "    </td>",
                '    <td class="publications">',
                f'      <a href="{url}">{citation}</a>',
                "    </td>",
                "  </tr>",
                "",
            ]
        )

    lines.extend(["</table>", ""])
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    authors = load_authors(args)

    all_hits: list[dict[str, Any]] = []
    for author in authors:
        all_hits.extend(fetch_author_records(author, verbose=args.verbose))

    unique = deduplicate(all_hits)

    unique = {
        rid: hit
        for rid, hit in unique.items()
        if publication_year(hit.get("metadata", {})) >= args.since_year
    }

    output = render_html(unique.values(), max_authors=args.max_authors)
    args.output.write_text(output, encoding="utf-8")

    print(
        f"[generate_publications.py {GENERATOR_VERSION}] "
        f"Wrote {args.output} with {len(unique)} unique published article(s) "
        f"from {len(authors)} author signature(s)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
