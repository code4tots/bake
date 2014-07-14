Float::Float(double f) : Object(FLOAT_TYPE), x(f) {}

Pointer Float::add(Pointer p) {
	switch(p->type) {
	case INT_TYPE:
		return new Float(x + p->cxxint().get_d());
	case FLOAT_TYPE:
		return new Float(x + p->cxxfloat());
	default:
		return not_supported();
	}
}
Pointer Float::subtract(Pointer p) {
	switch(p->type) {
	case INT_TYPE:
		return new Float(x - p->cxxint().get_d());
	case FLOAT_TYPE:
		return new Float(x - p->cxxfloat());
	default:
		return not_supported();
	}
}
Pointer Float::multiply(Pointer p) {
	switch(p->type) {
	case INT_TYPE:
		return new Float(x * p->cxxint().get_d());
	case FLOAT_TYPE:
		return new Float(x * p->cxxfloat());
	default:
		return not_supported();
	}
}
Pointer Float::divide(Pointer p) {
	switch(p->type) {
	case INT_TYPE:
		return new Float(x / p->cxxint().get_d());
	case FLOAT_TYPE:
		return new Float(x / p->cxxfloat());
	default:
		return not_supported();
	}
}

// string representation
Pointer Float::repr() { return new Str(std::to_string(x)); }

Pointer Float::equal(Pointer p) {
	switch(p->type) {
	case INT_TYPE:
		return new Bool(x == p->cxxint().get_d());
	case FLOAT_TYPE:
		return new Bool(x == p->cxxfloat());
	default:
		return not_supported();
	}
}

Pointer Float::less(Pointer p) {
	switch(p->type) {
	case INT_TYPE:
		return new Bool(x < p->cxxint().get_d());
	case FLOAT_TYPE:
		return new Bool(x == p->cxxfloat());
	default:
		return not_supported();
	}
}

Pointer Float::hash() {
	if (x == mpz_class(x).get_d()) {
		return new Int(mpz_class(x));
	}
	return new Int((size_t) x);
}

Pointer Float::truth() { return new Bool(x != 0); }
