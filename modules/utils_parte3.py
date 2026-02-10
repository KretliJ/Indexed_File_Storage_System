import os
from modules import models
import ctypes

#         ("cod_chave", ctypes.c_int),      # Chave de busca (ID da aplicação)
#         ("endereco_dados", ctypes.c_int), # Índice físico no arquivo .dat (0, 1, 2...)
#         ("estado", ctypes.c_int)          # 0=Livre, 1=Ocupado, 2=Removido

def inicializar_hash_vazia():
    # Cria o arquivo de hash preenchido com registros vazios (estado=0)"""
    print(f"Inicializando Tabela Hash com {models.TAMANHO_HASH_TABLE} posições...")
    registro_vazio = models.RegistroHash(0, -1, 0) # estado 0 = Livre
    
    with open(models.FILE_HASH, "wb") as f:
        for _ in range(models.TAMANHO_HASH_TABLE):
            f.write(registro_vazio)

def hash_function(chave):
    # Retorna a posição inicial baseada no resto da divisão
    return chave % models.TAMANHO_HASH_TABLE

# Desenvolvimento: Esta função assume que o arquivo que recebe referência já está aberto com a permissão "rb+"
def inserir_na_hash(chave, endereco_fisico, f_hash):
    
    # Tenta inserir uma chave na tabela hash.
    # Usa tentativa linear para colisões.
    
    posicao_inicial = hash_function(chave)
    posicao = posicao_inicial
    
    if f_hash.closed:
        print("Erro! Passe um arquivo aberto como 'rb+' !")
    else:
        while True:
            # 1. Vai até a posição calculada
            f_hash.seek(posicao * ctypes.sizeof(models.RegistroHash))
                
            # 2. Lê o registro que está lá
            buffer = f_hash.read(ctypes.sizeof(models.RegistroHash))
            registro = models.RegistroHash.from_buffer_copy(buffer)
                
            # 3. Verifica se está livre
            # (estado 0 = Livre, estado 2 = Removido -> Ambos são vagas úteis)
            if registro.estado == 0 or registro.estado == 2:
                # Está livre, grava aqui
                
                # Caso principal para a primeira incialização do hashmap

                novo_registro = models.RegistroHash(chave, endereco_fisico, 1) # 1 = Ocupado
                    
                # Volta o ponteiro para o início desse registro para sobrescrever
                f_hash.seek(posicao * ctypes.sizeof(models.RegistroHash))
                f_hash.write(novo_registro)
                return # Sucesso, sai da função
                
            # 4. Colisão: A posição está ocupada (estado 1)
            # Verificamos se não é a mesma chave (atualização) - opcional
            if registro.cod_chave == chave:
                print(f"Aviso: Chave {chave} duplicada detectada na indexação.")
                return

            # 5. Tenta a próxima posição (Linear Probing)
            posicao += 1
                
            # 6. Se chegou no fim do arquivo, volta para o começo (Circular)
            if posicao >= models.TAMANHO_HASH_TABLE:
                posicao = 0
                
            # 7. Se deu a volta completa e voltou ao início, a tabela está cheia
            if posicao == posicao_inicial:
                raise Exception("Erro: Tabela Hash está cheia! Aumente o TAMANHO_HASH_TABLE.")
            
    # 1. Vai até a posição calculada com hash_function(chave)
    # 2. Lê o registro da posição
    # 3. Verifica o estado da posição. Se livre grava ali.
    # 4. Se a posição está ocupada...
    # 5. ...tenta a próxima
    # 6. Se chegou ao fim volta ao começo
    # 7. Se deu a volta completa então está cheia

def buscar_na_hash(chave_busca, f_hash):
    # Busca uma chave na tabela hash e retorna o endereco_fisico (índice no .dat).
    # Retorna -1 se não encontrar para indicar escrita EOF.

    posicao_inicial = hash_function(chave_busca)
    posicao = posicao_inicial
    if f_hash.closed:
        print("Erro! Passe um arquivo aberto como 'rb+' !")
    else:
        while True:
            # 1. Posiciona e lê o registro
            f_hash.seek(posicao * ctypes.sizeof(models.RegistroHash))
            buffer = f_hash.read(ctypes.sizeof(models.RegistroHash))

            if not buffer: 
                break # Fim de arquivo inesperado
                
            registro = models.RegistroHash.from_buffer_copy(buffer)
            
            # 2. Análise do Estado
            if registro.estado == 0:
                # Encontrou espaço virgem -> A chave certamente não existe
                return -1
            
            if registro.estado == 1 and registro.cod_chave == chave_busca:
                # Encontrou Ocupado e a chave bate! Retorna onde está o dado real.
                return registro.endereco_dados
            
            # 3. Se for estado 2 (Removido) ou estado 1 com chave diferente, é uma colisão
            # 4. Continua procurando na próxima posição (Linear Probing)
            
            posicao += 1
            if posicao >= models.TAMANHO_HASH_TABLE:
                posicao = 0 # 5. Circular
            
            # 6. Se deu a volta completa e não achou
            if posicao == posicao_inicial:
                return -1

    # 1. Posiciona e lê o registro
    # 2. Análise do Estado
    # 3. Se for estado 2 (Removido) ou estado 1 com chave diferente, é uma colisão
    # 4. Continua procurando na próxima posição (Linear Probing)
    # 5. Circular
    # 6. Se deu a volta completa e não achou
    
def remover_da_hash(chave_busca, f_hash):
    
    # Busca a chave e marca o estado como 2 (Removido).
    # Não apaga o registro fisicamente, apenas lógica.
    
    posicao_inicial = hash_function(chave_busca)
    posicao = posicao_inicial
    
    # 1. Abrir como "r+b" para leitura e escrita
    if f_hash.closed:
        print("Erro! Passe um arquivo aberto como 'rb+' !")
    else:
        while True:
            # 2. Ir até a posição que deve ser removida
            f_hash.seek(posicao * ctypes.sizeof(models.RegistroHash))
            # 3. Ler da posição
            buffer = f_hash.read(ctypes.sizeof(models.RegistroHash))
            registro = models.RegistroHash.from_buffer_copy(buffer)
            
            if registro.estado == 0:
                # 4. Chegou num vazio, a chave não existe
                print(f"Erro: Chave {chave_busca} não encontrada para remoção.")
                return False
            
            if registro.estado == 1 and registro.cod_chave == chave_busca:
                # 5. Encontrado!
                registro.estado = 2 # Marca como Removido
                
                # 6. Volta para o começo do registro e grava a alteração
                f_hash.seek(posicao * ctypes.sizeof(models.RegistroHash))
                f_hash.write(registro)
                print(f"Sucesso: Chave {chave_busca} removida (Lápide criada).")
                return True
            
            # 7. Colisão: tenta o próximo
            posicao += 1
            if posicao >= models.TAMANHO_HASH_TABLE:
                posicao = 0
            
            if posicao == posicao_inicial:
                print("Erro: Tabela varrida completamente e chave não encontrada.")
                return False
            
    # 1. Abrir como "r+b" para leitura e escrita
    # 2. Ir até a posição que deve ser removida
    # 3. Ler da posição
    # 4. Se chegou num vazio, a chave não existe
    # 5. Se encontrado, marca como removido
    # 6. Volta para o começo do registro e grava a alteração
    # 7. Se colisão, tenta o próximo