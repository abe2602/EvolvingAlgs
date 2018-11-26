import numpy as np 
from PIL import Image, ImageDraw, ImageChops
import math 
import functools as ft
import operator
import gc
from matplotlib import pyplot as plt

TAM_POP = 50
MUT_RATE = 0.05
CHILDREN_PER_GEN = 8
GENERATIONS = 1000
POLY_NUM = 100
RESULT_NAME = "retangulos/mona/mona"
IMG_NAME = "retangulos/mona/ffff.jpg"


#Classe que representa um gene
#Cada gene eh composto por 3 ou 2 coordenadas (pois eh um triangulo ou retangulo), RGB e a transparencia da imagem
#Os valores das coordenadas e RGB sao gerados aleatoriamente.

class geneVazio(object):
	def __init__(self):
		self.p1 = ((), ())
		self.p2 = ((), ())
		#self.p3 = (np.random.randint(0, 200), np.random.randint(0, 200))
		#self.p4 = (np.random.randint(0, 200), np.random.randint(0, 200))
		self.rgba = {
					"r": 0, 
					"g": 0,
					"b": 0,
					"a": 128}

class gene(object):
	def __init__(self):
		self.p1 = (np.random.randint(0, 200), np.random.randint(0, 200))
		self.p2 = (np.random.randint(0, 200), np.random.randint(0, 200))
		#self.p3 = (np.random.randint(0, 200), np.random.randint(0, 200))
		#self.p4 = (np.random.randint(0, 200), np.random.randint(0, 200))
		self.rgba = {
					"r": np.random.randint(0, 255), 
					"g": np.random.randint(0, 255),
					"b": np.random.randint(0, 255),
					"a": 128}


#Cada individuo da nossa populacao tera um vetor de genes, um fitness, um pai e uma mae 
#A escolha do melhor de todos se da pelo melhor fitness, ou seja, aquele que obtiver o menor fitness(erro) eh o melhor de todos. 

class individuo(object):
	def __init__(self, image, pai = None, mae = None):
		self.genes = []

		if(pai and mae):
			self.genes = crossover(pai, mae, POLY_NUM)
			#array = crossover(pai, mae, POLY_NUM)
			#self.mutateFromParents(array)
		else:
			self.genes = initGenes()
		
		self.currentImage = getImage(self.genes)
		self.fitness = getFitness(image, self.currentImage)
		
	
	#Faz a mutacao - de acordo com a taxa de mutacao - do gene.
	#Ou seja, o vetor de genes eh criado e so alguns dos genes sao escolhidos
	
	def mutateFromParents(self, array):
		zipArray = zip(*[iter(array)]*5)
		#zipArray = zip(*[iter(array)]*6)
		self.genes = []
		
		for arr in zipArray:
			#g = geneVazio()
			g = gene()
			if np.random.uniform(0, 1) > MUT_RATE:
				#triangulos
				#g.p1 = arr[0]
				#g.p2 = arr[1]
				#g.p3 = arr[2]
				#g.rgba['r'] = arr[3]
				#g.rgba['g'] = arr[4]
				#g.rgba['b'] = arr[5]

				#retangulos
				g.p1 = arr[0]
				g.p2 = arr[1]
				g.rgba['r'] = arr[2]
				g.rgba['g'] = arr[3]
				g.rgba['b'] = arr[4]
			#else:
			#	g.p1 = (arr[0][0] + 10, arr[0][1] + 10)
			#	g.p2 = (arr[1][0] + 10, arr[1][1] + 10)
			#	g.rgba['r'] = arr[2] + 10
			#	g.rgba['g'] = arr[3] + 10
				#g.rgba['b'] = arr[4] + 10
			self.genes.append(g)

	def getArray(self):
		array = []
		for g in self.genes:
			array.append(g.p1)
			array.append(g.p2)
			#array.append(g.p3)
			array.append(g.rgba['r'])
			array.append(g.rgba['g'])
			array.append(g.rgba['b'])
		return array	


#Cria a nossa populacao de poligonos, os quais serao comparados com a imagem real
#Basicamente, retorna um vetor de "genes"

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

	find_best(pop)

	#pop.sort(key=lambda x: x.fitness)
	#pop = pop[:TAM_POP]
	pop = select_pop(pop)

	return pop


#encontra qual o melhor individuo e coloca o melhor na posicao 0
def find_best(pop):
	#encontra qual o melhor individuo
	best = 0
	for i in range(1, len(pop)):
		if pop[i].fitness < pop[best].fitness:
			best = i

	#coloca o melhor na posicao 0 da populacao
	if best != 0:
		aux = pop[0]
		pop[0] = pop[best]
		pop[best] = aux
	

#seleciona aleatoriamente individuos da populacao
#melhor individuo continua na posicao 0
def select_pop(pop):
	newPop = []
	
	if len(pop) <= TAM_POP:
		return pop
	else:
		newPop.append(pop[0]) #melhor de todos
		x = np.random.choice(pop[1:], size=TAM_POP-1, replace=False)
		for i in x:
			newPop.append(i)

	return newPop



#Mostra a imagem criada pelo vetor de poligonos aleatorios

def showImage(genes):
	im = Image.new("RGB", (200, 200), "white")
	draw = ImageDraw.Draw(im, "RGBA")

	for gene in genes:
		draw.rectangle([gene.p1, gene.p2], fill=(gene.rgba['r'], gene.rgba['g'], gene.rgba['b'], gene.rgba['a']))	
	del draw
	im.show()


#Retorna uma imagem que eh formada por triangulos

def getImagePaiMae(genes):
	im = Image.new("RGB", (200, 200), "white")
	draw = ImageDraw.Draw(im, "RGBA")
	i = 0
	
	for gene in genes:
		draw.rectangle([gene.p1, gene.p2], fill=(gene.rgba['r'], gene.rgba['g'], gene.rgba['b'], gene.rgba['a']))
	del draw
	return im


#Retorna uma imagem que eh formada por triangulos

def getImage(genes):
	im = Image.new("RGB", (200, 200), "white")
	draw = ImageDraw.Draw(im, "RGBA")
	
	for gene in genes:
		draw.rectangle([gene.p1, gene.p2], fill=(gene.rgba['r'], gene.rgba['g'], gene.rgba['b'], gene.rgba['a']))
		#draw.polygon([gene.p1, gene.p2, gene.p3], fill=(gene.rgba['r'], gene.rgba['g'], gene.rgba['b'], gene.rgba['a']))
	del draw
	return im


#Crossover Uniforme, escolhe um de cada dos pais - aleatoriamente

def crossover(pai, mae, POLY_NUM):
	#array1 = pai.getArray()
	#array2 = mae.getArray()
	newArray = []
	#flag = True
	#lastPosi = 0
	#pos = np.random.randint(0, 10)

	#while lastPosi < POLY_NUM * 5:
	#	if flag:
	#		newArray += array1[lastPosi:pos]
	#	else:
	#		newArray += array2[lastPosi:pos]
	#	flag = False
	#	lastPosi = pos
	#	pos = np.random.randint(lastPosi, lastPosi+10)

	for i in range(POLY_NUM):
		gene = geneVazio()
		gene.p1 = ((pai.genes[i].p1[0] + mae.genes[i].p1[0])/2, (pai.genes[i].p1[1] + mae.genes[i].p1[1])/2)
		gene.p2 = ((pai.genes[i].p2[0] + mae.genes[i].p2[0])/2, (pai.genes[i].p2[1] + mae.genes[i].p2[1])/2)

		x = np.random.randint(0,1)

		if x == 0:
			gene.rgba['r'] = pai.genes[i].rgba['r']
			gene.rgba['g'] = pai.genes[i].rgba['g']
			gene.rgba['b'] = pai.genes[i].rgba['b']
		else:
			gene.rgba['r'] = mae.genes[i].rgba['r']
			gene.rgba['g'] = mae.genes[i].rgba['g']
			gene.rgba['b'] = mae.genes[i].rgba['b']

		newArray.append(gene)

	return newArray


#Encontra a diferenca entre duas imagens (no caso, a imagem atual e a imagem alvo)

def getFitness(im1, im2):
	errors = np.asarray(ImageChops.difference(im1, im2)) / 255.0 #normaliza
	diff = math.sqrt(np.mean(np.square(errors)))
	#diff = np.sum(np.square(errors))
	return diff


#Funcao de evolucao. 
#Eh nela onde escolhemos os melhores candidatos e "descartamos" os demais.

def evolve(pop, im):
	lista = [[], []]
	for k in range(0, GENERATIONS):
		children = []
		#parents = []

		for j in range(1, TAM_POP): #Ciclo principal
			#torneio de 2
			pai = None
			mae = None
			pai1 = np.random.choice(pop)
			pai2 = np.random.choice(pop)
			mae1 = np.random.choice(pop)
			mae2 = np.random.choice(pop)
			if pai1.fitness < pai2.fitness:
				pai = pai1
			else:
				pai = pai2
			if mae1.fitness < mae2.fitness:
				mae = mae1
			else:
				mae = mae2
			child = individuo(im, pai, mae) #Individuo novo a partir de um pai e uma mae
			#child = individuo(im, pop[0], pop[j]) #melhor transa com todos
			children.append(child)

		#Adiciona os novos filhos
		pop += children

		#todos os individuos sofrem mutacao
		for i in range(1,len(pop)):
		#for i in range(1,TAM_POP):
			pop[i].mutateFromParents(pop[i].getArray())

		find_best(pop)
		#pop.sort(key=lambda x: x.fitness) #Ve quem sao os melhores
		#pop = pop[:TAM_POP] #Descarta os piores
		pop = select_pop(pop)
		

		if k % 10000 == 0 or k in [100, 500, 1000, 5000]: #Salva uma imagem a cada 10000 iteracoes
			print("Geracao: ", k, "pop: ", len(pop), "melhor: ", pop[0].fitness)
			name = RESULT_NAME + str(k) + ".png"
			pop[0].currentImage.save(name, "PNG")
		
		fit = []
		for i in pop:
			fit.append(i.fitness)
		lista[0].append(pop[0].fitness)
		lista[1].append(np.mean(fit))

	return pop, lista

if __name__ == '__main__':
	h1 = Image.open(IMG_NAME).convert("RGB")
	h1 = h1.resize((200, 200))

	pop = []
	pop = initPop(h1)

	x, lista = evolve(pop, h1)
	x[0].currentImage.save(RESULT_NAME + ".png", "PNG")
	x[0].currentImage.show()
	
	plt.suptitle(RESULT_NAME)
	plt.xlabel("Geracao")
	plt.ylabel("Fitnes")
	leg1, leg2 = plt.plot(lista[0], "r--", lista[1], "g--")
	plt.figlegend((leg1, leg2), ("Melhor", "Media"), "upper right")
	plt.show()



#arrumar negocio do sort
#ver mutacao
#fazer melhor transa com todos