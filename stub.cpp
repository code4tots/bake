// C++11 with gmp required
#include <gmpxx.h>
#include <string>
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include <functional>
#include <initializer_list>
#include <iostream>
#include <fstream>
#include <algorithm>
enum Type { NIL_TYPE, BOOL_TYPE, INT_TYPE, FLOAT_TYPE, STR_TYPE, LIST_TYPE, SET_TYPE, DICT_TYPE, FUNC_TYPE };
struct Pointer;
typedef std::initializer_list<Pointer>   Args;
typedef std::pair<const Pointer,Pointer> Pair;
typedef std::initializer_list<Pair>      Pairs;
typedef bool                                        cxxbool;
typedef mpz_class                                   cxxint;
typedef double                                      cxxfloat;
typedef std::string                                 cxxstr;
typedef std::vector<Pointer>                        cxxlist;
typedef std::unordered_set<Pointer>                 cxxset;
typedef std::unordered_map<Pointer,Pointer>         cxxdict;
typedef std::function<Pointer(Args)>                cxxfunc;
namespace std {
	template <> struct hash<Pointer> { size_t operator()(const Pointer&) const; };
	template <> struct equal_to<Pointer> { bool operator()(const Pointer&,const Pointer&) const; };
	template <> struct less<Pointer> { bool operator()(const Pointer&,const Pointer&) const; };
}
struct NotSupported {};
struct Pointer {
	Type type;
	void * value;
	Pointer() : type(NIL_TYPE), value(NULL) {}
	
	// Get a reference to the raw underlying C++ values. Handle with care.
	cxxbool&   get_cxxbool  () const { return *((cxxbool*)value); }
	cxxint&    get_cxxint   () const { return *((cxxint*)value); }
	cxxfloat&  get_cxxfloat () const { return *((cxxfloat*)value); }
	cxxstr&    get_cxxstr   () const { return *((cxxstr*)value); }
	cxxlist&   get_cxxlist  () const { return *((cxxlist*)value); }
	cxxset&    get_cxxset   () const { return *((cxxset*)value); }
	cxxdict&   get_cxxdict  () const { return *((cxxdict*)value); }
	cxxfunc&   get_cxxfunc  () const { return *((cxxfunc*)value); }
	
	// API for new objects with given values.
	// In the future, I may have a more sophisticated memory management schemes.
	static Pointer new_nil() { return Pointer(); }
	template <class T> static Pointer new_bool  (T t)              { return Pointer(BOOL_TYPE,  new cxxbool(t)); }
	template <class T> static Pointer new_int   (T t)              { return Pointer(INT_TYPE,   new cxxint(t)); }
	template <class T> static Pointer new_float (T t)              { return Pointer(FLOAT_TYPE, new cxxfloat(t)); }
	template <class T> static Pointer new_str   (T t)              { return Pointer(STR_TYPE,   new cxxstr(t)); }
					   static Pointer new_list  (Args t)           { return Pointer(LIST_TYPE,  new cxxlist(t)); }
					   static Pointer new_list  (const cxxlist& t) { return Pointer(LIST_TYPE,  new cxxlist(t)); }
					   static Pointer new_set   (Args t)           { return Pointer(SET_TYPE,   new cxxset(t)); }
	template <class T> static Pointer new_set   (T t)              { return Pointer(SET_TYPE,   new cxxset(t)); }
	template <class T> static Pointer new_dict  (T t)              { return Pointer(DICT_TYPE,  new cxxdict(t)); }
	template <class T> static Pointer new_func  (T t)              { return Pointer(FUNC_TYPE,  new cxxfunc(t)); }
	
	// Normally I would consider implementing operator bool to be bad practice.
	// However, there are some tricky boolean situations that are greatly simplified by this.
	operator bool() const {
		switch(type) {
		case NIL_TYPE   : return false;
		case BOOL_TYPE  : return get_cxxbool();
		case INT_TYPE   : return get_cxxint() != 0;
		case FLOAT_TYPE : return get_cxxfloat() != 0;
		case STR_TYPE   : return get_cxxstr().size() != 0;
		case SET_TYPE   : return get_cxxset().size() != 0;
		case LIST_TYPE  : return get_cxxlist().size() != 0;
		case DICT_TYPE  : return get_cxxdict().size() != 0;
		case FUNC_TYPE  : return true;
		}
		throw NotSupported();
	}
	
	// make a copy of this
	Pointer copy() const {
		switch(type) {
		case NIL_TYPE   : return *this;
		case BOOL_TYPE  : return new_bool(get_cxxbool());
		case INT_TYPE   : return new_int(get_cxxint());
		case FLOAT_TYPE : return new_float(get_cxxfloat());
		case STR_TYPE   : return new_str(get_cxxstr());
		case LIST_TYPE  : return new_list(get_cxxlist());
		case SET_TYPE   : return new_set(get_cxxset());
		case DICT_TYPE  : return new_dict(get_cxxdict());
		case FUNC_TYPE  : return new_func(get_cxxfunc());
		}
		throw NotSupported();
	}
	
	// ----------------------- methods for use in the language itself ------------------------
	
	// Operations required to make std library stuff happy.
	Pointer hash() const { // fairly naive hashes for now.
		switch(type) {
		case NIL_TYPE   : return new_int(0);
		case BOOL_TYPE  : return new_int(get_cxxbool());
		case INT_TYPE   : return *this;
		case FLOAT_TYPE : return new_int(get_cxxfloat());
		case STR_TYPE   : return new_int(get_cxxstr().size());
		case LIST_TYPE  : return new_int(get_cxxlist().size());
		case SET_TYPE   : return new_int(get_cxxset().size());
		case DICT_TYPE  : return new_int(get_cxxdict().size());
		case FUNC_TYPE  : return new_int((size_t)value);
		}
		throw NotSupported();
	}
	Pointer eq(const Pointer& p) const {
		return new_bool(this == p.value);
	}
	Pointer lt(const Pointer& p) const {
		return new_bool(false);
	}
	
	// Printing to screen
	Pointer print() const {
		std::cout << str().get_cxxstr() << std::endl;
		return *this;
	}
	Pointer str() const {
		switch(type) {
		case NIL_TYPE:
		case BOOL_TYPE:
		case INT_TYPE:
		case FLOAT_TYPE:
		case LIST_TYPE:
		case SET_TYPE:
		case DICT_TYPE:
		case FUNC_TYPE:
			return repr();
		case STR_TYPE:
			return *this;
		}
		throw NotSupported();
	}
	Pointer repr() const {
		switch(type) {
		case NIL_TYPE    : return new_str("nil");
		case BOOL_TYPE   : return new_str(get_cxxbool() ? "true" : "false");
		case INT_TYPE    : return new_str(get_cxxint().get_str());
		case FLOAT_TYPE  : return new_str(std::to_string(get_cxxfloat()));
		case STR_TYPE: {
			Pointer sp = new_str("\"");
			cxxstr& s = sp.get_cxxstr();
			for (char c : get_cxxstr()) {
				switch(c) {
				case '\\': s += "\\\\"; break;
				case '\n': s += "\\n"; break;
				case '\r': s += "\\r"; break;
				case '\t': s += "\\t"; break;
				case '"' : s += "\\\""; break;
				default  : s += c; break;
				}
			}
			s += "\"";
			return sp;
		}
		case LIST_TYPE: {
			Pointer sp = new_str("list ");
			cxxstr& s = sp.get_cxxstr();
			for (Pointer p : get_cxxlist()) {
				s.append(p.repr().get_cxxstr());
				s.append(" ");
			}
			s.append("end");
			return sp;
		}
		case SET_TYPE: {
			Pointer sp = new_str("set ");
			cxxstr& s = sp.get_cxxstr();
			for (Pointer p : get_cxxset()) {
				s.append(p.repr().get_cxxstr());
				s.append(" ");
			}
			s.append("end");
			return sp;
		}
		case DICT_TYPE: {
			Pointer sp = new_str("dict ");
			cxxstr& s = sp.get_cxxstr();
			for (Pair p : get_cxxdict()) {
				s.append(p.first.repr().get_cxxstr());
				s.append(" ");
				s.append(p.second.repr().get_cxxstr());
				s.append(" ");
			}
			s.append("end");
			return sp;
		}
		case FUNC_TYPE:
			return new_str("<function>");
		default          : return new_str("not implemented");
		}
	}
	
	// Function call
	Pointer call(Args args) const { return get_cxxfunc()(args); }
	
	// Arithmetic operators
	Pointer iadd(const Pointer& p) {
		switch(type) {
		case INT_TYPE:
			switch(p.type) {
			case INT_TYPE:
				get_cxxint() += p.get_cxxint();
				return *this;
			case FLOAT_TYPE:
				return *this = new_float(get_cxxint().get_d() + p.get_cxxfloat());
			default:
				throw NotSupported();
			}
		case FLOAT_TYPE:
			switch(p.type) {
			case INT_TYPE:
				get_cxxfloat() += p.get_cxxint().get_d();
				return *this;
			case FLOAT_TYPE:
				get_cxxfloat() += p.get_cxxfloat();
				return *this;
			default:
				throw NotSupported();
			}
		case STR_TYPE:
			switch(p.type) {
			case STR_TYPE: {
				cxxstr s(p.get_cxxstr());
				get_cxxstr().append(s);
				return *this;
			}
			default:
				throw NotSupported();
			}
		case LIST_TYPE:
			switch(p.type) {
			case LIST_TYPE: {
				cxxlist ls(p.get_cxxlist());
				get_cxxlist().insert(get_cxxlist().end(),ls.begin(),ls.end());
				return *this;
			}
			default:
				throw NotSupported();
			}
		case SET_TYPE:
			switch(p.type) {
			case SET_TYPE: {
				cxxset ls(p.get_cxxset());
				get_cxxset().insert(ls.begin(),ls.end());
				return *this;
			}
			default:
				throw NotSupported();
			}
		default:
			throw NotSupported();
		}
	}
	Pointer isub(const Pointer& p) {
		switch(type) {
		case INT_TYPE:
			switch(type) {
			case INT_TYPE:
				get_cxxint() -= p.get_cxxint();
				return *this;
			default:
				throw NotSupported();
			}
		default:
			throw NotSupported();
		}
	}
	
	Pointer add(const Pointer& p) const { return copy().iadd(p); }
	
private:
	Pointer(Type t, void * v) : type(t), value(v) {}
};

namespace std {
	size_t hash<Pointer>::operator()(const Pointer& p) const { return p.hash().get_cxxint().get_ui(); }
	bool equal_to<Pointer>::operator()(const Pointer& a, const Pointer& b) const { return a.eq(b).get_cxxbool(); }
	bool less<Pointer>::operator()(const Pointer& a, const Pointer& b) const { return a.lt(b).get_cxxbool(); }
}

void bake();

int main() {
	bake();
}
