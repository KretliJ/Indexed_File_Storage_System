import heapq
import os
import time
import math
from . import models
from . import utils

# FASE 1: GERAÇÃO DE PARTIÇÕES (SELEÇÃO POR SUBSTITUIÇÃO)
# Objetivo: Criar arquivos ordenados (runs) que sejam, em média, 
# 2x maiores que o tamanho da memória disponível.

class ElementoHeap:
    # Wrapper (envelope) para os registros dentro do Heap.
    # O segredo da Seleção por Substituição está em controlar se o elemento
    # pertence à 'run' (partição) atual ou se deve ficar 'congelado' para a próxima.

    def __init__(self, registro, run_id):
        self.registro = registro
        self.run_id = run_id # 0 = run atual, 1 = próxima run, 2 = próxima run, etc.

    def __lt__(self, other):
        # O Heap sempre colocará no topo quem tem o MENOR run_id.
        # Se os run_ids forem iguais, desempata pelo valor do registro.
        # Isso garante que elementos da próxima partição nunca saiam antes
        # de terminar a partição atual.
        if self.run_id != other.run_id:
            return self.run_id < other.run_id
        return self.registro < other.registro

def selecao_por_substituicao(filename, structure_class, record_size, mem_size_records=1000):
    print(f"\nIniciando Seleção por Substituição em '{filename}'...")
    start_time = time.perf_counter()
    utils._log_operacao(f"[Parte II] Iniciando Seleção por Substituição em '{filename}'.", "INFO", models.LOG_FILE_II)
     
    chunk_files = [] # Lista para guardar os nomes dos arquivos criados
    heap = []        # A memória principal (Priority Queue)
    
    try:
        with open(filename, "rb") as f_in:
            # Encher o heap inicial (Carregara a memória)
            # Ler do arquivo até encher a capacidade da memória (mem_size_records)
            for _ in range(mem_size_records):
                buffer = f_in.read(record_size)
                if not buffer:
                    break
                record = structure_class.from_buffer_copy(buffer)
                # Inicialmente todos pertencem à rodada (run) 0
                heapq.heappush(heap, ElementoHeap(record, 0))
            
            run_atual = 0
            f_out = None
            last_record_written = None # Guardar o último valor escrito no arquivo atual
            chunk_name = ""

            # Loop Principal executa enquanto houver dados na memória (heap)
            while heap:
                # 1. Pega o menor elemento disponível. 
                # Graças à classe ElementoHeap, se houver elementos da run_atual,
                # eles virão antes dos elementos da run_atual + 1 (próxima run).
                elemento = heapq.heappop(heap)
                
                # 2. Se o menor elemento do heap pertence a uma run futura (ex: run 1)
                # e ainda está na run 0, significa que a run 0 acabou (todos
                # os elementos restantes no heap estão "congelados" para o futuro).
                if elemento.run_id > run_atual:
                    if f_out: f_out.close() # Fecha o arquivo da partição anterior
                    run_atual = elemento.run_id
                    last_record_written = None # Reseta o controle de ordem
                
                # Criação do arquivo de partição (se não estiver aberto)
                if not f_out or f_out.closed:
                    chunk_name = f"__adv_run_{run_atual}.dat"
                    if chunk_name not in chunk_files:
                        chunk_files.append(chunk_name)
                        print(f"  -> Criando Partição {run_atual}...")
                    f_out = open(chunk_name, "ab") # Append binary

                # 3. Escreve o registro na partição atual
                f_out.write(elemento.registro)
                last_record_written = elemento.registro

                # 4. Lê o próximo registro do arquivo de entrada
                # para ocupar o lugar vago na memória (heap).
                buffer = f_in.read(record_size)
                if buffer:
                    new_record = structure_class.from_buffer_copy(buffer)
                    
                    # Substituição:
                    # Se o novo registro for MENOR que o último escrito, não pode
                    # ser escrito agora (pois quebraria a ordem crescente do arquivo).
                    # Então, ele é congelado (vai para a heap, mas marcado com
                    # run_id + 1) e só sairá quando abrir o próximo arquivo.
                    if new_record < last_record_written:
                        new_run_id = run_atual + 1
                    else:
                        # Se for maior ou igual, ele pode entrar na run atual.
                        new_run_id = run_atual
                    
                    heapq.heappush(heap, ElementoHeap(new_record, new_run_id))
            
            # Fecha o último arquivo pendente
            if f_out: f_out.close()

    except FileNotFoundError:
        print(f"Erro: Arquivo '{filename}' não encontrado.")
        return []
        
    print(f"  -> Seleção concluída. {len(chunk_files)} partições criadas.")
    return chunk_files



# FASE 2: INTERCALAÇÃO (ÁRVORE DE VENCEDORES)
# Objetivo: Ler K arquivos ordenados simultaneamente e gerar um único arquivo final,
# fazendo o mínimo de comparações possível usando uma estrutura de árvore.

class NoArvore:
    def __init__(self, registro, source_index):
        self.registro = registro
        self.source_index = source_index # Identifica de qual arquivo veio (0, 1, 2...)

class ArvoreVencedores:
    def __init__(self, arquivos_abertos, structure_class, record_size):
        self.arquivos = arquivos_abertos
        self.structure_class = structure_class
        self.record_size = record_size
        self.num_sources = len(arquivos_abertos)
        
        # A árvore é implementada como um vetor.
        # Tamanho 2*K. Os nós de 1 a K-1 são internos (vencedores parciais).
        # Os nós de K a 2K-1 são as folhas (buffer de entrada dos arquivos).
        self.tree_size = 2 * self.num_sources
        self.tree = [None] * self.tree_size
        
        # 1. Lê o primeiro registro de cada arquivo
        # e coloca nas folhas da árvore.
        for i in range(self.num_sources):
            self._ler_proximo_para_folha(i)
            
        # 2. Construção do Torneio Inicial
        # Percorre a árvore de baixo para cima (das folhas para a raiz),
        # fazendo os "jogos" para definir quem sobe.
        for i in range(self.num_sources - 1, 0, -1):
            self._jogar_partida(i)

    def _ler_proximo_para_folha(self, source_index):
        # Lê do arquivo correspondente e coloca na folha específica da árvore.
        f = self.arquivos[source_index]
        buffer = f.read(self.record_size)
        
        # Cálculo da posição da folha no vetor: offset + indice
        tree_index = self.num_sources + source_index
        
        if buffer:
            record = self.structure_class.from_buffer_copy(buffer)
            self.tree[tree_index] = NoArvore(record, source_index)
        else:
            # Se o arquivo acabou, colocamos None.
            # A lógica de comparação tratará None como perdedor automático.
            self.tree[tree_index] = None 

    def _jogar_partida(self, node_index):
        # Compara os dois filhos de um nó e promove o menor (vencedor) para o nó atual.
        # Fórmulas clássicas de heap array: filhos são 2*i e 2*i+1
        left_child = 2 * node_index
        right_child = 2 * node_index + 1
        
        if left_child >= self.tree_size: return

        vencedor = None
        cand1 = self.tree[left_child]
        cand2 = self.tree[right_child] if right_child < self.tree_size else None
        
        # Lógica de seleção (menor vence):
        if cand1 is None and cand2 is None:
            vencedor = None # Ambos os arquivos acabaram
        elif cand1 is None:
            vencedor = cand2 # Esquerda vazia, direita vence
        elif cand2 is None:
            vencedor = cand1 # Direita vazia, esquerda vence
        else:
            # Menor registro vence
            if cand1.registro < cand2.registro:
                vencedor = cand1
            else:
                vencedor = cand2
                
        self.tree[node_index] = vencedor

    def obter_vencedor(self):
        # O campeão absoluto do torneio sempre está na raiz (índice 1)
        return self.tree[1]

    def substituir_vencedor_e_rebalancear(self):
        # Após escrever o vencedor no arquivo final:
        # I. Descobrir de qual arquivo ele veio.
        # II. Ler o próximo registro desse arquivo.
        # III. Refazer o torneio apenas no caminho desse nó até a raiz.
        
        vencedor_atual = self.tree[1]
        if vencedor_atual is None:
            return # Árvore vazia, tudo terminado
            
        source_idx = vencedor_atual.source_index
        
        # 1. Preenche a folha vaga com novo dado
        self._ler_proximo_para_folha(source_idx)
        
        # 2. Replay: sobe a árvore ajustando apenas os jogos afetados
        idx = (self.num_sources + source_idx) // 2
        while idx > 0:
            self._jogar_partida(idx)
            idx //= 2 # Vai para o pai

def intercalacao_arvore_vencedores(main_filename, chunk_files, structure_class, record_size):
    print(f"\nIniciando Intercalação...")
    utils._log_operacao(f"[Parte II] Iniciando Intercalação (Árvore de Vencedores).", "INFO", models.LOG_FILE_II)
    
    open_files = []
    try:
        # Abre todos os arquivos de partição em modo leitura
        for fname in chunk_files:
            open_files.append(open(fname, "rb"))
            
        # Instancia a árvore (já faz o torneio inicial no __init__)
        arvore = ArvoreVencedores(open_files, structure_class, record_size)
        
        # Loop de escrita do arquivo final
        with open(main_filename, "wb") as f_out:
            count = 0
            while True:
                # 1. Quem é o menor de todos os arquivos agora?
                vencedor = arvore.obter_vencedor()
                
                # Se vencedor é None, todos os arquivos acabaram
                if vencedor is None:
                    break 
                
                # 2. Escreve no arquivo final
                f_out.write(vencedor.registro)
                
                # 3. Avança a fila do arquivo que venceu
                arvore.substituir_vencedor_e_rebalancear()
                count += 1
                
        print(f"  -> Intercalação concluída. {count} registros consolidados.")

    finally:
        # Fechamento dos arquivos temporários
        for f in open_files:
            f.close()

# FUNÇÃO PRINCIPAL (MERGESORT AVANÇADO)

def mergesort_avancado(filename, structure_class, record_size, mem_size_records=1000):
    start_total = time.perf_counter()
    
    # 1. Criação das partições (Runs)
    chunks = selecao_por_substituicao(filename, structure_class, record_size, mem_size_records)
    
    if not chunks:
        print("Nenhuma partição gerada.")
        return

    # 2. Intercalação (Merge)
    intercalacao_arvore_vencedores(filename, chunks, structure_class, record_size)
    
    # 3. Limpeza
    print("Limpando arquivos temporários...")
    for c in chunks:
        if os.path.exists(c):
            os.remove(c)
            
    end_total = time.perf_counter()
    print(f"Tempo Total: {end_total - start_total:.4f}s")
