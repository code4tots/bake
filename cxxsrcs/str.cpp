Str::Str(std::string s) : Object(STR_TYPE), x(s) {}

Pointer Str::str() { return this; }

Pointer Str::truth() { return new Bool(x.size() != 0); }
