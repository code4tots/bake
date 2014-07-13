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
	
	
protected:
	Object(Type);
	Pointer not_supported();
};
