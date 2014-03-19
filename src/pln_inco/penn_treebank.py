# -*- coding: utf-8 -*- 
from string import *

def ptb_conversion_word(s):
	""" Típico: Formatea un texto para ajustarlo a las convenciones del PennTreebank """

	if s.find('(') > -1:
		return '-LRB-'
	elif s.find(')') > -1:
		return '-RRB-'
	elif s.find('[') > -1:
		return '-LRB-'		
	elif s.find(']') > -1:
		return '-RRB-'
	elif s.find('{') > -1:
		return '-LCB-'
	elif s.find('}') > -1:
		return '-RCB-'
	elif s.find('/') > -1:
		# Agrego una contrabarra a todas las ocurrencias de '/'
		return replace(s,'/','\/')
	else:
		return s

def ptb_conversion_pos(pos_tag):
	""" Formatea un POS tag para ajustarlo a las convenciones del PennTreeBank. """

	if pos_tag.find('(') > -1:
		return '-LRB-'
	elif pos_tag.find(')') > -1:
		return '-RRB-'
	elif pos_tag.find('[') > -1:
		return '-LRB-'		
	elif pos_tag.find(']') > -1:
		return '-RRB-'
	elif pos_tag.find('{') > -1:
		return '-LRB-'
	elif pos_tag.find('}') > -1:
		return '-RRB-'
	else:
		return pos_tag
		
