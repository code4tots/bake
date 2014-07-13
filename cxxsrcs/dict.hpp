struct Dict : Container {
	std::unordered_map<Pointer,Pointer> x;
	Dict(Pairs);
	
	// string representation
	Pointer repr();
	
	Pointer len();
};
