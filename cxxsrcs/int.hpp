struct Int : Object {
	mpz_class x;
	Int(long i);
	Int(const std::string& i);
	Int(const mpz_class& i);
	
	Pointer add(Pointer);
	Pointer subtract(Pointer);
	Pointer multiply(Pointer);
	Pointer divide(Pointer);
	Pointer modulo(Pointer);
	
	// string representation
	Pointer repr();
	
	Pointer truth();
};
