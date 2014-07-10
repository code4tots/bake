.PHONY: clean all run

run: all
	./a.out
	
clean:
	rm -rf a.out cake.cpp

all: a.out

cake.cpp: cake.bake bakestub.cpp bake.py
	cat cake.bake | python3 bake.py > cake.cpp

a.out: cake.cpp
	g++ cake.cpp -I/usr/local/include/ --std=c++11 -lgmpxx -lgmp -L/usr/local/lib -Wall -Wfatal-errors

