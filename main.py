import os
from modules import utils
from modules import models
import random
from modules import utils_parte3

# PONTO DE ENTRADA

if __name__ == "__main__":

    arquivos_para_limpar = [
        models.FILE_APLICACOES,
        models.FILE_FUNCIONARIOS,
        models.FILE_PACIENTES,
        models.FILE_VACINAS,
        models.FILE_HASH,
        models.FILE_HEADER
    ]

    recriarBases = 0

    for arquivo in arquivos_para_limpar:
        if os.path.exists(arquivo):
            recriarBases += 1
            try:
                os.remove(arquivo)
                print(f"-> Removido: {arquivo}")
            except Exception as e:
                print(f"-> Erro ao remover {arquivo}: {e}")
    
    if recriarBases > 0:
        print("Registros removidos com sucesso. Reiniciando")
        utils.recriar_bases()
    else:  
        utils.recriar_bases()  



# Buscar 15 registros escolhidos em aleatorio e mostrar na tela
    print("=" * 80 + f"\n\nTamanho inicial da base: {models.FILE_APLICACOES_SIZE} registros.")

    # Apagar 50 registros escolhidos em aleatorio. Mostrar tamanho antes e depois da exclusão.
    ids_para_remover = random.sample(range(1, models.FILE_APLICACOES_SIZE + 1), 50)
    
    print(f"\nRemovendo 50 registros aleatórios...\n\n" + "=" * 80)
    for id_del in ids_para_remover:
        utils.remover_aplicacao(id_del)
    
    tamanho_apos_remocao = os.path.getsize(models.FILE_APLICACOES)
    print("=" * 80 + f"\n\nTamanho do arquivo após exclusão: {tamanho_apos_remocao} bytes.\n")

    # Criar 50 registros escolhidos em aleatorio. Mostrar tamanho depois da inserção.-
    print("=" * 80 + "\n\nInserindo 50 novos registros para testar reuso de espaço...\n\n")
    for i in range(101, 151): # IDs novos para deixar claro no log quais registros são novas entradas que estão ocupando espaços de cadastros antigos
        nova_app = models.AplicacaoVacina(
            cod=i, 
            cod_pac=random.randint(1, 100), 
            cod_vac=random.randint(1, 20), 
            cod_func=random.randint(1, 50), 
            data="03/02/2026"
        )
        utils.inserir_aplicacao(nova_app)
    
    tamanho_final = os.path.getsize(models.FILE_APLICACOES)
    print("=" * 80 + f"\n\nTamanho do arquivo após novas inserções: {tamanho_final} bytes.")
    
    if tamanho_final == tamanho_apos_remocao:
        print("O tamanho do arquivo é igual ao inicial! Espaços totalmente reutilizados.\n")

    # --- 4. BUSCAR 15 REGISTROS ALEATÓRIOS ---
    print("=" * 80 + "\n\nBuscando 15 registros aleatórios para validar o Hashmap...\n")
    # Os IDs ativos agora são alguns entre 1-100 (os que sobraram) e 101-150
    ids_ativos = [i for i in range(1, 151) if i not in ids_para_remover]
    amostra_busca = random.sample(ids_ativos, 15)

    for id_busca in amostra_busca:
        res = utils.buscar_aplicacao(id_busca)
        if res:
            print(f"Encontrado: {res}")
        else:
            print(f"Erro: ID {id_busca} deveria existir mas não foi encontrado.")