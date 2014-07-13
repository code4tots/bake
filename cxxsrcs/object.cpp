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
