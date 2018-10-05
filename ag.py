import numpy as np 
from PIL import Image, ImageDraw, ImageChops
import math 
import functools as ft
import operator
import gc

TAM_POP = 50
MUT_RATE = 0.05
CHILDREN_PER_GEN = 8
GENERATIONS = 100000
POLY_NUM = 100
RESULT_NAME = "retangulos/mona/mona"
IMG_NAME = "retangulos/mona/ffff.jpg"

"""
Classe que representa um gene
Cada gene é composto por 3 coordenadas (pois é um triangulo), RGB e a transparência da imagem
Os valors das coordenadas e RGB são gerados aleatoriamente.
"""
class gene(object):
	def __init__(self):
		self.p1 = (np.random.randint(0, 200), np.random.randint(0, 200))
		self.p2 = (np.random.randint(0, 200), np.random.randint(0, 200))
		self.p3 = (np.random.randint(0, 200), np.random.randint(0, 200))
		self.p4 = (np.random.randint(0, 200), np.random.randint(0, 200))
		self.rgba = {
					"r": np.random.randint(0, 255), 
					"g": np.random.randint(0, 255),
					"b": np.random.randint(0, 255),
					"a": 128}

"""
Cada individuo da nossa população terá um vetor de genes, um fitness
um pai e uma mãe 
A escolha do melhor de todos se dá pelo melhor fitness, ou seja, aquele
que obtiver o menor fitness(erro) é o melhor de todos. 
"""
class individuo(object):
	def __init__(self, image, pai = None, mae = None):
		self.genes = []

		if(pai and mae):
			array = crossover(pai, mae, POLY_NUM)
			self.mutateFromParents(array)
		else:
			self.genes = initGenes()
		
		self.currentImage = getImage(self.genes)
		self.fitness = getFitness(image, self.currentImage)
		
	"""
	Faz a mutação - de acordo com a taxa de mutação -
	do gene. Ou seja, o vetor de genes é criado e só alguns
	dos genes são escolhidos
	"""
	def mutateFromParents(self, array):
		zipArray = zip(*[iter(array)]*5)
		self.genes = []

		for arr in zipArray:
			g = gene()
			if np.random.uniform(0, 1) > MUT_RATE:
				g.p1 = arr[0]
				g.p2 = arr[1]
				g.rgba['r'] = arr[2]
				g.rgba['g'] = arr[3]
				g.rgba['b'] = arr[4]
			self.genes.append(g)

	def getArray(self):
		array = []
		for g in self.genes:
			array.append(g.p1)
			array.append(g.p2)
			array.append(g.rgba['r'])
			array.append(g.rgba['g'])
			array.append(g.rgba['b'])
		return array	

"""
Cria a nossa população de poligonos, os quais serão comparados com a imagem real
Basicamente, retorna um vetor de "genes"
"""
def initGenes():
	pop = []
	for i in range(POLY_NUM):
		x = gene()
		pop.append(x)
	return pop

def initPop(im):
	pop = []
	for i in range(TAM_POP*2):
		x = individuo(im)
		pop.append(x)

	pop.sort(key=lambda x: x.fitness)
	pop = pop[:TAM_POP]
	return pop
	
"""
Mostra a imagem criada pelo vetor de poligonos aleatórios
"""
def showImage(pop):
	im = Image.new("RGB", (200, 200), "white")
	draw = ImageDraw.Draw(im, "RGBA")

	for gene in pop:
		draw.rectangle([gene.p1, gene.p2], fill=(gene.rgba['r'], gene.rgba['g'], gene.rgba['b'], gene.rgba['a']))	
		del draw
	im.show()

"""
Retorna uma imagem que é formada por triangulos
"""
def getImagePaiMae(pop):
	im = Image.new("RGB", (200, 200), "white")
	draw = ImageDraw.Draw(im, "RGBA")
	i = 0
	
	for gene in pop:
		draw.rectangle([gene.p1, gene.p2], fill=(gene.rgba['r'], gene.rgba['g'], gene.rgba['b'], gene.rgba['a']))
	del draw
	return im

"""
Retorna uma imagem que é formada por triangulos
"""
def getImage(pop):
	im = Image.new("RGB", (200, 200), "white")
	draw = ImageDraw.Draw(im, "RGBA")
	for gene in pop:
		draw.rectangle([gene.p1, gene.p2], fill=(gene.rgba['r'], gene.rgba['g'], gene.rgba['b'], gene.rgba['a']))
	del draw
	return im

"""
Crossover Uniforme, escolhe um de cada dos pais - aleatoriamente
"""
def crossover(pai, mae, POLY_NUM):
	array1 = pai.getArray()
	array2 = mae.getArray()
	newArray = []
	flag = True
	lastPosi = 0
	pos = np.random.randint(0, 50)

	while lastPosi < POLY_NUM * 5:
		if flag:
			newArray += array1[lastPosi:pos]
		else:
			newArray += array2[lastPosi:pos]
		flag = False
		lastPosi = pos
		pos = np.random.randint(lastPosi, lastPosi+50)

	return newArray

"""
Encontra a diferença entre duas imagens (no caso, a imagem atual e a imagem alvo)
"""
def getFitness(im1, im2):
	errors = np.asarray(ImageChops.difference(im1, im2)) / 255 #normaliza
	diff = math.sqrt(np.mean(np.square(errors)))
	return diff

"""
Função de evolução. 
É nela onde escolhemos os melhores candidator e "descartamos" os demais.
"""
def evolve(pop, im):
	for k in range(0, GENERATIONS):
		children = []
		parents = []

		for j in range(CHILDREN_PER_GEN): #Ciclo principal
			pai = np.random.choice(pop)
			mae = np.random.choice(pop)
			child = individuo(im, pai, mae) #Individuo novo a partir de um pai e uma mae
			children.append(child)

		#Adiciona os novos filhos
		pop += children
		pop.sort(key=lambda x: x.fitness) #Vê quem são os melhores
		pop = pop[:TAM_POP] #Descarta os piores
		print("Geracao: ", k, "pop: ", len(pop))

		if k % 10000 == 0 or k in [100, 500, 1000]: #Salva uma imagem a cada 10000 iterações
			name = RESULT_NAME + str(k) + ".png"
			pop[0].currentImage.save(name, "PNG")

	return pop

if __name__ == '__main__':
	h1 = Image.open(IMG_NAME).convert("RGB")
	h1 = h1.resize((200, 200))

	pop = []
	pop = initPop(h1)

	x = evolve(pop, h1)
	x[0].currentImage.save(RESULT_NAME + ".png", "PNG")
	im.show()
	
