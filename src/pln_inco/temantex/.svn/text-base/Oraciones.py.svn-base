# -*- coding: UTF-8 -*-

from pln_inco.util.Tokenizador import *


def cargarOraciones(archivo_entrada, CargarInicioFinTokens=True):
	"""Retorna la lista de oraciones, cargadas desde un archivo de texto.

	Cada elemento es de tipo [(dic, tag_evento)] donde dic tiene claves 'token', 'lema'
	y 'tag_freeling' (eventualmente más)

	CargarInicioFinTokens determina si se espera que se carguen las posiciones de
	inicio y fin de cada token, o si esta información no está en el archivo.	
	"""

	f = open(archivo_entrada, 'rU')
	lineas = [linea[:-1].decode('utf-8') for linea in f.readlines()]
	f.close()

	# La primera línea del archivo .oraciones es la lista de atributos.
	atributos = [at for at in lineas[0].split(' ') if at != '']
	
	oraciones = []
	oracion = []
	for linea in lineas[2:]:
		if linea == '':
			oraciones.append(oracion)
			oracion = []
		else:
			valores = [l for l in linea.split(' ') if l != '']
			dic = {}
			for i in range(0, len(atributos)):
				dic[atributos[i]] = valores[i]

			# El tag va como elemento de la tupla, no del diccionario
			tag_evento = dic['tag_evento']
			del dic['tag_evento']

			inicio = -1
			fin = -1
			
			# Inicio y fin de tokens (opcionales)
			try:
				if CargarInicioFinTokens:
					inicio = int(dic['token_ini'])
					fin = int(dic['token_fin'])
				
				del dic['token_ini']
				del dic['token_fin']
			except KeyError:
				pass
			
			# Cambiamos el token (que ahora es un string) por el TokenTexto
			token = dic['token']
			dic['token'] = TokenTexto(token, inicio, fin)

			oracion.append((dic, tag_evento))

	return oraciones


def printOraciones(oraciones, archivo, ImprimirInicioFinTokens=True):
	"""Imprime oraciones a un archivo de texto.
	
	En ImprimirInicioFinTokens se indica si se quiere imprimir la información de inicio
	y fin de los tokens."""


	f = open(archivo, 'w')
	
	f.write('token ')
	if ImprimirInicioFinTokens:
		f.write('token_ini token_fin ')
	
	if len(oraciones) > 0:
		claves = oraciones[0][0][0].keys()
		claves.sort()
		# Para imprimir el token siempre adelante
		claves.remove('token')
		
		f.write(' '.join(c for c in claves).encode('utf-8') + ' tag_evento\n\n')

		for oracion in oraciones:
			tok = lambda atributos : '%s %d %d ' % (atributos['token'].texto, atributos['token'].ini, atributos['token'].fin) if ImprimirInicioFinTokens else '%s ' % atributos['token'].texto
			f.write('\n'.join((tok(atributos) + ' '.join(atributos[c] for c in claves) + ' ' + tag) for (atributos, tag) in oracion).encode('utf-8') + '\n')
			f.write('\n')
	
	f.close()


def printOracionesSalidaClasificacion(oraciones, archivo):
	"""Imprime oraciones a un archivo de texto.
	
	En cada oración el diccionario con los atributos debe tener la clave tag_clasificador."""


	f = open(archivo, 'w')
	
	if len(oraciones) > 0:
		claves = oraciones[0][0][0].keys()
		claves.sort()
		# Para imprimir el token siempre adelante
		claves.remove('token')
		claves.remove('tag_clasificador')
		
		str_claves = ' '.join(c for c in claves)
		
		f.write(('%-20s %-20s %-20s %s\n\n' % ('token', 'tag_evento', 'tag_clasificador', str_claves)).encode('utf-8'))

		for oracion in oraciones:
			for i, (dic, tag) in enumerate(oracion):
				valores_atributos = ' '.join(dic[c] for c in claves)
				f.write(('%-20s %-20s %-20s %s\n' % (dic['token'].texto, tag, dic['tag_clasificador'], valores_atributos)).encode('utf-8'))
			f.write('\n')
	
	f.close()
