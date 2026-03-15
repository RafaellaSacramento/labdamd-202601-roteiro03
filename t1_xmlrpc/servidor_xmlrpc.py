from xmlrpc.server import SimpleXMLRPCServer
import datetime

def calcular(operacao: str, a: float, b: float) -> float:
    ops = {
        "soma":          lambda x, y: x + y,
        "subtracao":     lambda x, y: x - y,
        "multiplicacao": lambda x, y: x * y,
        "divisao":       lambda x, y: x / y if y != 0 else float("inf"),
    }
    if operacao not in ops:
        raise ValueError(f"Operacao desconhecida: '{operacao}'")
    resultado = ops[operacao](a, b)
    print(f"[Servidor] calcular({operacao}, {a}, {b}) = {resultado}")
    return resultado


def registrar_evento(mensagem: str) -> str:
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    linha = f"[{ts}] {mensagem}"
    print(f"[Servidor] Evento: {linha}")
    return f"ACK: {linha}"


def listar_operacoes() -> list:
    return ["soma", "subtracao", "multiplicacao", "divisao"]

if __name__ == "__main__":
    HOST, PORT = "localhost", 8765
    server = SimpleXMLRPCServer((HOST, PORT), logRequests=False, allow_none=True)
    server.register_function(calcular,          "calcular")
    server.register_function(registrar_evento,  "registrar_evento")
    server.register_function(listar_operacoes,  "listar_operacoes")
    server.register_introspection_functions()
    print(f"Servidor XML-RPC em http://{HOST}:{PORT} | Ctrl+C para encerrar")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
