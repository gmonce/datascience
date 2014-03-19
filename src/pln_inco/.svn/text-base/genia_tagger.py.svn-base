# -*- coding: utf-8 -*- 
import subprocess
import shlex
import codecs
import os
"""
Operaciones para trabajar con el tagger GENIA
"""
	
def tag(fileName, geniaHome):
	""" 
	Dado un archivo, lo procesa con el tagger de Genia y devuelve el resultado
	@arg fileName: archivo texto a procesar
	@arg geniaHome: directorio donde está instalado el tagger de Genia  (se necesita porque GENIA solamente funciona si el archivo a taggear
	está en su directorio)
	"""

	# Como el tagger de GENIA solo funciona corriendo desde el directorio, me cambio ahí antes de ejecutarlo
	present_dir=os.getcwd()
	print geniaHome
	os.chdir(geniaHome)
	p=subprocess.Popen(['./geniatagger',fileName], stdout=subprocess.PIPE)
	result= p.communicate()[0]
	os.chdir(present_dir)
	return result