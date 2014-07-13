import re


binary_operators = {
	'+' : 'add',
	'-' : 'subtract',
	'*' : 'multiply',
	'/' : 'divide',
	'%' : 'modulo',
	
	'==' : 'equal',
	'<' : 'less',
	'>' : 'greater',
	'<=' : 'greater_equal',
	'>=' : 'less_equal',
	
	'and' : 'logical_and',
	'or' : 'logical_or'
}

keywords = ('var', 'if', 'else') + tuple(k for k in binary_operators.keys() if k.isalpha())

symbols = tuple(set(
	tuple(k for k in binary_operators.keys() if not k.isalpha()) + (
	# grouping/delimier
	'(', ')', '{', '}', '[', ']',
	',', ':', '\\',
	
	# assignment
	'=')))

token_types = {
	'int' : r'\d+(?!\.)',
	'float' : r'\d+\.\d*',
	'keyword' : '|'.join(keyword+r'(?!\w)' for keyword in keywords),
	'name' : ''.join(r'(?!'+keyword+r'(?!\w))' for keyword in keywords)+r'(?!r\"|r\'|\d)\w+',
	'str' : '|'.join('(?:'+s+')' for s in (r'\"(?:[^"]|(?:\\\"))*\"',r"\'(?:[^']|(?:\\\'))*\'",r'r\"[^"]*\"',r"r\'[^']*\'")),
	'symbol' : '|'.join('(?:'+re.escape(symbol)+')' for symbol in reversed(sorted(symbols))),
	'newline' : r'(?:[ \t]*\n)+',
}
ignore_regex = re.compile(r'(?:(?:[ \t]+)|(?:\#[^\n]*))*')
err_regex = re.compile(r'\S+')

# '()' and '[]' indicate expressions, and as such, inside such parentheses, newlines are insignificant.
parentheses = {
	'(' : ')',
	'[' : ']',
	
	# Note that '{' and '}' braces are treated as a special case by the lexer.
	# If the inner most brace during the lex is '{}', then newlines are significant.
	# This is because '{}' determine code blocks, and in code blocks, we have statements
	# for which whitespace is significant.
	'{' : '}'
}

class ParseException(Exception):
	pass

for token_type in token_types:
	token_types[token_type] = re.compile(token_types[token_type])

parentheses_inverse = { v : k for k, v in parentheses.items() }

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

def lex(string):
	parenthesis_depth = {parenthesis : 0 for parenthesis in parentheses}
	
	parenthesis_stack = []
	
	i = ignore_regex.match(string).end() # skip ignorables
	while i < len(string):
		for token_type, regex in token_types.items():
			m = regex.match(string,i)
			if m:
				i = m.end()
				if token_type != 'newline' or not parenthesis_stack or parenthesis_stack[-1] == '{':
					token = Token(token_type,string,m.group(),m.start(),m.end())
					if token in parentheses:
						parenthesis_stack.append(token)
					
					if token in parentheses_inverse:
						if [parentheses_inverse[token]] == parenthesis_stack[-1:]:
							parenthesis_stack.pop()
						else:
							raise ParseException('mismatched parenthesis')
					
					yield token
				break
		else:
			raise ParseException('unrecognized token: ' + err_regex.match(string,i).group())
		i = ignore_regex.match(string,i).end() # skip ignorables
	
	yield Token('newline',string,'\n',len(string),len(string))
	yield Token('eof',string,'',len(string),len(string))

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

def backtrack(parser):
	def backtracking_parser(token_stream):
		save = token_stream.tell()
		result = parser(token_stream)
		if not result:
			token_stream.seek(save)
		return result
	return backtracking_parser


def token_parser(token):
	@backtrack
	def parse_token(token_stream):
		if next(token_stream) == token:
			return token
	return parse_token

def alternation_parser(*parsers):
	def parse_alternatives(token_stream):
		for parser in parsers:
			result = parser(token_stream)
			if result:
				return result
	return parse_alternatives

def modify_name_expression(name):
	return 'x_x' + name

@backtrack
def parse_primary_expression(token_stream):
	token = token_stream.peek()
	type_ = token.type_
	
	if type_ in ('int', 'float', 'str', 'name') or token in ('(','[','{','\\'):
		next(token_stream)
		
		if type_ == 'name':
			return modify_name_expression(token)
		
		elif type_ in ('int','float','str'):
			if type_ == 'str':
				token = '"'+''.join('\\'+hex(ord(c))[1:] for c in eval(token))+'"'
			elif type_ == 'int' and int(token) >= 2 ** 31:
				token = '"'+token+'"'
			return '(Pointer(new ' + type_.capitalize() + '('+ token + ')))'
		
		elif token == '(':
			expression = parse_expression(token_stream)
			if next(token_stream) == ')':
				return expression
		
		elif token == '[':
			expressions = parse_comma_separated_expressions(token_stream)
			if next(token_stream) == ']':
				return '(new List({'+','.join(expressions)+'}))'
		
		elif token == '{':
			j = token_stream.tell()
			
			expressions = parse_comma_separated_expressions(token_stream)
			if next(token_stream) == '}':
				return '(new Set({'+','.join(expressions)+'}))'
			else:
				token_stream.seek(j)
				pairs = parse_comma_separated_pairs(token_stream)
				if next(token_stream) == '}':
					return '(new Dict({'+','.join(pairs)+'}))'
		
		elif token == '\\':
			arguments = []
			while token_stream.peek().type_ == 'name':
				arguments.append(modify_name_expression(next(token_stream)))
			
			body = parse_block_statement(token_stream)
			return '(new Func([&](Args args) -> Pointer {auto i = args.begin(); Pointer '+','.join(argument+'=*i++' for argument in arguments)+';'+body+'return x_xnil; }))'

@backtrack
def parse_expression_pair(token_stream):
	key = parse_expression(token_stream)
	if not key:
		return
	if next(token_stream) != ':':
		return
	value = parse_expression(token_stream)
	return '{'+key+','+value+'}'

# no backtrack as even success may yield a falsey value
def parse_comma_separated_pairs(token_stream):
	pairs = []
	while True:
		pair = parse_expression_pair(token_stream)
		if not pair:
			return pairs
		pairs.append(pair)
		if token_stream.peek() != ',':
			return pairs
		next(token_stream) # consume ','

def binary_expression_parser(parse_operator,parse_higher_priority_expression):
	@backtrack
	def parse_binary_expression(token_stream):
		a = parse_higher_priority_expression(token_stream)
		if not a:
			return None
		op = parse_operator(token_stream)
		if not op:
			return a
		b = parse_higher_priority_expression(token_stream)
		if not b:
			return None
		
		if op not in binary_operators:
			return '('+a+op+b+')'
		else:
			return a+'->'+binary_operators[op]+'('+b+')'
	return parse_binary_expression

def prefix_expression_parser(parse_operator,parse_higher_priority_expression):
	@backtrack
	def parse_prefix_expression(token_stream):
		operator = parse_operator(token_stream)
		if operator:
			expression = parse_higher_priority_expression(token_stream)
			if expression:
				return '('+operator+expression+')'
		else:
			return parse_higher_priority_expression(token_stream)
	return parse_prefix_expression
		
def postfix_expression_parser(parse_operator,parse_higher_priority_expression):
	@backtrack
	def parse_postfix_expression(token_stream):
		expression = parse_higher_priority_expression(token_stream)
		if not expression:
			return None
		operator = parse_operator(token_stream)
		if not operator:
			return expression
		return '('+expression+operator+')'
	return parse_postfix_expression

# no backtrack -- may return falsey value even on success
def parse_comma_separated_expressions(token_stream):
	expressions = []
	while True:
		expression = parse_expression(token_stream)
		if not expression:
			return expressions
		expressions.append(expression)
		if token_stream.peek() != ',':
			break
		next(token_stream)
	return expressions

@backtrack
def parse_function_arguments(token_stream):	
	arguments = []
	if next(token_stream) == '(':
		arguments = parse_comma_separated_expressions(token_stream)
		if next(token_stream) == ')':
			return '({'+','.join(arguments)+'})'

parse_expression = (
	binary_expression_parser(alternation_parser(token_parser('=')),
		binary_expression_parser(alternation_parser(*list(map(token_parser,('or','and')))),
			binary_expression_parser(alternation_parser(*list(map(token_parser,('==','<','>','<=','>=')))),
				binary_expression_parser(alternation_parser(*list(map(token_parser,('+','-')))),
					binary_expression_parser(alternation_parser(*list(map(token_parser,('*','/')))),
						prefix_expression_parser(alternation_parser(*list(map(token_parser,('+','-')))),
							postfix_expression_parser(parse_function_arguments,
								parse_primary_expression))))))))

@backtrack
def parse_empty_statement(token_stream):
	if next(token_stream).type_ == 'newline':
		return ';'

@backtrack
def parse_expression_statement(token_stream):
	expression = parse_expression(token_stream)
	if next(token_stream).type_ == 'newline':
		return expression + ';'

@backtrack
def parse_declaration_statement(token_stream):
	if next(token_stream) == 'var':
		declarations = []
		while True:
			if token_stream.peek().type_ != 'name':
				return
			
			name = modify_name_expression(next(token_stream))
			
			if token_stream.peek() == '=':
				next(token_stream)
				expression = parse_expression(token_stream)
				if not expression:
					return None
				declarations.append(name + '=' + expression)
			
			else:
				declarations.append(name)
			
			if token_stream.peek() != ',':
				break
			
			next(token_stream) # consume ','
		
		if next(token_stream).type_ == 'newline':
			return 'Pointer ' + ','.join(declarations) + ';'

@backtrack
def parse_if_statement(token_stream):
	if next(token_stream) == 'if':
		condition = parse_expression(token_stream)
		if condition:
			if_block = parse_block_statement(token_stream)
			if if_block:
				statement = 'if('+condition+'->truth()->cxxbool())'+if_block
				if token_stream.peek() == 'else':
					next(token_stream)
					else_block = parse_block_statement(token_stream)
					if else_block:
						statement += 'else'+else_block
					else:
						return
				return statement

@backtrack
def parse_while_statement(token_stream):
	if next(token_stream) == 'while':
		condition = parse_expression(token_stream)
		if condition:
			block = parse_block_statement(token_stream)
			if block:
				return 'while('+condition+'->truth()->cxxbool())'+block

# no backtrack -- may return falsey value even on success
def parse_statements(token_stream):
	statements = []
	while True:
		statement = parse_statement(token_stream)
		if not statement:
			return [statement for statement in statements if statement != ';']
		statements.append(statement)

@backtrack
def parse_block_statement(token_stream):
	if next(token_stream) == '{':
		statements = parse_statements(token_stream)
		if next(token_stream) == '}':
			return '{'+''.join(statements)+'}'

@backtrack
def parse_statement(token_stream):
	# any(parser(token_stream) for parser in (...))
	# does not work because it returns a bool instead of the first true value
	for parser in (parse_empty_statement,parse_expression_statement,parse_block_statement,parse_declaration_statement,parse_if_statement,parse_while_statement):
		result = parser(token_stream)
		if result:
			return result

def parse(token_stream):
	statements = parse_statements(token_stream)
	token = token_stream.peek()
	if token.type_ == 'eof':
		return ''.join(statements)
	raise ParseException('invalid statement on line ' + str(token.line_number) + '\n' + token.line)


if __name__ == '__main__':
	with open('cake.bake') as f:
		code = f.read()
	
	try:		
		cxx = parse(TokenStream(lex(code)))
	
	except ParseException as e:
		print(str(e))
		exit(1)
	
	else:
		with open('cream.cpp', 'w') as f:
			f.write('int main() {')
			f.write(cxx)
			f.write('}\n')



