import re
def build_lexer(keywords,symbols):
	"""Build the lexer
	Building the lexer is done inside a function because we need to know all
	the keywords and symbols before we can actually build the regex.
	However, we don't know those until the parser is built. So we must delay
	until all the parser is built.
	"""
	class Token(str):
		def __new__(cls,type_,whole_string,token_string,start,end):
			self = super(Token,cls).__new__(cls,token_string)
			self.type_ = type_
			self.whole_string = whole_string
			self.token_string = token_string
			self.start = start
			self.end = end
			
			self.line_number = 1+whole_string.count('\n',0,start)
			
			a = whole_string.rfind('\n',0,start) + 1
			b = whole_string.find('\n',start)
			if b == -1:
				b = len(whole_string)
			self.line = whole_string[a:b]
			
			return self
			
		def __repr__(self):
			return repr((self.type_,self.token_string,self.start,self.end))

	class TokenStream(object):
		def __init__(self,token_generator):
			self.token_list = list(token_generator)
			self.position = 0
		
		def peek(self):
			return self.token_list[self.position]
		
		def save(self):
			return self.position
		
		def load(self,position):
			self.position = position
		
		def next(self):
			return self.__next__()
		
		def __next__(self):
			self.position += 1
			return self.token_list[self.position-1]
	
	token_types = {
		'int' : r'\d+(?!\.)',
		'float' : r'\d+\.\d*',
		'keyword' : '|'.join(keyword+r'(?!\w)' for keyword in keywords),
		'name' : ''.join(r'(?!'+keyword+r'(?!\w))' for keyword in keywords)+r'(?!r\"|r\'|\d)\w+',
		'str' : '|'.join('(?:'+s+')' for s in (
			r'\"(?:[^"]|(?:\\\"))*\"',
			r"\'(?:[^']|(?:\\\'))*\'",
			r'r\"[^"]*\"',
			r"r\'[^']*\'")),
		'symbol' : '|'.join('(?:'+re.escape(symbol)+')' for symbol in reversed(sorted(symbols)))}
	ignore_regex = re.compile(r'(?:(?:\s+)|(?:\#[^\n]*))*')
	err_regex = re.compile(r'\S+')
	for token_type, regex_string in token_types.items():
		token_types[token_type] = re.compile(regex_string)

	def lex(string):
		i = 0
		while True:
			i = ignore_regex.match(string,i).end()
			if i >= len(string):
				break
			
			for type_, regex in token_types.items():
				m = regex.match(string,i)
				if m:
					i = m.end()
					yield Token(type_,string,m.group(),m.start(),i)
					break
			else:
				m = err_regex.match(string,i)
				t = Token('err',string,m.group(),m.start(),m.end())
				raise ParseException('Unrecognized token on line %s: %s\n%s'%
					(t.line_number, t, t.line))
		
		yield Token('eof',string,'',len(string),len(string))
	return lambda string : TokenStream(lex(string))

def build_parser():
	"""For the sake of symmetry, the parser is built inside a function as well
	"""
	keywords = set()
	symbols = set()
	class Parser(object):
		def __call__(self,stream):
			save = stream.save()
			result = self._parse(stream)
			if result is None:
				stream.load(save)
			return result
	class Proxy(Parser):
		def __init__(self):
			self.parser = None
		def _parse(self,stream):
			return self.parser(stream)
	class TokenSatisfying(Parser):
		def __init__(self,condition):
			self.condition = condition
		def _parse(self,stream):
			if self.condition(stream.peek()):
				return next(stream)
	class TokenOfType(TokenSatisfying):
		def __init__(self,type_):
			self.type_ = type_
			super(TokenOfType,self).__init__(lambda t : t.type_ == type_)
	class Token(TokenSatisfying):
		def __init__(self,token):
			super(Token,self).__init__(lambda t : t == token)
	class Keyword(Token):
		def __init__(self,keyword):
			keywords.add(keyword)
			super(Keyword,self).__init__(keyword)
	class Symbol(Token):
		def __init__(self,symbol):
			symbols.add(symbol)
			super(Symbol,self).__init__(symbol)
	class NamedString(str):
		def __new__(cls,s,name):
			self = super(NamedString,cls).__new__(cls,s)
			self.name = name
			return self
	class Named(Proxy):
		def __init__(self,name,parser):
			def action(x):
				if type(x) == str:
					return NamedString(x,name)
				x.name = name
				return x
			self.parser = OnSuccess(parser,action)
	class OnSuccess(Parser):
		def __init__(self,parser,action):
			self.parser = parser
			self.action = action
		def _parse(self,stream):
			result = self.parser(stream)
			if result is not None:
				return self.action(result)
	class OnFailure(Parser):
		def __init__(self,parser,action):
			self.parser = parser
			self.action = action
		def _parse(self,stream):
			result = self.parser(stream)
			if result is None:
				return self.action(result)
			return result
	class Or(Parser):
		def __init__(self,*parsers):
			self.parsers = parsers
		def _parse(self,stream):
			for parser in self.parsers:
				result = parser(stream)
				if result is not None:
					return result
	class And(Parser):
		def __init__(self,*parsers):
			self.parsers = parsers
		def _parse(self,stream):
			xs = []
			for parser in self.parsers:
				x = parser(stream)
				if x is None:
					return None
				xs.append(x)
			return xs
	class ZeroOrMore(Parser):
		def __init__(self,parser):
			self.parser = parser
		def _parse(self,stream):
			xs = []
			while True:
				x = self.parser(stream)
				if x is None:
					return xs
				xs.append(x)
	class OneOrMore(Proxy):
		def __init__(self,parser):
			def action(x):
				a, b = x
				return a + b
			self.parser = OnSuccess(And(parser,ZeroOrMore(parser)),action)
	class SeparatedBy(Proxy):
		def __init__(self,separator_parser,parser):
			def action(x):
				x, xs = x
				r = [x]
				for (sep,y) in xs:
					r.append(y)
				return r
			self.parser = OnSuccess(And(parser,ZeroOrMore(And(separator_parser,parser))),action)
	no_match = object()
	class Optional(Parser):
		def __init__(self,parser):
			self.parser = parser
		def _parse(self,stream):
			result = self.parser(stream)
			if result is None:
				return no_match
			return result
	class BinaryOperation(Proxy):
		def __init__(self,op_parser,parser):
			def action(xs):
				return [i for s in xs for i in s]
			def singleton(x):
				return [x]
			self.parser = OnSuccess(And(OnSuccess(parser,singleton),ZeroOrMore(And(op_parser,parser))),action)
	class LeftAssociativeBinaryOperation(Proxy):
		def __init__(self,action,op_parser,parser):
			def _action(xs):
				e = xs[0]
				for i in range(1,len(xs),2):
					e = action(e,xs[i],xs[i+1])
				return e
			self.parser = OnSuccess(BinaryOperation(op_parser,parser),_action)
	class RightAssociativeBinaryOperation(Proxy):
		def __init__(self,action,op_parser,parser):
			def _action(xs):
				e = xs[-1]
				for i in reversed(range(1,len(xs),2)):
					e = action(xs[i-1],xs[i],e)
				return e
			self.parser = OnSuccess(BinaryOperation(op_parser,parser),_action)
	class PostfixOperation(Proxy):
		def __init__(self,action,op_parser,parser):
			def _action(xss):
				e, xs = xss
				for x in xs:
					e = action(e,x)
				return e
			self.parser = OnSuccess(And(parser,ZeroOrMore(op_parser)),_action)
	class PrefixOperation(Proxy):
		def __init__(self,action,op_parser,parser):
			def _action(xss):
				xs, e = xss
				for x in reversed(xs):
					e = action(x,e)
				return e
			self.parser = OnSuccess(And(ZeroOrMore(op_parser),parser),_action)
	Expression = Proxy()
	Statement = Proxy()
	Name = OnSuccess(TokenOfType('name'),lambda x : 'x_x'+x)
	ListLiteral = OnSuccess(
		And(Keyword('list'),ZeroOrMore(Expression),Keyword('end')),
		lambda xs : "Pointer::new_list({"+','.join(xs[1])+"})")
	SetLiteral = OnSuccess(
		And(Keyword('set'),ZeroOrMore(Expression),Keyword('end')),
		lambda xs : 'Pointer::new_set({'+','.join(xs[1])+'})')
	DictLiteral = OnSuccess(
		And(Keyword('dict'),ZeroOrMore(And(Expression,Expression)),Keyword('end')),
		lambda xs : 'Pointer::new_dict({'+','.join('{'+x[0]+','+x[1]+'}' for x in xs[1])+'})')
	FuncLiteral = OnSuccess(
		And(Symbol('\\'),ZeroOrMore(Name),Symbol('{'),ZeroOrMore(Statement),Symbol('}')),
		lambda xs :
			'Pointer::new_func([&](Args args)->Pointer{'+
				(('auto i=args.begin();Pointer '+','.join(x+'=*i++' for x in xs[1])+';') if xs[1] else '')+
				''.join(xs[3])+'return Pointer::new_nil();})')
	PrimaryExpression = Or(
		OnSuccess(TokenOfType('int'),lambda x : 'Pointer::new_int('+str(x)+')'),
		OnSuccess(TokenOfType('float'), lambda x : 'Pointer::new_float('+str(x)+')'),
		OnSuccess(TokenOfType('str'), lambda x : 'Pointer::new_str("'+''.join('\\'+hex(ord(c))[1:] for c in str(x)+'")')),
		Name,
		OnSuccess(And(Symbol('('),Expression,Symbol(')')),lambda x : x[1]),
		ListLiteral,SetLiteral,DictLiteral,FuncLiteral)
	PrimaryPostfixExpression = PostfixOperation((lambda e,op:
			'%s.%s()'%(e,('_' if op[1] in ('int','float') else '')+op[1]) if op[0] == '.' else
			'%s.setitem(%s,%s)'%(e,op[1],op[3]) if '=' in op else
			'%s.call({%s})'%(e,','.join(op[1]))),
		Or(
			And(Symbol('.'),Or(TokenOfType('keyword'),TokenOfType('name'))),
			And(Symbol('['),Expression,Symbol('='),Expression,Symbol(']')),
			And(Symbol('['),ZeroOrMore(Expression),Symbol(']'))),
		PrimaryExpression)
	Expression.parser = PrimaryPostfixExpression
	ExpressionStatement = OnSuccess(Expression,lambda e : e+';')
	def action(xs):
		x, xs = xs
		ss = []
		for x in xs:
			s = x[0]
			if x[1] != no_match:
				s += '='+x[1][1]
			ss.append(s)
		return 'Pointer '+','.join(ss)+';'
	Declaration = OnSuccess(And(Keyword('var'),
		SeparatedBy(Symbol(','),
			And(Name,Optional(And(Symbol('='),Expression))))),action)
	Statement.parser = Or(Declaration,ExpressionStatement)
	TranslationUnit = OnSuccess(ZeroOrMore(Statement),lambda xs : ''.join(xs))
	lexer = build_lexer(keywords,symbols)
	return lambda string : TranslationUnit(lexer(string))
def main():
	from sys import argv
	if len(argv) != 3:
		print('usage: %s <bakefile-name> <outputfile-name>' % argv[0])
	else:
		with open(argv[1]) as f:
			code = f.read()
		cxx = build_parser()(code)
		with open(argv[2],'w') as f:
			f.write('void bake(){')
			f.write(cxx)
			f.write('}')
if __name__ == '__main__':
	main()
