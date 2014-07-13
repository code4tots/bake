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
	
	// logical operators
	Pointer logical_or(Pointer);
	Pointer logical_and(Pointer);
	
	// C++ interface
	// Dangerous. Use with caution.
	bool cxxbool();
	mpz_class& cxxint();
	std::string& cxxstr();
	
protected:
	Object(Type);
	Pointer not_supported();
};
