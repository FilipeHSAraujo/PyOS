# 🖥️ PyOS - Simulador Educacional de Sistema Operacional

![Status](https://img.shields.io/badge/Status-Educacional-blue)
![Python](https://img.shields.io/badge/Python-3.x-green)

## Aluno:Vinícius Gaspar de Araújo Silva 01797364


Este repositório contém o **PyOS**, um simulador lógico de Sistema Operacional desenvolvido em Python para fins didáticos. O projeto foi desenhado para cobrir os conceitos fundamentais das **Unidades I e II** da disciplina de Sistemas Operacionais, permitindo que alunos explorem a mecânica interna de um Kernel sem a complexidade de linguagens de baixo nível.

## 🎯 Objetivos Pedagógicos
* Compreender o **Bloco Descritor de Processo (PCB)**.
* Visualizar o **Chaveamento de Contexto** e o **Escalonamento Round Robin**.
* Praticar a **Sincronização de Processos** através de Semáforos (Mutex).
* Simular estados críticos como **Deadlock** e **Processos Zumbi**.
* Entender chamadas de sistema (Syscalls) como o `fork()`.

---

## 🚀 Como Executar

Certifique-se de ter o Python 3 instalado em sua máquina.

1.  Clone este repositório:
    ```bash
    git clone https://github.com/FilipeHSAraujo/PyOs.git
    ```
2.  Navegue até a pasta do projeto:
    ```bash
    cd PyOS
    ```
3.  Execute o Kernel:
    ```bash
    python init.py
    ```

---

## 🛠️ Comandos do Shell (User Space)

Ao iniciar o PyOS, você terá acesso a um terminal interativo (`root@pyos:~#`):

| Comando | Descrição |
| :--- | :--- |
| `spawn [nome]` | Cria um novo processo na RAM (gera um PID único). |
| `ps` | Lista todos os processos ativos e seus respectivos estados. |
| `cpu` | Executa 1 ciclo (tick) de clock no processador (Escalonador). |
| `lock [PID]` | Solicita acesso exclusivo a um recurso via Semáforo. |
| `unlock [PID]` | Libera o recurso bloqueado para outros processos. |
| `clear` | Limpa a tela do terminal. |
| `exit` | Desliga o simulador. |

---

## 🎮 Trilha de Desafios: Hackeando o Kernel

O projeto foi estruturado em níveis de dificuldade para que você possa evoluir o código original e implementar novas funcionalidades:

### 🟢 Nível 1: Limite de Memória (OOM)
* **Missão:** Impeça que o sistema aceite mais de 5 processos simultâneos.
* **Conceito:** Proteção de recursos e erro *Out of Memory*.

### 🟡 Nível 2: Automador de Clock (Comando `run`)
* **Missão:** Crie o comando `run` que executa o escalonador automaticamente em loop até a RAM esvaziar.
* **Conceito:** Timer Interrupt e automação de ciclos de CPU.

### 🟡 Nível 3: Gargalo de E/S (Estado BLOQUEADO)
* **Missão:** Implemente os comandos `block` e `unblock` para simular esperas de periféricos.
* **Conceito:** Ciclo de vida do processo e gerenciamento de E/S.

### 🟠 Nível 4: O Fim da Democracia (Prioridades)
* **Missão:** Adicione prioridades aos processos e altere o escalonador para processar primeiro os de alta prioridade.
* **Conceito:** Escalonamento Preemptivo por Prioridade.

### 🔴 Nível 5: Mago da Sincronização (Semáforos)
* **Missão:** Implemente o controle de acesso a um recurso compartilhado (ex: Impressora).
* **Conceito:** Exclusão mútua e Região Crítica.

### 🔴 Nível 6: Arquiteto do Caos (Simulação de Deadlock)
* **Missão:** Provoque uma espera circular entre dois processos por dois recursos distintos.
* **Conceito:** Impasse de recursos e interrupção do sistema.

### 🟣 Nível 7: O Apocalipse Zumbi
* **Missão:** Altere o sistema para que processos terminados permaneçam na RAM como `ZUMBI` até o comando `wait`.
* **Conceito:** Estruturas de dados pós-execução e coleta de lixo.

### 💀 Nível 8: O Boss Final (`fork()`)
* **Missão:** Implemente o comando `fork [PID]` para clonar um processo pai com seu contexto exato.
* **Conceito:** Hierarquia de processos e clonagem de contexto.

### 🔥 Nível Supremo: Comunicação entre Processos (IPC)
* **Missão:** Crie memória compartilhada para que processos possam ler e escrever mensagens entre si.
* **Conceito:** Isolamento de memória e IPC (Inter-Process Communication).

---

## 📘 Referência Teórica
Este projeto serve como material de apoio para as unidades curriculares de Sistemas Operacionais, focando em:
* **Unidade I:** Fundamentos, Processos e Threads.
* **Unidade II:** Gerência do Processador e Escalonamento.

---

Desenvolvido para fins educacionais. Sinta-se à vontade para expandir o Kernel! 💻✨
