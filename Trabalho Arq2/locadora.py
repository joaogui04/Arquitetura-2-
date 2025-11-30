import random
from copy import deepcopy
from enum import auto, Enum

class Moesi(Enum):
    M = 0
    O = 1
    E = 2
    S = 3
    I = 4

class Linha:
    dados : list[int]
    estado : Moesi
    bloco_mp : int

    def __init__(self):
        self.dados = [0, 0, 0, 0, 0]
        self.estado = Moesi.I
        self.bloco_mp = -1

class Caixa(Enum):

    MARIO = 0
    LUIGI = 1
    PEACH = 2

class Cache:
    linhas : list[Linha]
    fifo_index : int
    
    def __init__(self):
        self.linhas = [Linha() for i in range(5)]
        self.fifo_index = 0

    def buscar_bloco(self, bloco_jogo : int) -> int:
        
        for i in range(5):
            if self.linhas[i].bloco_mp == bloco_jogo and self.linhas[i].estado != Moesi.I:
                return i
    
        return -1
    
    def buscar_dado(self, bloco_jogo: int, posicao_dado:int):

        return self.linhas[bloco_jogo].dados[posicao_dado]
    
class Locadora:

    estoque : list[list[int]]
    caixas : list[Cache]
    

    def __init__(self):
        self.estoque = [[random.randint(0, 100) for i in range(5)] for d in range(50)]
        self.caixas = [Cache() for i in range(3)]

    def imprime_caixas(self):
        print("\n---- Estado das Caches ----\n")

        for x, caixa in enumerate(self.caixas):
            nome_caixa = Caixa(x).name  
            print("\nCaixa : " + nome_caixa)
 
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
        print(local_mp)
        print("--------------------------------------------------------------------")
        self.estoque[local_mp] = deepcopy(linha_cache.dados)

    def busca_mp(self, bloco_mp:int):
        return self.estoque[bloco_mp]

    def busca_em_outras_caches(self, jogo_id:int, caixa_solicitante:int):
        bloco_mp = jogo_id // 5
        for id_caixa in range(3): 
            if id_caixa == caixa_solicitante:
                continue  # pula a cache que pediu

            resultado = self.caixas[id_caixa].buscar_bloco(bloco_mp)

            if resultado != -1:
                return resultado , id_caixa

        return -1 , -1 

    def leitura(self, jogo_id: int, id_caixa:int):
        
        posicao_jogo = jogo_id % 5 
        bloco_mp = jogo_id // 5
        caixa_solicitante = self.caixas[id_caixa]
        nome_caixa = Caixa(id_caixa).name

        # Tenta achar na própria cache
        index_caixa = caixa_solicitante.buscar_bloco(bloco_mp)
        print(f"\n--- Leitura: Caixa {nome_caixa}, Jogo {jogo_id} (Bloco {bloco_mp}) ---")


        if index_caixa != -1:
             # --- READ HIT (RH) ---
            print(f"\t-> [RH] Read Hit na linha {index_caixa}")
            dado = caixa_solicitante.buscar_dado(index_caixa,posicao_jogo)
            print(f"\t-> Dado lido: {dado}")

        else:
            # --- READ MISS (RM) ---
            print(f"\t-> [RM] Read Miss")
            # 1. Preparar espaço (Algoritmo FIFO)
            index_substituida = caixa_solicitante.fifo_index
            linha_substituida = caixa_solicitante.linhas[index_substituida]

            print(f"\t-> Alocando na linha {index_substituida} (FIFO).")  
            # 2. Verificar se precisa de Write-Back antes de sobrescrever
            if linha_substituida.estado in [Moesi.M, Moesi.O]:
                self.write_back(linha_substituida)
                pass

            #Busca em Se tem Alguma Cache com o Dado 
            linha_outra_cache , caixa_buscada = self.busca_em_outras_caches(jogo_id, id_caixa)

           # Buscar em outras caches
            if linha_outra_cache != -1: 
                
                # Achou em outra cache (Cache-to-Cache)
                print(f"\t-> Dado encontrado na Caixa {Caixa(caixa_buscada).name} (Linha {linha_outra_cache})")

                # Copia a linha inteira da outra cache
                caixa_solicitante.linhas[index_substituida] = deepcopy(self.caixas[caixa_buscada].linhas[linha_outra_cache])

                # Quem pediu vira Shared (S)
                caixa_solicitante.linhas[index_substituida].estado = Moesi.S

                if self.caixas[caixa_buscada].linhas[linha_outra_cache].estado == Moesi.M:
                    self.caixas[caixa_buscada].linhas[linha_outra_cache].estado = Moesi.O
                elif self.caixas[caixa_buscada].linhas[linha_outra_cache].estado == Moesi.E:
                    self.caixas[caixa_buscada].linhas[linha_outra_cache].estado = Moesi.S
            
            else:
                
                caixa_solicitante.linhas[index_substituida].dados = deepcopy(self.busca_mp(bloco_mp))
                caixa_solicitante.linhas[index_substituida].bloco_mp = deepcopy(bloco_mp)
                caixa_solicitante.linhas[index_substituida].estado = Moesi.E
                
            # Mostra o dado solicitado
            dado = caixa_solicitante.buscar_dado(index_substituida, posicao_jogo)
            print(f"\t-> Dado lido: {dado}")

            # Avança o ponteiro FIFO
            caixa_solicitante.fifo_index = (index_substituida + 1) % 5





    def invalida_outros_caixas(self, id_caixa_agressor: int, bloco_mp: int):
        for i, caixa in enumerate(self.caixas):
            if i != id_caixa_agressor:
                index = caixa.buscar_bloco(bloco_mp)

                if index != -1:
                    linha = caixa.linhas[index]

                    if linha.estado != Moesi.I:
                        print(f"\t-> Invalidando cópia no Caixa {Caixa(i).name}")
                        linha.estado = Moesi.I



    def escrita(self, id_caixa : int, bloco_mp: int, novos_dados : list[int]):

        caixa_solicitante = self.caixas[id_caixa]
        nome_caixa = Caixa(id_caixa).name
        index_caixa = caixa_solicitante.buscar_bloco(bloco_mp)

        print(f"\n--- Solicitação de ESCRITA: Caixa {nome_caixa}, Bloco {bloco_mp} ---")

        if index_caixa != -1:
            print(f"\t-> Resultado: Write Hit na Linha {index_caixa}")

            linha = caixa_solicitante.linhas[index_caixa]
            estado_atual = linha.estado

            linha.dados = deepcopy(novos_dados)

            if estado_atual == Moesi.M:
                print(f"\t-> Estado mantido Modified (M).")
            else:
                print(f"\t-> Estado alterado de {estado_atual.name} para Modified (M).")
                linha.estado = Moesi.M
                self.invalida_outros_caixas(index_caixa, bloco_mp)

        else:

            print(f"\t-> Resultado: Write Miss")

            index_substituida = caixa_solicitante.fifo_index
            linha_substituida = caixa_solicitante.linhas[index_substituida]

            print(f"\t-> Alocando na linha {index_substituida} (FIFO).")  

            if linha_substituida.estado in [Moesi.M, Moesi.O]:
                self.write_back(linha_substituida)

            self.invalida_outros_caixas(index_caixa, bloco_mp)

            linha_substituida.bloco_mp = bloco_mp
            linha_substituida.dados = deepcopy(novos_dados) 
            linha_substituida.estado = Moesi.M

            print(f"\t-> Bloco {bloco_mp} gravado. Estado alterado para Modified(M).")

            caixa_solicitante.fifo_index = (index_substituida + 1) % 5
 
a = Locadora() 
a.imprime_caixas()
a.imprime_mp()

# if __name__ == "__main__":
#     locadora = Locadora()
    
#     print("\n=== PREPARAÇÃO DO CENÁRIO ===")
#     # Vamos escrever no CAIXA MARIO (0), no BLOCO 2 da Memória.
#     # Dados fictícios para identificar visualmente: [111, 222, 333, 444, 555]
#     # Bloco 2 contém os Jogos de ID: 10, 11, 12, 13, 14 (pois 2 * 5 = 10)
#     locadora.escrita(id_caixa=0, bloco_mp=2, novos_dados=[111, 222, 333, 444, 555])
    
#     print("\n=== TESTE 1: LEITURA COM SUCESSO (READ HIT) ===")
#     # Cenário: Cliente quer o Jogo de ID 12.
#     # Cálculo interno: 
#     #   Bloco = 12 // 5 = 2
#     #   Posição = 12 % 5 = 2 (deve retornar o valor 333)
#     print("Solicitando Jogo 12 (Está no Bloco 2, Posição 2)...")
#     locadora.leitura(jogo_id=12, id_caixa=0)

#     print("\n=== TESTE 2: LEITURA OUTRA POSIÇÃO MESMO BLOCO ===")
#     # Cenário: Cliente quer o Jogo de ID 10.
#     # Cálculo interno: 
#     #   Bloco = 10 // 5 = 2
#     #   Posição = 10 % 5 = 0 (deve retornar o valor 111)
#     print("Solicitando Jogo 10 (Está no Bloco 2, Posição 0)...")
#     locadora.leitura(jogo_id=10, id_caixa=0)

#     print("\n=== TESTE 3: LEITURA FALHA (READ MISS) ===")
#     # Cenário: Cliente quer Jogo 5 (Bloco 1).
#     # O Mario TEM o Bloco 2, mas NÃO TEM o Bloco 1.
#     # Como você ainda não implementou a busca na MP, isso não deve imprimir o dado,
#     # apenas o seu print de debug "AAAA..." e sair.
#     print("Solicitando Jogo 5 (Bloco 1 - Não está na cache)...")
#     locadora.leitura(jogo_id=14, id_caixa=0)


#     locadora.imprime_caixas()


if __name__ == "__main__":
    locadora = Locadora()
    
    id_mario = 0 # Vamos usar apenas o Mario para focar na substituição
    
    print("--- 1. ENCHENDO A CACHE (Ocupando as 5 linhas) ---")
    # Vamos escrever nos blocos 10, 11, 12, 13, 14 sequencialmente.
    # O FIFO Index vai mover de 0 -> 1 -> 2 -> 3 -> 4 -> 0
    for i in range(5):
        bloco = 10 + i
        print(f"Escrevendo Bloco {bloco}...")
        # Dados fictícios apenas para visualizar: [10,10,10,10], [11,11... etc
        locadora.escrita(id_mario, bloco_mp=bloco, novos_dados=[bloco]*5)

    print("\n--- ESTADO ANTES DO ESTOURO (CACHE CHEIA) ---")
    locadora.imprime_caixas()
    # PRESTE ATENÇÃO: 
    # Linha 0 tem Bloco 10 (foi o primeiro a entrar)
    # Próxima linha (fifo_index) deve ser 0
    
    print("\n--- 2. FORÇANDO A PRIMEIRA SUBSTITUIÇÃO (FIFO) ---")
    # Agora a cache está cheia. Vamos escrever no Bloco 99.
    # Como o fifo_index é 0, ele DEVE apagar a Linha 0 (Bloco 10) e escrever o 99.
    locadora.leitura(4,0)
    
    print("\n--- RESULTADO APÓS 1ª SUBSTITUIÇÃO ---")
    locadora.imprime_caixas()
    # VERIFIQUE NO CONSOLE:
    # A Linha 0 agora deve ter o Bloco 99.
    # A Linha 1 ainda tem o Bloco 11.
    # O fifo_index deve ter mudado para 1.

    print("\n--- 3. FORÇANDO A SEGUNDA SUBSTITUIÇÃO (FIFO) ---")
    # Vamos escrever no Bloco 88.
    # Como o fifo_index agora é 1, ele DEVE apagar a Linha 1 (Bloco 11).
    locadora.leitura(36,0)
    
    print("\n--- RESULTADO APÓS 2ª SUBSTITUIÇÃO ---")
    locadora.leitura(20,2)
    locadora.imprime_caixas()
    locadora.imprime_mp()
    # VERIFIQUE NO CONSOLE:
    # A Linha 1 agora deve ter o Bloco 88.
    # O fifo_index deve ter mudado para 2.


# if __name__ == "__main__":
#     sim = Locadora()
    
#     # Prepara o cenário inicial
#     print("### PREPARAÇÃO DE CENÁRIO ###")
#     # Escreve o Bloco 0 na Cache do MARIO (id 0) com dados customizados
#     sim.escrita(0, 0, [100, 101, 102, 103, 104]) 
    
#     # Escreve o Bloco 1 na Cache do LUIGI (id 1)
#     sim.escrita(1, 1, [200, 201, 202, 203, 204])

#     print("\n\n" + "#"*60)
#     print("           INICIANDO TESTES SOLICITADOS")
#     print("#"*60)

#     # ---------------------------------------------------------
#     # TESTE 1: Read HIT (Primeiro IF)
#     # Mario lê o Bloco 0 (Jogo 2, pos 2) que ele ACABOU de escrever.
#     # ---------------------------------------------------------
#     print("\n>>> TESTE 1: Read HIT (Mario lê algo que ele já tem)")
#     # Jogo ID 2 -> Bloco 0 (2//5=0), Pos 2 (2%5=2). Valor esperado: 102
#     sim.leitura(2, 0) 

#     # ---------------------------------------------------------
#     # TESTE 2: Read MISS -> Cache-to-Cache (Segundo IF/Logica)
#     # Peach (id 2) quer ler o Bloco 1 (Jogo 6).
#     # Ninguém tem na MP atualizado, mas LUIGI tem (Dirty/Modified).
#     # ---------------------------------------------------------
#     print("\n>>> TESTE 2: Read MISS buscando em outra cache (Peach lê dado do Luigi)")
#     # Jogo ID 6 -> Bloco 1 (6//5=1), Pos 1 (6%5=1). Valor esperado: 201
#     sim.leitura(6, 0) 

#     # ---------------------------------------------------------
#     # TESTE 3: Read MISS -> Memória Principal (Else final)
#     # Luigi quer ler o Bloco 2 (Jogo 10). Ninguém tem esse bloco.
#     # ---------------------------------------------------------
#     print("\n>>> TESTE 3: Read MISS total (Busca na Memória Principal)")
#     # Jogo ID 10 -> Bloco 2 (10//5=2), Pos 0 (10%5=0). Valor virá do Estoque original.
#     sim.leitura(10, 1)

#     # Visualização final
#     sim.imprime_caixas()
#     sim.imprime_mp()
