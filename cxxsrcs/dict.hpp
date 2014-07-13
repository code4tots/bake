struct Dict : Object {
	std::unordered_map<Pointer,Pointer> x;
	Dict(Pairs);
	
	// string representation
	Pointer repr();
	
	
	Pointer truth();
};
