# imports
import time
import sys
import random
 
# ==========================================
# ESTRUTURAS DE DADOS DO KERNEL
# ==========================================
 
# Tabela global de processos (Nossa "RAM")
tabela_processos = []
pid_counter = 1000  # PIDs na vida real começam em 1000
MAX_PROCESSOS = 10  # Aumentei o limite pra caber mais processos nos testes
 
# NIVEL 5: Tabela de semaforos (controle de recursos compartilhados)
semaforos = {}  # ex: {"impressora": 1}  -- 1 = livre, 0 = ocupado
 
# NIVEL 6: Tabela de recursos para deadlock
# cada recurso guarda qual PID ta segurando ele
recursos = {}  # ex: {"impressora": 1001, "scanner": 1002}
 
# NIVEL 7: fila de processos zumbi esperando o wait
tabela_zumbis = []
 
 
class PCB:
    """Bloco Descritor de Processo (Process Control Block)"""
    def __init__(self, nome, prioridade=1):
        global pid_counter
        self.pid = pid_counter
        self.nome = nome
        self.estado = "PRONTO"  # Estados: PRONTO, EXECUTANDO, BLOQUEADO, TERMINADO, ZUMBI
        self.ciclos_restantes = random.randint(2, 6)
        self.prioridade = prioridade  # NIVEL 4: quanto maior, mais urgente
 
        # NIVEL 6: lista de recursos que esse processo ta segurando
        self.recursos_em_uso = []
 
        # NIVEL 8: referencia ao processo pai (para fork)
        self.ppid = None  # Parent PID
 
        # NIVEL 9: caixa de mensagens IPC
        self.mensagens = []  # lista de strings que outros processos mandam
 
        pid_counter += 1
 
 
# ==========================================
# FUNCOES DO KERNEL E ESCALONADOR
# ==========================================
 
def boot():
    """Simula a inicializacao do Sistema Operacional"""
    print("Iniciando PyOS Kernel v9.0 (Edicao Final)...")
    time.sleep(1)
    print("Carregando modulos de memoria      [OK]")
    time.sleep(0.3)
    print("Iniciando escalonador de processos [OK]")
    time.sleep(0.3)
    print("Iniciando gerenciador de semaforos [OK]")
    time.sleep(0.3)
    print("Iniciando modulo IPC               [OK]")
    time.sleep(0.3)
    print("Sistema pronto. Digite 'help' para ver os comandos.\n")
 
 
def spawn_process(nome, prioridade=1):
    """Cria um novo processo e adiciona na tabela (RAM)"""
    # verifica limite de memoria
    ativos = [p for p in tabela_processos if p.estado != "ZUMBI"]
    if len(ativos) >= MAX_PROCESSOS:
        print("ERRO! Limite de processos atingido. Memoria cheia.")
        return None
 
    novo = PCB(nome, prioridade)
    tabela_processos.append(novo)
    print(f"[Kernel] Processo '{nome}' criado com PID {novo.pid} | Prioridade: {novo.prioridade} | Ciclos: {novo.ciclos_restantes}")
    return novo
 
 
def escalonador_tick():
    """
    NIVEL 4: Escalonador por PRIORIDADE (preemptivo)
    Em vez de pegar o primeiro da fila, pega o de maior prioridade
    """
    # so pega os que estao PRONTOS (ignora bloqueados e zumbis)
    prontos = [p for p in tabela_processos if p.estado == "PRONTO"]
 
    if not prontos:
        print("[CPU] Ociosa (Idle). Nenhum processo pronto na fila.")
        return
 
    # NIVEL 4: ordena por prioridade decrescente e pega o mais urgente
    prontos.sort(key=lambda p: p.prioridade, reverse=True)
    processo_atual = prontos[0]
 
    # CHAVEAMENTO DE CONTEXTO: entra na CPU
    processo_atual.estado = "EXECUTANDO"
    print(f"\n[CPU] Executando PID {processo_atual.pid} ({processo_atual.nome}) | Prioridade {processo_atual.prioridade}...")
    time.sleep(0.8)
 
    processo_atual.ciclos_restantes -= 1
 
    if processo_atual.ciclos_restantes <= 0:
        # NIVEL 7: em vez de remover direto, vira ZUMBI esperando o wait
        processo_atual.estado = "ZUMBI"
        tabela_processos.remove(processo_atual)
        tabela_zumbis.append(processo_atual)
 
        # libera recursos que o processo estava segurando (Nivel 6)
        for recurso in processo_atual.recursos_em_uso:
            if recurso in recursos and recursos[recurso] == processo_atual.pid:
                del recursos[recurso]
                print(f"[Kernel] Recurso '{recurso}' liberado pelo PID {processo_atual.pid}.")
 
        print(f"[Kernel] PID {processo_atual.pid} terminou. Estado: ZUMBI (aguardando wait).")
    else:
        # chaveamento de contexto: sai da CPU, vai pro fim da fila
        processo_atual.estado = "PRONTO"
        tabela_processos.remove(processo_atual)
        tabela_processos.append(processo_atual)
        print(f"[Kernel] Chaveamento: PID {processo_atual.pid} pausado e movido pro fim da fila.")
 
 
def run_scheduler():
    """Executa automaticamente a CPU ate todos os processos terminarem"""
    print("[Kernel] Iniciando execucao automatica...\n")
 
    while any(p.estado == "PRONTO" for p in tabela_processos):
        escalonador_tick()
        time.sleep(0.3)
 
    bloqueados = [p for p in tabela_processos if p.estado == "BLOQUEADO"]
    if bloqueados:
        print(f"\n[Kernel] Ainda existem {len(bloqueados)} processo(s) BLOQUEADO(s). Use 'unblock [PID]' pra destravar.")
    else:
        print("\n[Kernel] Todos os processos foram finalizados.")
 
    zumbis = len(tabela_zumbis)
    if zumbis > 0:
        print(f"[Kernel] {zumbis} processo(s) ZUMBI esperando o comando 'wait'.")
 
 
# ==========================================
# NIVEL 3: BLOCK e UNBLOCK (E/S)
# ==========================================
 
def bloquear_processo(alvo_pid):
    """Simula uma espera de E/S - o processo fica bloqueado ate o device responder"""
    for p in tabela_processos:
        if p.pid == alvo_pid:
            if p.estado == "PRONTO" or p.estado == "EXECUTANDO":
                p.estado = "BLOQUEADO"
                print(f"[Kernel] PID {alvo_pid} bloqueado (aguardando E/S de periferico).")
            else:
                print(f"[Kernel] PID {alvo_pid} nao pode ser bloqueado. Estado atual: {p.estado}")
            return
    print(f"[Kernel] PID {alvo_pid} nao encontrado.")
 
 
def desbloquear_processo(alvo_pid):
    """Simula a interrupcao do device avisando que terminou - processo volta pra fila"""
    for p in tabela_processos:
        if p.pid == alvo_pid:
            if p.estado == "BLOQUEADO":
                p.estado = "PRONTO"
                print(f"[Kernel] Interrupcao recebida! PID {alvo_pid} desbloqueado e voltou pra fila de prontos.")
            else:
                print(f"[Kernel] PID {alvo_pid} nao esta bloqueado. Estado atual: {p.estado}")
            return
    print(f"[Kernel] PID {alvo_pid} nao encontrado.")
 
 
# ==========================================
# NIVEL 5: SEMAFOROS (Exclusao Mutua)
# ==========================================
 
def criar_semaforo(nome, valor=1):
    """Cria um semaforo para controlar acesso a um recurso compartilhado"""
    if nome in semaforos:
        print(f"[Semaforo] '{nome}' ja existe com valor {semaforos[nome]}.")
        return
    semaforos[nome] = valor
    print(f"[Semaforo] '{nome}' criado com valor inicial {valor} (1=livre, 0=ocupado).")
 
 
def semaforo_wait(nome, pid_solicitante):
    """
    Operacao P (wait/down): tenta adquirir o semaforo
    Se estiver livre (1), decrementa pra 0 e entra na regiao critica
    Se estiver ocupado (0), bloqueia o processo
    """
    if nome not in semaforos:
        print(f"[Semaforo] '{nome}' nao existe. Use 'sem create {nome}' primeiro.")
        return
 
    processo = None
    for p in tabela_processos:
        if p.pid == pid_solicitante:
            processo = p
            break
 
    if processo is None:
        print(f"[Semaforo] PID {pid_solicitante} nao encontrado.")
        return
 
    if semaforos[nome] > 0:
        semaforos[nome] -= 1
        print(f"[Semaforo] PID {pid_solicitante} adquiriu '{nome}'. Entrando na regiao critica.")
    else:
        # semaforo ocupado, bloqueia o processo
        processo.estado = "BLOQUEADO"
        print(f"[Semaforo] '{nome}' ocupado! PID {pid_solicitante} foi BLOQUEADO (esperando recurso).")
 
 
def semaforo_signal(nome, pid_liberador):
    """
    Operacao V (signal/up): libera o semaforo
    Incrementa de volta pra 1, desbloqueando quem estava esperando
    """
    if nome not in semaforos:
        print(f"[Semaforo] '{nome}' nao existe.")
        return
 
    semaforos[nome] += 1
    print(f"[Semaforo] PID {pid_liberador} liberou '{nome}'. Saindo da regiao critica.")
 
    # desbloqueia o proximo processo que estava esperando (se houver)
    for p in tabela_processos:
        if p.estado == "BLOQUEADO":
            p.estado = "PRONTO"
            semaforos[nome] -= 1
            print(f"[Semaforo] PID {p.pid} foi desbloqueado e voltou pra fila.")
            break
 
 
# ==========================================
# NIVEL 6: DEADLOCK (espera circular)
# ==========================================
 
def adquirir_recurso(pid_solicitante, nome_recurso):
    """
    Processo tenta pegar um recurso fisico (impressora, scanner, etc)
    Se ja ta com outro processo, bloqueia -> pode causar deadlock
    """
    processo = None
    for p in tabela_processos:
        if p.pid == pid_solicitante:
            processo = p
            break
 
    if processo is None:
        print(f"[Recurso] PID {pid_solicitante} nao encontrado.")
        return
 
    if nome_recurso not in recursos:
        # recurso livre, entrega pra ele
        recursos[nome_recurso] = pid_solicitante
        processo.recursos_em_uso.append(nome_recurso)
        print(f"[Recurso] PID {pid_solicitante} adquiriu '{nome_recurso}'.")
    else:
        dono = recursos[nome_recurso]
        if dono == pid_solicitante:
            print(f"[Recurso] PID {pid_solicitante} ja possui '{nome_recurso}'.")
        else:
            # recurso ocupado, bloqueia e detecta possivel deadlock
            processo.estado = "BLOQUEADO"
            print(f"[Recurso] '{nome_recurso}' esta com PID {dono}. PID {pid_solicitante} BLOQUEADO.")
            detectar_deadlock()
 
 
def liberar_recurso(pid_dono, nome_recurso):
    """Processo libera um recurso que estava usando"""
    if nome_recurso in recursos and recursos[nome_recurso] == pid_dono:
        del recursos[nome_recurso]
        for p in tabela_processos:
            if p.pid == pid_dono and nome_recurso in p.recursos_em_uso:
                p.recursos_em_uso.remove(nome_recurso)
        print(f"[Recurso] PID {pid_dono} liberou '{nome_recurso}'.")
 
        # desbloqueia quem estava esperando esse recurso
        for p in tabela_processos:
            if p.estado == "BLOQUEADO":
                recursos[nome_recurso] = p.pid
                p.recursos_em_uso.append(nome_recurso)
                p.estado = "PRONTO"
                print(f"[Recurso] PID {p.pid} foi desbloqueado e adquiriu '{nome_recurso}'.")
                break
    else:
        print(f"[Recurso] PID {pid_dono} nao possui '{nome_recurso}'.")
 
 
def detectar_deadlock():
    """
    Detecta espera circular simples:
    Processo A tem X e quer Y
    Processo B tem Y e quer X
    -> DEADLOCK!
    """
    bloqueados = [p for p in tabela_processos if p.estado == "BLOQUEADO"]
    if len(bloqueados) < 2:
        return
 
    print("\n[DEADLOCK DETECTOR] Verificando espera circular...")
 
    # simplificado: se todos os recursos estao ocupados e tem gente bloqueada, avisa
    todos_bloqueados = all(p.estado == "BLOQUEADO" for p in tabela_processos if p.estado != "ZUMBI")
    if todos_bloqueados and len(tabela_processos) > 0:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("[DEADLOCK] IMPASSE DETECTADO! Espera circular entre processos!")
        print("Processos bloqueados:", [p.pid for p in bloqueados])
        print("Use 'kill [PID]' para matar um dos processos e quebrar o deadlock.")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
 
 
# ==========================================
# NIVEL 7: ZUMBI e WAIT
# ==========================================
 
def wait_zumbi():
    """
    Coleta os processos zumbi (como o wait() no Unix)
    O pai reconhece que o filho terminou e remove da tabela de zumbis
    """
    if not tabela_zumbis:
        print("[Kernel] Nenhum processo zumbi para coletar.")
        return
 
    coletados = len(tabela_zumbis)
    for z in tabela_zumbis:
        print(f"[Kernel] Zumbi PID {z.pid} ({z.nome}) coletado e removido da memoria.")
    tabela_zumbis.clear()
    print(f"[Kernel] {coletados} processo(s) zumbi removido(s). Memoria liberada.")
 
 
# ==========================================
# NIVEL 8: FORK (clonagem de processo)
# ==========================================
 
def fork_process(pid_pai):
    """
    Clona um processo pai criando um filho identico
    O filho herda nome, prioridade e ciclos restantes do pai
    """
    pai = None
    for p in tabela_processos:
        if p.pid == pid_pai:
            pai = p
            break
 
    if pai is None:
        print(f"[Fork] PID {pid_pai} nao encontrado.")
        return
 
    ativos = [p for p in tabela_processos if p.estado != "ZUMBI"]
    if len(ativos) >= MAX_PROCESSOS:
        print("[Fork] ERRO: Memoria cheia, nao da pra criar filho.")
        return
 
    # cria o filho copiando o contexto do pai
    filho = PCB(pai.nome + "_filho", pai.prioridade)
    filho.ciclos_restantes = pai.ciclos_restantes  # mesmo "trabalho" restante
    filho.ppid = pai.pid  # guarda referencia ao pai
    tabela_processos.append(filho)
 
    print(f"[Fork] PID {pid_pai} forkado! Filho criado com PID {filho.pid} (PPID={filho.ppid}).")
    print(f"       Filho herda: prioridade={filho.prioridade}, ciclos={filho.ciclos_restantes}")
 
 
# ==========================================
# NIVEL 9: IPC - COMUNICACAO ENTRE PROCESSOS
# ==========================================
 
def ipc_send(pid_remetente, pid_destino, mensagem):
    """
    Envia uma mensagem pra caixa postal de outro processo
    Tipo pipe/mailbox basico de IPC
    """
    destino = None
    for p in tabela_processos:
        if p.pid == pid_destino:
            destino = p
            break
 
    if destino is None:
        # checa tambem na fila de zumbis
        for z in tabela_zumbis:
            if z.pid == pid_destino:
                print(f"[IPC] PID {pid_destino} e um zumbi, nao pode receber mensagens.")
                return
        print(f"[IPC] PID {pid_destino} nao encontrado.")
        return
 
    destino.mensagens.append(f"De PID {pid_remetente}: {mensagem}")
    print(f"[IPC] Mensagem enviada de PID {pid_remetente} para PID {pid_destino}.")
 
 
def ipc_recv(pid_destino):
    """
    Le as mensagens da caixa postal de um processo
    Simula a syscall recv() ou read() de um pipe
    """
    processo = None
    for p in tabela_processos:
        if p.pid == pid_destino:
            processo = p
            break
 
    if processo is None:
        print(f"[IPC] PID {pid_destino} nao encontrado.")
        return
 
    if not processo.mensagens:
        print(f"[IPC] Caixa de PID {pid_destino} vazia.")
        return
 
    print(f"[IPC] Mensagens de PID {pid_destino} ({processo.nome}):")
    for i, msg in enumerate(processo.mensagens, 1):
        print(f"  [{i}] {msg}")
    processo.mensagens.clear()
    print(f"[IPC] {i} mensagem(ns) lida(s) e removida(s) da caixa.")
 
 
# ==========================================
# INTERFACE COM O USUARIO (SHELL)
# ==========================================
 
def shell():
    """O laco principal que aguarda comandos do usuario"""
    global tabela_processos
 
    while True:
        try:
            comando = input("root@pyos:~# ").strip().split()
 
            if not comando:
                continue
 
            acao = comando[0].lower()
 
            # ----- COMANDOS BASICOS -----
 
            if acao == "exit":
                print("Desligando o sistema...")
                break
 
            elif acao == "help":
                print("""
Comandos disponiveis:
  print("Comandos disponíveis:")
                print("  spawn [nome] - Cria um novo processo")
                print("  ps           - Lista os processos ativos")
                print("  cpu          - Executa 1 ciclo do processador (Escalonador)")
                print("  kill [PID]   - Encerra um processo à força")
                print("  clear        - Limpa a tela")
                print("  exit         - Desliga o sistema""")
 
            elif acao == "clear":
                print("\033[H\033[J", end="")
 
            elif acao == "spawn":
                if len(comando) >= 2:
                    nome = comando[1]
                    prio = int(comando[2]) if len(comando) >= 3 else 1
                    spawn_process(nome, prio)
                else:
                    print("Uso: spawn [nome] [prioridade_opcional]")
 
            elif acao == "ps":
                todos = tabela_processos
                if not todos:
                    print("Nenhum processo em execucao.")
                else:
                    print(f"\n{'PID':<6} | {'PPID':<6} | {'NOME':<15} | {'ESTADO':<12} | {'PRIO':<5} | {'CICLOS':<6} | {'RECURSOS'}")
                    print("-" * 75)
                    for p in todos:
                        ppid_str = str(p.ppid) if p.ppid else "-"
                        rec_str = ", ".join(p.recursos_em_uso) if p.recursos_em_uso else "-"
                        print(f"{p.pid:<6} | {ppid_str:<6} | {p.nome[:15]:<15} | {p.estado:<12} | {p.prioridade:<5} | {p.ciclos_restantes:<6} | {rec_str}")
 
                if tabela_zumbis:
                    print(f"\nZUMBIS ({len(tabela_zumbis)}): " + ", ".join(f"PID {z.pid}" for z in tabela_zumbis))
 
            elif acao == "kill":
                if len(comando) >= 2:
                    try:
                        alvo = int(comando[1])
                        # libera recursos do processo morto
                        for p in tabela_processos:
                            if p.pid == alvo:
                                for rec in p.recursos_em_uso:
                                    if rec in recursos:
                                        del recursos[rec]
                                break
                        tabela_processos = [p for p in tabela_processos if p.pid != alvo]
                        print(f"[Kernel] SIGKILL enviado. PID {alvo} destruido.")
                    except ValueError:
                        print("Erro: PID deve ser numero inteiro.")
                else:
                    print("Uso: kill [PID]")
 
            elif acao == "cpu":
                escalonador_tick()
 
            elif acao == "run":
                run_scheduler()
 
            # ----- NIVEL 3: E/S -----
 
            elif acao == "block":
                if len(comando) >= 2:
                    try:
                        bloquear_processo(int(comando[1]))
                    except ValueError:
                        print("PID deve ser numero inteiro.")
                else:
                    print("Uso: block [PID]")
 
            elif acao == "unblock":
                if len(comando) >= 2:
                    try:
                        desbloquear_processo(int(comando[1]))
                    except ValueError:
                        print("PID deve ser numero inteiro.")
                else:
                    print("Uso: unblock [PID]")
 
            # ----- NIVEL 5: SEMAFOROS -----
 
            elif acao == "sem":
                if len(comando) < 2:
                    print("Uso: sem [create|wait|signal|list] ...")
                    continue
 
                sub = comando[1].lower()
 
                if sub == "create":
                    if len(comando) >= 3:
                        criar_semaforo(comando[2])
                    else:
                        print("Uso: sem create [nome]")
 
                elif sub == "wait":
                    if len(comando) >= 4:
                        try:
                            semaforo_wait(comando[2], int(comando[3]))
                        except ValueError:
                            print("PID deve ser numero.")
                    else:
                        print("Uso: sem wait [nome] [PID]")
 
                elif sub == "signal":
                    if len(comando) >= 4:
                        try:
                            semaforo_signal(comando[2], int(comando[3]))
                        except ValueError:
                            print("PID deve ser numero.")
                    else:
                        print("Uso: sem signal [nome] [PID]")
 
                elif sub == "list":
                    if semaforos:
                        print(f"{'SEMAFORO':<15} | VALOR (1=livre, 0=ocupado)")
                        print("-" * 35)
                        for nome, val in semaforos.items():
                            status = "LIVRE" if val > 0 else "OCUPADO"
                            print(f"{nome:<15} | {val} ({status})")
                    else:
                        print("Nenhum semaforo criado.")
                else:
                    print(f"Subcomando desconhecido: {sub}")
 
            # ----- NIVEL 6: RECURSOS / DEADLOCK -----
 
            elif acao == "req":
                if len(comando) >= 3:
                    try:
                        adquirir_recurso(int(comando[1]), comando[2])
                    except ValueError:
                        print("PID deve ser numero.")
                else:
                    print("Uso: req [PID] [recurso]")
 
            elif acao == "rel":
                if len(comando) >= 3:
                    try:
                        liberar_recurso(int(comando[1]), comando[2])
                    except ValueError:
                        print("PID deve ser numero.")
                else:
                    print("Uso: rel [PID] [recurso]")
 
            elif acao == "recursos":
                if recursos:
                    print(f"{'RECURSO':<15} | DONO (PID)")
                    print("-" * 30)
                    for rec, pid in recursos.items():
                        print(f"{rec:<15} | {pid}")
                else:
                    print("Nenhum recurso em uso no momento.")
 
            # ----- NIVEL 7: ZUMBI / WAIT -----
 
            elif acao == "wait":
                wait_zumbi()
 
            elif acao == "zumbis":
                if tabela_zumbis:
                    print(f"{'PID':<6} | {'NOME':<15} | ESTADO")
                    print("-" * 35)
                    for z in tabela_zumbis:
                        print(f"{z.pid:<6} | {z.nome[:15]:<15} | {z.estado}")
                else:
                    print("Nenhum processo zumbi no momento.")
 
            # ----- NIVEL 8: FORK -----
 
            elif acao == "fork":
                if len(comando) >= 2:
                    try:
                        fork_process(int(comando[1]))
                    except ValueError:
                        print("PID deve ser numero inteiro.")
                else:
                    print("Uso: fork [PID]")
 
            # ----- NIVEL 9: IPC -----
 
            elif acao == "send":
                # send [pid_orig] [pid_dest] [mensagem com espacos]
                if len(comando) >= 4:
                    try:
                        pid_orig = int(comando[1])
                        pid_dest = int(comando[2])
                        mensagem = " ".join(comando[3:])
                        ipc_send(pid_orig, pid_dest, mensagem)
                    except ValueError:
                        print("PIDs devem ser numeros inteiros.")
                else:
                    print("Uso: send [PID_origem] [PID_destino] [mensagem]")
 
            elif acao == "recv":
                if len(comando) >= 2:
                    try:
                        ipc_recv(int(comando[1]))
                    except ValueError:
                        print("PID deve ser numero inteiro.")
                else:
                    print("Uso: recv [PID]")
 
            else:
                print(f"bash: {acao}: comando nao encontrado. Digite 'help'.")
 
        except KeyboardInterrupt:
            print("\nUse 'exit' para sair do PyOS.")
 
 
# ==========================================
# INICIO DO SISTEMA
# ==========================================
 
if __name__ == "__main__":
    boot()
    shell()
 