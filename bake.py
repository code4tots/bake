import re

symbols = set()
keywords = set()

def singleton(cls):
	return cls()

class ParseException(Exception):
	pass

class Parser(object):
	def __call__(self,stream):
		save = stream.tell()
		result = self.parse(stream)
		if result is None:
			stream.seek(save)
		return result
	
	def parse(self,stream):
		return self._parse(stream)

class OneOf(Parser):
	def __init__(self,parsers):
		self.parsers = parsers
	
	def __call__(self,stream):
		for parser in self.parsers:
			parse = parser(stream)
			if parse is not None:
				return parse

class ZeroOrMore(Parser):
	def __init__(self,parser):
		self.parser = parser
	
	def __call__(self,stream):
		parser = self.parser
		results = []
		while True:
			result = parser(stream)
			if result is None:
				return results
			results.append(result)

class CommaSeparated(Parser):
	def __init__(self,parser):
		self.parser = parser
	
	def __call__(self,stream):
		parser = self.parser
		results = []
		while True:
			result = parser(stream)
			if result is None:
				return None
			results.append(result)
			if not Comma(stream):
				return results

class Symbol(Parser):
	def __init__(self,symbol):
		self.symbol = symbol
		symbols.add(symbol)
	
	def _parse(self,stream):
		if stream.peek() == self.symbol:
			return next(stream)

class Keyword(Parser):
	def __init__(self,keyword):
		self.keyword = keyword
		keywords.add(keyword)
	
	def _parse(self,stream):
		if stream.peek() == self.keyword:
			return next(stream)

@singleton
class Int(Parser):
	def _parse(self,stream):
		if stream.peek().type_ == 'int':
			i = int(next(stream))
			if i > 2 ** 31:
				i = '"' + str(i) + '"'
			return 'Pointer(new Int('+str(i)+'))'

@singleton
class Float(Parser):
	def _parse(self,stream):
		if stream.peek().type_ == 'float':
			return 'Pointer(new Float('+next(stream)+'))'

@singleton
class Str(Parser):
	def _parse(self,stream):
		if stream.peek().type_ == 'str':
			return 'Pointer(new Str("'+''.join(
				'\\'+hex(ord(c))[1:] for c in eval(next(stream)))+'"))'

@singleton
class Name(Parser):
	def _parse(self,stream):
		if stream.peek().type_ == 'name':
			return 'x_x'+next(stream)

@singleton
class ParentheticalExpression(Parser):
	def _parse(self,stream):
		if OpenParenthesis(stream):
			e = Expression(stream)
			if e is not None:
				if CloseParenthesis(stream):
					return e

@singleton
class ExpressionPair(Parser):
	def _parse(self,stream):
		key = Expression(stream)
		if key is not None:
			if Colon(stream):
				value = Expression(stream)
				if value is not None:
					return '{%s,%s}'%(key,value)

@singleton
class PrimaryExpression(Parser):
	def _parse(self,stream):
		for parser in (Int,Float,Str,Name,ParentheticalExpression):
			result = parser(stream)
			if result is not None:
				return result
		
		if OpenBrace(stream):
			pairs = ZeroOrMore(ExpressionPair)(stream)
			if CloseBrace(stream):
				return 'Pointer(new Dict({'+','.join(map(str,pairs))+'}))'
		
		if OpenParenthesis(stream):
			e = Expression(stream)
			if CloseParenthesis(stream):
				return e

@singleton
class SecondaryExpression(Parser):
	def _parse(self,stream):
		e = PrimaryExpression(stream)
		if e is not None:
			while True:
				save = stream.tell()
				# function call
				if OpenParenthesis(stream):
					args = CommaSeparated(Expression)(stream)
					if args is not None and CloseParenthesis(stream):
						e = '%s->call({%s})'%(e,','.join(map(str,args)))
					else:
						stream.seek(save)
						return e
				# subscript
				elif OpenBracket(stream):
					arg = Expression(stream)
					if arg is not None:
						if CloseBracket(stream):
							e = '%s->getitem(%s)'%(e,arg)
						elif Equal(stream):
							v = Expression(stream)
							if v is not None and CloseBracket(stream):
								e = '%s->setitem(%s,%s)'%(e,arg,v)
							else:
								stream.seek(save)
								return e
						else:
							stream.seek(save)
							return e
					else:
						stream.seek(save)
						return e
				else:
					return e

class PrefixExpression(Parser):
	def __init__(self,operators,higher_priority_expression):
		self.operators = operators # operator name pairs
		self.higher_priority_expression = higher_priority_expression
	
	def _parse(self,stream):
		for operator,operator_name in self.operators:
			op = operator(stream)
			if op is not None:
				e = self.higher_priority_expression(stream)
				if e is not None:
					return '%s->%s()'%(e,operator_name)
		else:
			return self.higher_priority_expression(stream)

class BinaryExpression(Parser):
	def __init__(self,operators,higher_priority_expression):
		self.operators = operators # operator name pairs
		self.higher_priority_expression = higher_priority_expression
	
	def _parse(self,stream):
		a = self.higher_priority_expression(stream)
		if a is not None:
			for operator, operator_name in self.operators:
				op = operator(stream)
				if op is not None:
					b = self.higher_priority_expression(stream)
					if b is not None:
						return '%s->%s(%s)' % (a,operator_name,b)
					else:
						return
			else:
				return a

@singleton
class ExpressionStatement(Parser):
	def _parse(self,stream):
		e = Expression(stream)
		if e is not None:
			if Semicolon(stream):
				return e+';'

@singleton
class Declarator(Parser):
	def _parse(self,stream):
		name = Name(stream)
		if name is not None:
			if Equal(stream):
				expression = Expression(stream)
				if expression:
					return '%s=%s'%(name,expression)
				else:
					return None
			else:
				return name

@singleton
class Declaration(Parser):
	def _parse(self,stream):
		if Var(stream):
			decls = CommaSeparated(Declarator)(stream)
			if Semicolon(stream):
				return 'Pointer %s;'%','.join(decls)

@singleton
class SimpleAssignment(Parser):
	def _parse(self,stream):
		name = Name(stream)
		if name is not None:
			if Equal(stream):
				expression = Expression(stream)
				if expression is not None:
					if Semicolon(stream):
						return '%s=%s;'%(name,expression)

@singleton
class StatementBlock(Parser):
	def _parse(self,stream):
		if OpenBrace(stream):
			statements = Statements(stream)
			if CloseBrace(stream):
				return '{%s}'%''.join(map(str,statements))

@singleton
class WhileStatement(Parser):
	def _parse(self,stream):
		if While(stream):
			condition = Expression(stream)
			if condition is not None:
				body = StatementBlock(stream)
				if body is not None:
					return 'while(%s)%s'%(condition,body)

Semicolon = Symbol(';')
Colon = Symbol(':')
Comma = Symbol(',')
OpenParenthesis = Symbol('(')
CloseParenthesis = Symbol(')')
OpenBracket = Symbol('[')
CloseBracket = Symbol(']')
OpenBrace = Symbol('{')
CloseBrace = Symbol('}')
Equal = Symbol('=')
Var = Keyword('var')
While = Keyword('while')
Expression = (
	BinaryExpression(
		(
			(Symbol('+'), 'add'),
			(Symbol('-'), 'subtract')),
		PrefixExpression(
			(
				(Symbol('+'), 'positive'),
				(Symbol('-'), 'negative')),
			SecondaryExpression)))

Statement = OneOf((
	ExpressionStatement,
	Declaration,
	SimpleAssignment,
	StatementBlock,
	WhileStatement))

Statements = ZeroOrMore(Statement)

@singleton
class All(Parser):
	def _parse(self,stream):
		statements = Statements(stream)
		token = stream.peek()
		if token.type_ != 'eof':
			raise ParseException(
				'invalid statement on line %s: %s\n%s' % (token.line_number,token,token.line))
		return 'void bake(){'+''.join(map(str,statements))+'}\n'

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
	'symbol' : '|'.join('(?:'+re.escape(symbol)+')' for symbol in reversed(sorted(symbols)))
}
ignore_regex = re.compile(r'(?:(?:\s+)|(?:\#[^\n]*))*')
err_regex = re.compile(r'\S+')
for token_type, regex in token_types.items():
	token_types[token_type] = re.compile(regex)

def lex(string):
	def token_generator():
		i = ignore_regex.match(string).end()
		while i < len(string):
			for token_type, regex in token_types.items():
				m = regex.match(string,i)
				if m:
					i = m.end()
					yield Token(token_type,string,m.group(),m.start(),m.end())
					break
			else:
				m = err_regex.match(string,i)
				t = Token('err',string,m.group(),m.start(),m.end())
				raise ParseException(
					'Unrecognized token on line %s: %s\n%s' %
					(t.line_number,t.token_string,t.line))
			i = ignore_regex.match(string,i).end()
		yield Token('eof',string,'',len(string),len(string))
	return TokenStream(token_generator())

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
	
	def __next__(self):
		self.position += 1
		return self.token_list[self.position-1]
	
	def next(self):
		return self.__next__()
	
	def peek(self):
		return self.token_list[self.position]
	
	def seek(self,position):
		self.position = position
	
	def tell(self):
		return self.position

if __name__ == '__main__':
	try:
		with open('cake.bake') as f:
			code = f.read()
		
		translation = All(lex(code))
		
		with open('cream.cpp','w') as f:
			f.write(translation)
	
	except ParseException as e:
		print('\n'.join('^^^^^^^^^^ '+line for line in str(e).splitlines()))
		exit(1)
		#print(re.compile(r'$').sub(str(e),'*** '))


