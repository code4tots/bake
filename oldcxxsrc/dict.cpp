Dict::Dict(Pairs pairs) : Container(DICT_TYPE), x(pairs) {}

Pointer& Dict::subscript(Pointer p) {
	std::cout << "in subscript " << x.size() << std::endl;
	std::cout << "KEYS: ";
	for (auto y : x) {
		std::cout << y.first->type << ' ' << y.second->type << ' ';
	}
	return x[p];
}

Pointer Dict::repr() {
	std::cout << "inside Dict::repr" << std::endl;
	std::string s("{");
	for (auto i = x.begin(); i != x.end(); ++i) {
		if (i != x.begin()) {
			s += ", ";
		}
		std::cout << "partial   " << s << std::endl;
		std::cout << "partial 2 " << i->first->repr()->cxxstr() << std::endl;
		std::cout << "partial 3 " << i->second->repr()->cxxstr() << std::endl;
		s += i->first->repr()->cxxstr();
		s += ":";
		s += i->second->repr()->cxxstr();
	}
	s += "}";
	return new Str(s);
}

Pointer Dict::len() {
	return new Int(x.size());
}
