import re
from ply import lex, yacc

class Lexer(object):
	keywords = ('var', 'if', 'else')
	
	symbols = {
		',' : 'COMMA',
		'(' : 'LPAR',
		')' : 'RPAR',
		'[' : 'LBKT',
		']' : 'RBKT',
		'{' : 'LBCE',
		'}' : 'RBCE',
		'=' : 'EQ',
		'+' : 'PLUS',
		'-' : 'MINUS',
		'*' : 'STAR',
		'/' : 'SLASH',
		
		'==' : 'EQU',
	}
	
	tokens = (('NAME','INT','FLOAT','STRING','NEWLINE')+
		tuple(k.upper() for k in keywords) +
		tuple(symbols.values()))
	
	t_ignore = ' \t'
	
	def t_NEWLINE(self,t):
		r'\n+'
		t.lexer.lineno += len(t.value)
		return t
	
	def t_COMMENT(self,t):
		r'\#[^\n]*'
	
	def t_NUMBER(self,t):
		r'\d+(?:\.\d*)?'
		t.type = 'FLOAT' if '.' in t.value else 'INT'
		return t
	
	def t_NAME(self,t):
		r'(?!r\"|r\'|\d)\w+'
		if t.value in self.keywords:
			t.type = t.value.upper()
		return t
	
	t_STRING = '|'.join('(?:'+s+')' for s in (
		r'\"(?:[^"]|(?:\\\"))*\"',
		r"\'(?:[^']|(?:\\\'))*\'",
		r'r\"[^"]*\"',
		r"r\'[^']*\'"))
	
	def __init__(self, **kwargs):
		self.lexer = lex.lex(module=self, **kwargs)
	
	def token(self):
		return self.lexer.token()
	
	def input(self,data):
		return self.lexer.input(data)
	
	def test(self,data):
		self.lexer.input(data)
		while True:
			tok = self.lexer.token()
			if not tok: break
			print(tok)

for t, n in Lexer.symbols.items():
	setattr(Lexer,'t_'+n,re.escape(t))

class Parser(object):
	lexer = Lexer()
	tokens = Lexer.tokens
	
	precedence = (
		('left', 'EQU'),
		('left', 'PLUS', 'MINUS'),
		('left', 'STAR', 'SLASH'),
		('right', 'UMINUS'),
		('right', 'LPAR')
	)
	
	start = 'all'
	
	def p_all(self,t):
		'all : statements'
		print([str(x) for x in t[1]])
		t[0] = 'void bake() {\n' + ''.join(s.__str__(1) for s in t[1]) + '}\n'
	
	def p_statements_base(self,t):
		'statements : statement'
		t[0] = [t[1]]
	
	def p_statements_inductive_step(self,t):
		'statements : statements statement'
		t[0] = t[1]
		t[0].append(t[2])
	
	def p_statement_block(self,t):
		'statement : LBCE statements RBCE'
		t[0] = BlockStatement(t[2])
	
	def p_statement_expression(self,t):
		'statement : expression NEWLINE'
		t[0] = ExpressionStatement(t[1])
	
	def p_statement_declaration(self,t):
		'statement : VAR NAME EQ expression NEWLINE'
		t[0] = [t[2],t[4]]
	
	def p_if(self,t):
		'if_statement : IF LPAR expression RPAR statement'
		t[0] = IfStatement(t[3],t[5])
	
	def p_if_else(self,t):
		'if_else_statement : if_statement ELSE statement'
		t[0] = IfElseStatement(t[1],t[3])
	
	def p_statement_if(self,t):
		"""statement : if_statement
		             | if_else_statement"""
		# !!!!!!!!!!!!!!!!!!!!!!!!!!! Brings about a shift/reduce conflict.
		# The default behavior is to shift, which is the correct one in this case
		# (if ELSE is available, I want to shift and get an if_else_statement).
		t[0] = t[1]
	
	def p_statement_empty(self,t):
		'statement : NEWLINE'
		t[0] = EmptyStatement()
	
	def p_expression_int(self,t):
		'expression : INT'
		t[0] = IntExpression(t[1])
	
	def p_expression_float(self,t):
		'expression : FLOAT'
		t[0] = FloatExpression(t[1])
	
	def p_expression_string(self,t):
		'expression : STRING'
		t[0] = StringExpression(t[1])
	
	def p_expression_name(self,t):
		'expression : NAME'
		t[0] = NameExpression(t[1])
	
	def p_expression_list(self,t):
		'expression : LBKT expression_list RBKT'
		t[0] = ListExpression(t[2])
	
	def p_expression_group(self,t):
		'expression : LPAR expression RPAR'
		t[0] = t[2]
	
	def p_expression_add(self,t):
		'expression : expression PLUS expression'
		t[0] = AddExpression(t[1],t[3])
		
	def p_expression_subtract(self,t):
		'expression : expression MINUS expression'
		t[0] = SubtractExpression(t[1],t[3])
		
	def p_expression_multiply(self,t):
		'expression : expression STAR expression'
		t[0] = MultiplyExpression(t[1],t[3])
		
	def p_expression_divide(self,t):
		'expression : expression SLASH expression'
		t[0] = DivideExpression(t[1],t[3])
	
	def p_expression_minus(self,t):
		'expression : MINUS expression %prec UMINUS'
		t[0] = MinusExpression(t[2])
	
	def p_expression_function_call(self,t):
		'expression : expression LPAR expression_list RPAR'
		t[0] = FunctionCallExpression(t[1],t[3])
	
	def p_expression_equal(self,t):
		'expression : expression EQU expression'
		t[0] = EqualExpression(t[1],t[3])
	
	def p_expression_list_base(self,t):
		'expression_list : expression'
		t[0] = [t[1]]
	
	def p_expression_list_inductive_step(self,t):
		'expression_list : expression_list COMMA expression'
		t[0] = t[1]
		t[0].append(t[3])
	
	def __init__(self,**kargs):
		self.parser = yacc.yacc(module=self, **kargs)
	
	def parse(self,data):
		return self.parser.parse(data)


class Statement(object):
	_indentation = '\t'
	
	def indentation(self,depth):
		return self._indentation * depth

class BlockStatement(Statement):
	def __init__(self,statements):
		self.statements = statements
	
	def __str__(self,depth=0):
		return (
			self.indentation(depth) + '{\n' +
			''.join(s.__str__(depth+1) for s in self.statements) +
			self.indentation(depth) + '}\n')

class IfStatement(Statement):
	def __init__(self,condition,if_block):
		self.condition = condition
		self.if_block = if_block
	
	def __str__(self,depth=0):
		return (
			self.indentation(depth) + 'if (' + str(self.condition) + '->cxxbool())\n' +
			self.if_block.__str__(depth+1))
	
class IfElseStatement(Statement):
	def __init__(self,if_statement,else_block):
		self.if_statement = if_statement
		self.else_block = else_block
	
	def __str__(self,depth=0):
		return (
			self.if_statement.__str__(depth) +
			self.indentation(depth) + 'else\n' +
			self.else_block.__str__(depth+1))

class ExpressionStatement(Statement):
	def __init__(self,expression):
		self.expression = expression
	
	def __str__(self,depth=0):
		return self.indentation(depth) + str(self.expression) + ';\n'

class EmptyStatement(Statement):
	def __str__(self,depth=0):
		return ''

class Expression(object):
	pass

class IntExpression(Expression):
	def __init__(self,integer):
		self.integer = integer
	
	def __str__(self):
		return '(new Int('+self.integer+'))'

class FloatExpression(Expression):
	def __init__(self,floating):
		self.floating = floating
	
	def __str__(self):
		return '(new Float('+self.floating+'))'

class StringExpression(Expression):
	def __init__(self,string):
		self.string = string
	
	def to_c_string(self,string):
		return '"'+''.join('\\'+hex(ord(c))[1:] for c in string)+'"'
	
	def __str__(self):
		return '(new Str('+self.to_c_string(eval(self.string))+'))'

class NameExpression(Expression):
	def __init__(self,name):
		self.name = name
	
	def __str__(self):
		return 'ingredient_x' + self.name

class ListExpression(Expression):
	def __init__(self,expressions):
		self.expressions = expressions
	
	def __str__(self):
		return '(new List({'+','.join(map(str,self.expressions))+'}))'

class FunctionCallExpression(Expression):
	def __init__(self,expression,arguments):
		self.expression = expression
		self.arguments = arguments
	
	def __str__(self):
		return '%s->call({%s})'%(self.expression,','.join(map(str,self.arguments)))

class MethodExpression(Expression):
	def __init__(self,expression,argument=''):
		self.expression = expression
		self.argument = argument
	
	def __str__(self):
		return '%s->%s(%s)'%(self.expression,self.method_name,self.argument)

class AddExpression(MethodExpression):
	method_name = 'add'

class SubtractExpression(MethodExpression):
	method_name = 'subtract'

class MinusExpression(MethodExpression):
	method_name = 'minus'

class MultiplyExpression(MethodExpression):
	method_name = 'multiply'

class DivideExpression(MethodExpression):
	method_name = 'divide'

class EqualExpression(MethodExpression):
	method_name = 'equal'

if __name__ == '__main__':
	with open('stub.cpp') as f:
		stub = f.read()
	
	with open('cake.bake') as f:
		code = f.read()
	
	code = Parser().parse(code)
	
	with open('cake.cpp', 'w') as f:
		f.write(stub)
		f.write(code)
