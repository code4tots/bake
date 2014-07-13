Float::Float(double f) : Object(FLOAT_TYPE), x(f) {}

// string representation
Pointer Float::repr() { return new Str(std::to_string(x)); }

Pointer Float::truth() { return new Bool(x != 0); }
