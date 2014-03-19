# -*- coding: utf-8 -*- 
from subprocess import Popen, PIPE

"""
Operaciones para trabajar con graphviz
"""
	
def gen_jpeg_output(entrada):
	"""
	A partir de una entrada correspondiente a una especificación de graphviz devuelve el .jpeg correspondiente, llamando a graphviz
	"""
	p=Popen(['dot','-Tjpg'], stdin=PIPE, stdout=PIPE)
	return p.communicate(input=entrada)[0]
		

def gen_svg_output(entrada):
	"""
	A partir de una entrada correspondiente a una especificación de graphviz devuelve el .svg correspondiente, llamando a graphviz
	"""
	p=Popen(['dot','-Tsvg'], stdin=PIPE, stdout=PIPE)
	return p.communicate(input=entrada)[0]
		
