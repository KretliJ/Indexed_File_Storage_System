# **CSI104-2025-02 - Proposta de Trabalho Final**

## *Discente: Jonas Elias Kretli*

<!-- Descrever um resumo sobre o trabalho. -->

### 📋 Resumo
 
  Este trabalho final consiste no desenvolvimento de um Sistema de Gestão de Vacinação, focado na manipulação de arquivos binários. O sistema simula um ambiente de banco de dados customizado, capaz de gerenciar grandes volumes de dados (funcionários, pacientes, vacinas e aplicações) utilizando estruturas de tamanho fixo, indexação e algoritmos de ordenação externa (em disco).

### 1.🎯 Tema

  Desenvolvimento de um sistema de informação para controle de vacinação com persistência em arquivos binários e interface gráfica.

### 2.🚀 Escopo
  
  O sistema entregue contempla as seguintes funcionalidades e características:
  
  * **Arquitetura:** 4 arquivos principais (`.dat`) para armazenar vacinas, funcionários, pacientes, e aplicações, além de um arquivo de log que registra as operações feitas.
  * **Manipulação de Arquivos:** Implementação de leitura sequencial e aleatória (Random Access) utilizando o módulo ctypes para mapeamento direto de estruturas em C.
  * **Algoritmos Avançados:**
    * **Busca Binária:** Para recuperação rápida de registros por chave primária.
    * **Ordenação Externa (Mergesort):** Implementação de K-Way Merge para ordenar arquivos maiores que a memória RAM disponível.
    * **Indexação:** Criação e reconstrução dinâmica de índices para relação Um-para-Muitos (Paciente -> Aplicações).
  * **Funcionalidades da Lógica de Negócio:**
    * Cadastro de aplicações de vacinas.
    * Geração de Cartão de Vacinação em PDF, contendo o histórico completo do paciente.
  * **Interface Gráfica (GUI):** Interface amigável desenvolvida com `tkinter`, com suporte a rolagem, logs de operação em tempo real e thread dedicada para operações de manipulação em massa (evita aparência de congelamento da tela).
  * **Performance:** Geração de massa de dados utilizando multiprocessamento para criação rápida de registros na quantidade de milhares ou mais.
  
<!-- Apresentar restrições de funcionalidades e de escopo. -->
### 3.🛠️ Restrições

  * **Linguagem:** Python 3.13+
  * **Persistência:** Módulo `ctypes` (registros de tamanho fixo).
  * **Dados:** Criados exclusivamente de maneira aleatória dada a quantidade de registros dos arquivos operados.
    * Atualmente 10000 registros para vacinas, clientes e funcionários, podendo ser expandida.  
  * **Interface:** `tkinter` (Pacote nativo Python).
  * **Concorrência:** threading (para IO/Sort em background) e multiprocessing (para geração de dados).
  * **Relatórios:**
    * `operation_log.txt`: Registro de operações gerais.
    * `relatorio_parte2.txt`: Análise comparativa dos algoritmos de ordenação.
    * `reportlab`: Geração de PDFs.

### 4.📐 Modelagem
  * **Modelo de classes**
  <img alt="ModeloClasses 2025-2" src="https://github.com/KretliJ/CSI104_TP/blob/main/Diagrams/ModeloDiagramaClasses.png">

  * **Modelo Entidade Relacionamento**
  <img alt="ModeloER 2025-2" src="https://github.com/KretliJ/CSI104_TP/blob/main/Diagrams/ModeloER.png">
  
  * **Diagrama de Sequência**
  <img alt="ModeloSeq 2025-2" src="https://github.com/KretliJ/CSI104_TP/blob/main/Diagrams/DiagramaSequencia.png">
 
  * **Diagrama de Estados**
  <img alt="ModeloEstados 2025-2" src="https://github.com/KretliJ/CSI104_TP/blob/main/Diagrams/DiagramaEstados.png">
  
<!-- Construir alguns protótipos para a aplicação, disponibilizá-los no Github e descrever o que foi considerado. //-->
### 5.📅 Cronograma de Desenvolvimento

  * v1.0 (07/11): Protótipo de estruturas de dados e funções básica de criação de arquivos.
  * v1.2 (07/11): Definição das estruturas (`models.py`) e funções básicas de IO.
  * v1.4 (14/11): Implementação do Mergesort (V1) e geração de dados paralela.
  * v1.6 (20/11): Implementação da Interface Gráfica e conexão interna com serviços (Modelo MVC).
  * v2.0 (25/11): Implementação da Indexação, Geração de PDF, Tela de Manutenção/Debug e correção de bugs de concorrência.
  * v2.5 (26/11): Implementação de:
    * Funções de Seleção por substituição
    * Árvore Binária de vencedores
    * Logging dos resultados das questões propostas no Trabalho Prático – Parte II
    * Mudanças na lógica do sorting da função `_quicksort_in_ram_generic()`:
      * Sorting nativo Python -> Implementação manual 
  
### 6.📚 Referências

  * Material disciplina CSI104 - ALGORITMOS E ESTRUTURAS DE DADOS II.
  * Documentação Python (`ctypes`, `multiprocessing`, `tkinter`).
  * Documentação ReportLab (Geração de PDFs).
  * Knuth, D. E. The Art of Computer Programming, Vol. 3: Sorting and Searching.

### 7.⚙️ Instalação e Execução

  * Pré-requisitos
    * Python 3.13 ou superior
    * Git

 1. Clonar o repositório
    ```
    git clone https://github.com/KretliJ/CSI104_TP.git
    cd CSI104_TP
    ```
 2. Instalar Dependências:
    ```
    pip install reportlab
    ```
 3. Executar o arquivo principal:
    ```
    python main.py
    ```
Notas: 
  * Na primeira execução, o sistema irá criar automaticamente o diretório files/ e gerar os arquivos binários iniciais com dados de teste. Esse processo pode levar alguns segundos. Logs de INFO serão registrados e prints de debug serão mostrados no terminal.
  * Os arquivos de log geral e da parte II podem ser acessados na pasta "Logs"
  * Os testes comparativos podem ser realizados pela interface de usuário em: `Manutenção e Debug` -> `Gerar relatório comparativo`
    * Ou executados diretamente pelo terminal com:
    ```
    python teste_part2.py
    ```
