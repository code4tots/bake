#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <set>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include <functional>
#include <initializer_list>
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

struct Object;

struct Pointer {
	Object * x;
	Pointer(Object * p)       : x(p  ) {}
	Pointer(const Pointer& p) : x(p.x) {}
	Pointer& operator=(const Pointer& p) { x = p.x; return *this; }
	Object * operator->() const { return x; }
};

namespace std {
	template <> struct hash<Pointer> { size_t operator()(const Pointer& p) const; };
	template <> struct equal_to<Pointer> { bool operator()(const Pointer& a, const Pointer& b) const; };
	template <> struct less<Pointer> { bool operator()(const Pointer& a, const Pointer& b) const; };
	ostream& operator<<(ostream&,const Pointer);
}

typedef std::initializer_list<Pointer> Args;

struct Object {
	const Type type;
	
	// use like function
	virtual Pointer call(Args) { return not_supported(); }
	
	// arithmetic methods
	virtual Pointer add(Pointer) { return not_supported(); }
	
	// utilities
	virtual Pointer hash();
	virtual Pointer equal(Pointer);
	virtual Pointer less(Pointer);
	virtual Pointer truth();
	virtual Pointer repr();
	
	// conveniences
	Pointer not_equal(Pointer);
	
	// C++ interface
	bool cxxbool();
	mpz_class cxxint();
	std::string cxxstr();
	
protected:
	Object(Type t) : type(t) {}
	Pointer not_supported() const;
};

struct Nil : Object {
	static Pointer nil;
	
	Pointer repr();
	
private:
	Nil() : Object(NIL_TYPE) {}
};

struct Bool : Object {
	static Pointer True, False;
	bool x;
	
private:
	Bool(bool b) : Object(BOOL_TYPE), x(b) {}
	
	Pointer truth();
	Pointer repr();
	
	bool cxxbool() { return x; }
};

struct Int : Object {
	mpz_class x;
	Int(long i) : Object(INT_TYPE), x(i) {}
	Int(mpz_class i) : Object(INT_TYPE), x(i) {}
	
	Pointer add(Pointer);
	
	Pointer equal(Pointer);
	Pointer truth();
	Pointer repr();
};

struct Float : Object {
	double x;
	Float(double f) : Object(FLOAT_TYPE), x(f) {}
	
	Pointer repr();
};

struct Str : Object {
	std::string x;
	Str(std::string s) : Object(STR_TYPE), x(s) {}
	
	Pointer repr() { return this; }
};

struct List : Object {
	std::vector<Pointer> x;
	List(Args a) : Object(LIST_TYPE), x(a) {}
	List(std::vector<Pointer> v) : Object(LIST_TYPE), x(v) {}
	
	Pointer add(Pointer y) {
		if (y->type == LIST_TYPE) {
			std::vector<Pointer> v(x);
			v.insert(v.end(),((List*)y.x)->x.begin(),((List*)y.x)->x.end());
			return new List(v);
		}
		return not_supported();
	}
	
	Pointer repr() {
		std::string s("[");
		for (size_t i = 0; i < x.size(); i++) {
			if (i)
				s += ", ";
			s += x[i]->cxxstr();
		}
		s += "]";
		return new Str(s);
	}
};

struct Set : Object {
	std::unordered_set<Pointer> x;
	Set(Args a) : Object(SET_TYPE), x(a) {}
};

struct Dict : Object {
	std::unordered_map<Pointer,Pointer> x;
	Dict(std::initializer_list< std::pair<const Pointer,Pointer> > a) : Object(DICT_TYPE), x(a) {}
};

struct Func : Object {
	std::function<Pointer(Args)> x;
	Func(std::function<Pointer(Args)> f) : Object(FUNC_TYPE), x(f) {}
	Pointer call(Args args) { return x(args); }
};

void preheat();
void bake();

extern Pointer ingredient_xprint;
extern Pointer ingredient_xnil;

// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
// implementation

namespace std {
	size_t hash<Pointer>::operator()(const Pointer& p) const {
		return p->hash()->cxxint().get_ui();
	}
	bool equal_to<Pointer>::operator()(const Pointer& a, const Pointer& b) const {
		return a->equal(b)->cxxbool();
	}
	bool less<Pointer>::operator()(const Pointer& a, const Pointer& b) const {
		return a->less(b)->cxxbool();
	}
	ostream& operator<<(ostream& out,const Pointer p) {
		return out << p->cxxstr();
	}
}

Pointer Object::hash() { return new Int((size_t)this); }
Pointer Object::equal(Pointer p) { return this == p.x ? Bool::True : Bool::False; }
Pointer Object::less(Pointer p) { return Bool::False; }
Pointer Object::truth() { return Bool::True; }
Pointer Object::repr() { return new Str("<not yet implemented>"); }
Pointer Object::not_equal(Pointer p) { return equal(p)->cxxbool() ? Bool::False : Bool::True; }
bool Object::cxxbool() { return ((Bool*)truth().x)->x; }
mpz_class Object::cxxint() { return ((Int*)hash().x)->x; }
std::string Object::cxxstr() { return ((Str*)repr().x)->x; }
Pointer Object::not_supported() const { throw "operation not supported"; }

Pointer Nil::nil(new Nil());
Pointer Nil::repr() { return new Str("nil"); }

Pointer Bool::True(new Bool(true)), Bool::False(new Bool(false));
Pointer Bool::truth() { return this; }
Pointer Bool::repr() { return new Str(x ? "true" : "false"); }

Pointer Int::add(Pointer p) {
	switch(p->type) {
	case INT_TYPE:
		return new Int(x + ((Int*)p.x)->x);
	case FLOAT_TYPE:
		return new Float(x.get_d() + ((Float*)p.x)->x);
	default:
		return not_supported();
	}
}
Pointer Int::equal(Pointer p) {
	switch(p->type) {
	case INT_TYPE:
		return x == ((Int*)p.x)->x ? Bool::True : Bool::False;
	case FLOAT_TYPE:
		return x.get_d() == ((Float*)p.x)->x ? Bool::True : Bool::False;
	default:
		return Bool::False;
	}
}
Pointer Int::truth() { return x ? Bool::True : Bool::False; }
Pointer Int::repr() { return new Str(x.get_str()); }

Pointer Float::repr() { return new Str(std::to_string(x)); }


// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
// preheat

void preheat() {
	// TODO: if there are preparations I must make before starting the program, do it here.
}


Pointer ingredient_xnil(Nil::nil);

Pointer ingredient_xprint(new Func(
	[&](Args args) -> Pointer {
		for (auto arg : args) {
			std::cout << arg << std::endl;
		}
		return Nil::nil;
	}
));

Pointer ingredient_xtrue(Bool::True);
Pointer ingredient_xfalse(Bool::False);

// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------------
// main
using namespace std;

int main() {
	preheat();
	bake();
}

