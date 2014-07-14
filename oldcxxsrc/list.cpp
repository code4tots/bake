List::List(Args a) : Container(LIST_TYPE), x(a) {}

// string representation
Pointer List::repr() {
	std::string s("[");
	for (auto i = x.begin(); i != x.end(); ++i) {
		if (i != x.begin()) {
			s += ", ";
		}
		s += (*i)->repr()->cxxstr();
	}
	s += "]";
	return new Str(s);
}

Pointer List::len() {
	return new Int(x.size());
}
