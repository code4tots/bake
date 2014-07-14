Func::Func(std::function<Pointer(Args)> f) : Object(FUNC_TYPE), x(f) {}
Pointer Func::call(Args args) { return x(args); }
