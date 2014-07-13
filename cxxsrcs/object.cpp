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
Pointer Object::hash() { return new Int((size_t)(this)); }

// C++ interface
bool Object::cxxbool() { return ((Bool*)this)->x; }
mpz_class& Object::cxxint() { return ((Int*)this)->x; }
std::string& Object::cxxstr() { return ((Str*)this)->x; }

// protected
Object::Object(Type t) : type(t) {}
Pointer Object::not_supported() { throw "not supported"; return not_supported(); }
