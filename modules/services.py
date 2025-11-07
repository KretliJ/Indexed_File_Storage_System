import time
import os

from . import data_access
from . import utils
from .models import * 

# APLICAÇÃO DE VACINA

def registrar_aplicacao_sem_ordenar(paciente_id: int, vacina_id: int, funcionario_id: int, data_aplicacao: str):
 
    try:
        # USA O LOGGER DO 'UTILS'
        utils._log_operacao(f"Tentativa de aplicação: PAC={paciente_id}, VAC={vacina_id}, FUNC={funcionario_id}")
        
        # VERIFICAR SE AS ENTIDADES EXISTEM
        paciente = data_access.bin_seek_por_cod(FILE_PACIENTES, RECORD_SIZE_PAC, Paciente, paciente_id)
        if not paciente:
            msg = f"Falha: Paciente com ID {paciente_id} não encontrado."
            utils._log_operacao(msg, "ERRO")
            return (False, msg)

        vacina = data_access.bin_seek_por_cod(FILE_VACINAS, RECORD_SIZE_VAC, Vacina, vacina_id)
        if not vacina:
            msg = f"Falha: Vacina com ID {vacina_id} não encontrada."
            utils._log_operacao(msg, "ERRO")
            return (False, msg)

        func = data_access.bin_seek_por_cod(FILE_FUNCIONARIOS, RECORD_SIZE_FUNC, Funcionario, funcionario_id)
        if not func:
            msg = f"Falha: Funcionário com ID {funcionario_id} não encontrado."
            utils._log_operacao(msg, "ERRO")
            return (False, msg)

        # CRIAR O NOVO REGISTRO DE RELACIONAMENTO
        novo_id_aplicacao = data_access.get_next_id(FILE_APLICACOES, RECORD_SIZE_APLIC, AplicacaoVacina)
        
        nova_aplicacao = AplicacaoVacina(
            cod_aplicacao=novo_id_aplicacao,
            cod_paciente_fk=paciente_id,
            cod_vacina_fk=vacina_id,
            cod_funcionario_fk=funcionario_id,
            data_aplicacao=data_aplicacao.encode('utf-8')
        )

        # ADICIONAR O REGISTRO
        if data_access.adicionar_registro(FILE_APLICACOES, nova_aplicacao):
            msg = f"Sucesso: Aplicação {novo_id_aplicacao} registrada. (Arquivo {FILE_APLICACOES} agora desordenado)."
            utils._log_operacao(msg, "INFO")
            # Invalida o índice
            _invalidar_indice_paciente()
            return (True, msg)
        else:
            msg = f"Falha: Erro ao salvar aplicação {novo_id_aplicacao} no disco."
            utils._log_operacao(msg, "ERRO")
            return (False, msg)

    except Exception as e:
        utils._log_operacao(f"Erro inesperado em registrar_aplicacao: {e}", "CRÍTICO")
        return (False, f"Erro inesperado: {e}")

def _invalidar_indice_paciente():

    try:
        if os.path.exists(FILE_IDX_PACIENTE_APLIC):
            os.rename(FILE_IDX_PACIENTE_APLIC, FILE_IDX_PACIENTE_APLIC + ".invalid")
            utils._log_operacao(f"Índice '{FILE_IDX_PACIENTE_APLIC}' invalidado (requer reconstrução).", "AVISO")
    except Exception as e:
        utils._log_operacao(f"Falha ao invalidar índice '{FILE_IDX_PACIENTE_APLIC}': {e}", "ERRO")

# GERAÇÃO DE CARTÃO

def gerar_cartao_paciente(paciente_id: int):

    # Gera um arquivo 'cartao_paciente.txt' para um paciente específico

    utils._log_operacao(f"Iniciando geração de cartão para PACIENTE ID={paciente_id}.")
    
    # Verifica se o índice é válido
    if not os.path.exists(FILE_IDX_PACIENTE_APLIC):
        msg = f"Falha ao gerar cartão: O índice '{FILE_IDX_PACIENTE_APLIC}' não existe ou está inválido. Reconstrua o índice."
        print(msg)
        utils._log_operacao(msg, "ERRO")
        return False, msg

    # Busca pelo Paciente
    paciente = data_access.bin_seek_por_cod(FILE_PACIENTES, RECORD_SIZE_PAC, Paciente, paciente_id)
    if not paciente:
        msg = f"Falha: Paciente com ID {paciente_id} não encontrado."
        utils._log_operacao(msg, "ERRO")
        return False, msg

    nome_paciente = paciente.nome.decode('utf-8').strip('\\x00')
    
    # Busca Rápida no índice
    aplicacoes_ids = data_access.bin_seek_all_matches_in_index(
        FILE_IDX_PACIENTE_APLIC, 
        RECORD_SIZE_IDX_PAC, 
        IndicePacienteAplicacao,
        paciente_id
    )

    if not aplicacoes_ids:
        msg = f"Nenhuma aplicação encontrada para o paciente {nome_paciente} (ID {paciente_id})."
        utils._log_operacao(msg, "INFO")
        # Cria um cartão vazio
        with open(CARTAO_PATH, "w", encoding="utf-8") as f_cartao:
            f_cartao.write(f"CARTÃO DE VACINAÇÃO\n")
            f_cartao.write("========================================\n")
            f_cartao.write(f"Paciente: {nome_paciente} (ID: {paciente_id})\n")
            f_cartao.write("\nNENHUMA APLICAÇÃO REGISTRADA.\n")
        return True, msg

    # Gerar o arquivo de cartão .txt
    try:
        total_apps = 0
        with open(CARTAO_PATH, "w", encoding="utf-8") as f_cartao:
            f_cartao.write(f"CARTÃO DE VACINAÇÃO\n")
            f_cartao.write("========================================\n")
            f_cartao.write(f"Paciente: {nome_paciente} (ID: {paciente_id})\n")
            f_cartao.write("========================================\n\n")
            
            # Para cada ID de aplicação encontrado
            for app_id in aplicacoes_ids:
                # Pula direto para o registro no arquivo principal
                aplicacao = data_access.bin_seek_por_cod(
                    FILE_APLICACOES, RECORD_SIZE_APLIC, AplicacaoVacina, app_id
                )
                
                if aplicacao:
                    # Busca os nomes para o cartão
                    vacina = data_access.bin_seek_por_cod(
                        FILE_VACINAS, RECORD_SIZE_VAC, Vacina, aplicacao.cod_vacina_fk
                    )
                    func = data_access.bin_seek_por_cod(
                        FILE_FUNCIONARIOS, RECORD_SIZE_FUNC, Funcionario, aplicacao.cod_funcionario_fk
                    )
                    
                    # Formata a saída
                    data_str = aplicacao.data_aplicacao.decode('utf-8').strip('\\x00')
                    
                    vac_str = vacina.nome_fabricante.decode('utf-8').strip('\\x00') if vacina else "Vacina Desconhecida"
                    
                    lote_str = vacina.lote.decode('utf-8').strip('\\x00') if vacina and vacina.lote else ""
                    f_cartao.write(f"Data: {data_str}\n")
                    f_cartao.write(f"   Vacina: {vac_str} (Lote: {lote_str})\n")
                    
                    func_str = func.nome.decode('utf-8').strip('\\x00') if func else "Funcionário Desconhecido"
                    f_cartao.write(f"   Aplicada por: {func_str}\n\n")
                    total_apps += 1
            
            f_cartao.write("========================================\n")
            f_cartao.write(f"Total de aplicações: {total_apps}\n")

        msg = f"Cartão do paciente {nome_paciente} (ID {paciente_id}) gerado com sucesso ({total_apps} aplicações)."
        utils._log_operacao(msg, "INFO")
        return True, msg

    except Exception as e:
        msg = f"Erro ao gerar cartão para paciente ID {paciente_id}: {e}"
        utils._log_operacao(msg, "CRÍTICO")
        return False, msg