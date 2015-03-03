Query Reformulation and Answer Filtering
===========================

##Requirements
- Simplified Wrapper & Interface Generator ([SWIG](http://swig.org/)) -  can be installed using Linux package managers or brew on Mac OS X
- The SRI Language Modeling Toolkit ([SRILM](http://www.speech.sri.com/projects/srilm)) - a tarball with the needed modifications can be found [here](https://www.dropbox.com/s/3o5418byb5d6h3x/srilm-1.7.1.tar.gz). Note that the toolkit should be built using the Makefile with the current directory as the directory that contains the Makefile.
- Python development headers should be installed:
    - On Ubuntu:
        $ apt-get install python-dev
    - On Fedora:
        $ yum install python-devel
    - On Mac OS X, Python headers should be installed if you have xcode and the latest version of the command line tools.


##Installation
1. Make the SRILM python interface using the Makefile included. Ensure that you set the SRILM environment variable to the directory of the SRILM toolkit. e.g.
    $ SRILM=/home/tom/Downloads/srilm make
2. Download the language model from here and then place it in this directory.