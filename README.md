## Publications
One can generate the publications.html file directly via

python3 generate_publications_v7.py \
    --authors-file authors.txt \
    --search-term SciDAC \
    --verbose \
    --output publications.html

Either pass the via the authors.txt or on the command line.

The v7 version of the code relies on the "pdftotext" package, which can be installed via HomeBrew on MacOS:
  "brew install poppler"
The v6 does a "fulltext" search via SPIRES, which is token based and can get confused by "SciDAC5". The v7 code downloads the PDF and does effectively a "grep" on the file, searching for the search term.
