# -*- coding: UTF-8 -*-

import re

class TokenTexto:
	def __init__(self, texto='', ini=-1, fin=-1):
		self.texto = texto
		self.ini = ini
		self.fin = fin

	def __str__(self):
		return "%s [%d:%d]" % (self.texto, self.ini, self.fin)

def obtenerTokens(texto):
	regexp = re.compile(r'\w+|[^\w\s]', re.UNICODE)
	return [TokenTexto(m.group(0), m.start(), m.end()) for m in regexp.finditer(texto)]
