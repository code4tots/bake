#include <vector>
#include <unordered_map>
#include <unordered_set>

struct NotSupported;
struct Pointer;
struct Object;
struct Environment;
struct RootEnvironment;
struct ChildEnvironment;
struct Vm;

struct NotSupported {
};

struct Pointer {
	Object * x;
	Pointer(Object * const p) : x(p) {}
	Pointer(const Pointer& p) : x(p.x) {}
	Object * operator->() const { return x; }
};

struct Object {
};

struct Environment {
	virtual Pointer getitem(Pointer)=0;
	virtual Pointer setitem(Pointer,Pointer)=0;
	virtual Pointer declare(Pointer)=0;
};

struct RootEnvironment : Environment {
	
};

struct ChildEnvironment : Environment {
	Environment * parent;
	
};

struct Vm {
	std::vector<Pointer> stack;
	std::vector<std::string> string_constants;
	std::vector<mpz_class> integer_constants;
	Environment * environment;
	
	void load(size_t);
	void loadi(long i);
	void add();
};


