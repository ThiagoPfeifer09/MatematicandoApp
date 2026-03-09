import requests

def enviar_resultado_googleforms(nome, tempo, operacao, rodadas, acertos, erros, nivel):
    url = 'https://docs.google.com/forms/d/e/1FAIpQLSdijBNdEphLiYVQzqrFpoaRAAvlrpXu4PIEA7OaL2Fzwh-T7A/formResponse'

    data = {
        'entry.629119395': nome,         # Nome do jogador
        'entry.1381544257': tempo,       # Tempo total
        'entry.203482403': operacao,     # Tipo de operação
        'entry.1619061979': rodadas,     # Total de questões
        'entry.1931923581': acertos,     # Acertos
        'entry.599479554': erros,        # Erros
        'entry.1854575042': nivel        # Nível
    }

    response = requests.post(url, data=data)
    if response.status_code == 200:
        print("✅ Dados enviados com sucesso.")
    else:
        print(f"❌ Erro ao enviar dados: {response.status_code}")
