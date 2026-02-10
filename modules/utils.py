import ctypes
import random
import os
from . import models
from . import utils_parte3

# --- DADOS MOCK ---
NOMES = ["Ana", "Carlos", "Bruno", "Daniela", "Eduardo", "Fernanda", "Gabriel", "Helena"]
VACINAS = ["Pfizer", "Coronavac", "AstraZeneca", "Janssen"]

# --- FUNÇÃO GENÉRICA DE EXPORTAÇÃO (PRINT) ---

def exportar_base_para_log(arquivo_bin, struct_class, titulo):
    """Lê um arquivo binário sequencialmente e escreve o __str__ no log txt."""
    
    tamanho_registro = ctypes.sizeof(struct_class)
    
    print(f"Exportando {titulo} para {models.LOG_DUMP}...")
    
    try:
        with open(arquivo_bin, "rb") as f_in, open(models.LOG_DUMP, "a", encoding="utf-8") as f_log:
            f_log.write(f"\n{'='*40}\nRELATÓRIO: {titulo}\n{'='*40}\n")
            
            contador = 0
            while True:
                buffer = f_in.read(tamanho_registro)
                if not buffer:
                    break
                
                registro = struct_class.from_buffer_copy(buffer)
                f_log.write(str(registro) + "\n")
                contador += 1
            
            f_log.write(f"\nTotal de registros: {contador}\n")
            print(f"-> Sucesso. {contador} registros exportados.")
            
    except FileNotFoundError:
        print(f"Erro: Arquivo {arquivo_bin} não encontrado.")

# --- FUNÇÕES DE CRIAÇÃO DA BASE (POPULATE) ---

def gerar_base_funcionarios():
    print(f"Gerando {models.FILE_FUNCIONARIOS_SIZE} Funcionários...")
    with open(models.FILE_FUNCIONARIOS, "wb") as f:
        for i in range(1, models.FILE_FUNCIONARIOS_SIZE + 1):
            func = models.Funcionario(
                cod=i,
                nome=random.choice(NOMES),
                cpf=f"{random.randint(100,999)}.000.000-00",
                data_nascimento="01/01/1990",
                salario=random.uniform(2000, 5000)
            )
            f.write(func)

def gerar_base_pacientes():
    print(f"Gerando {models.FILE_PACIENTES_SIZE} Pacientes...")
    with open(models.FILE_PACIENTES, "wb") as f:
        for i in range(1, models.FILE_PACIENTES_SIZE + 1):
            pac = models.Paciente(
                cod=i,
                nome=random.choice(NOMES),
                cpf=f"{random.randint(100,999)}.111.222-33",
                data_nascimento="15/05/1985",
                endereco="Rua Exemplo, 123"
            )
            f.write(pac)

def gerar_base_vacinas():
    print(f"Gerando {models.FILE_VACINAS_SIZE} Vacinas...")
    with open(models.FILE_VACINAS, "wb") as f:
        for i in range(1, models.FILE_VACINAS_SIZE + 1):
            vac = models.Vacina(
                cod=i,
                nome_fabricante=random.choice(VACINAS),
                lote=f"LOTE-{random.randint(1000,9999)}",
                data_validade="31/12/2030",
                descricao="Vacina Viral"
            )
            f.write(vac)

def gerar_base_aplicacoes():
    # Requer que as outras bases existam para simular FKs validas (opcional, aqui é aleatorio)
    # * = Diferenças desta função para a da parte II
    print(f"Gerando {models.FILE_APLICACOES_SIZE} Aplicações...")
    # * inicialização do hashmap
    utils_parte3.inicializar_hash_vazia()
    with open(models.FILE_APLICACOES, "wb") as f:
        # * abertura do arquivo de hashmap
        with open(models.FILE_HASH, "rb+") as f_hash:
            for i in range(1, models.FILE_APLICACOES_SIZE + 1):
                app = models.AplicacaoVacina(
                    cod=i,
                    cod_pac=random.randint(1, 100),
                    cod_vac=random.randint(1, 20),
                    cod_func=random.randint(1, 100),
                    data="20/01/2026"
                )
                f.write(app)
                # * criar a base de aplicações também gera seu hashmap
                utils_parte3.inserir_na_hash(i, i-1, f_hash)

# Função Wrapper para rodar tudo
def recriar_bases():
    if os.path.isfile(models.FILE_APLICACOES):
        print("Erro: As bases já existem!")
    else:    
        # Limpa log antigo
        if os.path.exists(models.LOG_DUMP):
            os.remove(models.LOG_DUMP)

        # Gera Binários
        gerar_base_funcionarios()
        gerar_base_pacientes()
        gerar_base_vacinas()
        gerar_base_aplicacoes()

        # Gera header
        models.inicializar_header()
        # Imprime no Log
        exportar_base_para_log(models.FILE_FUNCIONARIOS, models.Funcionario, "FUNCIONÁRIOS")
        exportar_base_para_log(models.FILE_PACIENTES, models.Paciente, "PACIENTES")
        exportar_base_para_log(models.FILE_VACINAS, models.Vacina, "VACINAS")
        exportar_base_para_log(models.FILE_APLICACOES, models.AplicacaoVacina, "APLICAÇÕES")

# ================================================================================
#                                   NOVAS FUNÇÕES 
# ================================================================================

def inserir_aplicacao(nova_app):
    # Insere uma aplicação gerenciando manualmente o Header de espaços vazios.
    
    print(f"--- Inserindo Aplicação ID {nova_app.cod_aplicacao} ---")
    
    # 0. Garante que o Header existe (criação manual se não existir)
    if not os.path.exists(models.FILE_HEADER):
        with open(models.FILE_HEADER, "wb") as f_criacao:
            h_init = models.Header(topo_pilha=-1)
            f_criacao.write(h_init)

    endereco_final = -1

    # 1. Abrir e Ler o Header
    # "rb+" pois pode precisar atualizar o topo depois
    with open(models.FILE_HEADER, "rb+") as f_header:
        # Ler o que há no header
        f_header.seek(0)
        header = models.Header.from_buffer_copy(f_header.read(ctypes.sizeof(models.Header)))
        
        # 2. Verificar se há espaço na Pilha de Excluídos
        # se header for -1, ignora e escreve no fim
        if header.topo_pilha != -1:
            print(f"-> Header aponta para índice {header.topo_pilha}. Reutilizando espaço...")
            
            # --- Lógica de reutilização - pop no stack ---
            endereco_reutilizado = header.topo_pilha
            
            with open(models.FILE_APLICACOES, "rb+") as f_dados:
                # 3. Abrir arquivo de aplicações e ir até o registro que será sobrescrito
                offset = endereco_reutilizado * models.RECORD_SIZE_APLIC
                f_dados.seek(offset)
                
                # 4. Ler o ponteiro para o próximo
                # O registro antigo guarda no campo 'cod_aplicacao' o próximo índice livre
                buffer_lixo = f_dados.read(models.RECORD_SIZE_APLIC)
                registro_lixo = models.AplicacaoVacina.from_buffer_copy(buffer_lixo)
                proximo_na_pilha = registro_lixo.cod_aplicacao
                
                # Mudança vs lógica do desafio 5: O registro é propositalmente tratado como lixo 
                # porque se o header aponta para cá, sabe-se que é lixo
                
                # Logo, se lê o código que estaria na estrutura "AplicacaoVacina" e o trata como o "endereçamento" do próximo bloco livre
                # Isso continua até que o cod_aplicacao seja "-1"

                # 5. Sobrescrever com o novo dado
                f_dados.seek(offset)
                f_dados.write(nova_app)
            
            # 6. Devolver ao header o que havia no registro
            header.topo_pilha = proximo_na_pilha
            
            # Atualiza o arquivo header fisicamente
            f_header.seek(0)
            f_header.write(header)
            
            # 7. Endereço para inserção encontrado
            endereco_final = endereco_reutilizado

        else:
            print("-> Header indica pilha vazia (-1). Inserindo no final (Append)...")
            
            # --- Lógida de append ao EOF Padrão ---
            with open(models.FILE_APLICACOES, "ab") as f_dados_append:
                # Pega a posição atual (fim do arquivo) para saber o índice
                f_dados_append.seek(0, 2) # Fim
                bytes_total = f_dados_append.tell()
                endereco_final = bytes_total // models.RECORD_SIZE_APLIC
                
                f_dados_append.write(nova_app)
                # O header não muda aqui, continua -1

    # 8. Atualizar a Tabela Hash
    # Chave -> Novo Endereço Físico
    if endereco_final != -1:
        print(f"-> Atualizando Hash: Chave {nova_app.cod_aplicacao} -> Endereço {endereco_final}")
        with open(models.FILE_HASH, "rb+") as f_hash:
            # A chave permanece a mesma que existia antes
            utils_parte3.inserir_na_hash(nova_app.cod_aplicacao, endereco_final, f_hash)

    # --- FLUXO DE INSERÇÃO ---
    # 1. Abrir e Ler o Header
    # 2. Verificar se há espaço na Pilha de Excluídos
    # 3. Abrir arquivo de aplicações e ir até o registro que será sobrescrito
    # 4. Ler o ponteiro para o próximo
    # 5. Sobrescrever com o novo dado
    # 6. Devolver ao header o que havia no registro
    # 7. Endereço para inserção encontrado
    # 8. Atualizar a Tabela Hash


# Retorna None se não existe
def buscar_aplicacao(id_busca):
    print(f"--- Iniciando busca pelo ID: {id_busca} ---")
    
    endereco_fisico_encontrado = -1

    # 1. Abre o arquivo de hash para consulta
    with open(models.FILE_HASH, "rb") as f_hash:
        # 2. Delega a lógica de busca (Linear Probing/Estados) para a função interna
        # A função já retorna o endereço físico ou -1 se não encontrar
        endereco_fisico_encontrado = utils_parte3.buscar_na_hash(id_busca, f_hash)

    # 3. Verifica se o endereço físico foi encontrado
    if endereco_fisico_encontrado != -1:
        print(f"-> Registro encontrado! Endereço físico: {endereco_fisico_encontrado}")
        
        # 4. Acesso Direto ao Arquivo de Dados (Seek Direto)
        with open(models.FILE_APLICACOES, "rb") as f_dados:
            # 5. Calcula o deslocamento (offset) baseado no endereço recuperado
            offset_dados = endereco_fisico_encontrado * ctypes.sizeof(models.AplicacaoVacina)
            f_dados.seek(offset_dados)
            
            # 6. Lê e reconstrói o objeto AplicacaoVacina
            buffer_dados = f_dados.read(ctypes.sizeof(models.AplicacaoVacina))
            if buffer_dados:
                return models.AplicacaoVacina.from_buffer_copy(buffer_dados)
    
    print(f"-> ID {id_busca} não localizado na base de dados.")
    return None

# --- FLUXO DA FUNÇÃO ---
# 1. Abre arquivo de hash
# 2. Delega busca para buscar_na_hash()
# 3. Recebe o endereço físico (ou -1)
# 4. Se encontrou, abre o arquivo de aplicações
# 5. Realiza o seek direto no endereço físico
# 6. Retorna o objeto encontrado

def remover_aplicacao(id_busca):
    print(f"--- Iniciando remoção do ID: {id_busca} ---")
    
    # 1. Localizar o endereço físico antes de remover do hash
    # Precisa saber onde o dado está no .dat para poder marcar como livre
    endereco_fisico = -1
    with open(models.FILE_HASH, "rb") as f_hash_leitura:
        # busca pelo proprio hashmap
        endereco_fisico = utils_parte3.buscar_na_hash(id_busca, f_hash_leitura)
    
    if endereco_fisico == -1:
        print(f"Erro: ID {id_busca} não encontrado na base.")
        return False

    # 2. Atualizar o Hashmap
    # Abre o hashmap em modo de escrita para usar a função remover_da_hash
    with open(models.FILE_HASH, "rb+") as f_hash_escrita:
        sucesso_hash = utils_parte3.remover_da_hash(id_busca, f_hash_escrita)
    
    if not sucesso_hash:
        return False

    # 3. Gerenciamento de Espaço (Pilha de Excluídos)
    # Rrealizar o Push deste endereço na pilha de vazios
    
    # 4. Abrir o Header para pegar o topo atual
    if not os.path.exists(models.FILE_HEADER):
        with open(models.FILE_HEADER, "wb") as f_init:
            f_init.write(models.Header(topo_pilha=-1))

    with open(models.FILE_HEADER, "rb+") as f_header:
        f_header.seek(0)
        header = models.Header.from_buffer_copy(f_header.read(ctypes.sizeof(models.Header)))
        topo_antigo = header.topo_pilha
        
        # 5. Ir ao arquivo de aplicações e transformar o registro em um "nó" da pilha
        with open(models.FILE_APLICACOES, "rb+") as f_dados:
            offset = endereco_fisico * ctypes.sizeof(models.AplicacaoVacina)
            f_dados.seek(offset)
            
            # 6. Criar um registro vazio onde o ID armazena o "endereço" para o próximo buraco
            registro_vazio = models.AplicacaoVacina()
            registro_vazio.cod_aplicacao = topo_antigo # O campo cod vira o ponteiro de endereço
            registro_vazio.cod_funcionario_fk = 0
            registro_vazio.cod_paciente_fk = 0
            registro_vazio.cod_vacina_fk = 0
            # Zera todos os registros para identificar que é um registro vazio
            
            f_dados.write(registro_vazio)
            
        # 7. Atualizar o Header para que o novo buraco seja o topo
        header.topo_pilha = endereco_fisico
        f_header.seek(0)
        f_header.write(header)

    print(f"-> Sucesso: Espaço no índice {endereco_fisico} liberado e adicionado à pilha.")
    return True

# --- FLUXO DE REMOÇÃO ---
# 1. Localizar o endereço físico antes de remover do hash
# 2. Atualizar o Hashmap
# 3. Gerenciamento de Espaço (Pilha de Excluídos)
# 4. Abrir o Header para pegar o topo atual
# 5. Ir ao arquivo de aplicações e transformar o registro em um "nó" da pilha
# 6. Criar um registro vazio onde o ID armazena o "endereço" para o próximo buraco
# 7. Atualizar o Header para que o novo buraco seja o topo

