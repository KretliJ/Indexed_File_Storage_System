import data_access
import utils
from models import Funcionario, Paciente, Vacina, AplicacaoVacina, RECORD_SIZE_FUNC, RECORD_SIZE_PAC, RECORD_SIZE_VAC, RECORD_SIZE_APLIC
import time # Importa 'time' para os timestamps do log

# Define os arquivos "principais"
FILE_PACIENTES = "pacientes.dat"
FILE_VACINAS = "vacinas.dat"
FILE_FUNCIONARIOS = "funcionarios.dat"
FILE_APLICACOES = "aplicacoes.dat"

# Define o nome do arquivo de log
OPERATION_LOG_FILE = "operation_log.txt"

def _log_operacao(mensagem: str, status: str = "INFO"):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] [{status}] - {mensagem}\n"
    
    try:
        with open(OPERATION_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"ALERTA CRÍTICO: Falha ao escrever no log '{OPERATION_LOG_FILE}': {e}")
        print(f"MENSAGEM DE LOG PERDIDA: {log_entry}")

# LÓGICA DE NEGÓCIO

def aplicar_nova_vacina(paciente_id: int, vacina_id: int, funcionario_id: int, data_aplicacao: str):

    log_msg_inicio = f"Iniciando tentativa de aplicação: Paciente ID={paciente_id}, Vacina ID={vacina_id}, Funcionario ID={funcionario_id}."
    _log_operacao(log_msg_inicio)
    print(f"Registrando aplicação para paciente {paciente_id}...")
    
    # Verifica
    paciente = data_access.bin_seek_por_cod(FILE_PACIENTES, RECORD_SIZE_PAC, Paciente, paciente_id)
    if not paciente:
        # Loga a falha
        mensagem_erro = f"Falha na aplicação: Paciente com ID {paciente_id} não encontrado."
        _log_operacao(mensagem_erro, "ERRO")
        print(mensagem_erro)
        return

    vacina = data_access.bin_seek_por_cod(FILE_VACINAS, RECORD_SIZE_VAC, Vacina, vacina_id)
    if not vacina:
        # Loga a falha
        mensagem_erro = f"Falha na aplicação: Vacina com ID {vacina_id} não encontrada."
        _log_operacao(mensagem_erro, "ERRO")
        print(mensagem_erro)
        return
        
    funcionario = data_access.bin_seek_por_cod(FILE_FUNCIONARIOS, RECORD_SIZE_FUNC, Funcionario, funcionario_id)
    if not funcionario:
        # Loga a falha
        mensagem_erro = f"Falha na aplicação: Funcionário com ID {funcionario_id} não encontrado."
        _log_operacao(mensagem_erro, "ERRO")
        print(mensagem_erro)
        return

    # Criar novo registro
    novo_id_aplicacao = data_access.get_next_id(FILE_APLICACOES, RECORD_SIZE_APLIC, AplicacaoVacina) 
    
    nova_aplicacao = AplicacaoVacina(
        cod_aplicacao=novo_id_aplicacao,
        cod_paciente_fk=paciente_id,
        cod_vacina_fk=vacina_id,
        cod_funcionario_fk=funcionario_id,
        data_aplicacao=data_aplicacao
    )

    # Adicionar o registro
    data_access.adicionar_registro(FILE_APLICACOES, nova_aplicacao)
    _log_operacao(f"Aplicação ID {novo_id_aplicacao} registrada em '{FILE_APLICACOES}'. Arquivo agora está desordenado.")
    
    # Reordenar o arquivo
    print("O arquivo de aplicações está desordenado. Reordenando...")
    _log_operacao(f"Iniciando reordenação (mergesort) de '{FILE_APLICACOES}'...")
    
    utils.mergesort_file(FILE_APLICACOES, RECORD_SIZE_APLIC, 10000) 
    
    # Loga o sucesso final
    _log_operacao(f"Operação concluída: Arquivo '{FILE_APLICACOES}' reordenado. Aplicação ID {novo_id_aplicacao} finalizada.")
    print("Aplicação de vacina registrada e arquivo reordenado com sucesso.")

# TODO: (adicionar outras funções de serviço aqui como 'cadastrar_novo_paciente')
# adicionar chamadas a _log_operacao() nelas também.

