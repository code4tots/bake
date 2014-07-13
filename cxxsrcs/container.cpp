Pointer Container::truth() {
	return new Bool(len()->cxxint() != 0);
}
