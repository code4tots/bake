Bool::Bool(bool b) : Object(BOOL_TYPE), x(b) {}

// string representation
Pointer Bool::repr() { return new Str(x ? "true" : "false"); }
