import ctypes
import os
import random
import time
import heapq
import math
import multiprocessing
from typing import Type # Para type hinting da classe ctypes
from models import Funcionario, Paciente, Vacina


# MERGESORT

def mergesort_file(main_filename: str, 
                   structure_class: Type[ctypes.Structure], 
                   record_size_bytes: int, 
                   chunk_records_count: int):
    # Ordena um arquivo binário escalável usando Mergesort.
   
    start_time = time.perf_counter()
    print(f"Iniciando 'External Mergesort' de '{main_filename}'...")
    print(f"Registros por chunk: {chunk_records_count:,}")
    
    chunk_files = [] # Lista para guardar os nomes dos arquivos temporários

    try:
        # Fase de sort
        print("\nFASE 1: Criando e ordenando chunks em RAM...")
        chunk_num = 0
        total_records = 0
        
        with open(main_filename, "rb") as f_main:
            while True:
                records_in_memory = []
                # Lê um chunk para a memória
                for _ in range(chunk_records_count):
                    buffer = f_main.read(record_size_bytes)
                    if not buffer:
                        break
                    # Converte os bytes para o tipo de estrutura específico
                    records_in_memory.append(structure_class.from_buffer_copy(buffer))
                
                if not records_in_memory:
                    break # Fim do arquivo

                # Ordena o chunk em RAM
                records_in_memory.sort()
                
                # Salva o chunk ordenado em um arquivo temporário
                chunk_name = f"__chunk_sorted_{chunk_num}.dat"
                chunk_files.append(chunk_name)
                
                with open(chunk_name, "wb") as f_chunk:
                    for record in records_in_memory:
                        f_chunk.write(record)
                
                print(f"  -> Chunk {chunk_num} com {len(records_in_memory)} registros foi ordenado e salvo.")
                total_records += len(records_in_memory)
                chunk_num += 1
        
        print(f"  -> Fase 1 concluída: {total_records:,} registros divididos em {len(chunk_files)} chunks.")

        if not chunk_files:
            print("Arquivo principal está vazio. Abortando.")
            return

        # Fase de merge
        print("\nFASE 2: Mesclando os chunks ordenados...")
        
        open_chunk_files = []
        min_heap = [] # Fila de prioridade
        
        try:
            # Abre todos os chunks e lê o primeiro registro de cada
            for i, chunk_name in enumerate(chunk_files):
                f = open(chunk_name, "rb")
                open_chunk_files.append(f)
                
                buffer = f.read(record_size_bytes)
                if buffer:
                    record = structure_class.from_buffer_copy(buffer)
                    # Adiciona no heap: (objeto_record, índice_do_chunk)
                    heapq.heappush(min_heap, (record, i))

            # Abre o arquivo de saída e substitui o original
            with open(main_filename, "wb") as f_out:
                registros_escritos = 0
                while min_heap:
                    # Pega o menor registro de todos os chunks
                    record, chunk_index = heapq.heappop(min_heap)
                    
                    # Escreve o menor registro no arquivo final
                    f_out.write(record)
                    registros_escritos += 1

                    # Lê o próximo registro do chunk de onde o menor saiu
                    f_chunk = open_chunk_files[chunk_index]
                    next_buffer = f_chunk.read(record_size_bytes)
                    
                    if next_buffer:
                        # Se houver um próximo, adiciona ao heap
                        next_record = structure_class.from_buffer_copy(next_buffer)
                        heapq.heappush(min_heap, (next_record, chunk_index))
                
                print(f"  -> Fase 2 concluída. {registros_escritos:,} registros escritos.")

        finally:
            # File handles dos chunks são fechados
            for f in open_chunk_files:
                f.close()

    except FileNotFoundError:
        print(f"Erro: Arquivo principal '{main_filename}' não encontrado.")
        return
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o mergesort: {e}")
        raise
    finally:
        # Limpar os arquivos temporários
        print("\nFASE 3: Limpando arquivos temporários...")
        cleaned_count = 0
                
        # Apaga os arquivos do disco
        for chunk_name in chunk_files:
            if os.path.exists(chunk_name):
                os.remove(chunk_name)
                cleaned_count += 1
        print(f"  -> {cleaned_count} arquivos chunk removidos.")

    end_time = time.perf_counter()
    print(f"\n'External Mergesort' de '{main_filename}' concluído!")
    print(f"Tempo total: {end_time - start_time:.2f} segundos.")

# FUNÇÃO DE EMBARALHAMENTO

def fat_scramble(main_filename: str, record_size_bytes: int, chunk_records_count: int):
    
    # Embaralha um arquivo em disco sem carregar na RAM
    # O nome foi escolhido ao desenvolver o método em função de arquivos grandes

    print(f"Iniciando 'Fat Scramble' (Embaralhamento Externo) de '{main_filename}'...")
    start_time = time.perf_counter()
    
    chunk_files = []
    chunk_num = 0

    try:
        # Quebrar, embaralhar chunks internos e salvar
        print("Passo 1: Lendo, embaralhando e salvando chunks...")
        with open(main_filename, "rb") as f_main:
            while True:
                
                buffer_chunk = f_main.read(chunk_records_count * record_size_bytes)
                if not buffer_chunk:
                    break
                
                records_in_memory = []
                for i in range(0, len(buffer_chunk), record_size_bytes):
                    record_data = buffer_chunk[i : i + record_size_bytes]
                    if len(record_data) == record_size_bytes:
                        records_in_memory.append(record_data) 
                
                if not records_in_memory:
                    break
                random.shuffle(records_in_memory)
                
                # Salva o chunk embaralhado
                chunk_name = f"__chunk_scrambled_{chunk_num}.dat"
                chunk_files.append(chunk_name)
                with open(chunk_name, "wb") as f_chunk:
                    for record_buffer in records_in_memory:
                        f_chunk.write(record_buffer)
                
                print(f"  -> Chunk {chunk_num} embaralhado e salvo.")
                chunk_num += 1

        if not chunk_files:
            print("Arquivo principal está vazio. Abortando.")
            return

        # Remontar, embaralhando a ordem dos chunks
        print("\nPasso 2/2: Remontando arquivo principal com chunks em ordem aleatória...")
        random.shuffle(chunk_files) # Embaralha a ordem dos arquivos
        
        with open(main_filename, "wb") as f_out: # Sobrescreve o arquivo original
            for chunk_name in chunk_files:
                print(f"  -> Adicionando chunk '{chunk_name}'...")
                with open(chunk_name, "rb") as f_chunk:
                    f_out.write(f_chunk.read())
        
        print("Arquivo principal remontado e embaralhado.")

    except FileNotFoundError:
        print(f"Erro: Arquivo '{main_filename}' não encontrado.")
        return
    except Exception as e:
        print(f"Ocorreu um erro inesperado durante o scramble: {e}")
    finally:
        # Limpeza
        print("\nLimpando arquivos temporários...")
        cleaned_count = 0
        for chunk_name in chunk_files:
            if os.path.exists(chunk_name):
                os.remove(chunk_name)
                cleaned_count += 1
        print(f"  -> {cleaned_count} arquivos chunk removidos.")

    end_time = time.perf_counter()
    print(f"\n'Fat Scramble' de '{main_filename}' concluído!")
    print(f"Tempo total: {end_time - start_time:.2f} segundos.")

# VERIFICAÇÃO DE ORDENAÇÃO

def verifica_ordenacao(filename: str, 
                        structure_class: Type[ctypes.Structure], 
                        record_size_bytes: int):
    
    # Verifica ordenação de forma sequencial 

    print(f"\nIniciando verificação de ordenação de '{filename}'...")
    try:
        with open(filename, "rb") as f:
            buffer = f.read(record_size_bytes)
            if not buffer:
                print("Arquivo está vazio.")
                return True # Vazio é ordenado

            last_record = structure_class.from_buffer_copy(buffer)
            count = 1
            
            while True:
                buffer = f.read(record_size_bytes)
                if not buffer:
                    break
                
                count += 1
                current_record = structure_class.from_buffer_copy(buffer)
                
                if current_record < last_record:
                    print(f"\nErro de ordenação")
                    print(f"Registro {count}: ID {current_record} veio DEPOIS de ID {last_record}")
                    return False
                
                last_record = current_record
                
                if count % 1000000 == 0: # Feedback a cada 1M para arquivos muito grandes apenas
                    print(f"  ... {count:,} registros verificados. (OK)")

        print(f"VERIFICAÇÃO CONCLUÍDA: {count:,} registros estão perfeitamente ordenados.")
        return True
        
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filename}' não encontrado.")
        return False

# GERAÇÃO DOS ARQUIVOS INICIAIS EM PROCESSAMENTO PARALELO

DADOS_AMOSTRA_NOME = [
    "Ana", "Carlos", "Débora", "Gustavo", "Silvia", "Bruno", "Carla", "Diego", 
    "Gabriela", "Sofia", "Genésio", "Lucas", "Anderson", "Clara", "Hellen", 
    "Maria", "Lara", "Milena", "Ricardo", "Vanessa", "Joaquim", "Beatriz",
    "Felipe", "Elisa", "Raul", "Tatiana", "Marcos", "Livia", "Sergio", "Paula",
    "Otavio", "Julia", "Roberto", "Isabela", "Caio", "Fernanda", "Tiago"
]
DADOS_AMOSTRA_VACINA = [
    "Pfizer", "Coronavac", "AstraZeneca", "Janssen", "Moderna", "Sputnik V",
    "Covaxin", "Sinopharm"
]

dados_amostra_worker = []

def _inicializa_worker_gerador(amostra):
    global dados_amostra_worker
    dados_amostra_worker = amostra
    random.seed(os.getpid())

def _gera_chunk_de_FUNCIONARIOS(args):

    start_id, tamanho_chunk, record_size_bytes = args
    print(f"[Worker {os.getpid()}] Gerando chunk de {tamanho_chunk} FUNCIONARIOS (ID: {start_id})...")
    
    buffer = bytearray(tamanho_chunk * record_size_bytes)
    offset = 0
    
    for i in range(start_id, start_id + tamanho_chunk):
        cod = i
        nome = dados_amostra_worker[i % len(dados_amostra_worker)]
        cpf = f"{i%1000:03}.{random.randint(100, 999)}.{random.randint(100, 999)}-{i%100:02}"
        ano = random.randint(1970, 2002)
        mes = random.randint(1, 12)
        dia = random.randint(1, 28)
        data_nascimento = f"{dia:02d}/{mes:02d}/{ano}"
        salario = round(random.uniform(1500.0, 12000.0), 2)
        
        novo_funcionario = Funcionario(cod, nome, cpf, data_nascimento, salario)
        
        ctypes.memmove(ctypes.byref(buffer, offset), ctypes.byref(novo_funcionario), record_size_bytes)
        offset += record_size_bytes
        
    return buffer

def _gera_chunk_de_PACIENTES(args):

    start_id, tamanho_chunk, record_size_bytes = args
    print(f"[Worker {os.getpid()}] Gerando chunk de {tamanho_chunk} PACIENTES (ID: {start_id})...")
    
    buffer = bytearray(tamanho_chunk * record_size_bytes)
    offset = 0
    
    for i in range(start_id, start_id + tamanho_chunk):
        cod = i
        nome = dados_amostra_worker[i % len(dados_amostra_worker)]
        cpf = f"{i%1000:03}.{random.randint(100, 999)}.{random.randint(100, 999)}-{i%100:02}"
        ano = random.randint(1940, 2023) # Pacientes podem ter idades variadas
        mes = random.randint(1, 12)
        dia = random.randint(1, 28)
        data_nascimento = f"{dia:02d}/{mes:02d}/{ano}"
        
        # Assume o construtor Paciente(cod, nome, cpf, data_nascimento)
        novo_paciente = Paciente(cod, nome, cpf, data_nascimento) 
        
        ctypes.memmove(ctypes.byref(buffer, offset), ctypes.byref(novo_paciente), record_size_bytes)
        offset += record_size_bytes
        
    return buffer

def _gera_chunk_de_VACINAS(args):
    start_id, tamanho_chunk, record_size_bytes = args
    print(f"[Worker {os.getpid()}] Gerando chunk de {tamanho_chunk} VACINAS (ID: {start_id})...")
    
    buffer = bytearray(tamanho_chunk * record_size_bytes)
    offset = 0
    
    for i in range(start_id, start_id + tamanho_chunk):
        cod = i
        nome_fabricante = dados_amostra_worker[i % len(dados_amostra_worker)]
        lote = f"LOTE-{i%1000:03d}-{random.randint(100,999)}"
        
        # Gera data de validade futura
        ano = random.randint(2025, 2027) 
        mes = random.randint(1, 12)
        dia = random.randint(1, 28)
        data_validade = f"{dia:02d}/{mes:02d}/{ano}"
        
        # Assume o construtor Vacina(cod, nome_fabricante, lote, data_validade)
        nova_vacina = Vacina(cod, nome_fabricante, lote, data_validade)
        
        ctypes.memmove(ctypes.byref(buffer, offset), ctypes.byref(nova_vacina), record_size_bytes)
        offset += record_size_bytes
        
    return buffer

def gera_arquivo_FUNCIONARIOS_paralelo(filename, num_registros, record_size_bytes, chunk_por_cpu=5):
    print(f"Iniciando geração de arquivo '{filename}' com {num_registros:,} registros...")
    start_time = time.perf_counter()

    try:
        num_processos = multiprocessing.cpu_count()
        total_chunks = num_processos * chunk_por_cpu
        tamanho_chunk = math.ceil(num_registros / total_chunks)
        
        lista_tarefas = []
        for i in range(total_chunks):
            start_id = 1 + (i * tamanho_chunk)
            tamanho_real = min(tamanho_chunk, num_registros - start_id + 1)
            if tamanho_real <= 0:
                break
            lista_tarefas.append((start_id, tamanho_real, record_size_bytes))

        print(f"Usando {num_processos} processos para {len(lista_tarefas)} tarefas (FUNCIONARIOS).")
        
        with open(filename, "wb") as f:
            # Passa a lista de nomes para os workers
            with multiprocessing.Pool(processes=num_processos, 
                                      initializer=_inicializa_worker_gerador, 
                                      initargs=(DADOS_AMOSTRA_NOME,)) as pool:
                
                total_escrito = 0
                for i, chunk_de_bytes in enumerate(pool.imap_unordered(_gera_chunk_de_FUNCIONARIOS, lista_tarefas)):
                    f.write(chunk_de_bytes)
                    
                    registros_no_chunk = len(chunk_de_bytes) // record_size_bytes
                    total_escrito += registros_no_chunk
                    print(f"Progresso: {i+1}/{len(lista_tarefas)} chunks escritos... ({total_escrito:,}/{num_registros:,} registros)")

        end_time = time.perf_counter()
        print("\n--- Concluído ---")
        print(f"Arquivo '{filename}' gerado com sucesso.")
        print(f"Tempo total: {end_time - start_time:4.2f} segundos.")
    
    except Exception as e:
        print(f"Ocorreu um erro ao gerar o arquivo: {e}")

def gera_arquivo_PACIENTES_paralelo(filename, num_registros, record_size_bytes, chunk_por_cpu=5):
    
    # Função principal que orquestra o pool de workers

    print(f"Iniciando geração de arquivo '{filename}' com {num_registros:,} registros...")
    start_time = time.perf_counter()

    try:
        num_processos = multiprocessing.cpu_count()
        total_chunks = num_processos * chunk_por_cpu
        tamanho_chunk = math.ceil(num_registros / total_chunks)
        
        lista_tarefas = []
        for i in range(total_chunks):
            start_id = 1 + (i * tamanho_chunk)
            tamanho_real = min(tamanho_chunk, num_registros - start_id + 1)
            if tamanho_real <= 0:
                break
            lista_tarefas.append((start_id, tamanho_real, record_size_bytes))

        print(f"Usando {num_processos} processos para {len(lista_tarefas)} tarefas (PACIENTES).")
        
        with open(filename, "wb") as f:
            with multiprocessing.Pool(processes=num_processos, 
                                      initializer=_inicializa_worker_gerador, 
                                      initargs=(DADOS_AMOSTRA_NOME,)) as pool:
                
                total_escrito = 0

                for i, chunk_de_bytes in enumerate(pool.imap_unordered(_gera_chunk_de_PACIENTES, lista_tarefas)):
                    f.write(chunk_de_bytes)
                    
                    registros_no_chunk = len(chunk_de_bytes) // record_size_bytes
                    total_escrito += registros_no_chunk
                    print(f"Progresso: {i+1}/{len(lista_tarefas)} chunks escritos... ({total_escrito:,}/{num_registros:,} registros)")

        end_time = time.perf_counter()
        print("\n--- Concluído ---")
        print(f"Arquivo '{filename}' gerado com sucesso.")
        print(f"Tempo total: {end_time - start_time:4.2f} segundos.")
    
    except Exception as e:
        print(f"Ocorreu um erro ao gerar o arquivo: {e}")

def gera_arquivo_VACINAS_paralelo(filename, num_registros, record_size_bytes, chunk_por_cpu=5):

    print(f"Iniciando geração de arquivo '{filename}' com {num_registros:,} registros...")
    start_time = time.perf_counter()

    try:
        num_processos = multiprocessing.cpu_count()
        total_chunks = num_processos * chunk_por_cpu
        tamanho_chunk = math.ceil(num_registros / total_chunks)
        
        lista_tarefas = []
        for i in range(total_chunks):
            start_id = 1 + (i * tamanho_chunk)
            tamanho_real = min(tamanho_chunk, num_registros - start_id + 1)
            if tamanho_real <= 0:
                break
            lista_tarefas.append((start_id, tamanho_real, record_size_bytes))

        print(f"Usando {num_processos} processos para {len(lista_tarefas)} tarefas (VACINAS).")
        
        with open(filename, "wb") as f:
            with multiprocessing.Pool(processes=num_processos, 
                                      initializer=_inicializa_worker_gerador, 
                                      initargs=(DADOS_AMOSTRA_VACINA,)) as pool:
                
                total_escrito = 0
                for i, chunk_de_bytes in enumerate(pool.imap_unordered(_gera_chunk_de_VACINAS, lista_tarefas)):
                    f.write(chunk_de_bytes)
                    
                    registros_no_chunk = len(chunk_de_bytes) // record_size_bytes
                    total_escrito += registros_no_chunk
                    print(f"Progresso: {i+1}/{len(lista_tarefas)} chunks escritos... ({total_escrito:,}/{num_registros:,} registros)")

        end_time = time.perf_counter()
        print("\n--- Concluído ---")
        print(f"Arquivo '{filename}' gerado com sucesso.")
        print(f"Tempo total: {end_time - start_time:4.2f} segundos.")
    
    except Exception as e:
        print(f"Ocorreu um erro ao gerar o arquivo: {e}")

# FUNÇÕES DE LOGGING

def log_tempo(log_filename: str):

    # Lê um arquivo de log, calcula métricas e adiciona um resumo ao final.
  
    total_time = 0.0
    total_comparisons = 0
    entry_count = 0
    
    print(f"Calculando métricas do arquivo '{log_filename}'...")

    try:
        with open(log_filename, 'r', encoding='utf-8') as f:
            for line in f:
                if "Duração:" in line:
                    try:
                        part_after_keyword = line.split("Duração:")[1]
                        time_str = part_after_keyword.split('s')[0].strip()
                        total_time += float(time_str)

                        if "Comparações:" in line:
                            comp_part = line.split("Comparações:")[1]
                            comp_str = comp_part.split(".")[0].strip().replace(",", "")
                            total_comparisons += int(comp_str)
                        
                        entry_count += 1
                    except (IndexError, ValueError, TypeError):
                        pass # Ignora linhas mal formatadas ou de média anterior

    except FileNotFoundError:
        print(f"Erro: Arquivo de log '{log_filename}' não foi encontrado.")
        return
    
    if entry_count == 0:
        print("Nenhuma entrada de 'Duração' válida foi encontrada no log.")
        return

    average_time = total_time / entry_count
    average_comparisons = total_comparisons / entry_count

    # Adiciona o resultado ao final do arquivo
    try:
        with open(log_filename, 'a', encoding='utf-8') as f:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            
            f.write("\n_________________________________________\n")
            f.write(f"[{timestamp}] CÁLCULO DE MÉDIA GERAL\n")
            f.write(f"Total de buscas registradas: {entry_count}\n")
            f.write(f"Tempo total de execução: {total_time:.6f}s\n")
            f.write(f"Tempo médio de execução: {average_time:.6f}s\n")
            f.write(f"Total de comparações: {total_comparisons:,}\n")
            f.write(f"Média de comparações: {average_comparisons:,.2f}\n")
            f.write("_________________________________________\n")
        
        print(f"Métricas calculadas e adicionadas a '{log_filename}'.")

    except Exception as e:
        print(f"Ocorreu um erro ao escrever a média no log: {e}")

def log_resumo_geral(log_especifico: str, log_geral: str = "log_geral.txt"):
    
    # Calcula o resumo de um log específico (ex: log_bin.txt) e anexa esse resumo a um log mestre (log_geral.txt).

    total_time = 0.0
    total_comparisons = 0
    entry_count = 0
    
    print(f"Calculando resumo de '{log_especifico}' para adicionar a '{log_geral}'...")

    try:
        with open(log_especifico, 'r', encoding='utf-8') as f:
            for line in f:
                if "Duração:" in line:
                    try:
                        part_after_keyword = line.split("Duração:")[1]
                        time_str = part_after_keyword.split('s')[0].strip()
                        total_time += float(time_str)
                        
                        if "Comparações:" in line:
                            comp_part = line.split("Comparações:")[1]
                            comp_str = comp_part.split(".")[0].strip().replace(",", "")
                            total_comparisons += int(comp_str)
                        
                        entry_count += 1
                    except (IndexError, ValueError, TypeError):
                        pass 
    
    except FileNotFoundError:
        print(f"Erro: Arquivo de log '{log_especifico}' não foi encontrado.")
        return
    
    if entry_count == 0:
        print(f"Nenhuma entrada válida foi encontrada em '{log_especifico}'.")
        return

    average_time = total_time / entry_count
    average_comparisons = total_comparisons / entry_count

    # Adicionar resumo ao log geral
    try:
        with open(log_geral, 'a', encoding='utf-8') as f:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            
            f.write("\n_________________________________________\n")
            f.write(f"[{timestamp}] RESUMO DO ARQUIVO: '{log_especifico}'\n")
            f.write(f"Total de buscas registradas: {entry_count}\n")
            f.write(f"Tempo total de execução: {total_time:.6f}s\n")
            f.write(f"Tempo médio de execução: {average_time:.6f}s\n")
            f.write(f"Total de comparações: {total_comparisons:,}\n")
            f.write(f"Média de comparações: {average_comparisons:,.2f}\n")
            f.write("_________________________________________\n")
        
        print(f"Resumo de '{log_especifico}' foi adicionado com sucesso a '{log_geral}'.")

    except Exception as e:
        print(f"Ocorreu um erro ao escrever no log geral '{log_geral}': {e}")

