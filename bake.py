"half-baked programming language"

from sys import stderr

with open('bakestub.cpp') as f:
	cxxstub = f.read()

symbols = tuple(reversed(sorted([
	'(', ')', '{', '}', '[', ']', ',',
	'='
])))

keywords = set([
	'var',
	'if', 'else'
])

import re

comment_regex      = r'\#[^\n]*'
newline_regex      = r'\n'
space_regex        = r'[ \t]+'
float_regex        = r'\d+\.\d*'
int_regex          = r'\d+'
word_regex         = r'\w+'
single_quote_regex = r"\'(?:[^']|(?:\\\'))*\'"
double_quote_regex = r'\"(?:[^"]|(?:\\\"))*\"'
symbol_regex = '|'.join('(?:'+re.escape(symbol)+')' for symbol in symbols)

master_regex = '(?:'+'|'.join('(?:'+r+')' for r in(
	comment_regex,
	newline_regex,
	space_regex,
	float_regex,
	int_regex,
	word_regex,
	single_quote_regex,
	double_quote_regex,
	symbol_regex))+')'


sanity_regex       = re.compile(master_regex + '*')
master_regex       = re.compile(master_regex)
not_space_regex    = re.compile(r'\S+')
newline_regex      = re.compile(newline_regex)
space_regex        = re.compile(space_regex)
float_regex        = re.compile(float_regex)
int_regex          = re.compile(int_regex)
word_regex         = re.compile(word_regex)
quote_regex        = re.compile('(?:'+single_quote_regex+'|'+double_quote_regex+')')
single_quote_regex = re.compile(single_quote_regex)
double_quote_regex = re.compile(double_quote_regex)
symbol_regex       = re.compile(symbol_regex)

def lex(s):
	m = sanity_regex.match(s)
	e = m.end()
	if e != len(s):
		t = not_space_regex.match(s,e).group(0)
		raise Exception('unrecognized token: ' + repr(t))
	
	m = master_regex.findall(s)
	ts = [t for t in m if t and (t == '\n' or not t.isspace()) and t[0] != '#']
	nts = []
	for t in ts:
		if t != '\n' or (nts and nts[-1] != '\n'):
			nts.append(t)
	return nts

class Include(str):
	pass

class Stmt(object):
	indentation = '\t'

class BlockStmt(Stmt):
	def __init__(self,stmts):
		self.stmts = stmts
	
	def __str__(self,depth=0):
		i = self.indentation * depth
		return i+'{\n'+''.join(s.__str__(depth+1) for s in self.stmts)+i+'}\n'

class ExprStmt(Stmt):
	def __init__(self,expr):
		self.expr = expr
	
	def __str__(self,depth=0):
		return self.indentation * depth + str(self.expr) + ';\n'

class Decl(Stmt):
	def __init__(self,name,expr=None):
		self.name = name
		self.expr = expr
	
	def __str__(self,depth=0):
		s = self.indentation * depth + 'Object * ' + str(self.name)
		if self.expr is not None:
			s += ' = ' + str(self.expr)
		s += ';\n'
		return s

class IfStmt(Stmt):
	def __init__(self,expr,iblk,eblk):
		self.expr = expr
		self.iblk = iblk
		self.eblk = eblk
	
	def __str__(self,depth=0):
		s  = self.indentation*depth + 'if ('+str(self.expr)+'->cxxbool())\n'
		s += self.iblk.__str__(depth)
		if self.eblk:
			s += self.indentation*depth + 'else\n'
			s += self.eblk.__str__(depth)
		return s
		
class EmtpyStmt(Stmt):
	def __str__(self,depth=0):
		return ''
		
class Expr(object):
	pass

class Name(Expr):
	def __init__(self,name):
		self.name = name
	
	def __str__(self):
		return 'ingredient_x' + self.name

class Int(Expr):
	def __init__(self,i):
		self.i = i
	
	def __str__(self):
		return '(new Int(' + str(self.i) + '))'

class Float(Expr):
	def __init__(self,f):
		self.f = f
	
	def __str__(self):
		return '(new Float(' + str(self.f) + '))'

class String(Expr):
	def __init__(self,s):
		self.s = s
	
	def __str__(self):
		return '(new Str(' + str(self.s) + '))'

class Call(Expr):
	def __init__(self,f,args):
		self.f = f
		self.args = args
		
	def __str__(self):
		return str(self.f)+'->call({'+','.join(map(str,self.args))+'})'

class Subs(Expr):
	def __init__(self,a,i):
		self.a = a
		self.i = i
	
	def __str__(self):
		return str(self.a)+'->subscript('+str(self.i)+')'

def parse(s):
	ts = lex(s)      # list of tokens
	i = [0]          # current token index in the parse
	
	def tk(di=0):
		j = i[0] + di
		return ts[j] if j < len(ts) else ''
	
	def ntk():
		t = tk()
		if i[0] < len(s):
			i[0] += 1
		return t
	
	def consume(t):
		if tk() == t:
			return ntk()
	
	def float_(): # float token
		if float_regex.match(tk()):
			return Float(ntk())
	
	def int_(): # int token
		if int_regex.match(tk()):
			return Int(ntk())
	
	def string():
		if quote_regex.match(tk()):
			return String(ntk())
	
	def word(): # word token
		if word_regex.match(tk()) and tk() not in keywords:
			return Name(ntk())
	
	def parexpr(): # parenthetical expressions
		j = i[0]
		if consume('('):
			e = expr()
			if not e or tk() != ')':
				i[0] = j
				return
			ntk() # consume ')'
			return e
	
	def prexpr(): # primary expressions
		return float_() or int_() or string() or word() or parexpr()
	
	def fexpr(): # function calls and subscripts
		e = prexpr()
		
		if not e:
			return
		
		while tk() in ['(','[']:
			checkpoint = i[0]
			if consume('('):
				args = []
				if tk() != ')':
					a = expr()
					args.append(a)
					if not a:
						i[0] = checkpoint
						return e
					while tk() == ',':
						ntk()
						a = expr()
						args.append(a)
						if not a:
							i[0] = checkpoint
							return e
				if not consume(')'):
					i[0] = checkpoint
					return e
				
				e = Call(e,args)
			
			elif consume('['):
				a = expr()
				if not a:
					i[0] = checkpoint
					return e
				
				if not consume(']'):
					i[0] = checkpoint
					return e
				
				e = Subs(e,a)
		
		return e
	
	def expr():
		return fexpr()
	
	def exprstmt():
		j = i[0]
		e = expr()
		if not e:
			return
		
		if not consume('\n'):
			i[0] = j
			return
		
		return ExprStmt(e)
	
	def decl():
		j = i[0]
		
		if not consume('var'):
			return
		
		n = word()
		if not n:
			i[0] = j
			return
		
		e = None
		if consume('='):
			e = expr()
			if not e:
				i[0] = j
				return
		
		if not consume('\n'):
			i[0] = j
			return
		
		return Decl(n,e)
	
	def blockstmt():
		j = i[0]
		if consume('{'):
			ss = []
			st = stmt()
			while st:
				ss.append(st)
				st = stmt()
			if not consume('}'):
				i[0] = j
				return
			return BlockStmt(ss)
	
	def ifstmt():
		j = i[0]
		if consume('if'):
			if not consume('('):
				i[0] = j
				return
			
			e = expr()
			if not e or not consume(')'):
				i[0] = j
				return
			
			b = stmt()
			if not b:
				i[0] = j
				return
			
			eb = None
			if consume('else'):
				eb = stmt()
				if not b:
					i[0] = j
					return
			
			return IfStmt(e,b,eb)
	
	def emptystmt():
		if consume('\n'):
			return EmtpyStmt()
	
	def stmt():
		return emptystmt() or blockstmt() or ifstmt() or exprstmt() or decl()
	
	sts = []     # list of parsed statements
	st = stmt()
	while st:
		sts.append(st)
		st = stmt()
	
	return sts

def translate(s):
	stmts = parse(s)
	incs  = [stmt for stmt in stmts if     isinstance(stmt,Include)]
	stmts = [stmt for stmt in stmts if not isinstance(stmt,Include)]
	
	code = cxxstub
	
	for inc in incs:
		with open(inc+'.cpp') as f:
			code += f.read()
	
	code += 'void bake() {\n'
	code += ''.join(stmt.__str__(1) for stmt in stmts)
	code += '}\n'
	
	return code

if __name__ == '__main__':
	from sys import stdin
	print(translate(stdin.read()))

