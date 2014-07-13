struct Int : Object {
	mpz_class x;
	Int(long i);
	Int(std::string i);
	
	// string representation
	Pointer repr();
	
	Pointer truth();
};
