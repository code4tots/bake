Set::Set(Args args) : Container(SET_TYPE), x(args) {}

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

Pointer Set::len() {
	return new Int(x.size());
}
