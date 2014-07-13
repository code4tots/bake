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

typedef std::pair<const Pointer,Pointer>   Pair;
typedef std::initializer_list<Pair>        Pairs;
typedef std::initializer_list<Pointer>     Args;

struct Pointer {
	Object * x;
	Pointer(Object *);
	Pointer(const Pointer&);
	Pointer& operator=(const Pointer&);
	Object * operator->() const;
	Pointer operator()(Args);
	Pointer operator[](Pointer);
};

namespace std {
	template <> struct hash<Pointer> {
		size_t operator()(const Pointer&) const;
	};
	
	template <> struct equal_to<Pointer> {
		bool operator()(const Pointer&, const Pointer&) const;
	};
}
