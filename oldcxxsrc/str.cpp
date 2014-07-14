Str::Str(std::string s) : Container(STR_TYPE), x(s) {}

Pointer Str::str() { return this; }

Pointer Str::len() { return new Int(x.size()); }

