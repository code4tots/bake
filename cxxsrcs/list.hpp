struct List : Container {
	std::vector<Pointer> x;
	List(Args a);
	
	// string representation
	Pointer repr();
	
	Pointer len();
};
