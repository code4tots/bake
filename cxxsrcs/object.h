struct Object {
	const Type type;
	
	virtual Pointer call(Args);
	virtual Pointer subscript(Pointer);
	
	// binary operators
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
	virtual Pointer hash();
	
	// C++ interface
	// Dangerous. Use with caution.
	bool cxxbool();
	mpz_class& cxxint();
	std::string& cxxstr();
	
protected:
	Object(Type);
	Pointer not_supported();
};
