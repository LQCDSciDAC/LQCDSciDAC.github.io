## Publications
One can generate the publications.html file directly via

python3 generate_publications.py \
    --authors-file authors.txt \
    --search-term SciDAC \
    --verbose \
    --output publications.html

Either pass the via the authors.txt or on the command line.

The code relies on the "pdftotext" package, which can be installed via HomeBrew on MacOS:
  "brew install poppler"
