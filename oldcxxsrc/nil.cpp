Nil::Nil() : Object(NIL_TYPE) {}

// string representation
Pointer Nil::repr() { return new Str("nil"); }

Pointer Nil::truth() { return new Bool(false); }
