import re

class ParseException(Exception):
	pass

class Parser(object):
	def __call__(self,stream):
		save = stream.save()
		result = self._parse(stream)
		if result is None:
			stream.load(save)
		return result

class Proxy(Parser):
	def set_parser(self,parser):
		self.parser = parser
	
	def _parse(self,stream):
		return self.parser(stream)

class TokenConditionMatcher(Parser):
	def __init__(self,condition):
		self.condition = condition
	
	def _parse(self,stream):
		if self.condition(stream.peek()):
			return next(stream)

class Action(Parser):
	def __init__(self,parser,action):
		self.parser = parser
		self.action = action
	
	def _parse(self,stream):
		result = self.parser(stream)
		if result is not None:
			return self.action(result)

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
	def __init__(self,parsers,action):
		self.parsers = parsers
		self.action = action
	
	def _parse(self,stream):
		results = []
		for parser in self.parsers:
			result = parser(stream)
			if result is None:
				return
			results.append(result)
		return self.action(*results)

class ZeroOrMore(Parser):
	def __init__(self,parser,action):
		self.parser = parser
		self.action = action
	
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
	def action(self,left,operator,right):
		return ['binary-operation', left, operator, right]
	
	def __init__(self,associativity,operator_parser,higher_priority_expression_parser):
		if associativity not in ('left','right'):
			raise ParseException('"%s" is not a valid associativity' % associativity)
		
		self.associativity = associativity
		self.operator_parser = operator_parser
		self.higher_priority_expression_parser = higher_priority_expression_parser
	
	def _parse(self,stream):
		higher_priority_expression_parser = self.higher_priority_expression_parser
		operator_parser = self.operator_parser
		associativity = self.associativity
		action = self.action
		
		e = higher_priority_expression_parser(stream)
		if e is None:
			return
		terms = [e]
		while True:
			op = operator_parser(stream)
			if op is None:
				break
			terms.append(op)
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

class TernaryOperation(Parser):
	def action(self,left_expression,left_operator,middle_expression,right_operator,right_expression):
		return ['ternary-operation',left_expression,left_operator,middle_expression,right_operator,right_expression]
	
	def __init__(self,associativity,left_operator_parser,right_operator_parser,higher_priority_expression_parser):
		self.binary_operation_parser = BinaryOperation(
			associativity,
			And((left_operator_parser,higher_priority_expression_parser,right_operator_parser),lambda l,m,r:[l,m,r]),
			higher_priority_expression_parser)
		
		def catch_action(left_expression,middle,right_expression):
			left_operator, middle_expression, right_operator = middle
			return self.action(left_expression,left_operator,middle_expression,right_operator,right_expression)
		
		self.binary_operation_parser.action = catch_action
		
	def _parse(self,stream):
		return self.binary_operation_parser(stream)

class PrefixOperation(Parser):
	def action(self,operator,expression):
		return ['prefix-operation', operator, expression]
	
	def __init__(self,operator_parser,higher_priority_expression_parser):
		self.operator_parser = ZeroOrMore(operator_parser,lambda ops : ops)
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
	def action(self,expression,operator):
		return ['postfix-operation', expression, operator]
	
	def __init__(self,operator_parser,higher_priority_expression_parser):
		self.operator_parser = ZeroOrMore(operator_parser, lambda ops: ops)
		self.higher_priority_expression_parser = higher_priority_expression_parser
	
	def _parse(self,stream):
		operator_parser = self.operator_parser
		higher_priority_expression_parser = self.higher_priority_expression_parser
		action = self.action
		
		e = higher_priority_expression_parser(stream)
		if e is not None:
			operators = self.operator_parser(stream)
			for op in operators:
				e = action(e,op)
			return e

class FunctionCall(PostfixOperation):
	def action(self,expression,arguments):
		return ['function-call', expression, arguments]
	
	def __init__(self,higher_priority_expression_parser):
		self.operator_parser = ZeroOrMore(And((
				Symbol('['),
				ZeroOrMore(Expression,lambda args : args),
				Symbol(']')),
					lambda lb, args, rb : args), lambda ops : ops)
		self.higher_priority_expression_parser = higher_priority_expression_parser

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

keywords = set()
symbols = set()

Expression = Proxy()
Expressions = ZeroOrMore(Expression, lambda expressions : expressions)
Statement = Proxy()
Statements = ZeroOrMore(Statement, lambda statements : statements)

Int = Action(TokenTypeMatcher('int'),lambda s : ['int',s])
Float = Action(TokenTypeMatcher('float'),lambda s : ['float',s])
Str = Action(TokenTypeMatcher('str'), lambda s : ['str',s])
Name = Action(TokenTypeMatcher('name'),lambda s : ['variable',s])
ParentheticalExpression = And((Symbol('('),Expression,Symbol(')')),lambda l, x, r: x)
ListLiteralExpression = And((Symbol('{'),Expressions,Symbol('}')),lambda l,x,r:['list-literal',x])
FunctionLiteralExpression = And(
	(Keyword('def'),
		Symbol('['),
		ZeroOrMore(Name,lambda names : names),
		Symbol(']'),
		Statements,
		Keyword('end')),
	lambda def_, lb, args, rb, body, end_: ['function-literal', args, body])

PrimaryExpression = Or((Int,Float,Str,Name,ParentheticalExpression))

Expression.set_parser(
	BinaryOperation(
		'right',
		Symbol('='),
	TernaryOperation(
		'left',
		Symbol('?'),Symbol(':'),
	BinaryOperation(
		'left',
		Symbol('||'),
	BinaryOperation(
		'left',
		Symbol('&&'),
	BinaryOperation(
		'left',
		Or((Symbol('+'),Symbol('-'))),
	BinaryOperation(
		'left',
		Or((Symbol('*'),Symbol('/'),Symbol('%'))),
	BinaryOperation(
		'right',
		Symbol('**'),
	PrefixOperation(
		Or((Symbol('+'),Symbol('-'))),
	FunctionCall(
	PrimaryExpression))))))))))


ExpressionStatement = Action(Expression,lambda expression : ['expression', expression])

IfElseStatement = And(
	(Keyword('if'),Expression,Statements,Keyword('else'),Statements,Keyword('end')),
	lambda if_, condition, if_body, else_, else_body, end_: ['if-else',condition,if_body,else_body])

WhileStatement = And(
	(Keyword('while'),Expression,Statements,Keyword('end')),
	lambda while_, condition, body, end_: ['while',condition,body])

Statement.set_parser(Or((ExpressionStatement,IfElseStatement,WhileStatement)))

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
ignore_regex = re.compile(r'(?:(?:\s+)|(?:\#[^\n]*))*')
err_regex = re.compile(r'\S+')
for token_type, regex_string in token_types.items():
	token_types[token_type] = re.compile(regex_string)

statements = Statements(TokenStream(lex('''
if 1
	f[2]
else
	3
end

f = def [a b c]
	
end

''')))
for statement in statements:
	print(statement)
