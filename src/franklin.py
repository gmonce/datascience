# -*- coding: utf-8
# Funciones mencionadas en el Paper
# "The 'Margin of Error' for Differences in Polls", de Charles Franklin
# https://abcnews.go.com/images/PollingUnit/MOEFranklin.pdf
# Ni siquiera es genérico, es solamente el código para un pequeño artículo sobre encuestas de Factum
# @gmonce

import math
# Cantidad de casos (tomados de la encuesta, siempre son iguales)
n=968

# Error estándar
def se(p):
    return math.sqrt(p*(1-p)/n)

# Intervalo de confianza para una proporción p
def ci(p):
    return (round(p-1.96*se(p),3), round(p+1.96*se(p),3))

# Intervalo de confianza, como porcentaje
def ci_porc(p):
    return (round(-1.96*se(p),4), round(+1.96*se(p),4))

# Dados dos valores en la encuesta, indica si la diferencia es estadísticamente significativa
def ci_dif(p1,p2):
    ci=round(p1-p2-1.96*math.sqrt(((p1+p2)-(p1-p2)**2)/(n-1)),3)
    cd=round(p1-p2+1.96*math.sqrt(((p1+p2)- (p1-p2)**2)/(n-1)),3)
    print p1,p2,"Diferencia:",(p1-p2)
    print "Intervalo:",(ci,cd)
    if (ci<0 and cd>0) or (ci>0 and cd<0):
        print "La diferencia no es significativa"
    else:
        print "La diferencia es significativa"

# Calcula si la diferencia del mismo valor entre dos encuestas es estadísticamente significativa
def ci_dif_between(p1,p2):
    print p1,p2, "Diferencia",(p1-p2)
    q1=1-p1
    q2=1-p2
    ci=round(p2-p1-1.96*math.sqrt(p1*q1/n+p2*q2/n),3)
    cd=round(p2-p1+1.96*math.sqrt(p1*q1/n+p2*q2/n),3)
    print "Intervalo:",(ci,cd)
    if (ci<0 and cd>0) or (ci>0 and cd<0):
        print "La diferencia no es significativa"
    else:
        print "La diferencia es significativa"
    


