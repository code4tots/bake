Pointer
	x_xnil(new Nil()),
	x_xtrue(new Bool(true)),
	x_xfalse(new Bool(false)),
	x_xprint(new Func([&](Args args) -> Pointer {
		for (auto arg : args) {
			std::cout << arg->str()->cxxstr() << ' ';
		}
		std::cout << std::endl;
		return Pointer(NULL);
	}));

