# **Indexed File Storage Engine (Projeto Didático)**

Implementação educacional de um mecanismo de armazenamento em arquivos binários com índice hash persistente, remoção lógica e reutilização de espaço em disco.

O foco do projeto é demonstrar fundamentos de sistemas de armazenamento, não fornecer um banco de dados pronto para produção.

## **Objetivo**
 * Armazenamento persistente em arquivo binário com registros de tamanho fixo
 * Acesso direto aos dados via índice hash
 * Remoção lógica com lápides
 * Reuso de espaço físico através de uma free list em pilha

## **Arquitetura**
 * Componente	Função
 * aplicacoes.dat	Arquivo de dados (heap file)
 * aplicacoes_hash.dat	Índice hash persistente (endereçamento aberto + linear probing)
 * header.dat	Topo da pilha de espaços livres

## **Operações**
### **Inserção**
 * Reutiliza espaço livre quando disponível
 * Caso contrário, insere no final do arquivo
 * Atualiza o índice hash

### **Busca**
 * Consulta o índice hash
 * Acesso direto ao registro via seek

### **Remoção**
 * Marca o índice hash como removido (lápide)
 * Empilha o espaço liberado para reutilização futura

## **Tecnologias**

* `Python 3`
* `ctypes` para controle de layout de memória
* Arquivos binários (.dat)
* Acesso direto por offset

## **Observações**
 * Projeto focado em fundamentos de sistemas
 * Não implementa concorrência, transações ou recuperação de falhas
 * Base recriada a cada execução para fins de teste


traduzir para inglês

ou ajustar o
