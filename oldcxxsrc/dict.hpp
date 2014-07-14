struct Dict : Container {
	std::unordered_map<Pointer,Pointer> x;
	Dict(Pairs);
	
	Pointer& subscript(Pointer p);
	
	// string representation
	Pointer repr();
	
	Pointer len();
};
