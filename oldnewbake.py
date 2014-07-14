import re

class StringStream(object):
	def __init__(self,string):
		self.string = string
		self.position = 0
	
	def save(self):
		return self.position
	
	def load(self,position):
		self.position = position

def singleton(cls):
	return cls()

class Construct(object):
	keywords = set()
	
	def parse(self,string_stream):
		save = string_stream.save()
		result = self._parse(string_stream)
		if result is None:
			string_stream.load(save)
		return result
	
	def startswith(self,string):
		return self.string.startswith(string,self.position)

class Symbol(Construct):
	def __init__(self,symbol):
		self.symbol = symbol
	
	def _parse(self,string_stream):
		if string_stream.startswith(self.symbol):
			string_stream.position += len(self.symbol)
			return self.symbol

class Keyword(Construct):
	def __init__(self,keyword):
		self.keyword = keyword
		self.keywords.add(keyword)
	
	def _parse(self,string_stream):
		s = string_stream.string
		i = string_stream.position
		c = s[i]
		if s.startswith(self.keyword,i) and (i >= len(s) or (c !='_' and not c.isalnum())):
			string_stream.position += len(self.keyword)
			return self.keyword

class Expression(Construct):
	pass

@singleton
class name(Expression):
	def _parse(self,string_stream):
		s = string_stream.string
		i = string_stream.position
		if i < len(s):
			c = s[i]
			if c.isalpha() or c == '_':
				j = i+1
				c = s[j]
				while j < len(s) and c.isalphnum() or c == '_':
					j += 1
					c = s[j]
				n = s[i:j]
				if n not in self.keywords:
					string_stream.position = j
					return n

@singleton
class number(Expression):
	def _parse(self,string_stream):
		s = string_stream.string
		i = string_stream.position
		if i < len(s) and s[i].isdigit():
			j = i+1
			while s[j].isdigit():
				j += 1
			
			if j < len(s) and s[j] == '.':
				j += 1
				while s[j].isdigit():
					j += 1
				string_stream.position = j
				return s[i:j]
			else:
				string_stream.position = j
				return s[i:j]

@singleton
class string_literal(Expression):
	def _parse(self,string_stream):
		s = string_stream.string
		i = string_stream.position
		if i < len(s):
			q = s[i]
			if q in ('"',"'"):
				j = i+1
				while True:
					if j >= len(s):
						return # invalid string literal
					else:
						c = s[j]
						if c == '\\':
							j += 2
						elif c == q:
							j += 1
							string_stream.position = j
							return s[i:j]
						else:
							j += 1

@singleton
class primary_expression(Expression):
	def _parse(self,string_stream):
		for construct in (number,name,string_literal):
			result = construct.parse(string_stream)
			if result is not None:
				return result
		
		if string_stream

class BinaryExpression(Expression):
	def __init__(self,operator,higher_priority_expression):
		self.higher_priority_expression = higher_priority_expression
		self.operator = operator
		
		class BinaryExpressionInstance(object):
			def __init__(self,first,operator,second):
				self.first = first
				self.second = second
				self.operator = operator
		
		self.constructor = BinaryExpressionInstance
	
	def _parse(self,string_stream):
		first = self.higher_priority_expression.parse(string_stream)
		if first is not None:
			operator = self.operator.parse(string_stream)
			if operator is None:
				return first
			second = self.operator.parse(string_stream)
			if second is not None:
				return self.constructor(first,operator,second)

class PostfixExpression(Expression):
	def __init__(self,operator,higher_priority_expression):
		self.higher_priority_expression = higher_priority_expression
		self.operator = operator
		
		class PostfixExpressionInstance(object):
			def __init__(self,expression,operator):
				self.expression = expression
				self.operator = operator
		
		self.constructor = PostfixExpressionInstance
	
	def _parse(self,string_stream):
		expression = self.higher_priority_expression.parse(string_stream)
		if expression is not None:
			operator = self.operator.parse(string_stream)
			if operator is None:
				return expression
			else:
				return self.constructor(expression,operator)

class PrefixExpression(Expression):
	def __init__(self,operator,higher_priority_expression):
		self.higher_priority_expression = higher_priority_expression
		self.operator = operator
		
		class PrefixExpressionInstance(object):
			def __init__(self,operator,expression):
				self.operator = operator
				self.expression = expression
		
		self.constructor = PrefixExpressionInstance
	
	def _parse(self,string_stream):
		operator = self.operator.parse(string_stream)
		if operator is not None:
			expression = self.higher_priority_expression.parse(string_stream)
			if expression is not None:
				return self.constructor(operator,prefix)
		else:
			return self.higher_priority_expression(string_stream)




