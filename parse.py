import re

class Parser(object):
	def __call__(self,stream):
		save = stream.position
		result = self._parse(stream)
		if result is None:
			stream.position = save
		return result
	
	def set_parse_action(self,action):
		self.action = action
		return self

class TokenConditionMatcher(Parser):
	def __init__(self,condition):
		self.condition = condition
	
	def _parse(self,stream):
		if self.condition(stream.peek()):
			return next(stream)

class TokenMatcher(TokenConditionMatcher):
	def __init__(self,token):
		super(TokenMatcher,self).__init__(lambda t : t == token)
		self.token = token

class TokenTypeMatcher(TokenConditionMatcher):
	def __init__(self,type_):
		super(TokenTypeMatcher,self).__init__(lambda t : t.type_ == type_)
		self.type_ = type_

class Keyword(TokenMatcher):
	def __init__(self,keyword):
		super(Keyword,self).__init__(keyword)
		keywords.add(keyword)

class Symbol(TokenMatcher):
	def __init__(self,symbol):
		super(Symbol,self).__init__(symbol)
		symbols.add(symbol)

class Or(Parser):
	def __init__(self,parsers):
		self.parsers = parsers
	
	def _parse(self,stream):
		for parser in self.parsers:
			result = parser(stream)
			if result is not None:
				return result

class And(Parser):
	def __init__(self,parsers):
		self.parsers = parsers
	
	def _parse(self,stream):
		results = []
		for parser in self.parsers:
			result = parser(stream)
			if result is None:
				return
			results.append(result)
		return self.action(*results)

class ZeroOrMore(Parser):
	def __init__(self,parser):
		self.parser = parser
	
	def _parse(self,stream):
		parser = self.parser
		results = []
		while True:
			result = parser(stream)
			if result is None:
				break
			results.append(result)
		return self.action(results)

class BinaryOperation(Parser):
	def __init__(self,operator_parser,higher_priority_expression_parser,associativity='left'):
		self.operator_parser = operator_parser
		self.higher_priority_expression_parser = higher_priority_expression_parser
		self.associativity = associativity
		if associativity not in ('left','right'):
			raise ParseException('"%s" is not a valid associativity' % associativity)
	
	def _parse(self,stream):
		higher_priority_expression_parser = self.higher_priority_expression_parser
		operator_parser = self.operator_parser
		action = self.action
		associativity = self.associativity
		
		e = higher_priority_expression_parser(stream)
		if e is None:
			return
		terms = [e]
		while True:
			op = operator_parser(stream)
			if op is None:
				break
			terms.append(e)
			e = higher_priority_expression_parser(stream)
			if e is None:
				return
			terms.append(e)
		
		if associativity == 'left':
			e = terms[0]
			for i in range(1,len(terms),2):
				e = action(e,terms[i],terms[i+1])
		elif associativity == 'right':
			e = terms[-1]
			for i in reversed(range(1,len(terms),2)):
				e = action(terms[i-1],terms[i],e)
		
		return e

class PrefixOperation(Parser):
	def __init__(self,operator_parser,higher_priority_expression_parser):
		self.operator_parser = ZeroOrMore(operator_parser).set_parse_action(lambda ops : ops)
		self.higher_priority_expression_parser = higher_priority_expression_parser
	
	def _parse(self,stream):
		higher_priority_expression_parser = self.higher_priority_expression_parser
		action = self.action
		
		operators = self.operator_parser(stream)
		
		e = higher_priority_expression_parser(stream)
		if e is not None:
			for op in reversed(operators):
				e = action(op,e)
			return e

class PostfixOperation(Parser):
	def __init__(self,operator_parser,higher_priority_expression_parser):
		self.operator_parser = operator_parser
		self.higher_priority_expression_parser = higher_priority_expression_parser
	
	def _parse(self,stream):
		operator_parser = self.operator_parser
		higher_priority_expression_parser = self.higher_priority_expression_parser
		

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





keywords = set()
symbols = set()





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
}
ignore_regex = re.compile(r'(?:(?:[ \t]+)|(?:\#[^\n]*))*')
err_regex = re.compile(r'\S+')


