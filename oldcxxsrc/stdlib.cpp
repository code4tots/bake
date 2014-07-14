static Pointer
	x_xnil(new Nil()),
	x_xtrue(new Bool(true)),
	x_xfalse(new Bool(false)),
	x_xprint(new Func([&](Args args) -> Pointer {
		for (auto arg : args) {
			std::cout << arg->str()->cxxstr() << ' ';
		}
		std::cout << std::endl;
		return x_xnil;
	})),
	x_xint(new Func([&](Args args) -> Pointer {
		if (args.size() != 1)
			return not_supported();
		
		Pointer x = * args.begin();
		
		switch(x->type) {
		case INT_TYPE:
			return x;
		case FLOAT_TYPE:
			return new Int(x->cxxfloat());
		default:
			return not_supported();
		}
	}));

