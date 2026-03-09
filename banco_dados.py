import requests
import json

# --- CONFIGURAÇÃO ---
SUPABASE_URL = "https://guttlccbfwdrpmeillqo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd1dHRsY2NiZndkcnBtZWlsbHFvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc2NTk5MzMsImV4cCI6MjA4MzIzNTkzM30.jYtwjIIHMOEKNSUDWb-tuKK_4o8dYar1bahVVO59AUE"

# Cabeçalhos obrigatórios para a API REST do Supabase
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal" # Retorna pouco dados no POST/PATCH para economizar dados
}

# =========================================================
# 1. GESTÃO DE CONTA (LOGIN, CADASTRO, RECUPERAÇÃO)
# =========================================================

def verificar_login(nome_usuario, senha_usuario):
    """Verifica nome e senha para login manual"""
    # Filtra por nome e senha exatos
    url = f"{SUPABASE_URL}/rest/v1/conta?nome=eq.{nome_usuario}&senha=eq.{senha_usuario}&select=*"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            usuarios = response.json()
            if len(usuarios) > 0:
                return True, "Login realizado!", usuarios[0]
            else:
                return False, "Usuário ou senha incorretos.", None
        return False, "Erro no servidor.", None
    except Exception as e:
        return False, "Erro de conexão.", None

def obter_usuario_por_id(user_id):
    """Busca dados do usuário pelo ID (usado no login automático/sessão)"""
    url = f"{SUPABASE_URL}/rest/v1/conta?id=eq.{user_id}&select=*"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            usuarios = response.json()
            if len(usuarios) > 0:
                return True, "Sucesso", usuarios[0]
        return False, "Usuário não encontrado", None
    except Exception as e:
        return False, str(e), None

def criar_conta(nome, senha, email):
    """Cria um novo usuário na tabela conta"""
    # 1. Verifica se o nome já existe
    check_url = f"{SUPABASE_URL}/rest/v1/conta?nome=eq.{nome}&select=id"
    try:
        resp_check = requests.get(check_url, headers=HEADERS, timeout=10)
        if resp_check.json():
            return False, "Este nome de usuário já existe."
    except:
        return False, "Erro ao verificar disponibilidade."

    # 2. Cria a conta
    dados = {"nome": nome, "senha": senha, "email": email}
    try:
        resp = requests.post(f"{SUPABASE_URL}/rest/v1/conta", headers=HEADERS, json=dados, timeout=10)
        # 201 Created ou 204 No Content são sucessos
        if resp.status_code in [200, 201, 204]:
            return True, "Sucesso!"
        else:
            return False, "Erro ao criar conta."
    except Exception as e:
        return False, f"Erro: {e}"

def verificar_dados_recuperacao(nome, email):
    """Verifica se nome e email batem para recuperação de senha"""
    url = f"{SUPABASE_URL}/rest/v1/conta?nome=eq.{nome}&email=eq.{email}&select=id"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        dados = resp.json()
        if dados:
            return True, dados[0]['id'] # Retorna o ID do usuário
        return False, "Dados inválidos."
    except:
        return False, "Erro de conexão."

def atualizar_senha(user_id, nova_senha):
    """Atualiza a senha do usuário via ID"""
    url = f"{SUPABASE_URL}/rest/v1/conta?id=eq.{user_id}"
    try:
        resp = requests.patch(url, headers=HEADERS, json={"senha": nova_senha}, timeout=10)
        if resp.status_code in [200, 204]:
            return True, "Sucesso"
        return False, "Erro ao atualizar"
    except:
        return False, "Erro conexão"

# =========================================================
# 2. SALVAMENTO DE JOGOS ESPECÍFICOS (SUDOKU, VELHA)
# =========================================================

def salvar_sudoku(user_id, pontos, erros, acertos, dificuldade, tempo_str, venceu):
    url = f"{SUPABASE_URL}/rest/v1/sudoku"
    dados = {
        "user_id": int(user_id),
        "pontos": int(pontos),
        "erros": int(erros),
        "acertos": int(acertos),
        "dificuldade": dificuldade,
        "tempo": str(tempo_str),
        "venceu": bool(venceu)
    }
    try:
        requests.post(url, headers=HEADERS, json=dados, timeout=5)
        return True, "Salvo"
    except:
        return False, "Erro"

def salvar_jogovelha(user_id, vitoria, derrota, empate, dificuldade, tempo_str):
    url = f"{SUPABASE_URL}/rest/v1/jogovelha"
    dados = {
        "user_id": int(user_id),
        "vitorias": 1 if vitoria else 0,
        "derrotas": 1 if derrota else 0,
        "empates": 1 if empate else 0,
        "dificuldade": dificuldade,
        "tempo": str(tempo_str)
    }
    try:
        requests.post(url, headers=HEADERS, json=dados, timeout=5)
        return True
    except:
        return False

# =========================================================
# 3. RANKING GERAL E SALVAMENTO DE PARTIDAS
# =========================================================

def salvar_partida(nome, escola, jogo, dificuldade, acertos, erros, tempo):
    """Salva partidas genéricas (Álgebra, Frações, Geometria, etc)"""
    url = f"{SUPABASE_URL}/rest/v1/partidas"
    dados = {
        "nome": nome,
        "escola": escola,
        "jogo": jogo,
        "dificuldade": dificuldade,
        "acertos": int(acertos),
        "erros": int(erros),
        "tempo": tempo
    }
    try:
        requests.post(url, headers=HEADERS, json=dados, timeout=5)
        return True, "Salvo com sucesso!"
    except:
        return False, "Erro ao salvar online"

def buscar_ranking(jogo=None, dificuldade=None):
    """Busca o ranking filtrado por jogo e dificuldade"""
    # Base da URL ordenando por acertos decrescente
    url = f"{SUPABASE_URL}/rest/v1/partidas?select=*&order=acertos.desc&limit=50"

    # Aplica filtros se eles existirem e não forem "Todos" ou None
    if jogo and jogo != "Todos" and jogo != "JOGO":
        # encode uri component simples (caso tenha espaços)
        url += f"&jogo=eq.{jogo}"

    if dificuldade and dificuldade != "Todos" and dificuldade != "NIVEL":
        url += f"&dificuldade=eq.{dificuldade}"

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def obter_ranking_unificado():
    url = f"{SUPABASE_URL}/rest/v1/ranking_global?select=*"
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []