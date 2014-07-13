Pointer::Pointer(Object * p) : x(p) {}
Pointer::Pointer(const Pointer& p) : x(p.x) {}
Pointer& Pointer::operator=(const Pointer& p) { x = p.x; return *this;}
Object * Pointer::operator->() const { return x; }
Pointer Pointer::operator()(Args args) { return x->call(args); }
Pointer Pointer::operator[](Pointer i) { return x->subscript(i); }
