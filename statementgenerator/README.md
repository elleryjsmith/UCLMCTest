Question Answer Statement Generator
===========================

##Requirements
- Simplified Wrapper & Interface Generator ([SWIG](http://swig.org/)) -  can be installed using Linux package managers or brew on Mac OS X
- The SRI Language Modeling Toolkit ([SRILM](http://www.speech.sri.com/projects/srilm)) - a tarball with the needed modifications can be found [here](https://www.dropbox.com/s/7lt6kg56xb2h1rk/srilm.tar.gz?dl=0). Note that the toolkit should be built using the Makefile with the current directory as the directory that contains the Makefile.
- Python development headers should be installed:
    - On Ubuntu:
	$ apt-get install python-dev
    - On Fedora:
        $ yum install python-devel
    - On Mac OS X, Python headers should be installed if you have xcode and the latest version of the command line tools.


##Installation and usage
1. Use the Makefile within the statementgenerator folder to build the python interface for the SRILM toolkit.  Ensure that you set the SRILM environment variable to the directory of the SRILM toolkit. e.g.
	$ SRILM=/home/tom/Downloads/srilm make
2. Download the language model from [here](https://www.dropbox.com/s/f0odv0oh1gwjqdb/wikimodel.lm?dl=0)  and then place it in the statementgenerator directory.
3. Run the generator from the main directory of the repo i.e.
	$ python statementgenerator.py mc160.dev
which will create a .tsv file with the generated statements in datasets/generatedstatements/.
	
