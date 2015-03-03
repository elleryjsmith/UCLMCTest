#SRILM=/home/tom/Downloads/srilm
SRILM_LIBS=$(SRILM)/lib/i686-m64
SRILM_INC=$(SRILM)/include

PYTHON_INC=$(shell python-config --includes)


python: clean _srilm.so

_srilm.so: srilm.o srilm_python_wrap.o
	g++ -shared $^ -loolm -ldstruct -lmisc -lz -lgomp -L$(SRILM_LIBS) -o $@

srilm_python_wrap.o: srilm_python_wrap.c
	g++ -c -fpic $< -I/usr/local/include/ -I$(SRILM_INC) $(PYTHON_INC)

srilm_python_wrap.c: srilm_python.i
	swig -python $<

srilm.o: srilm.c
	g++ -c -fpic $< -I/usr/local/include/ -I$(SRILM_INC) $(PYTHON_INC)

clean:
	\rm -fr srilm.o srilm_*_wrap.* *.so srilm.py*
