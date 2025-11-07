import services
import utils

def menu_principal():
    while True:
        print("\n--- Sistema de Vacinação ---")
        print("1. Aplicar Vacina")
        print("2. Cadastrar Novo Paciente")
        print("3. Listar todos os Pacientes")
        print("4. (Manutenção) Reordenar arquivo de Pacientes")
        print("0. Sair")
        
        op = input("Escolha uma opção: ")
        
        if op == '1':
            try:
                pac_id = int(input("ID do Paciente: "))
                vac_id = int(input("ID da Vacina: "))
                func_id = int(input("ID do Funcionário: "))
                data = input("Data (dd/mm/aaaa): ")
                services.aplicar_nova_vacina(pac_id, vac_id, func_id, data)
            except ValueError:
                print("Erro: IDs devem ser números.")
        
        elif op == '2':
            # ... (chamar services.cadastrar_novo_paciente) ...
            pass
            
        elif op == '3':
            # ... (chamar data_access.ler_sequencial para pacientes e imprimir) ...
            pass

        elif op == '4':
            print("Iniciando reordenação de manutenção...")
            # (chamar utils.mergesort_file para pacientes)
            pass

        elif op == '0':
            print("Saindo...")
            break

if __name__ == "__main__":
    menu_principal()
