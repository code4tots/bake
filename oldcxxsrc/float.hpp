struct Float : Object {
	double x;
	Float(double f);
	
	Pointer add(Pointer);
	Pointer subtract(Pointer);
	Pointer multiply(Pointer);
	Pointer divide(Pointer);
	
	// string representation
	Pointer repr();
	
	Pointer equal(Pointer);
	Pointer less(Pointer);
	Pointer hash();
	
	Pointer truth();
};
