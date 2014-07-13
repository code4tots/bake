struct Set : Object {
	std::unordered_set<Pointer> x;
	Set(Args);
	
	// string representation
	Pointer repr();
	
	Pointer truth();
};
