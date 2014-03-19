# -*- coding: UTF-8 -*-

import os
import re
from subprocess import Popen, PIPE
from pln_inco.util.Tokenizador import *


# Utilizamos el 'analyzer' de FreeLing
# La variable de entorno $FREELINGSHARE debe estar seteada
base_cmd_freeling = ['analyzer', '-f', '%s/config/es.cfg' % os.environ['FREELINGSHARE']]


def salidaProceso(cmd, entrada):
	"""Ejecuta el proceso referido en cmd.
	Devuelve una lista con todas las líneas de la salida."""
	print cmd
	p = Popen(cmd, stdin=PIPE, stdout=PIPE)
	# Freeling no soporta UTF-8
	salida_pipe = p.communicate(input=entrada.encode('iso-8859-1'))[0].decode('iso-8859-1')
	tokens = [linea for linea in salida_pipe.split('\n')]
	return tokens


def obtenerSalidaFreeling(texto, outf, parametros):
	"""Devuelve una lista con información del texto, obtenida con Freeling.
	Freeling utilizará el archivo de configuración por defecto para el idioma español.

	En outf se indica el parámetro que se le pasaría al analyzer
	(plain, token, splitted, morfo, tagged, parsed, dep).
	En parametros pueden ir más parámetros de configuración de Freeling. Por ejemplo,
	parametros podría ser ['--ner', 'basic', '--noafx'].
	
	La salida se devuelve como texto plano."""

	cmd =  base_cmd_freeling + ['--outf', outf] + parametros
	return [linea[:-1] for linea in salidaProceso(cmd, texto)]


def obtenerInfoEtiquetadoFreeling(texto):
	"""Devuelve una lista de las oraciones identificadas por Freeling.
	
	Cada oración es una lista de tuplas (token, lema, tag gramatical).
	Los tokens son los strings tal cuál los genera Freeling, sin marcas de dónde comienzan y
	terminan en el texto original."""

	# Las opciones '--noafx', '--noloc', '--nonumb', '--nodate', '--noquant' no las utilizamos,
	# pues la función que determina dónde comienzan y terminan los tokens de Freeling
	# (obtenerLemasEtiquetasFreeling) funciona de todas formas.
	#
	# Las líneas de freeling vienen en formato "token lema tag prob".
	salida_Freeling = obtenerSalidaFreeling(texto, 'tagged', ['--ner', 'basic', '--flush'])[:-1]
	oraciones = []
	oracion = []
	for linea in salida_Freeling:
		if linea != '':
			oracion.append(tuple(linea.split(" ")[:-1]))
		else:
			oraciones.append(oracion)
			oracion = []

	return oraciones


def sacarTildes(texto):
	"""Función auxiliar que reemplaza los tildes por su versión no acentuada.
	Se utiliza solamente en la función obtenerLemasEtiquetasFreeling() para casos
	como "contándoselo" que Freeling convierte en "contando", "se", "lo" (saca el
	tilde de la primera parte)."""
	
	strs = {u'á': u'a', u'é': u'e', u'í': u'i', u'ó': u'o', u'ú': u'u'} 
	for k, v in strs.items():
		texto = texto.replace(k, v)
		texto = texto.replace(k.upper(), v.upper())
	return texto


def obtenerOracionesEtiquetadasFreeling(text_file, encoding):
	"""Devuelve una lista de las oraciones identificadas por Freeling.
	
	Cada oración es una lista de tuplas (token, lema, tag gramatical).
	Para cada token de Freeling se devuelve	una estructura TokenTexto con información de la posición
	de inicio y fin del token en el	texto original.

	El resultado es una lista cuyos elementos son [(TokenTexto, diccionario)] donde diccionario
	tiene la información que brindó Freeling (indexable por claves claves 'lema_freeling' y
	'tag_freeling').

	En encoding se debe especificar la codificación del archivo de texto, por ejemplo 'iso-8859-1'
	o 'utf-8'."""

	f = open(text_file, 'rU')
	texto = f.read().decode(encoding)
	
	tokens_mios = obtenerTokens(texto)
	oraciones_freeling = obtenerInfoEtiquetadoFreeling(texto)

	f.close()

	resultado = []
	
	j = 0 # Índice para recorrer tokens_mios
	
	# Recorremos todas las oraciones que nos dio Freeling
	for tokens_freeling in oraciones_freeling:
	
		resultado_oracion = []

		# Vamos recorriendo todos los tokens de Freeling de la oración.
		# Asignamos el token de Freeling a una variable temporal token_freeling, y vamos
		# "reconociendo" tokens nuestros dentro de éste.
		# Si token_freeling queda vacío, entonces quiere decir que todos los tokens nuestros
		# que están dentro del token freeling fueron reconocidos y agregados a mis_tags.
		i = 0
		while i < len(tokens_freeling):
			(token_freeling, lema, tag_freeling) = tokens_freeling[i]
			token_mio = tokens_mios[j]

			#
			# Ej.
			# Token freeling = "A_pesar_de_todo"
			# Tokens mios = "A", "pesar", "de", "todo"
			#
			# Ej.
			# Tokens freeling = "de", "el"
			# Token mio = "del"
			#
			# Ej.
			# Tokens freeling = "con_el_culo_a_el_aire"
			# Tokens mios = "con", "el", "culo", "al", "aire".
			# (sí, no se me ocurre otra por el momento :P)
			#
		
			mi_TokenTexto_freeling = TokenTexto(token_freeling)

			while len(token_freeling) > 0:
		
				#print '-> %s %s' % (token_mio.texto, token_freeling)
			
				# Casos especiales
				#        del -> de el
				#        al -> a el
				#
				# Cuidado especial en casos de locuciones como "con_el_culo_a_el_aire", donde el token_freeling
				# eventualmente será algo como "a_el_aire".
				#
				caso_del = token_mio.texto.lower() == 'del' and token_freeling.lower()[:3] != 'del' and token_freeling.lower()[:2] == 'de'
				caso_al = token_mio.texto.lower() == 'al' and token_freeling.lower()[:2] != 'al' and token_freeling.lower()[:1] == 'a'
			
				# Casos de sufijos
				#       contándoselo -> contando se lo
				#       vámonos -> vamos nos
				if len(token_freeling) < len(token_mio.texto) and not (caso_del or caso_al):
					#print '-> %s %s' % (token_mio.texto, token_freeling)
			
					# Ej.
					# token_freeling: contando
					# token_mio: contándoselo
					mio_sin_tildes = sacarTildes(token_mio.texto)
				
					# Ej.
					# token_freeling: contando
					# mio_sin_tildes: contandoselo
				
					mi_TokenTexto_freeling.ini = token_mio.ini
					mi_TokenTexto_freeling.fin = token_mio.fin
					resultado_oracion.append((mi_TokenTexto_freeling, {'lema_freeling' : lema, 'tag_freeling' : tag_freeling}))
				
					resto = mio_sin_tildes.replace(token_freeling, '', 1)
					if resto == mio_sin_tildes:
						# Por un caso particular "vámonos" que Freeling separa en "vamos", "nos".
						# Falla al reemplazar.
						#
						# Consideramos el caso cuando la palabra original termina en s
						if token_freeling[-1].lower() == 's':
							token_freeling = token_freeling[:-1]
						resto = mio_sin_tildes.replace(token_freeling, '', 1)
					
						if resto == mio_sin_tildes:
							print u'Problema reemplazando "%s" en "%s", quizá explote al devolver los tokens de Freeling.' % (token_freeling, mio_sin_tildes)

					# Ej.
					# resto: selo
					#print 'Inserto resto=%s' % resto
					tokens_mios.insert(j+1, TokenTexto(resto, token_mio.ini, token_mio.fin))
				
					token_freeling = ''
					j += 1
				
				else:

					if caso_del or caso_al:
				
						# Cambiamos nuestros token "del" o "al" por "de" y "a", y agregamos el "el" que falta
						if caso_del:
							token_mio.texto = 'de'
						elif caso_al:
							token_mio.texto = 'a'
				
						tokens_mios.insert(j+1, TokenTexto('el', token_mio.ini, token_mio.fin))

					# token_mio debería estar al principio en token_freeling
					# Lo borramos del token_freeling
			
					token_freeling_viejo = token_freeling
					token_freeling = token_freeling.replace(token_mio.texto, '', 1)
					if len(token_freeling) > 0 and token_freeling[0] == '_':
						token_freeling = token_freeling[1:]
			
					# Si no hizo nada, caso raro. Probablemente sea porque quedan caracteres raros al final del token de Freeling.
					if token_freeling_viejo == token_freeling:
						token_freeling = ''

					# Seteamos el ini (si ya lo habíamos seteado, el valor será distinto a -1)
					if mi_TokenTexto_freeling.ini == -1:
						mi_TokenTexto_freeling.ini = token_mio.ini
					# Seteamos el fin (si token_freeling quedó vacío, y por lo tanto terminamos de reconocer)
					# y agregamos a la lista...
					if token_freeling == '':
						mi_TokenTexto_freeling.fin = token_mio.fin
						resultado_oracion.append((mi_TokenTexto_freeling, {'lema_freeling' : lema, 'tag_freeling' : tag_freeling}))

					j += 1
					# Agarramos el siguiente si los hay
					if j < len(tokens_mios):
						token_mio = tokens_mios[j]

			i += 1
		
		resultado.append(resultado_oracion)

	return resultado


__all__ = ['obtenerOracionesEtiquetadasFreeling', 'obtenerSalidaFreeling', 'obtenerInfoEtiquetadoFreeling']

