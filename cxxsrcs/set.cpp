Set::Set(Args args) : Object(SET_TYPE), x(args) {}

// string representation
Pointer Set::repr() {
	std::string s("{");
	for (auto i = x.begin(); i != x.end(); ++i) {
		if (i != x.begin()) {
			s += ", ";
		}
		s += (*i)->repr()->cxxstr();
	}
	s += "}";
	return new Str(s);
}

Pointer Set::truth() {
	return new Bool(x.size() != 0);
}
