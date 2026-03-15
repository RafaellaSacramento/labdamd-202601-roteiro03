import xmlrpc.client

ENDPOINT = "http://localhost:8765/"


def main():
    proxy = xmlrpc.client.ServerProxy(ENDPOINT, allow_none=True)

    print("=== Chamadas XML-RPC para o servidor de calculadora ===\n")

    metodos = proxy.system.listMethods()
    print(f"Metodos disponiveis no servidor: {metodos}\n")

    chamadas = [
        ("soma",          10.0, 3.0),
        ("subtracao",     10.0, 3.0),
        ("multiplicacao",  4.0, 7.0),
        ("divisao",       22.0, 7.0),
    ]
    for op, a, b in chamadas:
        try:
            resultado = proxy.calcular(op, a, b)
            print(f"  calcular('{op}', {a}, {b}) = {resultado:.6f}")
        except xmlrpc.client.Fault as e:
            print(f"  Erro do servidor [{e.faultCode}]: {e.faultString}")

    print()
    ack = proxy.registrar_evento("Aluno concluiu Tarefa 1")
    print(f"  registrar_evento -> '{ack}'")

    print("\n  Testando operacao invalida ('raiz_quadrada'):")
    try:
        proxy.calcular("raiz_quadrada", 9.0, 0.0)
    except xmlrpc.client.Fault as e:
        print(f"  Fault recebido: {e.faultString}")


if __name__ == "__main__":
    try:
        main()
    except ConnectionRefusedError:
        print("Servidor nao disponivel.")
        print("Execute primeiro: python servidor_xmlrpc.py")
