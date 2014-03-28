#encoding: utf-8
from treetagger import TreeTagger
tt=TreeTagger(language='english',encoding='latin-1')
tagged_sent=tt.tag('What is the airspeed of an unladen swallow? And what about the € sign?')
print tagged_sent




