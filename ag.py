import numpy as np 
from PIL import Image, ImageDraw, ImageChops
import math 
import functools as ft
import operator

TAM_POP = 100

"""
Classe que representa um gene
Cada gene é composto por 3 coordenadas (pois é um triangulo), RGB e a transparência da imagem
Os valors das coordenadas e RGB são gerados aleatoriamente.
"""
class gene(object):
	def __init__(self):
		self.p1 = (np.random.randint(0, 500), np.random.randint(0, 500))
		self.p2 = (np.random.randint(0, 500), np.random.randint(0, 500))
		self.p3 = (np.random.randint(0, 500), np.random.randint(0, 500))
		self.rgba = {
					"r": np.random.randint(0, 255), 
					"g": np.random.randint(0, 255),
					"b": np.random.randint(0, 255),
					"a": 128}
		
"""
Cria a nossa população de poligonos, os quais serão comparados com a imagem real
Basicamente, retorna um vetor de "genes"
"""
def initPop():
	pop = []
	for i in range(TAM_POP):
		x = gene()
		pop.append(x)

	return pop
	
"""
Mostra a imagem criada pelo vetor de poligonos aleatórios
"""
def showImage(pop):
	im = Image.new("RGB", (500, 500), "white")
	draw = ImageDraw.Draw(im, "RGBA")

	for x in pop:
		draw.polygon([x.p1, x.p2, x.p3], fill=(x.rgba["r"], x.rgba["g"],
											x.rgba["b"], x.rgba["a"]))
	del draw
	im.show()


def mutatePop(pop):
	print(len(pop))

if __name__ == '__main__':

	pop = initPop()
	mutatePop(pop)
	#showImage(pop)

