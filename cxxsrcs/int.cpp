Int::Int(long i) : Object(INT_TYPE), x(i) {}
Int::Int(const std::string& i) : Object(INT_TYPE), x(i) {}
Int::Int(const mpz_class& i) : Object(INT_TYPE), x(i) {}

Pointer Int::add(Pointer p) {
	switch(p->type) {
	case INT_TYPE:
		return new Int(x + p->cxxint());
	default:
		return not_supported();
	}
}
Pointer Int::subtract(Pointer p) {
	switch(p->type) {
	case INT_TYPE:
		return new Int(x - p->cxxint());
	default:
		return not_supported();
	}
}
Pointer Int::multiply(Pointer p) {
	switch(p->type) {
	case INT_TYPE:
		return new Int(x * p->cxxint());
	default:
		return not_supported();
	}
}
Pointer Int::divide(Pointer p) {
	switch(p->type) {
	case INT_TYPE:
		return new Int(x / p->cxxint());
	default:
		return not_supported();
	}
}
Pointer Int::modulo(Pointer p) {
	switch(p->type) {
	case INT_TYPE:
		return new Int(x % p->cxxint());
	default:
		return not_supported();
	}
}

// string representation
Pointer Int::repr() { return new Str(x.get_str()); }

Pointer Int::equal(Pointer p) {
	switch(p->type) {
	case INT_TYPE:
		return new Bool(x == p->cxxint());
	default:
		return new Bool(false);
	}
}

Pointer Int::less(Pointer p) {
	switch(p->type) {
	case INT_TYPE:
		return new Bool(x < p->cxxint());
	default:
		return new Bool(false);
	}
}

Pointer Int::hash() {
	return new Int(x.get_ui());
}

Pointer Int::truth() { return new Bool(x != 0); }
