import numpy as np 
from PIL import Image, ImageDraw, ImageChops
import math 
import functools as ft
import operator
import gc
from matplotlib import pyplot as plt

TAM_POP = 50
ESTAG = 0
MUT_RATE = 10
MUT_2 = 0.2
MUT_3 = 0.01
#CHILDREN_PER_GEN = 8
GENERATIONS = 5000
POLY_NUM = 100
RESULT_NAME = "retangulos/mona/mona"
IMG_NAME = "retangulos/mona/cecilha.png"


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
			#self.mutate(array)
		else:
			self.genes = initGenes()
		
		self.currentImage = getImage(self.genes)
		self.fitness = getFitness(image, self.currentImage)
		
	
	#Faz a mutacao - de acordo com a taxa de mutacao - do gene.
	#Ou seja, o vetor de genes eh modificado em apenas alguns genes
	
	def mutate(self, genes):
		
		x = np.random.uniform(0, 1) 
		
		if x > MUT_2:
			#so muta 1 gene aleatorio
			self.mut(np.random.randint(0, POLY_NUM))

		elif x > MUT_3:
			#muta 2 genes aleatorios
			self.mut(np.random.randint(0, POLY_NUM))
			self.mut(np.random.randint(0, POLY_NUM))

		else:
			#muta 3 genes aleatorios
			self.mut(np.random.randint(0, POLY_NUM))
			self.mut(np.random.randint(0, POLY_NUM))
			self.mut(np.random.randint(0, POLY_NUM))


	def mut(self, i):
		self.genes[i].p1 = (rand_limits(self.genes[i].p1[0], 200), rand_limits(self.genes[i].p1[1], 200))
		self.genes[i].p2 = (rand_limits(self.genes[i].p2[0], 200), rand_limits(self.genes[i].p2[1], 200))
		self.genes[i].rgba['r'] = rand_limits(self.genes[i].rgba['r'], 255)
		self.genes[i].rgba['g'] = rand_limits(self.genes[i].rgba['g'], 255)
		self.genes[i].rgba['b'] = rand_limits(self.genes[i].rgba['b'], 255)


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


#Soma um numero entre -10 e 10
#Verifica se os valores de um gene estao dentro dos limites da imagem e das cores
def rand_limits(num, limit):
	num = num + np.random.randint(-MUT_RATE, MUT_RATE + 1)

	if num < 0:
		num = 0
	elif num > limit:
		num = limit

	return num


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

	pop = select_pop(pop)

	return pop


#encontra qual o melhor individuo e coloca o melhor na posicao 0
def find_best(pop):
	global ESTAG, MUT_RATE

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
		ESTAG = 0
	else:
		ESTAG += 1
		if ESTAG % 21 == 0:
			MUT_RATE += 5
		elif ESTAG == 100:
			MUT_RATE = 5
			ESTAG = 0
	

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


#Crossover Uniforme, escolhe ate 10 genes de cada dos pais - aleatoriamente

def crossover(pai, mae, POLY_NUM):
	array1 = pai.getArray()
	array2 = mae.getArray()
	newArray = []
	flag = np.random.randint(0,1)
	lastPosi = 0
	pos = np.random.randint(0, 10)

	while lastPosi < POLY_NUM * 5:
		if flag == 0:
			newArray += array1[lastPosi:pos]
		else:
			newArray += array2[lastPosi:pos]
		flag = np.random.randint(0,2)
		lastPosi = pos
		pos = np.random.randint(lastPosi, lastPosi+10)

	zipArray = zip(*[iter(newArray)]*5)
	genes = []
	for arr in zipArray:
		g = geneVazio()
		g.p1 = arr[0]
		g.p2 = arr[1]
		g.rgba['r'] = arr[2]
		g.rgba['g'] = arr[3]
		g.rgba['b'] = arr[4]
		genes.append(g)

	return genes


#Encontra a diferenca entre duas imagens (no caso, a imagem atual e a imagem alvo)

def getFitness(im1, im2):
	errors = np.asarray(ImageChops.difference(im1, im2)) / 255.0 #normaliza
	diff = math.sqrt(np.mean(np.square(errors)))
	return diff


#Individuo novo a partir de um pai e uma mae
def torneio2(im, pop):
	children = []

	for j in range(1, TAM_POP): #Ciclo principal
	 	pai = None
		mae = None
		pais = np.random.choice(pop, 2, False)
		maes = np.random.choice(pop, 2, False)

		if pais[0].fitness < pais[1].fitness:
			pai = pais[0]
		else:
			pai = pais[1]
		if maes[0].fitness < maes[1].fitness:
			mae = maes[0]
		else:
			mae = maes[1]

		child = individuo(im, pai, mae)
		children.append(child)

	return children


#melhor transa com todos
def best_all(im, pop):
	children = []

	for j in range(1, TAM_POP):		 
		child = individuo(im, pop[0], pop[j])
		children.append(child)

	return children

#Funcao de evolucao. 
#Eh nela onde escolhemos os melhores candidatos e "descartamos" os demais.

def evolve(pop, im):
	lista = [[], []]
	for k in range(0, GENERATIONS):
		children = []

		children = torneio2(im, pop)
		#children = best_all(im, pop)

		#Adiciona os novos filhos
		pop += children

		#todos os individuos sofrem mutacao
		for i in range(1,len(pop)):
			pop[i].mutate(pop[i].genes)

		find_best(pop)
		pop = select_pop(pop)
		

		if k % 10000 == 0 or k in [100, 500, 1000, 5000]: #Salva uma imagem a cada 10000 iteracoes
			print("Geracao: ", k, "pop: ", len(pop), "melhor: ", pop[0].fitness)
			name = RESULT_NAME + str(k) + "f" + str(round(pop[0].fitness, 3)) + ".png"
			pop[0].currentImage.save(name, "PNG")
		
		#estrutura auxiliar para fazer o grafico
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
	x[0].currentImage.save(RESULT_NAME + "f" + str(round(x[0].fitness, 3)) + ".png", "PNG")
	x[0].currentImage.show()
	

	#faz o grafico de fitnessxgeracao, melhor e media da populacao
	plt.suptitle(RESULT_NAME)
	plt.xlabel("Geracao")
	plt.ylabel("Fitnes")
	leg1, leg2 = plt.plot(lista[0], "r--", lista[1], "g--")
	plt.figlegend((leg1, leg2), ("Melhor", "Media"), "upper right")
	plt.show()
