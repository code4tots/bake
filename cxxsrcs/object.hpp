struct Object {
	const Type type;
	
	virtual Pointer call(Args);
	virtual Pointer subscript(Pointer);
	
	// arithmetic operators
	virtual Pointer add(Pointer);
	virtual Pointer subtract(Pointer);
	virtual Pointer multiply(Pointer);
	virtual Pointer divide(Pointer);
	virtual Pointer modulo(Pointer);
	
	// string representation
	virtual Pointer str();
	virtual Pointer repr();
	
	// comparison and hashing
	virtual Pointer equal(Pointer);
	virtual Pointer less(Pointer);
	virtual Pointer hash();
	
	virtual Pointer truth();
	
	virtual Pointer len();
	
	// logical operators
	Pointer logical_or(Pointer);
	Pointer logical_and(Pointer);
	
	// convenience comparison methods
	Pointer greater(Pointer);
	Pointer less_equal(Pointer);
	Pointer greater_equal(Pointer);
	
	// C++ interface
	// Dangerous. Use with caution.
	bool cxxbool();
	mpz_class& cxxint();
	double cxxfloat();
	std::string& cxxstr();
	
protected:
	Object(Type);
};
