#include <string>
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include <functional>
#include <algorithm>
#include <gmpxx.h>

enum Type {
	NIL_TYPE,
	BOOL_TYPE,
	INT_TYPE,
	FLOAT_TYPE,
	STR_TYPE,
	LIST_TYPE,
	SET_TYPE,
	DICT_TYPE,
	FUNC_TYPE
};

struct Object {
	const Type type;
protected:
	Object(const Type t) : type(t) {};
};

typedef Object * Pointer;

struct Nil : Object {
	Nil() : Object(NIL_TYPE) {}
};

struct Bool : Object {
	bool x;
	Bool(bool b) : Object(BOOL_TYPE), x(b) {}
};

struct Int : Object {
	mpz_class x;
	Int(long i) : Object(INT_TYPE), x(i) {}
};

struct Float : Object {
	double x;
	Float(double f) : Object(FLOAT_TYPE), x(f) {}
};

struct Str : Object {
	std::string x;
	Str(std::string s) : Object(STR_TYPE), x(s) {}
};

struct List : Object {
	std::vector<Pointer> x;
	List(std::initializer_list<Pointer> v) : Object(LIST_TYPE), x(v) {}
};

struct Set : Object {
	std::unordered_set<Pointer> x;
	Set(std::initializer_list<Pointer> s) : Object(SET_TYPE), x(s) {}
};

struct Dict : Object {
	std::unordered_map<Pointer,Pointer> x;
	Dict(std::initializer_list< std::pair<const Pointer, Pointer> > m) : Object(DICT_TYPE), x(m) {}
};

struct Func : Object {
	std::function<Pointer(std::initializer_list<Pointer>)> x;
	Func(std::function<Pointer(std::initializer_list<Pointer>)> f) : Object(FUNC_TYPE), x(f) {}
};

int main() {
	
}