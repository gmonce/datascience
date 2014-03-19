# -*- coding: UTF-8 -*-

from pln_inco.Freeling import *
from pln_inco.temantex.AnotAtrib import *
from pln_inco.util.Tokenizador import *


def cargarAnotacionesEventos(text_file, encoding_text_file, annotations_file):
	"""Retorna una lista de pares (TokenTexto, [anotación]) donde la segunda componente es vacía
	si el token no tiene anotaciones. De lo contrario, la misma es la lista de anotaciones asociadas al token.

	Salvo pocas excepciones, como las palabras anotadas como INTRUSO (que están dentro de un evento),
	la lista de anotaciones tendrá solo un elemento."""

	# Abrimos el archivo en "modo universal" para no tener problemas con los fines de línea Unix/Windows
	f = open(text_file, 'rU')
	texto = f.read().decode(encoding_text_file) # Codificación del archivo del corpus
	f.close()
	
	annots_por_pos = obtenerAnotaciones(annotations_file)
	poss = sorted(annots_por_pos.keys())
	
	# Cargamos los tokens, inicialmente sin asignarle anotación a ninguno de ellos.
	tokens_anotaciones = [(token, []) for token in obtenerTokens(texto)]
	ultimo_indice_token = 0

	#
	# Recorremos todas las anotaciones ordenadas por la posición de comienzo
	#
	for i in range(0, len(annots_por_pos)):
		pos = poss[i]
		a = annots_por_pos[pos]

		# Si la anotación tiene marcados comienzo y fin
		if a.ini != -1 and a.fin != -1:		
			# Buscamos el siguiente token cuyo inicio coincida con la anotación
			encontre = False
			while not encontre:
				token = tokens_anotaciones[ultimo_indice_token][0]
				# El >= es por las dudas, por si la anotación estaba mal marcada y comienza en un
				# espacio o similar (antes de la palabra del evento)
				if token.ini >= a.ini:
					encontre = True
				else:
					ultimo_indice_token += 1
			
			# Asignamos la anotación a los tokens que corresponden
			# (aquellos cuyo fin es <= al de la anotación)
			indice_token_actual = ultimo_indice_token
			while tokens_anotaciones[indice_token_actual][0].fin <= a.fin:
				tokens_anotaciones[indice_token_actual][1].append(a)
				indice_token_actual += 1

	return tokens_anotaciones


def quedarseConUnaAnotacion(lista_tokens_anotaciones):
	"""Antes de combinar con la salida de Freeling, le damos una pasada a nuestra
	lista de tokens para que cada token quede con exactamente una anotación.

	El único caso para el que sirve esto es para los "intrusos", de forma que
	la etiqueta "intruso" le gane a "evento"."""

	lista_tokens_anotacion = []
	for (token, anotaciones) in lista_tokens_anotaciones:
		if len(anotaciones) >= 1:
			anotacion_ganadora = anotaciones[0] # Por defecto queda la primera
			for a in anotaciones:
				if a.tipo.upper() == 'INTRUSO':
					anotacion_ganadora = a
			lista_tokens_anotacion.append((token, anotacion_ganadora))
		else:
			lista_tokens_anotacion.append((token, None))

	return lista_tokens_anotacion


def mergeFreelingConAnotaciones(text_file, encoding_text_file, annotations_file):
	"""Combina las anotaciones del xml de knowtator con la salida del etiquetado gramatical de Freeling

	Devuelve una lista de oraciones, siendo cada elemento de ésta una lista de tipo [(TokenTexto, diccionario)],
	donde los tokens corresponden a los de Freeling, y diccionario tiene la información que brindaba Freeling,
	además de la anotación en la clave 'anotacion'."""

	lista_token_mio_anotacion = quedarseConUnaAnotacion(cargarAnotacionesEventos(text_file, encoding_text_file, annotations_file))
	oraciones_freeling = obtenerOracionesEtiquetadasFreeling(text_file, encoding_text_file)
	
	ultimo_indice_token_mio = 0

	for oracion in oraciones_freeling:
		for (tok_freeling, dic_info_freeling) in oracion:
			#print 'Freeling: %s' % tok_freeling.texto.encode('utf-8')
		
			# Recorro todos los tokens mios que están "dentro" del token freeling y voy juntando
			# todas las anotaciones.
			anotaciones = []			
			for (token, anotacion) in lista_token_mio_anotacion:
				if token.ini >= tok_freeling.ini and token.fin <= tok_freeling.fin:
					anotaciones.append(anotacion)
		
			# De todas las anotaciones, nos quedamos con una sola.
			# Arbitrariamente, la primera.
			if len(anotaciones) > 0:
				anotacion = anotaciones[0]
			else:
				anotacion = None
		
			dic_info_freeling['anotacion'] = anotacion		

	return oraciones_freeling


def getValorAtributo(anotacion, nom_atributo):
	for at in anotacion.atributos:
		if at.name == nom_atributo:
			return at.value
	return ''


def obtenerOracionesTokensEtiquetados(text_file, encoding_text_file, annotations_file):
	"""Misma salida que mergeFreelingConAnotaciones(), con la salvedad de que se elimina
	la clave 'anotacion' y pasa a ser 'tag_evento'.
	
	Finalmente entonces se devuelve una lista de tuplas (tag, diccionario) donde diccionario
	tiene claves {token, lema_freeling,	tag_freeling, tag_evento}.
	El elemento diccionario['token'] es de tipo TokenTexto, corresponde a un token de Freeling
	y tiene las posiciones de inicio y fin marcadas.
	El primer componente de la tupla resultado, tag, es un string que puede tomar los
	siguientes valores:
		* B_EVENTO, I_EVENTO
		* B_INDICE, I_INDICE
		* INTRUSO
		* O"""

	en_evento = False
	en_indice = False
	
	anotacion_evento_anterior = None
	anotacion_indice_anterior = None
	
	oraciones = mergeFreelingConAnotaciones(text_file, encoding_text_file, annotations_file)

	lista_res = []
	
	for oracion in oraciones:
		res_oracion = []
		for (token, a) in oracion:
			anotacion = a['anotacion']
			del a['anotacion'] # Eliminamos la anotación, la cambiaremos por tag_evento que corresponda

			if anotacion == None:
				en_evento = False
				en_indice = False
				tag_evento = 'O'
			
			elif anotacion.tipo.upper() == 'EVENTO':
				if not en_evento:
					tag_evento = 'B_EVENTO'
					anotacion_evento_anterior = anotacion
					
					en_evento = True
				else:
					# Chequeamos que sea de verdad parte del mismo evento. Lo será solamente en el caso
					# en que la anotación del elemento anterior sea la misma.
					if anotacion_evento_anterior == anotacion:
						tag_evento = 'I_EVENTO'
					else:
						tag_evento = 'B_EVENTO'
						anotacion_evento_anterior = anotacion
			elif anotacion.tipo.upper() == 'INDICE':
				if not en_indice:
					tag_evento = 'B_INDICE_%s' % getValorAtributo(anotacion, 'clase').upper()
					en_indice = True
				else:
					if anotacion_indice_anterior == anotacion:
						tag_evento = 'I_INDICE_%s' % getValorAtributo(anotacion, 'clase').upper()
					else:
						tag_evento = 'B_INDICE_%s' % getValorAtributo(anotacion, 'clase').upper()
						anotacion_indice_anterior = anotacion
			elif anotacion.tipo.upper() == 'INTRUSO':
				tag_evento = 'INTRUSO'

			a['token'] = token
			res_oracion.append((a, tag_evento))
		
		lista_res.append(res_oracion)

	return lista_res


__all__ = ['obtenerOracionesTokensEtiquetados']
