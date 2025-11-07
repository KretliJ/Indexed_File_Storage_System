import ctypes

class Funcionario(ctypes.Structure):
    # Estrutura ctypes que mapeia diretamente a structs em C
    _fields_ = [
        ("cod", ctypes.c_int),
        ("nome", ctypes.c_char * 50),
        ("cpf", ctypes.c_char * 15),
        ("data_nascimento", ctypes.c_char * 11),
        ("salario", ctypes.c_double),
    ]

    # Equivalente de 'funcionario()'
    def __init__(self, cod=0, nome='', cpf='', data_nascimento='', salario=0.0):
        super().__init__()
        self.cod = cod
        # Strings devem ser codificadas em bytes para caber num array c_char
        self.nome = nome.encode('utf-8')
        self.cpf = cpf.encode('utf-8')
        self.data_nascimento = data_nascimento.encode('utf-8')
        self.salario = salario

    # Equivalente de 'imprime()'
    def __str__(self):
        # Cria representação formatada para funcionario
        # Decodifica as strings para imprimir
        nome_str = self.nome.decode('utf-8').strip('\\x00')
        cpf_str = self.cpf.decode('utf-8').strip('\\x00')
        data_str = self.data_nascimento.decode('utf-8').strip('\\x00')
        
        return (f"**********************************************\n"
                f"Funcionario de codigo {self.cod}\n"
                f"Nome: {nome_str}\n"
                f"CPF: {cpf_str}\n"
                f"Data de Nascimento: {data_str}\n"
                f"Salario: {self.salario:4.2f}\n")
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

    # Equivalente de 'imprime()'
    def __str__(self):
        # Cria representação formatada para funcionario
        # Decodifica as strings para imprimir
        nome_str = self.nome.decode('utf-8').strip('\\x00')
        cpf_str = self.cpf.decode('utf-8').strip('\\x00')
        data_str = self.data_nascimento.decode('utf-8').strip('\\x00')
        endereco_str = self.endereco.decode('utf-8').strip('\\x00')
        
        return (f"**********************************************\n"
                f"Paciente de codigo {self.cod}\n"
                f"Nome: {nome_str}\n"
                f"CPF: {cpf_str}\n"
                f"Data de Nascimento: {data_str}\n"
                f"Endereço: {endereco_str}\n")
    def __lt__(self, other):
        return self.cod < other.cod
    def __eq__(self, other):
        return self.cod == other.cod

class Vacina(ctypes.Structure):
    _fields_ = [
        ("cod_vacina", ctypes.c_int),
        ("nome_fabricante", ctypes.c_char * 50),
        ("lote", ctypes.c_char * 20),
        ("data_validade", ctypes.c_char * 11),
        ("descricao", ctypes.c_char * 50)
    ]
    def __init__(self, cod=0, nome_fabricante='', lote='', data_validade='', descricao=''):
        self.cod_vacina = cod 
        self.nome_fabricante = nome_fabricante.encode('utf-8')
        self.lote = lote.encode('utf-8')
        self.data_validade = data_validade.encode('utf-8')
        self.descricao = descricao.encode('utf-8')

    # Equivalente de 'imprime()'
    def __str__(self):
        # Cria representação formatada para funcionario
        # Decodifica as strings para imprimir
        nome_str = self.nome_fabricante.decode('utf-8').strip('\\x00')
        lote_str = self.lote.decode('utf-8').strip('\\x00')
        data_str = self.data_validade.decode('utf-8').strip('\\x00')
        descricao_str = self.descricao.decode('utf-8').strip('\\x00')
    
        return (f"**********************************************\n"
                f"Vacina de codigo {self.cod}\n"
                f"Nome: {nome_str}\n"
                f"Lote: {lote_str}\n"
                f"Data de validade: {data_str}\n"
                f"Descrição: {descricao_str}\n")
    def __lt__(self, other):
        return self.cod < other.cod
    def __eq__(self, other):
        return self.cod == other.cod


class AplicacaoVacina(ctypes.Structure):

    _fields_ = [
        ("cod_aplicacao", ctypes.c_int), # Chave primária
        ("cod_paciente_fk", ctypes.c_int), # Chave estrangeira
        ("cod_vacina_fk", ctypes.c_int),   # Chave estrangeira
        ("cod_funcionario_fk", ctypes.c_int),# Chave estrangeira
        ("data_aplicacao", ctypes.c_char * 11),
    ]

RECORD_SIZE_FUNC = ctypes.sizeof(Funcionario)
RECORD_SIZE_PAC = ctypes.sizeof(Paciente)
