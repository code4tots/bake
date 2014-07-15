import re

keywords = set()
symbols = set()

class Parser(object):
	def __call__(self,stream):
		save = stream.position
		result = self._parse(stream)
		if result is None:
			stream.position = save
		return result

class TokenMatcher(Parser):
	def __init__(self,token):
		self.token = token
	
	def _parse(self,stream):
		if stream.peek() == self.token:
			return next(stream)

class TokenTypeMatcher(Parser):
	def __init__(self,type_):
		self.type_ = type_
	
	def _parse(self,stream):
		if stream.peek().type_ == self.type_:
			return next(stream)

class Keyword(TokenMatcher):
	def __init__(self,keyword):
		super(Keyword,self).__init__(keyword)
		keywords.add(keyword)

class Symbol(TokenMatcher):
	def __init__(self,symbol):
		super(Symbol,self).__init__(symbol)
		symbols.add(symbol)

class Token(str):
	def __init__(self,type_,whole_string,token_string,start,end):
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
	'symbol' : '|'.join('(?:'+re.escape(symbol)+')' for symbol in reversed(sorted(symbols))),
	'newline': r'(?:[ \t]*\n)+'
}
ignore_regex = re.compile(r'(?:(?:[ \t]+)|(?:\#[^\n]*))*')
err_regex = re.compile(r'\S+')

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
			print('Unrecognized token on line %s: %s\n%s'%
				(t.line_number, t, t.line))

