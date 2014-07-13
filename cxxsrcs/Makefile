HDR=pointer.h object.h nil.h bool.h int.h float.h str.h list.h set.h dict.h func.h stdlib.h
SRC=$(HDR:.h=.cpp)

.PHONY: all clean

all: $(HDR) $(SRC)
	cat $(HDR) $(SRC) > stub.cpp

clean:
	rm -rf stub.cpp
