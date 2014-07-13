HHDR=pointer.h object.h nil.h bool.h int.h float.h str.h list.h set.h dict.h func.h stdlib.h
HDR=$(HHDR:.h=.hpp)
SRC=$(HHDR:.h=.cpp)

.PHONY: all clean

all: stub.cpp

stub.cpp: $(HDR) $(SRC)
	cat $(HDR) $(SRC) > stub.cpp

clean:
	rm -rf stub.cpp
