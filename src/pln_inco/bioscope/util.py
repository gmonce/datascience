# -*- coding: utf-8 -*- 

import nltk,nltk.tokenize,xml.etree
import os,codecs,fnmatch,re,types, copy,shutil
import os.path
import pickle
from sys import *
from pln_inco import graphviz,penn_treebank,stanford_parser
from string import *
import sqlite3
import time

class BioscopeCorpusProcessor:
	""" Métodos para procesar el corpus original, generando eventualmente archivos intermedios
	
	@ivar working_dir: directorio de trabajo
	@type working_dir: C{string}
	
	@ivar txt_dir: directorio con los textos originales, un archivo por documento
	@type txt_dir: C{string}
	
	@ivar parsed_files_dir: directorio para el resultado del análisis sintactico de las oraciones
	@type parsed_files_dir: C{string}
	
	@ivar bioscope_files_dir: directorio con los archivos con marcas bioscope, uno por documento
	@type bioscope_files_dir: C{string}
	
	@ivar event_dir: directorio con los documentos en el Genia Event para el corpus
	@type event_dir: C{string}
	
	@ivar genia_files_dir: directorio con los archivos resultante del análisis con Genia de los textos originales. Uno por cada oración
	@type genia_files_dir: C{string}
	
	@ivar att_dir: directorio con los archivos de atributos de las oraciones, para mostrar
	@type att_dir: C{string}
	
	@ivar crf_corpus_dir: directorio con el corpus para procesar con crf y sus resultados
	@type crf_corpus_dir: C{string}
		
	@ivar genia_articles_dir: archivos con el resultado del análisis de GENIA, separado por documentos
	@type genia_articles_dir: C{string}
	
	@ivar genia_temp_file: archivo temporal para el análisis de genia. Siempre se llama 'genia_temp.txt' y está en el directorio de trabajo
	@type genia_temp_file: C{string}
	@ivar genia_temp_results_files: resultado del análisis con Genia. Siempre se llama 'genia_temp.genia' y está en el directorio de trabajo
	@type genia_temp_results_files: C{string}
	
	@ivar genia_event_corpus_dir: corpus Genia Event original
	@type genia_event_corpus_dir: C{string}
	
	@ivar parser_grammar_file: archivo con la gramática para el parser de Stanford
	@type parser_grammar_file: C{string}
	
	@ivar original_bioscope_corpus: corpus Bioscope original, consistente en un solo archivo
	@type original_bioscope_corpus: C{xml.etree.ElementTree}
	
	@ivar bioscope_files_corpus: corpus Bioscope original, separado por documentos
	@type bioscope_files_corpus: C{nltk.corpus.XMLCorpusReader}
	
	@ivar parsed_files_corpus: archivos con el análisis sintáctico, separado por documentos
	@type parsed_files_corpus: C{nltk.corpus.BracketParseCorpusReader}
	
	@ivar genia_files_corpus: archivos con el resultado del análisis de GENIA, separado por oraciones
	@type genia_files_corpus: C{nltk.corpus.WordListCorpusReader}
	
	@ivar training_filename: corpus de entrenamiento para CRF/Yamcha 
	@type training_filename:C{string}

	@ivar att_database: archivo SQLite donde se guarda el corpus. Se llama attributes.db, y está en el C{working_dir}
	@type att_database:C{string}
	
	"""
	
	
	def __init__(self, working_dir, bioscope_xml_file):
	
		"""
		Carga las variables necesarias de configuración para procesar los archivos del corpus genia original y resultados intermedios
		
		@arg working_dir: directorio de trabajo
		@type working_dir: C{string}
		@arg bioscope_xml_file: archivo del corpus bioscope
		@type bioscope_xml_file: C{string}
		@rtype: C{None}
		"""
		
		# Directorio para los archivos
		self.working_dir=working_dir
		self.txt_dir=os.path.join(working_dir,'txt')
		self.parsed_files_dir=os.path.join(working_dir,'parsed')
		self.bioscope_files_dir=os.path.join(working_dir,'bioscope')
		self.event_dir=os.path.join(working_dir,'event')
		self.genia_files_dir=os.path.join(working_dir,'genia')
		self.attribute_table_files_dir=os.path.join(working_dir,'attributes')
		self.genia_articles_dir=os.path.join(working_dir,'genia_articles')
		self.image_files_dir=os.path.join(working_dir,'img')

	
		# Archivo temporal para análisis con genia, y su resultado
		self.genia_temp_file=os.path.join(working_dir,'genia_temp.txt')
		self.genia_temp_results_file=os.path.join(working_dir,'genia_temp.genia')
		
		
		# Directorio con la instalación de genia
		self.genia_home=os.path.expandvars('$GENIA_TAGGER_HOME')		
		
		# Ubicación del corpus Genia Event
		self.genia_event_corpus_dir=os.path.expandvars('$GENIA_EVENT')
		
		# Gramática para el parser de Stanford
		self.parser_grammar_file=os.path.join(os.path.expandvars('$STANFORD_PARSER_HOME'),'englishPCFG.ser.gz')
		
	
		# Corpus XML a leer
		self.original_bioscope_corpus=nltk.corpus.XMLCorpusReader(working_dir,'.\*\.xml').xml(bioscope_xml_file)
	
		# Corpus de archivos .bioscope
		self.bioscope_files_corpus=nltk.corpus.XMLCorpusReader(self.bioscope_files_dir,'.\*\.bioscope')
		
		# Corpus de archivos .parsed
		self.parsed_files_corpus=nltk.corpus.BracketParseCorpusReader(self.parsed_files_dir,'.\*\.parsed')
		
		# Corpus de archivos .genia
		self.genia_files_corpus=nltk.corpus.WordListCorpusReader(self.genia_files_dir,'\.\*\.genia')
		
		# Base de datos SQLite para guardar los atributos
		self.att_database=os.path.join(working_dir,'attributes.db');

		
	def get_doc_ids(self,prefix):
		""" 
		Devuelve una lista con los identificadores de documentos del corpus
		@arg prefix: prefijo que se desea agregar al identificador
		@type prefix: C{String}
		@rtype: C{List}
		
		"""
		
		ids=[]
		for docset in self.original_bioscope_corpus.getchildren(): # Recorro los document set (en este caso es uno solo)		
			for doc in docset.getchildren(): # Recorro los documentos			
				docId=doc.getchildren()[0].text 
				ids.append(prefix+docId)
		return ids
	
	def get_sentence_ids(self,docId):
		""" 
		Dado un documento, devuelve una lista con los identificadores de oraciones en un documento del corpus 
		@rtype:C{List}
		
		"""
		
		# Abro el archivo .bioscope correspondiente al documento
		bioscope_doc=self.bioscope_files_corpus.xml(docId+'.bioscope')
		ids=[]
		for sentence in bioscope_doc.getchildren():
			ids.append(sentence.get('id'))
		
		return ids							
			
	def load_parsed_sentences(self,docId):
		""" 
		Devuelve una lista de árboles de parsing, correspondientes a las oraciones del documento
		Vienen ordenadas como aparecen en el archivo
		@rtype: C{List}
		"""
		
		# Lo primero que hace es parsear el documento, solamente si el documento tiene alguna marca de incertidumbre
		return self.parsed_files_corpus.parsed_sents(docId+'.parsed')
		
		
	def get_genia_words(self,docId,sentenceId):
		""" 
		Devuelve una lista de (word,lemma,pos,chunk,ne) a partir de lo generado por el tagger de Genia 
		para el documento y oración correspondiente.
		@rtype: C{List}
		"""
		genia_raw_words=self.genia_files_corpus.words(docId+'.'+sentenceId+'.genia')
		genia_words=[]
		for word in genia_raw_words:
			(word,lemma,pos,chunk,ne)=split(rstrip(word,os.linesep),'\t')		
			genia_words.append((word,lemma,pos,chunk,ne))
		return genia_words
		
	
	
			
		
	def get_levels(self,docId,sentenceId,scope_type):
		"""
		Dada una oración, devuelve la cantidad de niveles máximo de anidamiento para los hedges. 
		@rtype: Int
		"""
		

		def includes_hedging_or_negation(element,xcope_id,scope_type):
			"""
			Dado un elemento del arbol xml de bioscope (C{xml.etree.ElementTree}), devuelve True si corresponde a un scope de hedging o de negación
			@type element: C{xml.etree.ElementTree}		
			@rtype: Bool
			@type scope_type: String
			"""
			if element.tag=='cue' and element.get('type')==scope_type and element.get('ref')==xcope_id:
				return True
			else:
				for ch in element.getchildren():
					if includes_hedging_or_negation(ch,xcope_id,scope_type):
						return True
				return False


		def get_bioscope_element_hedge_or_negation_levels(element,scope_type):
			"""
			Dado un elemento del arbol xml de bioscope (C{xml.etree.ElementTree}), devuelve el número de niveles de anidamiento de los hedges
			@type element: C{xml.etree.ElementTree}		
			@rtype: Int
			"""
		
			if element.tag=='xcope' and includes_hedging_or_negation(element,element.get('id'),scope_type):
				nested_levels=1
			else:
				nested_levels=0

			# Sumo los niveles de hedge de los hijos
			child_max_nested_levels=0
			for ch in element.getchildren():
					if get_bioscope_element_hedge_or_negation_levels(ch,scope_type) > child_max_nested_levels:
						child_max_nested_levels=get_bioscope_element_hedge_or_negation_levels(ch,scope_type)
			return child_max_nested_levels+nested_levels
					
		# Abro el archivo .bioscope correspondiente al documento
		bioscope_doc=self.bioscope_files_corpus.xml(docId+'.bioscope')
		for sentence in bioscope_doc.getchildren():
			if sentence.get('id')==sentenceId:
				# Proceso la oración y obtengo los tags de especulación
				hedge_levels= get_bioscope_element_hedge_or_negation_levels(sentence,scope_type)

		return hedge_levels
		
	def get_bioscope_tokens(self,docId,sentenceId):
		"""
		Dada una oración, la obtiene a partir del documento original, y la tokeniza (utilizando C{nltk.tokenize.TreebankWordTokenizer}).
		Devuelve una lista de pares propiedad:valor para cada token.
		@rtype: C{List}
		"""



		# Obtengo el nivel máximo de hedging en la oración
		max_hedge_levels=self.get_levels(docId,sentenceId,scope_type='speculation')
		hedge_scopes = ['O' for i in range(max_hedge_levels)]
		max_negation_levels=self.get_levels(docId,sentenceId,scope_type='negation')
		negation_scopes = ['O' for i in range(max_negation_levels)]
		
		
		def includes_hedging_or_negation(element,xcope_id,scope_type):
			"""
			Dado un elemento del arbol xml de bioscope (C{xml.etree.ElementTree}), devuelve True si corresponde a un scope de hedging o de negación
			@type element: C{xml.etree.ElementTree}		
			@rtype: Bool
			@type scope_type: String
			"""
			if element.tag=='cue' and element.get('type')==scope_type and element.get('ref')==xcope_id:
				return True
			else:
				for ch in element.getchildren():
					if includes_hedging_or_negation(ch,xcope_id,scope_type):
						return True
	
				return False
		
		
		def get_bioscope_element_spec_tags(element,hedge_cue_num,negation_cue_num,hedge_scopes,negation_scopes):
			
			""" 
			Dada un elemento del árbol xml de bioscope (C{xml.etree.ElementTree}), devuelve las marcas correspondientes para anotar el documento
			Adicionalmente, si es un texto, lo tokeniza.

			@type element: C{xml.etree.ElementTree}
			@arg is_hedge_cue: indica si lo que hay en el elemento es una hedge cue. Este atributo cambia a True cuando el elemento tiene tag 'cue' y tipo 'speculation'
			@type is_hedge_cue: Bool
			@arg is_negation_cue: indica si lo que hay en el elmento es una cue de negación.  Este atributo cambia a True cuando el elemento tiene tag 'cue' y tipo 'negation'
			@type is_negation_cue:Bool
			@arg hedge_scopes: indica si estamos en algún scope de hedging. Cada elemento del array en True indica que en ese nivel (y en los anteriores) hay hedging
			@type hedge_scopes: List
			@arg negation_scopes: indica si estamos en algún scope de negación. Cada elemento del array en True indica que en ese nivel (y en los anteriores) hay negación
			@type negation_scopes: List

			"""
		
			# Tokenizador de acuerdo al Treebank, que es lo mismo que usa Genia... espero
			wt=nltk.tokenize.TreebankWordTokenizer()

			#print >> stderr, "Proceso el elemento ",element.tag, "con id=",element.get('id'), "de tipo ", element.get('type')
			#print >> stderr,'Texto:',element.text
			
			# Determino los atributos con los que voy a anotar a cada token
			hedge_cues=['O' for i in range(max_hedge_levels)]
			negation_cues=['O' for i in range(max_negation_levels)]
			if element.tag=='sentence':
				# Al comienzo de la oración, el tag de marca de especulación es Falso
				# El tag de marca de negación está vacío
				# La lista de scopes está vacía
				hedge_scopes=['O' for i in hedge_scopes]
				negation_scopes=['O' for i in negation_scopes]
				hedge_cues=['O' for i in hedge_cues]
				negation_cues=['O' for i in negation_cues]
			elif element.tag=='cue' and element.get('type')=='negation':
				# Si estoy en un cue de negación, no puedo estar en un cue de especulación
				# Pero sí podría estar dentro de un scope, así que el scope no cambia
				#hedge_cue_num=0
				#is_negation_cue=True
				pass
			elif element.tag=='cue' and element.get('type')=='speculation':
				# Comienza un bloque de cue de especulación
				# Los elementos dentro de este scope están marcados como de especulación
				# Esto no cambia nada los scopes
				#hedge_cue_num=hedge_cue_num+1
				#is_negation_cue=False				
				pass
			elif element.tag=='xcope':
				# Si estoy en un scope de especulación o negación , todavía no tengo indicador de marca de especulación (aunque seguramente esté dentro del bloque)
				# Los elementos dentro de este tag van a tener marca de scope
				#hedge_cue_num=0
				#is_negation_cue=False				
				
				# Si es un hedge de scope, entonces aumento un nivel de anidamiento
				# Sino seguimos igual
				if includes_hedging_or_negation(element,element.get('id'),scope_type='speculation'):
					hedge_cue_num=hedge_cue_num+1
					# Creo un nuevo nivel de hedging
					j=0
					for i in hedge_scopes:
						if i!='O':
							j=j+1
						else:
							# Sustituyo la primer 'O' por una 'B'
							hedge_scopes[j]='B'
							break
					
				if includes_hedging_or_negation(element,element.get('id'),scope_type='negation'):
					negation_cue_num=negation_cue_num+1				
					# Creo un nuevo nivel de negation
					j=0
					for i in negation_scopes:
						if i!='O':
							j=j+1
						else:
							# Sustituyo la primer 'O' por una 'B'
							negation_scopes[j]='B'
							break

			
			# Si tiene texto asociado lo tokenizo y agrego los tags correspondientes a cada una de las palabras
			if element.text:
				element_text=wt.tokenize(element.text)
			else:
				element_text=[]
				
			element_tagged_text=[]
			
			#print >> stderr, 'Texto a tokenizar:',element.text

			first_token=True
			for elem in element_text:
				
				# Cargo el valor de marca de especulación
				
				if hedge_cue_num>0 and element.get('type')=='speculation':
					if first_token:
						hedge_cues[hedge_cue_num-1]='B-SPECCUE'
						first_token=False
					else:
						hedge_cues[hedge_cue_num-1]='I-SPECCUE'
				else:
					hedge_cues=['O' for i in hedge_cues]
					
				# Cargo el valor de marca de negación
				if negation_cue_num>0  and element.get('type')=='negation':
					if first_token:
						negation_cues[negation_cue_num-1]='B-NEGCUE'
						first_token=False
					else:
						negation_cues[negation_cue_num-1]='I-NEGCUE'
				else:
					negation_cues=['O' for i in negation_cues]
					
				# Cargo el valor de las marcas de scope
				j=0
				hedge_scope_marks=[]
				for i in hedge_scopes:
					if i=='B':
						hedge_scope_marks.append('B-SPECXCOPE')
						hedge_scopes[j]='I'
					elif i=='I':
						hedge_scope_marks.append('I-SPECXCOPE')						
					else:
						hedge_scope_marks.append('O')	
					j=j+1


				# Cargo el valor de las marcas de negation
				j=0
				negation_scope_marks=[]
				for i in negation_scopes:
					if i=='B':
						negation_scope_marks.append('B-NEGXCOPE')
						negation_scopes[j]='I'
					elif i=='I':
						negation_scope_marks.append('I-NEGXCOPE')						
					else:
						negation_scope_marks.append('O')	
					j=j+1
					
			
				# Si no hay ningún scope, siempre pongo 'O'
				if not hedge_scope_marks:
					hedge_scope_marks=['O']

				if not negation_scope_marks:
					negation_scope_marks=['O']

				if not hedge_cues:
					hedge_cues=['O']
				
				if not negation_cues:
					negation_cues=['O']
					
					
				#print >> stderr, 'Anoto el texto ',elem, ' con el tag ',hedge_cues
				element_tagged_text.append((elem,{'SpecCue':[h for h in hedge_cues],'NegCue':[h for h in negation_cues],'specXcope':hedge_scope_marks,'negXcope':negation_scope_marks}))
					
							
			#print >> stderr, 'Texto taggeado:',element_tagged_text
			
			# Proceso los hijos
			j=0
			for ch in element.getchildren():
				element_tagged_text += get_bioscope_element_spec_tags(ch,hedge_cue_num,negation_cue_num,hedge_scopes,negation_scopes)
			
			#Proceso lo que hay a la derecha del tag
			
			if element.tail:
				element_tail=wt.tokenize(element.tail)
			else:
				element_tail=[]

			element_tagged_tail=[]
			
			
			# Lo que está a la derecha del bloque nunca es marca de especulación ni de negación
			hedge_cues=['O' for i in hedge_cues]
			negation_cues=['O' for i in negation_cues]
			
			# Si terminó el scope de especulación, borro el último nivel de anidamiento
			if includes_hedging_or_negation(element,element.get('id'),scope_type='speculation') and element.tag=='xcope':
				j=0
				for i in hedge_scopes:
					if i !='O':
						j=j+1
					else:
						hedge_scopes[j-1]='O'
						break
				#Si llego al final, tengo que poner True el primero, porque había uno solo
				hedge_scopes[j-1]='O'
						
			# Si terminó el scope de especulación, borro el último nivel de anidamiento
			if includes_hedging_or_negation(element,element.get('id'),scope_type='negation') and element.tag=='xcope':
				j=0
				for i in negation_scopes:
					if i !='O':
						j=j+1
					else:
						negation_scopes[j-1]='O'
						break
				#Si llego al final, tengo que poner True el primero, porque había uno solo
				negation_scopes[j-1]='O'
						
						

			# Cargo el valor de las marcas de scope
			j=0
			hedge_scope_marks=[]
			for i in hedge_scopes:
				if i=='B':
					hedge_scope_marks.append('B-SPECXCOPE')
					hedge_scopes[j]='I'
				elif i=='I':
					hedge_scope_marks.append('I-SPECXCOPE')						
				else:
					hedge_scope_marks.append('O')	
				j=j+1

			# Cargo el valor de las marcas de negation
			j=0
			negation_scope_marks=[]
			for i in negation_scopes:
				if i=='B':
					negation_scope_marks.append('B-NEGXCOPE')
					negation_scopes[j]='I'
				elif i=='I':
					negation_scope_marks.append('I-NEGXCOPE')						
				else:
					negation_scope_marks.append('O')	
				j=j+1


					
			if not hedge_scope_marks:
				hedge_scope_marks=['O']

			if not negation_scope_marks:
				negation_scope_marks=['O']
				
			if not hedge_cues:
				hedge_cues=['O']
				
							
			if not negation_cues:
				negation_cues=['O']
			
			
			for elem in element_tail:
				#print >> stderr, 'Anoto el texto ',elem, ' con el tag ',hedge_cues
				element_tagged_tail.append((elem,{'SpecCue':[h for h in hedge_cues],'NegCue':[h for h in negation_cues], 'specXcope':hedge_scope_marks,'negXcope':negation_scope_marks}))



			#print >> stderr'Texto taggeado:',element_tagged_tail
			#print >> stderr,  'Retorno ',element_tagged_text + element_tagged_tail
			return element_tagged_text + element_tagged_tail
			
		
		# Abro el archivo .bioscope correspondiente al documento
		bioscope_doc=self.bioscope_files_corpus.xml(docId+'.bioscope')
		for sentence in bioscope_doc.getchildren():
			if sentence.get('id')==sentenceId:
				# Proceso la oración y obtengo los tags de especulación
				tokens=get_bioscope_element_spec_tags(sentence,hedge_cue_num=0,negation_cue_num=0, hedge_scopes=hedge_scopes, negation_scopes=negation_scopes)
		return tokens
				
		



def bioscope_get_text(xml_element):
	""" 
	Función auxiliar que obtiene el texto abarcado por un elemento xml del corpus bioscope sin las marcas intermedias 
	@arg xml_element: XML del corpus Bioscope
	@type xml_element: C{xml.etree.ElementTree}
	@rtype: C{String}
	"""

	# Si es una oración, hago trampa y no le pongo el tail para evitar los tabuladores del final que no sé para
	# qué los tiene
	if xml_element.text: 
		texto=xml_element.text
	else:
		texto=''

	if xml_element.tail and xml_element.tag != 'sentence':
		tail=xml_element.tail
	else:
		tail=''

	texto_hijos=[bioscope_get_text(ch) for ch in xml_element.getchildren()]
	res=''.join([texto]+texto_hijos+[tail])
	return res
				

def bioscope_retokenize(genia_words,bioscope_tokens):
	"""
	Dada una lista de palabras resultado de la tokenización por el tagger de genia y otra lista resultado de la tokenización
	del texto utilizando C{nltk.tokenize.TreebankWordTokenizer()}, retokeniza al segundo para que quede igual al de Genia. 
	
	@arg genia_words: lista de palabras, resultado del análisis con el Genia Tagger
	@type genia_words: C{List}
	@arg bioscope_tokens: lista de tokens resultado del análisis con C{nltk.tokenize.TreebankWordTokenizer()}
	@type bioscope_tokens: C{List}
	@return: bioscope_tokens, retokenizado
	@rtype: C{List}
	"""
	
	#print >> stderr, "Retokenizo ",[x[0] for x in genia_words]
	#print >> stderr, "Bioscope tiene: ", [x[0] for x in bioscope_tokens]
	
	import warnings
	# Ignoro los warnings al convertir unicode, no quiero problemas
	warnings.simplefilter('ignore')

	for i in range(0,len(genia_words)):
		if i<len(bioscope_tokens):
			genia_word=genia_words[i][0]
			treebank_token=bioscope_tokens[i][0]
			#print >> stderr,  genia_word,bioscope_word

			
			if genia_word != treebank_token:
				# Caso 0: paréntesis y eso que parecen diferentes pero no lo son
				if treebank_token in ('(',')','[',']','{','}'):
					pass
				else:
					# Caso 2: si la palabra de genia es igual a la de bioscope más la siguiente, bioscope lo separó
					if i<len(bioscope_tokens)-1 and genia_word==treebank_token+bioscope_tokens[i+1][0]:
						#print>>stderr, "Aplico regla 2"
						bioscope_tokens[i]=(bioscope_tokens[i][0]+bioscope_tokens[i+1][0], bioscope_tokens[i][1]) 
						del(bioscope_tokens[i+1])
					# Caso 3: podrían ser tres palabras 
					elif i<len(bioscope_tokens)-2 and  genia_word==treebank_token+bioscope_tokens[i+1][0]+bioscope_tokens[i+2][0]:
						bioscope_tokens[i]=(bioscope_tokens[i][0]+bioscope_tokens[i+1][0]+bioscope_tokens[i+2][0], bioscope_tokens[i][1]) 					
						del(bioscope_tokens[i+1])
						del(bioscope_tokens[i+1])
					# Caso 4: podrían ser cuatro palabras !
					elif i<len(bioscope_tokens)-3 and genia_word==treebank_token+bioscope_tokens[i+1][0]+bioscope_tokens[i+2][0]+bioscope_tokens[i+3][0]:
						#print>>stderr, "Aplico regla 4"
						bioscope_tokens[i]=(bioscope_tokens[i][0]+bioscope_tokens[i+1][0]+bioscope_tokens[i+2][0]+bioscope_tokens[i+3][0], bioscope_tokens[i][1]) 					
						del(bioscope_tokens[i+1])
						del(bioscope_tokens[i+1])
						del(bioscope_tokens[i+1])
	
	
	warnings.simplefilter('always')
	return bioscope_tokens
	

def gen_conll_file_hc(dbname,tablename,sentence_type,filename,xs,y,predicted_y):
	""" 
	Genera el archivo para el entrenamiento/evaluación con CRF++, a partir de la tabla de bioscope que se le indique
	Este archivo está en formato CoNLL, tiene una línea por token, los atributos están
	separados por espacio, y el último es el que vamos a usar para clasificar. Las oraciones están separadas por líneas
	en blanco
	@arg dbname: nombre del archivo que tiene la base de datos
	@type dbname:C{string}
	@arg tablename: nombre de la tabla a partir de la cual generar el archivo
	@type tablename:C{string}
	@arg sentence_type: indica el string que deben tener las instancias en el campo SENTENCE_TYPE. Si vale ALL, entonces genera sobre todas las tuplas
	@type sentence_type: C{string}
	@arg xs: lista de atributos a generar. Tienen que ser iguales a las columnas de la tabla de atributos de bioscope. No incluyen la clase a aprender.
	@type xs: List
	@arg y: Clase a aprender (es uno de los atributos)
	@type y:List
	@arg predicted_y: Ya me pasan la clase aprendida (estoy generando directamente el archivo de evaluación)
	@type predicted_y: C{string}
	"""

	content=''	
	t0=time.clock()
	f=open(filename,'w+')
	conn= sqlite3.connect(dbname)	
	conn.text_factory = str
	conn.row_factory=sqlite3.Row
	c=conn.cursor()
	
	# Armo la lista separada por comas de los atributos
	# Por supuesto deben llamarse igual que las columnas de la tabla
	#print "Genero ",xs, " sobre la tabla ",tablename
	cabezal_select=','.join(xs)
	cabezal_select=cabezal_select+','+y+' '
	if predicted_y:
		# Podría tener dos valores para la clase, lo que quiere decir que ya estoy generando el archivo de evaluación
		cabezal_select=cabezal_select+','+predicted_y+' '

	if sentence_type=='ALL':
		c.execute('select document_id,sentence_id,token_num, '+cabezal_select+' from '+tablename+' order by document_id,sentence_id,token_num')
	else:
		c.execute('select document_id,sentence_id,token_num, '+cabezal_select+' from '+tablename+' where sentence_type=?  order by document_id,sentence_id,token_num', (sentence_type,))	
	
	prev_sentence_id='-1'	
	in_scope=False
	for row in c:
		if (prev_sentence_id != row['sentence_id']):
			#Fin de la oración, dejo un espacio en blanco, excepto en la primera
			if prev_sentence_id != '-1':					
				content=content+'\n'
			prev_sentence_id = row['sentence_id']
		for k in row.keys():
			value=row[k]		
			content=content+str(value)+'\t'

		#Borro el último tabulador
		content=rstrip(content)
		content=content+'\n'	
		f.write(content)
		content=''
	f.close()
	c.close()
	#print 'Tiempo del proceso:', time.clock()-t0
	
