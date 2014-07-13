Dict::Dict(Pairs pairs) : Object(DICT_TYPE), x(pairs) {}

Pointer Dict::repr() {
	std::string s("{");
	for (auto i = x.begin(); i != x.end(); ++i) {
		if (i != x.begin()) {
			s += ", ";
		}
		s += i->first->repr()->cxxstr();
		s += ":";
		s += i->second->repr()->cxxstr();
	}
	s += "}";
	return new Str(s);
}