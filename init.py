#imports
import time
import sys
import random

# ==========================================
# ESTRUTURAS DE DADOS DO KERNEL
# ==========================================

# Tabela global de processos (Nossa "RAM")
tabela_processos = []
pid_counter = 1000  # PIDs na vida real começam em 1000 
MAX_PROCESSOS = 5  # Limite de processos para simular falta de memória

class PCB:
    """Bloco Descritor de Processo (Process Control Block)"""
    def __init__(self, nome):
        global pid_counter
        self.pid = pid_counter
        self.nome = nome
        self.estado = "PRONTO"  # Estados possíveis: PRONTO, EXECUTANDO, TERMINADO
        self.ciclos_restantes = random.randint(2, 6)  # Define o "peso" do processo (quantos ticks ele precisa)
        pid_counter += 1

# ==========================================
# FUNÇÕES DO KERNEL E ESCALONADOR
# ==========================================

def boot():
    """Simula a inicialização do Sistema Operacional"""
    print("Iniciando PyOS Kernel v1.0...")
    time.sleep(1)
    print("Carregando módulos de memória [OK]")
    time.sleep(0.5)
    print("Iniciando escalonador de processos [OK]")
    time.sleep(0.5)
    print("Bem-vindo ao terminal. Digite 'help' para comandos.\n")



def spawn_process(nome):
    """Cria um novo processo e adiciona na tabela (RAM)"""

    # Verifica limite de memória/processos
    if len(tabela_processos) >= MAX_PROCESSOS:
        print("ERRO! Limite de processos atingido.")
        return

    novo_processo = PCB(nome)
    tabela_processos.append(novo_processo)

    print(f"[Kernel] Processo '{nome}' criado com PID {novo_processo.pid}")

def escalonador_tick():
    """Simula um ciclo (quantum) do processador executando a fila (Round Robin)"""
    prontos = [p for p in tabela_processos if p.estado != "TERMINADO"]
    
    if not prontos:
        print("[CPU] Ociosa (Idle). Nenhum processo na fila de prontos.")
        return

    processo_atual = prontos[0]
    
    # CHAVEAMENTO DE CONTEXTO: Entrando na CPU
    processo_atual.estado = "EXECUTANDO"
    print(f"\n[CPU] Executando PID {processo_atual.pid} ({processo_atual.nome})...")
    time.sleep(1)  # Simula o tempo real da CPU processando a tarefa
    
    # Decrementa o trabalho necessário (simula que ele fez progresso)
    processo_atual.ciclos_restantes -= 1
    
    # Verifica se o processo terminou seu trabalho
    if processo_atual.ciclos_restantes <= 0:
        processo_atual.estado = "TERMINADO"
        print(f"[Kernel] Processo PID {processo_atual.pid} finalizou e liberou a memória.")
        # Remove da tabela de processos (limpa a RAM)
        tabela_processos.remove(processo_atual)
    else:
        # CHAVEAMENTO DE CONTEXTO: Saindo da CPU por preempção (acabou o tempo dele)
        processo_atual.estado = "PRONTO"
        # Tira do início da fila e coloca no final (Round Robin)
        tabela_processos.remove(processo_atual)
        tabela_processos.append(processo_atual)
        print(f"[Kernel] Chaveamento de contexto. PID {processo_atual.pid} pausado e movido para o fim da fila.")

def run_scheduler():
    """Executa automaticamente a CPU até todos os processos terminarem"""

    print("[Kernel] Iniciando execução automática da CPU...\n")

    while len(tabela_processos) > 0:
        escalonador_tick()
        time.sleep(0.5)

    print("\n[Kernel] Todos os processos foram finalizados.")

# ==========================================
# INTERFACE COM O USUÁRIO (SHELL)
# ==========================================

def shell():
    """O laço principal que aguarda comandos do usuário"""
    global tabela_processos
    
    while True:
        try:
            # O Prompt do nosso SO
            comando = input("root@pyos:~# ").strip().lower().split()
            
            # Evita erro se o usuário apertar Enter vazio
            if not comando:
                continue
                
            acao = comando[0]
            
            if acao == "exit":
                print("Desligando o sistema...")
                break
                
            elif acao == "help":
                print("Comandos disponíveis:")
                print("  spawn [nome] - Cria um novo processo")
                print("  ps           - Lista os processos ativos")
                print("  cpu          - Executa 1 ciclo do processador (Escalonador)")
                print("  kill [PID]   - Encerra um processo à força")
                print("  clear        - Limpa a tela")
                print("  exit         - Desliga o sistema")
                
            elif acao == "clear":
                print("\033[H\033[J", end="")  # Código ANSI para limpar terminal
                
            elif acao == "spawn":
                if len(comando) > 1:
                    spawn_process(comando[1])
                else:
                    print("Uso correto: spawn [nome_do_processo]")
                    
            elif acao == "ps":
                # Formatação em colunas para ficar parecido com o Linux
                print(f"{'PID':<6} | {'NOME':<12} | {'ESTADO':<12} | {'CICLOS RESTANTES'}")
                print("-" * 55)
                for p in tabela_processos:
                    print(f"{p.pid:<6} | {p.nome[:12]:<12} | {p.estado:<12} | {p.ciclos_restantes}")
                if not tabela_processos:
                    print("Nenhum processo em execução.")
                    
            elif acao == "kill":
                if len(comando) > 1:
                    try:
                        alvo = int(comando[1])
                        # Recria a lista mantendo todos, exceto o alvo
                        tabela_processos = [p for p in tabela_processos if p.pid != alvo]
                        print(f"[Kernel] Sinal SIGKILL enviado. PID {alvo} destruído.")
                    except ValueError:
                        print("Erro: O PID deve ser um número inteiro.")
                else:
                    print("Uso correto: kill [PID]")
                    
            elif acao == "cpu":
                escalonador_tick()
            elif acao == "run":
                run_scheduler()
                
            else:
                print(f"bash: {acao}: comando não encontrado. Digite 'help'.")
                
        # Intercepta o Ctrl+C para não "quebrar" o simulador com erro feio
        except KeyboardInterrupt:
            print("\nPor favor, use 'exit' para sair do PyOS.")

# ==========================================
# INÍCIO DO SISTEMA
# ==========================================

if __name__ == "__main__":
    boot()
    shell()