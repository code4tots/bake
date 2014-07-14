struct Set : Container {
	std::unordered_set<Pointer> x;
	Set(Args);
	
	// string representation
	Pointer repr();
	
	Pointer len();
};
