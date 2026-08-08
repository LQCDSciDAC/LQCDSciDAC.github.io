## Publications
One can generate the publications.html file directly via

python3 generate_publications_v10.py \
    --authors-file authors.txt \
    --search-term SciDAC \
    --include-ids-file include_ids.txt \
    --exclude-ids-file exclude_ids.txt \
    --output publications.html

Either pass the via the authors.txt or on the command line.

The v10 version of the code relies on the "pdftotext" package, which can be installed via HomeBrew on MacOS:
  "brew install poppler"
The v10 code downloads the PDF and does effectively a "grep" on the file, searching for the search term. The include and exclude ids (v10) are the INSPIRE article ids to handle appropriately - always include them and always exclude them. If in both, always exclude.

The v6 does a "fulltext" search via SPIRES, which is token based and can get confused by "SciDAC5". This version does not rely on the "poppler" package.

