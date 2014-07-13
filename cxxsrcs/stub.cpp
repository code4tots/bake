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
struct Pointer;

typedef std::initializer_list<Pointer> Args;

struct Pointer {
	Object * x;
	Pointer(Object *);
	Pointer(const Pointer&);
	Pointer& operator=(const Pointer&);
	Object * operator->() const;
	Pointer operator()(Args);
	Pointer operator[](Pointer);
};

struct Object {
	const Type type;
	
	virtual Pointer call(Args);
	virtual Pointer subscript(Pointer);
	
	// binary operators
	virtual Pointer add(Pointer);
	virtual Pointer subtract(Pointer);
	virtual Pointer multiply(Pointer);
	virtual Pointer divide(Pointer);
	virtual Pointer modulo(Pointer);
	
	
protected:
	Object(Type);
	Pointer not_supported();
};
struct Nil : Object {
	Nil();
};Pointer::Pointer(Object * p) : x(p) {}
Pointer::Pointer(const Pointer& p) : x(p.x) {}
Pointer& Pointer::operator=(const Pointer& p) { x = p.x; return *this;}
Object * Pointer::operator->() const { return x; }
Pointer Pointer::operator()(Args args) { return x->call(args); }
Pointer Pointer::operator[](Pointer i) { return x->subscript(i); }
Pointer Object::call(Args) { return not_supported(); }
Pointer Object::subscript(Pointer) { return not_supported(); }

// binary operators
Pointer Object::add(Pointer) { return not_supported(); }
Pointer Object::subtract(Pointer) { return not_supported(); }
Pointer Object::multiply(Pointer) { return not_supported(); }
Pointer Object::divide(Pointer) { return not_supported(); }
Pointer Object::modulo(Pointer) { return not_supported(); }

// protected
Object::Object(Type t) : type(t) {}
Pointer Object::not_supported() { throw "not supported"; return not_supported(); }
Nil::Nil() : Object(NIL_TYPE) {}