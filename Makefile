.PHONY: clean all

all: a.out
	./a.out

a.out: cake.cpp
	g++ -I/usr/local/include/ --std=c++11 -lgmpxx -lgmp -L/usr/local/lib -Wall -Wfatal-errors -Wpedantic cake.cpp

cake.cpp: stub.cpp cream.cpp
	cat stub.cpp cream.cpp > cake.cpp

cream.cpp: cake.bake bake.py
	python3 bake.py

