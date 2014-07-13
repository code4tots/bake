Int::Int(long i) : Object(INT_TYPE), x(i) {}
Int::Int(std::string i) : Object(INT_TYPE), x(i) {}

// string representation
Pointer Int::repr() { return new Str(x.get_str()); }

Pointer Int::truth() { return new Bool(x != 0); }
