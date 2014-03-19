# -*- coding: UTF-8 -*-

import xml.dom.minidom

class Anotacion:
	"""Representa una anotacion de evento o indice, con sus atributos."""

	def __init__(self, annot):
		self.id = annot.getElementsByTagName('mention')[0].attributes['id'].value
		if len(annot.getElementsByTagName('span')) > 0 and len(annot.getElementsByTagName('spannedText')[0].childNodes) > 0:
			span = annot.getElementsByTagName('span')[0]
			self.ini = int(span.attributes['start'].value) - 1
			self.fin = int(span.attributes['end'].value) - 1
			
			# Guardamos el texto que representa al evento
			# self.spannedText = annot.getElementsByTagName('spannedText')[0].childNodes[0].data
		else:
			self.ini = -1
			self.fin = -1

	def set_atributos(self, attset, attribs_por_id):
		atributos = []
		self.tipo = attset.getElementsByTagName('mentionClass')[0].attributes['id'].value
		for hasSlotMention in attset.getElementsByTagName('hasSlotMention'):
			attrib_id = hasSlotMention.attributes['id'].value
			if not attribs_por_id.has_key(attrib_id):
				#print 'Warning: no se encontro el atributo ' + attrib_id + ', es un atributo complejo?'
				pass
			else:
				atributos.append(attribs_por_id[attrib_id])
		self.atributos = atributos
	
	def open_tag(self):
		atributos_str = ' '.join(a.toString() for a in self.atributos)
		return '<' + self.tipo + ' ' + atributos_str + '>'

	def close_tag(self):
		return '</' + self.tipo + '>'


class Atributo:
	"""Representa el atributo de una anotacion, por ejemplo modo o factividad."""

	def __init__(self, slot):
		self.id = slot.attributes['id'].value
		mentionSlot = slot.getElementsByTagName('mentionSlot')[0]
		self.name = mentionSlot.attributes['id'].value
		stringSlotMentionValue = slot.getElementsByTagName('stringSlotMentionValue')[0]
		self.value = stringSlotMentionValue.attributes['value'].value
	
	def toString(self):
		return self.name + '="' + self.value + '"'


def obtenerAnotaciones(annotations_file):
	"""Retorna un diccionario de anotaciones (elementos de clase Anotacion), indexado por
	la posición inicial de la anotación.
	
	De esta forma, haciendo anots = obtenerAnotaciones(archivo_knowtator.xml) podremos
	referenciar a la anotación que comienza en el caracter 56 haciendo simplemente anots[56]."""

	annot_doc = xml.dom.minidom.parse(annotations_file)
	
	#print 'Cargando valores de atributos'
	attribs = annot_doc.getElementsByTagName('stringSlotMention')
	attribs_por_id = {}
	for attrib in attribs:
		#if len(attrib.getElementsByTagName('mentionSlot')) == 0:
		#	print attrib.attributes['id'].value + " no tiene atributo asociado (mentionSlot)"
		a = Atributo(attrib)
		attribs_por_id[a.id] = a
	
	#print 'Cargando conjuntos de atributos'
	attsets = annot_doc.getElementsByTagName('classMention')
	attsets_por_id = {}
	for attset in attsets:
		id = attset.attributes['id'].value
		attsets_por_id[id] = attset
	
	#print 'Cargando anotaciones'
	annots = annot_doc.getElementsByTagName('annotation')
	annots_por_pos = {}
	for annot in annots:
		a = Anotacion(annot)
		if len(annot.getElementsByTagName('span')) == 0:
			#print 'Warning: la anotacion ' + a.id + ' no tiene un span definido'
			pass
		else:
			attset = attsets_por_id[a.id]
			a.set_atributos(attset, attribs_por_id)
			annots_por_pos[a.ini] = a
	
	return annots_por_pos
