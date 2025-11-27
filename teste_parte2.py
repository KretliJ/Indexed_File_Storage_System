from modules import models, utils, advanced_sort, data_access
import os
import shutil
import time

def log_teste(mensagem):
   
    # Função helper para imprimir na tela e salvar no relatório.
   
    print(mensagem)
    utils._log_operacao(mensagem, "RELATORIO", arquivo_destino=models.LOG_FILE_II)

def rodar_teste():
    print("=== TESTE PARTE II DO TRABALHO PRÁTICO ===")
    
    # Arquivo de teste
    ARQUIVO_TESTE = "files/teste_ordenacao.dat"
    NUM_REGS = 100_000
    log_teste("\n1. Gerando massa de dados desordenada (100.000 registros)...")   
    # Gerar arquivo desordenado usando o gerador existente
    print("\nGerando massa de dados desordenada...")
    utils.gera_arquivo_FUNCIONARIOS_paralelo(ARQUIVO_TESTE, NUM_REGS, models.RECORD_SIZE_FUNC)
    utils.fat_scramble_generic(ARQUIVO_TESTE, models.RECORD_SIZE_FUNC, 5000) # Garante desordem
    
    # Cópia para o teste 2
    ARQUIVO_TESTE_2 = "files/teste_ordenacao_v2.dat"
    shutil.copy(ARQUIVO_TESTE, ARQUIVO_TESTE_2)
    
    # TESTE 1: Mergesort parte I
    print("\n---------------------------------------------------")
    print("Executando (Sort Interno + Heap Merge)")
    print("---------------------------------------------------")
    log_teste("\n---------------------------------------------------")
    log_teste("2. Executando Mergesort Parte I (Sort Interno + Heap Merge)")
    log_teste("---------------------------------------------------")

    start_v1 = time.perf_counter()
    utils.mergesort_file(ARQUIVO_TESTE, models.Funcionario, models.RECORD_SIZE_FUNC, chunk_records_count=5000)
    end_v1 = time.perf_counter()
    
    tempo_v1 = end_v1 - start_v1
    print(f"Tempo Parte I: {tempo_v1:.4f} segundos")
    log_teste(f"Tempo Parte I: {tempo_v1:.4f} segundos")
    
    
    # TESTE 2: Mergesort parte II
    print("\n---------------------------------------------------")
    print("Executando Seleção Subst. + Árvore Vencedores")
    print("---------------------------------------------------")
    log_teste("\n---------------------------------------------------")
    log_teste("3. Executando Mergesort Parte II (Seleção Subst. + Árvore Vencedores)")
    log_teste("---------------------------------------------------")  

    start_v2 = time.perf_counter()
    # mem_size_records é o tamanho do heap em RAM. 
    # Seleção por substituição = runs 2 * mem_size.
    advanced_sort.mergesort_avancado(ARQUIVO_TESTE_2, models.Funcionario, models.RECORD_SIZE_FUNC, mem_size_records=5000)
    end_v2 = time.perf_counter()
    
    tempo_v2 = end_v2 - start_v2
    print(f"Tempo Parte II: {tempo_v2:.4f} segundos")
    log_teste(f"Tempo Parte II: {tempo_v2:.4f} segundos")
    # RELATÓRIO
    print("\n===================================================")
    print("                   RELATÓRIO                       ")
    print("===================================================")
    print(f"Registros processados: {NUM_REGS}")
    print(f"Método Quicksort + Heap:      {tempo_v1:.4f}s")
    print(f"Método Substituição + Árvore:{tempo_v2:.4f}s")
    log_teste("\n===================================================")
    log_teste("                RELATÓRIO FINAL                    ")
    log_teste("===================================================")
    log_teste(f"Registros processados: {NUM_REGS}")
    log_teste(f"Método Parte I (Quicksort + Heap):      {tempo_v1:.4f}s")
    log_teste(f"Método Parte II (Substituição + Árvore):{tempo_v2:.4f}s")
    
    diff = tempo_v1 - tempo_v2
    if diff > 0:
        print(f"-> Parte II foi {diff:.4f}s mais rápida.")
        log_teste(f"-> Parte II foi {diff:.4f}s mais rápida.")
    else:
        print(f"-> Parte I foi {abs(diff):.4f}s mais rápida.")
        log_teste(f"-> Parte I foi {abs(diff):.4f}s mais rápida.")
        
    log_teste("")        
    log_teste("A Seleção por Substituição (Parte II) reduz drasticamente o número de arquivos temporários")
    log_teste("criados, ao permitir gerar partições (runs) maiores que a memória disponível")

    log_teste("")
    log_teste("A Árvore de Vencedores mostrou-se eficiente para a intercalação, pois reduz")
    log_teste("o número de comparações necessárias para decidir o próximo menor registro")
    log_teste("quando comparado a uma busca linear simples, embora tenha complexidade similar")
    log_teste("a um heap.")
    
    print(f"\nRelatório gerado em: {os.path.abspath(models.LOG_FILE_II)}")
if __name__ == "__main__":
    rodar_teste()