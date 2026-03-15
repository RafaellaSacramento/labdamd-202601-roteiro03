import json
import socket
import threading
import time
from typing import Any


def _skeleton_tratar_conexao(conn: socket.socket, registro: dict):
    with conn:
        tamanho = int.from_bytes(conn.recv(4), "big")
        chamada = json.loads(conn.recv(tamanho).decode())
        nome, args = chamada["method"], chamada["args"]
        print(f"  [Skeleton] Recebeu chamada: {nome}({args})")
        try:
            if nome not in registro:
                raise KeyError(f"Metodo '{nome}' nao registrado")
            resultado = registro[nome](*args)
            resposta = json.dumps({"result": resultado}).encode()
        except Exception as e:
            resposta = json.dumps({"error": str(e)}).encode()
        conn.sendall(len(resposta).to_bytes(4, "big") + resposta)


def _skeleton_iniciar(host: str, port: int, registro: dict, parar: threading.Event):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(5)
        srv.settimeout(0.5)
        print(f"  [Skeleton] Servidor ouvindo em {host}:{port}")
        while not parar.is_set():
            try:
                conn, addr = srv.accept()
                threading.Thread(
                    target=_skeleton_tratar_conexao,
                    args=(conn, registro),
                    daemon=True,
                ).start()
            except socket.timeout:
                continue


def _stub_chamar(host: str, port: int, nome: str, args: list) -> Any:
    payload = json.dumps({"method": nome, "args": args}).encode()
    print(f"  [Stub]     Enviando: {payload.decode()}")
    with socket.create_connection((host, port), timeout=3) as s:
        s.sendall(len(payload).to_bytes(4, "big") + payload)
        tamanho = int.from_bytes(s.recv(4), "big")
        resposta = json.loads(s.recv(tamanho).decode())
    if "error" in resposta:
        raise RuntimeError(f"Erro remoto: {resposta['error']}")
    return resposta["result"]


def somar(a: float, b: float) -> float:
    return a + b


def obter_info() -> dict:
    return {"servico": "calculadora", "versao": "1.0", "status": "online"}

REGISTRO = {"somar": somar, "obter_info": obter_info}
HOST, PORT = "localhost", 9876

parar = threading.Event()
t = threading.Thread(
    target=_skeleton_iniciar,
    args=(HOST, PORT, REGISTRO, parar),
    daemon=True,
)
t.start()
time.sleep(0.15)

print("=" * 55)
print("  DEMONSTRACAO: Stub + Skeleton RPC manual via sockets")
print("=" * 55)

print("\nChamada 1: somar(7, 5)")
r = _stub_chamar(HOST, PORT, "somar", [7, 5])
print(f"  Resultado recebido: {r}\n")

print("Chamada 2: obter_info()")
info = _stub_chamar(HOST, PORT, "obter_info", [])
print(f"  Resultado recebido: {info}\n")

print("Chamada 3: metodo inexistente (erro esperado)")
try:
    _stub_chamar(HOST, PORT, "metodo_que_nao_existe", [])
except RuntimeError as e:
    print(f"  Erro propagado corretamente: {e}\n")

parar.set()
print("Servidor encerrado.\n")
print("=" * 55)
print("  COMPONENTES REVELADOS POR ESTA TAREFA")
print("=" * 55)
print("  Stub (cliente):    serializa args -> envia bytes -> deserializa resultado")
print("  Skeleton (serv.):  recebe bytes -> dispatch -> serializa resultado")
print("  Marshalling:       Python dict/list/float -> bytes JSON (ou Protobuf no gRPC)")
print("  Framing:           4 bytes de tamanho + payload (delimitador de mensagem)")
print("  Dispatch table:    dicionario nome->funcao (registry no servidor)")
