import random
from copy import deepcopy
from enum import auto, Enum

class Moesi(Enum):
    M = auto()
    O = auto()
    E = auto()
    S = auto()
    I = auto()

class Linha:
    dados : list[int]
    estado : Moesi
    bloco_mp : int

    def __init__(self):
        self.dados = [0, 0, 0, 0]
        self.estado = Moesi.I
        self.bloco_mp = -1

class Caixa(Enum):

    MARIO = auto()
    LUIGI = auto()
    PEACH = auto()

class Cache:
    linhas : list[Linha]
    fifo_index : int

    def __init__(self):
        self.linhas = [Linha() for i in range(5)]
        self.fifo_index = 0

    def buscar_bloco(self, bloco_jogo : int) -> int:
        # Não entendi direito
        for i in range(5):
            if self.linhas[i].bloco_mp == bloco_jogo and self.linhas[i].estado != Moesi.I:
                return i
    
        return -1
    
class Locadora:

    estoque : list[list[int]]
    caixas : list[Cache]

    def __init__(self):
        self.estoque = [[random.randint(0, 300) for i in range(5)] for d in range(10)]
        self.caixas = [Cache() for i in range(3)]

    def imprime_caixas(self):
        print("\n---- Estado das Caches ----\n")

        for caixa in self.caixas:
            print("\nCaixa : ") #caixa.name) # ARRUMA ISSO AQUI LUCAS
 
            for j in range(len(caixa.linhas)):

                estado = caixa.linhas[j].estado
                bloco = caixa.linhas[j].bloco_mp if caixa.linhas[j].bloco_mp != -1 else "N/A"
                dados = caixa.linhas[j].dados

                print("Linha: " + str(j) + " Bloco MP " + str(bloco) + " Estado " + str(estado) + " Dados " + str(dados))

            print("Próxima linha : " + str(caixa.fifo_index))

        print("-------------------")

    def imprime_mp(self):
        print("---- Estado da Memória Principal ----")

        for i in range(len(self.estoque)):
            print("Linha " + str(i) + " : " + "Bloco MP " + str(self.estoque[i]))

        print("-------------------")

    def write_back(self, linha_cache : Linha):

        local_mp = linha_cache.bloco_mp
        self.estoque[local_mp] = linha_cache.dados.deepcopy()

    def verifica_estado(self, linha : Linha):
        pass


a = Locadora() 
a.imprime_caixas()
a.imprime_mp()