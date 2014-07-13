Pointer Object::call(Args) { return not_supported(); }
Pointer Object::subscript(Pointer) { return not_supported(); }

// binary operators
Pointer Object::add(Pointer) { return not_supported(); }
Pointer Object::subtract(Pointer) { return not_supported(); }
Pointer Object::multiply(Pointer) { return not_supported(); }
Pointer Object::divide(Pointer) { return not_supported(); }
Pointer Object::modulo(Pointer) { return not_supported(); }

// string representation
Pointer Object::str() { return repr(); }
Pointer Object::repr() { return new Str("<not yet implemented>"); }

// comparison and hashing
Pointer Object::equal(Pointer p) { return new Bool(this == p.x); }
Pointer Object::less(Pointer p) { return new Bool(false); }
Pointer Object::hash() { return new Int((size_t)(this)); }

Pointer Object::truth() { return new Bool(true); }

// logical operators
Pointer Object::logical_or(Pointer p) { return truth()->cxxbool() ? this : p; }
Pointer Object::logical_and(Pointer p) { return truth()->cxxbool() ? p : this; }

// convenience comparison methods
Pointer Object::greater(Pointer p) { return p->less(this); }
Pointer Object::less_equal(Pointer p) { return less(p)->logical_or(equal(p)); }
Pointer Object::greater_equal(Pointer p) { return greater(p)->logical_or(equal(p)); }

// C++ interface
bool Object::cxxbool() { return ((Bool*)this)->x; }
mpz_class& Object::cxxint() { return ((Int*)this)->x; }
std::string& Object::cxxstr() { return ((Str*)this)->x; }

// protected
Object::Object(Type t) : type(t) {}

struct NotSupported {};
Pointer Object::not_supported() { throw NotSupported(); }
