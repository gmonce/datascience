# -*- coding: utf-8 -*- 

import nltk,nltk.tokenize,xml.etree
import os,codecs,fnmatch,re,types, copy,shutil
import pickle
from sys import *
from pln_inco import graphviz,penn_treebank,stanford_parser
from string import *
import pln_inco
import pln_inco.bioscope.util

class BioscopeCorpus:
	""" 
	Corpus Bioscope: contiene toda la información que se levanta a memoria del corpus. La relación con los archivos originales se hace a través de la instancia de BioscopeCorpus Processor (bcp) asociada
	
	@ivar documents: lista de L{bioscope.BioscopeDocument}, indexada por identificador de documento
	@type documents: C{List}
	"""
	
	def __init__(self,bcp,prefix):
		"""
		Carga los documentos del corpus a partir de los archivos correspondiente.
		@arg bcp: Configuración del ambiente para obtener los documentos originales.
		@type bcp: L{bioscope.util.BioscopeCorpusProcessor}
		@rtype: C{None}
		@arg prefix: Patrón a buscar al comienzo del nombre del documento
		@type prefix: String
		"""
		
		# Obtengo los identificadores de documentos
		document_ids=bcp.get_doc_ids('a')

		# Creo la lista de documentos
		self.documents=dict()
		contador=0
		total=len(document_ids)
		for docId in document_ids:
			if re.match(prefix,docId):
				contador+=1
				print "Levanto el documento...",docId, contador, " de ", total
				#try:
				d=BioscopeDocument(docId,bcp)
				d.add_genia_and_bioscope_info(bcp)			
				self.documents[docId]=d
				#except IndexError:
					#print "Hubo problemas con el documento ",docId
					#print "rm "+docId+".parsed"
		
class BioscopeDocument:
	""" 
	Documento de Bioscope, incluyendo toda la información de parsing y tagging 
	
	@ivar docId: identificador del documento en el corpus
	@type docId: C{string}
	@ivar sentences: instancias de L{bioscope.BioscopeSentence} contenidas en el documento
	@type sentences: C{Dictionary}
	"""
	
	
	def __init__(self, docId,bcp):
		""" 
		Crea el documento y las instancias de las oraciones que lo componen, levantando la información de los archivos correspondientes. NO levanta la información de Genia, 
		esto se hace en L{bioscope.BioscopeDocument.add_genia_and_bioscope_info}
		
		@type bcp: L{bioscope.util.BioscopeCorpusProcessor}
		@rtype: C{None}
		"""

		self.docId=docId
		#print "Inicializo el documento ",docId
		
		# Obtengo los identificadores de las oraciones del documento
		sentence_ids=bcp.get_sentence_ids(docId)

	
		# Las oraciones del corpus son un diccionario indexado por el identificador de la oración
		self.sentences=dict()
		i=0
		for sentenceId in sentence_ids:
			#print >> stderr,  "Levanto la oración:",sentenceId
			s=BioscopeSentence(self.docId,sentenceId,i,bcp)
			self.sentences[sentenceId]=s
			i+=1
		#print >>stderr, "Proceso finalizado, se levantaron ",i-1," oraciones. Largo del array:",len(self.sentences)

		# Cargo las oraciones parseadas, a partir del archivo .parsed correspondiente
		parsed_sentences=bcp.load_parsed_sentences(docId)
		#print >>stderr, "Largo del array de parsed sentences:",len(parsed_sentences)
		for (key,sentence) in self.sentences.iteritems():
			#print>>stderr, key, sentence.sindex
			sentence.data=parsed_sentences[sentence.sindex]
	def add_genia_and_bioscope_info(self,bcp):	
		"""
		Agrega al árbol de parsing original de cada oración la información obtenida a partir del tagger Genia
		@rtype: C{None}
		"""
	
		#print >> stderr, "agrego la informacion de Genia/Bioscope para el documento ",self.docId
		for (key,sentence) in self.sentences.iteritems():
			#print >> stderr, "agrego la informacion de Genia/Bioscope para la oracion ",sentence.sentenceId			

			parse_tree=sentence.data

			
			#Levanto las palabras de la oración, según genia
			genia_words=bcp.get_genia_words(self.docId,sentence.sentenceId)
			
			#Levanto las palabras de la oración, según bioscope

			bioscope_tokens=bcp.get_bioscope_tokens(self.docId,sentence.sentenceId)
			#print bioscope_tokens[0][0]
			#if sentence.sentenceId=='S315.12':
			#	print sentence.sentenceId, " bioscope tokens=", [(bt[0],bt[1]['specXcope']) for bt in bioscope_tokens]
			
			# Si la tokenizacion de bioscope difiere de la de Genia, intento retokenizar con unos heurísticos ahí
			if len(genia_words)!=len(bioscope_tokens) and genia_words and bioscope_tokens:
				bioscope_tokens=pln_inco.bioscope.util.bioscope_retokenize(genia_words,bioscope_tokens)
				
			if len(genia_words)==len(bioscope_tokens)==len(parse_tree.leaves()):
				j=0
				for p in parse_tree.leaves():
					# Recorro cada hoja, y etiqueto su padre con los valores
					# adicionales que obtengo de lo que dice genia
					# Tienen las mismas palabras, así que recorro de a uno el genia y el árbol
					tpos=parse_tree.leaf_treeposition(j)
					leaf_parent= tpos[0:len(tpos)-1]

					# Modifico el nodo del árbol para agregar estos atributos en node
					# La propiedad node antes tenía el POS
					# Ahora pasa a ser un diccionario. Gracias, pyhton, por dejarme hacer estas cosas
					pos=parse_tree[leaf_parent].node

					(word,lemma,pos2,chunk,ne)=genia_words[j] 
					#print >> stderr, "Word=",word

					# Levanto las propiedades de bioscope
					# Debería tener las mismas palabras porque usé el mismo tokenizador
					specCue=bioscope_tokens[j][1]['SpecCue']
					negCue=bioscope_tokens[j][1]['NegCue']
					specXcope=bioscope_tokens[j][1]['specXcope']
					negXcope=bioscope_tokens[j][1]['negXcope']
					
					parse_tree[leaf_parent].node={'lemma':lemma, 'pos':pos, 'chunk':chunk, 'entity':ne, 
					'specCue':specCue, 'negCue':negCue,'specXcope':specXcope,'negXcope':negXcope}
					

					j+=1
				sentence.data_loaded=True
			else:
				#print >> stderr, "Problem:"+sentence.sentenceId+":"+self.docId
				#print >> stderr, sentence.sentenceId+':'+self.docId+':'+"Genia    words:",[x[0] for x in genia_words]
				#print >> stderr, sentence.sentenceId+':'+self.docId+':'+"Bioscope words:",[x[0] for x in bioscope_tokens]
				#print >> stderr, sentence.sentenceId+':'+self.docId+':'+"Leaves:        ",[x for x in parse_tree.leaves()]
				#print >> stderr, "Largo:",len(genia_words)," ",len(bioscope_tokens)," ", len(parse_tree.leaves())
				sentence.data_loaded=False
				
	
			
		
class BioscopeSentence:
	""" Una oración del corpus, incluyendo toda la información de parsing y tagging. Parte de un L{bioscope.BioscopeDocument}
		@ivar docId: identificador del documento que contiene la oración
		@type docId: C{string}
		@ivar sentenceId: identificador de la oración en el corpus
		@type sentenceId: C{string}
		@ivar sindex: índice entero de la oración dentro del documento
		@type sindex: C{int}
		@ivar data: árbol de análisis sintáctico de la oración. 
		@type data: C{nltk.Tree}
		@ivar data_loaded: indicador de si ya se cargó el contenido del documento en la estructura
		@type data_loaded: C{bool}
	"""
	
	def __init__(self,docId,sentenceId,sindex,bcp):
		"""
		Crea la estructura que va a contener la oración, NO levanta los datos (esto se hace en la clase L{bioscope.BioscopeDocument}, 
		porque se cargan todas las oraciones de un documento al mismo tiempo).
		
		@rtype:C{None}
		@type bcp: L{bioscope.util.BioscopeCorpusProcessor}
		
		"""
		self.docId=docId
		self.sentenceId=sentenceId
		self.sindex=sindex
		self.data=None
		self.data_loaded=False
		
	def has_hedging(self):
		"""
		Devuelve true si la oración tiene alguna marca de hedging, false en caso contrario
		@rtype: C{bool}
		"""


		def has_hedge_cue(s): # Esto es solamente para un nodo
			""" 
			Dado un nodo, devuelve True si es un diccionario y no tiene  marca de Cue.
			@rtype: bool
			@arg s: Nodo del árbol a evaluar si corresponde a una marca de especulación
			@type s: types.StringType o types.DictType
			"""
			if isinstance(s,types.StringType):
				return False
			elif isinstance(s,types.DictType):
				if s['specCue'] !='O':
					return True
				else:
					return False


		def has_hedging(t):
			"""
			Dado un arbol, devuelve True si tiene alguna marca de hedging. Devuelve True si la raíz corresponde a un hedge cue, o (recursivamente) si alguno de los árboles hijos incluye una marca.
			@rtype:bool
			@arg t:
			@type t: nltk.tree.Tree
			"""
			hh=False
			if has_hedge_cue(t.node):
				return True
			else:
				for child in t: 
					if isinstance(child,nltk.tree.Tree):
						hh=has_hedging(child)

					if hh:
						return True

			return False
			
		return has_hedging(self.data)


	def has_negation(self):
		"""
		Devuelve true si la oración tiene alguna marca de negación, false en caso contrario
		@rtype: C{bool}
		"""


		def has_negation_cue(s): # Esto es solamente para un nodo
			""" 
			Dado un nodo, devuelve True si es un diccionario y no tiene  marca de Negation
			@rtype: bool
			@arg s: Nodo del árbol a evaluar si corresponde a una marca de negación
			@type s: types.StringType o types.DictType
			"""
			if isinstance(s,types.StringType):
				return False
			elif isinstance(s,types.DictType):
				if s['negCue'] !='O':
					return True
				else:
					return False


		def has_negation(t):
			"""
			Dado un arbol, devuelve True si tiene alguna marca de negation. Devuelve True si la raíz corresponde a un negation cue, o (recursivamente) si alguno de 
			los árboles hijos incluye una marca.
			@rtype:bool
			@arg t:
			@type t: nltk.tree.Tree
			"""
			hh=False
			if has_negation_cue(t.node):
				return True
			else:
				for child in t: 
					if isinstance(child,nltk.tree.Tree):
						hh=has_negation(child)

					if hh:
						return True

			return False
			
		return has_negation(self.data)


	def get_dot(self):
		"""
		Devuelve un string en formato graphviz que representa el árbol de la oración (incluyendo las marcas de tagging).
		@rtype: C{string}
		"""
		
		def gv_rep(s):
			""" 
			Dado un nodo, devuelve un string para una etiqueta graphviz, discriminando si sólo tiene el tag, o es un diccionario
			de parejas propiedad/valor
			"""
			
			if isinstance(s,types.StringType):
				# Devuelvo el string nomás
				res=s
			elif isinstance(s,types.DictType):
				# Armo el string con los valores del diccionario
				res=s['pos']
				
				if s['chunk'] != 'O':
					res=res+'\\n'+'chunk:'+s['chunk']
				
				if s['entity']!='O':
					res=res+'\\n'+'entity:'+s['entity']
				
				if s['specCue'][0] !='O':
					res=res+'\\n'+'specCue:'+",".join(s['specCue'])
				
				if s['negCue'][0] !='O':
					res=res+'\\n'+'negCue:'+",".join(s['negCue'])
				
				if s['specXcope'][0] !='O':
					res=res+'\\n'+'specXcope:'+",".join(s['specXcope'])
					
				if s['negXcope'][0] !='O':
					res=res+'\\n'+'negXcope:'+",".join(s['negXcope'])
					

				#if s['specXcope']!='O':
				#	res=res+'\\n'+'specXcope:'+s['specXcope']
				#	res=res+'\\n'+'specXcopeRef:'+s['specXcopeRef']
					
				
				#if s['specXcope2']!='O':
				#	res=res+'\\n'+'specXcope2:'+s['specXcope2']
				#	res=res+'\\n'+'specXcopeRef2:'+s['specXcopeRef2']
				
				
			else:
				res="Error"
		
			return res
				  
		def gv_print(t,inicial=1):
			"""
			Dado un arbol, genera una representación dot
			comenzando la numeración de los nodos en el valor dado por el párametro inicial
			"""
			
			# Muestro el nodo raíz del árbol
			s='%s [label="%s"]' % (inicial,gv_rep(t.node))
	
			pos=inicial+1
			for child in t: 
			
				
				if isinstance(child,nltk.tree.Tree):
					(s_child,newpos)=gv_print(child,pos)
					s=s+'\n'+ s_child
					s=s+'\n%s -> %s' % (inicial,pos)
					pos=newpos
				elif isinstance(child, str):
					s=s+'\n%s [label="%s", shape=plaintext]' % (pos,child)
					s=s+'\n%s -> %s' % (inicial,pos)			
				pos=pos+1
			return (s,pos-1)


		s="digraph G{\n"		
		s+=gv_print(self.data)[0]
		s+="\n}"
		
		return s
		
	def get_basic_attributes(self):
		"""
		Devuelve la lista de tokens de la oración junto con sus atributos.
		El primer elemento es la lista de nombres de los atributos
		@rtype: C{List}
		"""


		def get_tree_leaves(t):
			"""
			Dado un arbol, devuelve una lista con los elementos y sus tags
			haciendo un recorrido in-order
			"""
			
			# Solamente muestro si el hijo es un string
			# Ahí voy a tener todos los atributos
			# Sino simplemente hago recursión
			res=[]
			for child in t: 
				if isinstance(child, str):
					s=t.node
					res=[(child,s['lemma'],s['pos'],s['chunk'],strip(s['entity']),s['specCue'],s['negCue'],s['specXcope'],s['negXcope'])]
				else:
					res += get_tree_leaves(child)
			return res
				
		
		s_table=[('TOKEN','LEMMA','POS','CHUNK','NE','SPEC-CUE','NEG-CUE','SPEC-XCOPE','NEG-XCOPE')]
		s_table += get_tree_leaves(self.data)
		return s_table
	
	def get_leaf_grandparent(self,leaf_pos,gp_number):
		"""
		Dada una hoja del árbol, devuelve él arbol de su abuelo y una especificación de la posición en el árbol original, vía un treepos
		@arg leaf_pos: Número de hoja
		@type leaf_pos: L{int}
		@arg gp_number: número de grandparent que es. Abuelo=2, Bisabuelo=3, etc.
		@rtype: C{nltk.Tree}		
		
		
		"""
		parse_tree=self.data
		# Obtengo el treepos de la hoja
		leaf_treepos=parse_tree.leaf_treeposition(leaf_pos)
		# El de su abuelo es el mismo, sin los gp_number últimos pasos
		leaf_grandparent=leaf_treepos[0:len(leaf_treepos)-gp_number]
		
		s=parse_tree[leaf_grandparent]
		return (s,leaf_grandparent)
	
	def get_node_scope(self,treepos):
		"""
		Dado un nodo del árbol, devuelve las posiciones de la primera y última hoja de su alcance
		@arg treepos: Especificación de la posición del nodo en el árbol de la oración
		@type treepos: C{List}
		@rtype: C{sequence}
		"""
		parse_tree=self.data
		subtree=parse_tree[treepos]
		#print "Treepos del árbol:",treepos
		#print subtree.leaves()
		#print "Cantidad de hojas:", len(subtree.leaves())
		#subtree_start=subtree.leaf_treeposition(0)
		# Me muevo siempre bajando por 0, hasta encontrar una palabra
		# De esa forma encuentro la izquierda del scope
		current_treepos=treepos
		while not isinstance(parse_tree[current_treepos],types.StringType):
			current_treepos=current_treepos+(0,)
		subtree_start_treepos=current_treepos
		subtree_end=subtree.leaf_treeposition(len(subtree.leaves())-1)
		subtree_end_treepos=treepos+subtree_end
		
		#print "Comienzo subtree:",subtree_start_treepos, 
		#print "Arbol:",parse_tree[subtree_start_treepos]

		#print "Fin subtree:",subtree_end_treepos
		#print "Arbol:",parse_tree[subtree_end_treepos]		
		j=0
		for l in parse_tree.leaves():
			if parse_tree.leaf_treeposition(j) == subtree_start_treepos:
				start=j
			if parse_tree.leaf_treeposition(j)== subtree_end_treepos:
				if parse_tree[subtree_end_treepos]=='.':
					end=j-1
				else:
					end=j
				break
			j+=1
		return (start,end)
			

	def get_node_hedge_scope(self,treepos):
		"""
		Dado un nodo del árbol, devuelve las posiciones de la primera y última hoja de su alcance
		Desde el punto de vista del hedging (lo que puede hacer que se poden algunas ramas del constituyente
		para que ajuste más a los criterios de bioscope
		@arg treepos: Especificación de la posición del nodo en el árbol de la oración
		@type treepos: C{List}
		@rtype: C{sequence}
		"""
		parse_tree=self.data
		subtree=parse_tree[treepos]
		
		#Obtengo treepos de objetos que me interesan

		# Padre:
		#parent_treepos=treepos[0:len(treepos)-1]

		# Abuelo:
		#gparent_treepos=treepos[0:len(parent_treepos)-1]
		
		# Hermano a la izquierda del padre, si existe
		#left_parent_brother=treepos[0:parent_treepos[-1]-1]
		
		# Hermano a la derecha del padre
		#right_parent_brother=treepos[0:parent_treepos[-1]+1]
		
		# Hijos del árbol
		children=parse_tree[treepos]
		# Pos del nodo
		pos=parse_tree[treepos].node
		
		#print "Treepos del árbol:",treepos
		#print subtree.leaves()
		#print "Cantidad de hojas:", len(subtree.leaves())
		#subtree_start=subtree.leaf_treeposition(0)
		
		# Me muevo siempre bajando por 0, hasta encontrar una palabra
		# De esa forma encuentro la izquierda del scope
		# 
		current_treepos=treepos		
		
		# Si es un S, al bajar omito los ADVP y los PP a la izquierda
		# A partir de la corrida 37
		if parse_tree[treepos].node in ['S','SBAR']:
			child_number=0
			for child in parse_tree[treepos]:
				if isinstance(child.node,types.DictType):
					if child.node['lemma']<>',':
						current_treepos=treepos+(child_number,)
						break
				else:
					if child.node not in ['ADVP','PP']:
						current_treepos=treepos+(child_number,)
						break
					else:
						#print "Encontr� un ejemplo de ADVP o PP a la izquierda en la oraci�n "
						pass
				child_number+=1

		# Si es un NP, elimino los determinantes al principio, si están antes de un adjetivo
		# Aparece en la corrida 37
		# En la corrida 40 esto se cambió por una regla de postprocesamiento
		elif parse_tree[treepos].node in ['NP']:
			children=parse_tree[treepos]
			j=0
			while j<len(children):
				child=children[j]
				if isinstance(child.node,types.DictType):
					if child.node['pos']=='DT' and children[j+1].node['pos']=='JJ':
						pass
					else:
						#print "Encontr� un ejemplo de determinante antes de adjetivo a la izquierda "
						current_treepos=treepos+(j,)
						break
				j+=1
				
		while not isinstance(parse_tree[current_treepos],types.StringType):
			current_treepos=current_treepos+(0,)
		subtree_start_treepos=current_treepos
		subtree_end=subtree.leaf_treeposition(len(subtree.leaves())-1)
		subtree_end_treepos=treepos+subtree_end
		
		#print "Comienzo subtree:",subtree_start_treepos, 
		#print "Arbol:",parse_tree[subtree_start_treepos]

		#print "Fin subtree:",subtree_end_treepos
		#print "Arbol:",parse_tree[subtree_end_treepos]		
		j=0
		for l in parse_tree.leaves():
			if parse_tree.leaf_treeposition(j) == subtree_start_treepos:
				start=j
			if parse_tree.leaf_treeposition(j)== subtree_end_treepos:
				if parse_tree[subtree_end_treepos]=='.':
					end=j-1
				else:
					end=j
				break
			j+=1
		return (start,end)
		
		
	def get_scope_start(self,treepos):
		"""
		Dado un árbol y un nodo dado por una posición en el árbol, devuelve el comienzo del alcance del nodo
		"""
		
		parse_tree=self.data
		
		# Me muevo siempre tomando la primera rama a la izquierda, hasta llegar a una hoja
		current_treepos=treepos
		while not isinstance(parse_tree[current_treepos],types.StringType):
			current_treepos=current_treepos+(0,)
		subtree_start_treepos=current_treepos
		
		# Recorro las hojas hasta encontrar la que busco
		j=0
		for l in parse_tree.leaves():
			if parse_tree.leaf_treeposition(j) == subtree_start_treepos:
				start=j
				break
			else:
				j+=1
		
		return start



	def get_scope_end(self,treepos):
			"""
			Dado un árbol y un nodo dado por una posición en el árbol, devuelve el final del alcance del nodo
			"""
			parse_tree=self.data
			subtree_end=parse_tree[treepos].leaf_treeposition(len(parse_tree[treepos].leaves())-1)
			subtree_end_treepos=treepos+subtree_end
			
			# Recorro las hojas hasta encontrar la que busco
			j=0
			for l in parse_tree.leaves():
				if parse_tree.leaf_treeposition(j)== subtree_end_treepos:
					if parse_tree[subtree_end_treepos] in ('.',':'):
						end=j-1
					else:
						end=j
					break
				j+=1
			
			return end


	
	def get_node_hedge_scope(self,treepos,hedge_cue_pos,use_heuristics):
		"""
		Dado un nodo del árbol, devuelve las posiciones (empezando de 0) de la primera y última hoja de su alcance
		Desde el punto de vista del hedging (lo que puede hacer que se poden algunas ramas del constituyente
		para que ajuste más a los criterios de bioscope. 
		También utiliza la posición de la hedge cue en la secuencia para hacer el procesamiento
		@arg treepos: Especificación de la posición del nodo en el árbol de la oración
		@type treepos: C{List}
		@rtype: C{sequence}
		"""
		parse_tree=self.data
		subtree=parse_tree[treepos]
		node_pos=subtree.node
		hedge_cue_treepos=parse_tree.leaf_treeposition(hedge_cue_pos)
		leaves=parse_tree.leaves()

		
		#parent_treepos=treepos[0:len(treepos)-1]
		#gparent_treepos=treepos[0:len(parent_treepos)-1]
		#left_parent_brother=treepos[0:parent_treepos[-1]-1]
		#right_parent_brother=treepos[0:parent_treepos[-1]+1]
		
		#print "Treepos del árbol:",treepos
		#print subtree.leaves()
		#print "Cantidad de hojas:", len(subtree.leaves())
		#subtree_start=subtree.leaf_treeposition(0)
		
		# Obtengo las posiciones de comienzo y fin
		start=self.get_scope_start(treepos)
		end=self.get_scope_end(treepos)
		
		# A partir de la corrida 37
		if use_heuristics:
			if node_pos in ['S','SBAR','VP']:
				# Si es un S, omito los ADVP y los PP y los SBAR a la izquierda en el scope
				j=0
				for child in subtree:
					if isinstance(child.node,types.DictType):
						if child.node['lemma']<>',':
							start=self.get_scope_start(treepos+(j,))
							break
					else:
						if child.node not in ['ADVP','PP','SBAR']:
							start=self.get_scope_start(treepos+(j,))
							break
						else:
							#print "Encontre ejemplo de regla 1"
							pass
					
					j+=1



				# Si a la derecha hay algún because, entonces el final es el token anterior al because
				j=hedge_cue_pos
				while j<=end:
					child=leaves[j]
					#print j,child
					if child in ['because','since','like','unlike','unless','minus','although','ie']:
						#print "Ejecuté regla de preposicion o CC"
						#print "Encontre ejemplo de regla 2"

						end=j-1
						break

					elif child in ['as'] and leaves[j-1]==',':
						end=j-1
						break

					j+=1
					"""
					elif child in ['and'] and leaves[j-1]==',':
						end=j-1
						break
					"""					

				# Si el último token es una coma, entonces la quito también
				if leaves[end]==',':
					#print "ajusté coma final"
					end=end-1
			elif node_pos in ['NP']:
				#print "Apareció un node pos en NP"
				# Si es un NP, entonces in incluyo al hermano a la derecha del padre, si es un PP, y si existe!
				#print "Treepos:",treepos
				parent_treepos=treepos[0:len(treepos)-1]
				#print "Parent treepos:",parent_treepos			
				#print parent_treepos
				if parent_treepos:
					try:
						right_parent_brother=parent_treepos+(treepos[-1]+1,)
						#print "Right parent treepos:",right_parent_brother				
						#print "Hermano a la derecha del padre es un: ",parse_tree[right_parent_brother].node				
						if parse_tree[right_parent_brother].node=='PP':
							#print "Encontre ejemplo de regla 3"
							end=self.get_scope_end(right_parent_brother)
					except IndexError:
						pass

				# Finalmente, elimino determinantes si la hedge cue es un JJ
				hedge_cue_treepos2=hedge_cue_treepos[0:len(hedge_cue_treepos)-1]
				if parse_tree[hedge_cue_treepos2].node['pos']=='JJ':
					# Obtengo la primer hoja para ver si es un determinante
					first_leaf=parse_tree.leaf_treeposition(start)
					first_leaf_parent=first_leaf[0:len(first_leaf)-1]
					#print parse_tree[first_leaf_parent].node

					if parse_tree[first_leaf_parent].node['pos']=='DT':	
						#print "Encontre ejemplo de regla 4"
						start+=1
		
		return (start,end)
		
	
