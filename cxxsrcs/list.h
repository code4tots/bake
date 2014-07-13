struct List : Object {
	std::vector<Pointer> x;
	List(Args a);
	
	// string representation
	Pointer repr();
};
