# -*- coding: utf-8 -*- 

import nltk,nltk.tokenize,xml.etree
import os,codecs,fnmatch,re,types, copy,shutil
import pickle
from sys import *
from pln_inco import graphviz,penn_treebank,stanford_parser,genia_tagger
from string import *
import pln_inco.bioscope.util
import time
import sqlite3
import random


def apply_sr0 (dbname, scope_table_name, rule_field_name):
	"""
	Dada una tabla de atributos, y un campo donde incluirlo, carga el valor según la regla de scope 0
	La regla de scope 0 dice que si el lemma es suggest y es HC, entonces su scope va desde la palabra suggest hasta
	una palabra antes que el punto final (me equivoco a propósito, porque suggest podría ser "has been suggested" y el scope no es ese)
	Si no hay punto final, entonces la regla no aplica
	@arg dbname: nombre del archivo que tiene la base de datos
	@type dbname:C{string}
	@arg scope_table_name: tabla de scopes a actualizar
	@type scope_table_name:C{string}
	@arg rule_field_name: campo en la tabla donde poner el resultado de la aplicación de la regla
	@type rule_field_name:C{string}
	"""

	# Inicializo la conexión
	conn= sqlite3.connect(dbname)	
	conn.text_factory = str
	conn.row_factory=sqlite3.Row
	c=conn.cursor()

	
	# Primero agrego el campo, por si no existe
	try:
		c.execute('alter table '+scope_table_name+' add column '+ rule_field_name+' text default \'O\'')
	except sqlite3.OperationalError:
		pass
	conn.commit()
	
	# Actualizo todo en O (por si la tabla ya existía)
	c.execute('update '+scope_table_name+' set  '+ rule_field_name+'=\'O\'')
	conn.commit()
	
	
	# Recorro ahora la tabla y aplico la regla
	scope_positions=[]
	c.execute('select * from '+ scope_table_name +' order by document_id,sentence_id,hc_start,token_num')
	last_sentence=''
	last_hc_start=''
	row=c.fetchone()
	while (row):
		# Cargo los tokens de la oración en un array
		last_sentence=row['sentence_id']
		last_hc_start=row['hc_start']
		sentence_tokens=[]
			
		sentence_tokens.append(row)
		while 1:
			row=c.fetchone()
			if row:
				if row['sentence_id'] == last_sentence and row['hc_start']==last_hc_start:
					sentence_tokens.append(row)
					# Guardo el document_id,sentence_id,hc_start, que es igual para todas
					document_id=row['document_id']
					sentence_id=row['sentence_id']
					hc_start=row['hc_start']				
				else:
					break
			else:
				break
					
		# Tengo en sentence_tokens la oración
		first=-1
		last=-1
		
		hc_token=[(x['token_num'],x['lemma'],x['hc_start']) for x in sentence_tokens if x['lemma']=='suggest' and x['token_num']==x['hc_start']]
		if hc_token:
			#print 'Encontré un caso de la regla en la oración',sentence_id, 'comienzo de hc ',hc_token
			first=hc_token[0][0]
			punto_final=[x['token_num'] for x in sentence_tokens if x['lemma']=='.']
			if punto_final:
				last=punto_final[0]-1
			else:
				last=-1

		# Actualizo el par first last para la oración
		if first >=0 or last >=0:
			scope_positions.append((document_id,sentence_id,hc_start,first,last))
			
	# Una vez finalizado, hago los updates correspondientes
	for s in scope_positions:
		if s[3] != -1:
			#print 'Actualizo ',scope_table_name, rule_field_name, s[0],s[1],s[2], 'en la posición ',s[3]
			c.execute('update '+scope_table_name+' set '+rule_field_name+'=\'F\' where document_id=? and sentence_id=? and hc_start=? and token_num=?',(s[0],s[1],s[2],s[3]))
			
		if s[4] != -1:
			#print 'Actualizo L',scope_table_name, rule_field_name, s[0],s[1],s[2], 'en la posición ',s[4]
			c.execute('update '+scope_table_name+' set '+rule_field_name+'=\'L\' where document_id=? and sentence_id=? and hc_start=? and token_num=?',(s[0],s[1],s[2],s[4]))
	conn.commit()

