# -*- coding: utf-8 -*- 
import subprocess
import shlex
import codecs
import tempfile
"""
Operaciones para trabajar con el parser de Stanford
"""
	
def parse(fileName, grammar_file):
	""" 
	Dada una lista de oraciones, las parsea con el Stanford Parser. Asume que la variable CLASSPATH ya tiene seteado el stanford-parser.bat. 
	@arg grammar_file: contiene el archivo de la gramática para parsear
	@arg fileName: archivo texto a procesar
	"""
	#command_line='java -mx500m edu.stanford.nlp.parser.lexparser.LexicalizedParser -tokenized -tokenizerOptions "normalizeCurrency=false" -tagSeparator / -outputFormat "penn" englishPCFG.ser.gz -'
	command_line='java -mx1000m edu.stanford.nlp.parser.lexparser.LexicalizedParser -sentences newline -tokenized -escaper edu.stanford.nlp.process.PTBEscapingProcessor -tagSeparator / -outputFormat "penn" edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz -'
	args=shlex.split(command_line)
	
	#Sustituyo por el grammar file 
	#args[-2]=grammar_file
	args[-1]=fileName
	
	target=tempfile.NamedTemporaryFile(delete=False)
	target_name=target.name
	p=subprocess.Popen(args,stdout=target)
	p.wait()
	target.close()
	target=open(target_name,'r')
	result=target.read()
	target.close()
	return result
	
	
	

