Pointer::Pointer(Object * p) : x(p) {}
Pointer::Pointer(const Pointer& p) : x(p.x) {}
Pointer& Pointer::operator=(const Pointer& p) { x = p.x; return *this;}
Object * Pointer::operator->() const { return x; }
Pointer Pointer::operator()(Args args) { return x->call(args); }
Pointer Pointer::operator[](Pointer i) { return x->subscript(i); }

namespace std {
	size_t hash<Pointer>::operator()(const Pointer& a) const {
		return a->hash()->cxxint().get_ui();
	}
	
	bool equal_to<Pointer>::operator()(const Pointer& a, const Pointer& b) const {
		return a->equal(b)->cxxbool();
	}
}
