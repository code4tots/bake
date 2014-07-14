.PHONY: clean all run

run: all
	./a.out

clean:
	rm -rf a.out cake.cpp __pycache__ cream.cpp

all: a.out

cake.cpp: stub.cpp cream.cpp
	cat stub.cpp cream.cpp > cake.cpp

cream.cpp: cake.bake bake.py
	python3 bake.py

a.out: cake.cpp
	g++ cake.cpp -I/usr/local/include/ --std=c++11 -lgmpxx -lgmp -L/usr/local/lib -Wall -Wfatal-errors -Wpedantic
