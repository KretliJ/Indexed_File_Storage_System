import ctypes
import math
import os

# --- ESTRUTURAS ---

class Funcionario(ctypes.Structure):
    _fields_ = [
        ("cod", ctypes.c_int),
        ("nome", ctypes.c_char * 50),
        ("cpf", ctypes.c_char * 15),
        ("data_nascimento", ctypes.c_char * 11),
        ("salario", ctypes.c_double),
    ]

    def __init__(self, cod=0, nome='', cpf='', data_nascimento='', salario=0.0):
        super().__init__()
        self.cod = cod
        self.nome = nome.encode('utf-8')
        self.cpf = cpf.encode('utf-8')
        self.data_nascimento = data_nascimento.encode('utf-8')
        self.salario = salario

    def __str__(self):
        return (f"ID: {self.cod} | Nome: {self.nome.decode('utf-8').strip()}")

    def __lt__(self, other):
        return self.cod < other.cod

    def __eq__(self, other):
        return self.cod == other.cod
    
class Paciente(ctypes.Structure):
    _fields_ = [
        ("cod_paciente", ctypes.c_int),
        ("nome", ctypes.c_char * 50),
        ("cpf", ctypes.c_char * 15),
        ("data_nascimento", ctypes.c_char * 11),
        ("endereco", ctypes.c_char * 50)
    ]

    def __init__(self, cod=0, nome='', cpf='', data_nascimento='', endereco=''):
        super().__init__()
        self.cod_paciente = cod 
        self.nome = nome.encode('utf-8')
        self.cpf = cpf.encode('utf-8')
        self.data_nascimento = data_nascimento.encode('utf-8')
        self.endereco = endereco.encode('utf-8')

    def __str__(self):
        return (f"ID: {self.cod_paciente} | Nome: {self.nome.decode('utf-8').strip()}")

    def __lt__(self, other):
        return self.cod_paciente < other.cod_paciente

    def __eq__(self, other):
        return self.cod_paciente == other.cod_paciente
    
class Vacina(ctypes.Structure):
    _fields_ = [
        ("cod_vacina", ctypes.c_int),
        ("nome_fabricante", ctypes.c_char * 50),
        ("lote", ctypes.c_char * 20),
        ("data_validade", ctypes.c_char * 11),
        ("descricao", ctypes.c_char * 50)
    ]

    def __init__(self, cod=0, nome_fabricante='', lote='', data_validade='', descricao=''):
        super().__init__()
        self.cod_vacina = cod 
        self.nome_fabricante = nome_fabricante.encode('utf-8')
        self.lote = lote.encode('utf-8')
        self.data_validade = data_validade.encode('utf-8')
        self.descricao = descricao.encode('utf-8')

    def __str__(self):
        return (f"ID: {self.cod_vacina} | Fab: {self.nome_fabricante.decode('utf-8').strip()}")
    
    def __lt__(self, other):
        return self.cod_vacina < other.cod_vacina

    def __eq__(self, other):
        return self.cod_vacina == other.cod_vacina
    
class AplicacaoVacina(ctypes.Structure):
    _fields_ = [
        ("cod_aplicacao", ctypes.c_int),
        ("cod_paciente_fk", ctypes.c_int),
        ("cod_vacina_fk", ctypes.c_int),
        ("cod_funcionario_fk", ctypes.c_int),
        ("data_aplicacao", ctypes.c_char * 11),
    ]

    def __init__(self, cod=0, cod_pac=0, cod_vac=0, cod_func=0, data=''):
        super().__init__()
        self.cod_aplicacao = cod
        self.cod_paciente_fk = cod_pac
        self.cod_vacina_fk = cod_vac
        self.cod_funcionario_fk = cod_func
        self.data_aplicacao = data.encode('utf-8')

    def __str__(self):
        return (f"ID App: {self.cod_aplicacao} | Pac: {self.cod_paciente_fk} | Vac: {self.cod_vacina_fk}")
    
    def __lt__(self, other):
        return self.cod_aplicacao < other.cod_aplicacao

    def __eq__(self, other):
        return self.cod_aplicacao == other.cod_aplicacao

class RegistroHash(ctypes.Structure):
    _fields_ = [
        ("cod_chave", ctypes.c_int),      # Chave de busca (ID da aplicação)
        ("endereco_dados", ctypes.c_int), # Índice físico no arquivo .dat (0, 1, 2...)
        ("estado", ctypes.c_int)          # 0=Livre, 1=Ocupado, 2=Removido
    ]

def is_prime(n):
    # Checa se um número é primo
    if n <= 1:
        return False
    # Checa para fatores até raíz de n
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def find_closest_prime(n):
    # Encontra o primo mais próximo de n

    if is_prime(n):
        return n

    # Busca para maior que n
    for i in range(1, n):
        higher = n + i
        
        if is_prime(higher):
            return higher

class Header(ctypes.Structure):
    _fields_ = [
        ("topo_pilha", ctypes.c_int) # Armazena o índice do último registro removido
    ]

def inicializar_header():
    # Cria o arquivo header com a pilha vazia (-1)
    if not os.path.exists(FILE_HEADER):
        print("Inicializando Header da Pilha de Excluídos...")
        h = Header(topo=-1)
        with open(FILE_HEADER, "wb") as f:
            f.write(h)

# --- CONSTANTES ---

RECORD_SIZE_FUNC = ctypes.sizeof(Funcionario)
RECORD_SIZE_PAC = ctypes.sizeof(Paciente)
RECORD_SIZE_VAC = ctypes.sizeof(Vacina)
RECORD_SIZE_APLIC = ctypes.sizeof(AplicacaoVacina)

FILE_PATH = "files"
LOGS_PATH = "Logs"

# Garante diretórios
os.makedirs(FILE_PATH, exist_ok=True)
os.makedirs(LOGS_PATH, exist_ok=True)

# 1. Caminho da base
# 2. Tamanho da base em registros

FILE_FUNCIONARIOS = os.path.join(FILE_PATH, "funcionarios.dat")
FILE_FUNCIONARIOS_SIZE = 50

FILE_PACIENTES = os.path.join(FILE_PATH, "pacientes.dat")
FILE_PACIENTES_SIZE = 100

FILE_VACINAS = os.path.join(FILE_PATH, "vacinas.dat")
FILE_VACINAS_SIZE = 20

FILE_APLICACOES = os.path.join(FILE_PATH, "aplicacoes.dat")
FILE_APLICACOES_SIZE = 100

FILE_HASH = os.path.join(FILE_PATH, "aplicacoes_hash.dat")
# Primo próximo ao dobro do tamanho de aplicacoes.dat (para evitar muitas colisões)
TAMANHO_HASH_TABLE = find_closest_prime(2*FILE_APLICACOES_SIZE)

FILE_HEADER = os.path.join(FILE_PATH, "header.dat")

LOG_DUMP = os.path.join(LOGS_PATH, "dump_base.txt")