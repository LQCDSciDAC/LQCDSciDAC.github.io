# LQCDSciDAC.github.io
Web pages for US Dept. of Energy ASCR/NP LQCD SciDAC project

_____


Instructions for building a local version for testing:

MacOS: brew install ruby (this provides “gem”)

Linux: apt-get install ruby

gem install jekyll

gem install bundler

git clone git@github.com:LQCDSciDAC/LQCDSciDAC.github.io.git

cd LQCDSciDAC.github.io.git

bundle install

bundle exec jekyll build

bundle exec jekyll serve

then in your favourite web browser you can type:

http://127.0.0.1:4000



