struct Int : Object {
	mpz_class x;
	Int(long i);
	
	// string representation
	Pointer repr();
};
