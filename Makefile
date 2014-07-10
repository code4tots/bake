.PHONY: clean all run

run: all
	./a.out
	
clean:
	rm -rf a.out cake.cpp __pycache__ parser.out parsetab.py

all: a.out

cake.cpp: cake.bake stub.cpp bake.py
	python3 bake.py

a.out: cake.cpp
	g++ cake.cpp -I/usr/local/include/ --std=c++11 -lgmpxx -lgmp -L/usr/local/lib -Wall -Wfatal-errors

