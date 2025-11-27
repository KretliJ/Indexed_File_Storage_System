import heapq
import os
import time
import math
from . import models
from . import utils

# GERAÇÃO DE PARTIÇÕES: REPLACEMENT SELECTION

class ElementoHeap:
    
    # Wrapper para permitir marcar um elemento como pertencente à próxima run
    
    def __init__(self, registro, run_id):
        self.registro = registro
        self.run_id = run_id # 0 = run atual, 1 = próxima run

    def __lt__(self, other):
        # A comparação é o run_id (menor primeiro)
        if self.run_id != other.run_id:
            return self.run_id < other.run_id
        # Se forem da mesma run compara os registros
        return self.registro < other.registro

def selecao_por_substituicao(filename, structure_class, record_size, mem_size_records=1000):
    # Gera partições ordenadas (runs) usando Seleção por Substituição.
    # Retorna lista com nomes dos arquivos partição gerados.
    
    print(f"\nIniciando Seleção por Substituição em '{filename}'...")
    start_time = time.perf_counter()
    utils._log_operacao(f"[Parte II] Iniciando Seleção por Substituição em '{filename}'.", "INFO", models.LOG_FILE_II)
     
    chunk_files = []
    heap = []
    
    try:
        with open(filename, "rb") as f_in:
            # Encher o heap inicial
            for _ in range(mem_size_records):
                buffer = f_in.read(record_size)
                if not buffer:
                    break
                record = structure_class.from_buffer_copy(buffer)
                # Todos começam na run 0
                heapq.heappush(heap, ElementoHeap(record, 0))
            
            run_atual = 0
            f_out = None
            last_record_written = None
            chunk_name = ""

            # Enquanto houver elementos no heap
            while heap:
                # Pega o menor elemento considerando run atual vs próxima
                elemento = heapq.heappop(heap)
                
                # Se pertence a uma run futura, troca de arquivo
                if elemento.run_id > run_atual:
                    if f_out: f_out.close()
                    run_atual = elemento.run_id
                    last_record_written = None # Reseta para nova run
                
                # Novo arquivo de partição se necessário
                if not f_out or f_out.closed:
                    chunk_name = f"__adv_run_{run_atual}.dat"
                    if chunk_name not in chunk_files:
                        chunk_files.append(chunk_name)
                        print(f"  -> Criando Partição {run_atual}...")
                    f_out = open(chunk_name, "ab") # Append binary

                # Escreve o registro
                f_out.write(elemento.registro)
                last_record_written = elemento.registro

                # Lê o próximo do arquivo de entrada para substituir
                buffer = f_in.read(record_size)
                if buffer:
                    new_record = structure_class.from_buffer_copy(buffer)
                    
                    # run atual ou a próxima?
                    if new_record < last_record_written:
                        new_run_id = run_atual + 1
                    else:
                        new_run_id = run_atual
                    
                    heapq.heappush(heap, ElementoHeap(new_record, new_run_id))
            
            if f_out: f_out.close()

    except FileNotFoundError:
        print(f"Erro: Arquivo '{filename}' não encontrado.")
        utils._log_operacao(f"Erro: Arquivo '{filename}' não encontrado.", "ERRO", models.LOG_FILE_II)
        return []
        
    print(f"  -> Seleção concluída. {len(chunk_files)} partições criadas.")
    utils._log_operacao(f"[Parte II] Seleção concluída. {len(chunk_files)} partições geradas.", "INFO", models.LOG_FILE_II)
    return chunk_files

# INTERCALAÇÃO: TOURNAMENT TREE

class NoArvore:
    def __init__(self, registro, source_index):
        self.registro = registro
        self.source_index = source_index # Índice do arquivo de onde veio

class ArvoreVencedores:
    def __init__(self, arquivos_abertos, structure_class, record_size):
        self.arquivos = arquivos_abertos
        self.structure_class = structure_class
        self.record_size = record_size
        self.num_sources = len(arquivos_abertos)
        
        self.tree_size = 2 * self.num_sources
        self.tree = [None] * self.tree_size
        
        # Primeiro registro de cada arquivo para as folhas
        for i in range(self.num_sources):
            self._ler_proximo_para_folha(i)
            
        # Construir a árvore inicial
        for i in range(self.num_sources - 1, 0, -1):
            self._jogar_partida(i)

    def _ler_proximo_para_folha(self, source_index):
        # Lê do arquivo e coloca na folha correspondente
        f = self.arquivos[source_index]
        buffer = f.read(self.record_size)
        
        tree_index = self.num_sources + source_index
        
        if buffer:
            record = self.structure_class.from_buffer_copy(buffer)
            self.tree[tree_index] = NoArvore(record, source_index)
        else:
            # Arquivo acabou, infinito para sempre perder
            self.tree[tree_index] = None 

    def _jogar_partida(self, node_index):
        # Compara os dois filhos de um nó e define o vencedor
        left_child = 2 * node_index
        right_child = 2 * node_index + 1
        
        # um dos filhos não existe ignora
        if left_child >= self.tree_size: return

        vencedor = None
        cand1 = self.tree[left_child]
        cand2 = self.tree[right_child] if right_child < self.tree_size else None
        
        if cand1 is None and cand2 is None:
            vencedor = None # Ambos vazios fim das streams
        elif cand1 is None:
            vencedor = cand2
        elif cand2 is None:
            vencedor = cand1
        else:
            if cand1.registro < cand2.registro:
                vencedor = cand1
            else:
                vencedor = cand2
                
        self.tree[node_index] = vencedor

    def obter_vencedor(self):
        # Retorna o vencedor global
        return self.tree[1]

    def substituir_vencedor_e_rebalancear(self):
        # Remove o vencedor atual, e re-joga
        vencedor_atual = self.tree[1]
        if vencedor_atual is None:
            return # Árvore vazia
            
        source_idx = vencedor_atual.source_index
        
        # Ler próximo registro para a folha de onde veio o vencedor
        self._ler_proximo_para_folha(source_idx)
        
        # Re-jogar o torneio apenas no caminho da folha até a raiz
        idx = (self.num_sources + source_idx) // 2
        while idx > 0:
            self._jogar_partida(idx)
            idx //= 2


def intercalacao_arvore_vencedores(main_filename, chunk_files, structure_class, record_size):
    print(f"\nIniciando Intercalação...")
    utils._log_operacao(f"[Parte II] Iniciando Intercalação (Árvore de Vencedores).", "INFO", models.LOG_FILE_II)
    
    open_files = []
    try:
        # Abrir todos os chunks
        for fname in chunk_files:
            open_files.append(open(fname, "rb"))
            
        # Inicializar árvore
        arvore = ArvoreVencedores(open_files, structure_class, record_size)
        
        # Escrever no arquivo final
        with open(main_filename, "wb") as f_out:
            count = 0
            while True:
                vencedor = arvore.obter_vencedor()
                if vencedor is None:
                    break # Fim de todos os arquivos
                
                f_out.write(vencedor.registro)
                arvore.substituir_vencedor_e_rebalancear()
                count += 1
                
        print(f"  -> Intercalação concluída. {count} registros consolidados.")
        utils._log_operacao(f"[Parte II] Intercalação concluída. {count} registros consolidados.", "INFO", models.LOG_FILE_II)

    finally:
        for f in open_files:
            f.close()



def mergesort_avancado(filename, structure_class, record_size, mem_size_records=1000):
    # Combina Seleção por Substituição + Árvore de Vencedores
    start_total = time.perf_counter()
    
    # Geração de Partições
    chunks = selecao_por_substituicao(filename, structure_class, record_size, mem_size_records)
    
    if not chunks:
        print("Nenhuma partição gerada.")
        return

    # Intercalação
    intercalacao_arvore_vencedores(filename, chunks, structure_class, record_size)
    
    # Limpeza
    print("Limpando arquivos temporários...")
    for c in chunks:
        if os.path.exists(c):
            os.remove(c)
            
    end_total = time.perf_counter()
    print(f"Tempo Total: {end_total - start_total:.4f}s")
    
    utils._log_operacao(f"Mergesort Avançado (Parte II) concluído em {end_total - start_total:.4f}s", "INFO", models.LOG_FILE_II)