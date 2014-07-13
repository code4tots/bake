struct Func : Object {
	std::function<Pointer(Args)> x;
	Func(std::function<Pointer(Args)>);
	Pointer call(Args);
};
