
class GerenciadorErros:
    def __init__(self):
        self.erros = {}

        self.banco_de_dicas = {
            # --- ESTATÍSTICA ---
            "moda": "Dica: Revise sobre MODA. Lembre-se que é o item que mais aparece repetido!",
            "media": "Dica: A Média precisa de atenção. Lembre de somar tudo e dividir pela quantidade.",
            "probabilidade": "Dica: Estude Frações em Probabilidade (O que eu quero ÷ Total que existe).",

            # --- ÁLGEBRA ---
            "balanca": "Dica: Na álgebra, tudo que você tira de um lado do '=', deve tirar do outro!",
            "equacao": "Dica: Lembre-se de usar a operação matemática INVERSA para isolar o X.",
            "funcao_linear": "Dica: Em Gráficos, a inclinação muda o ângulo e a altura move a linha inteira.",

            # --- GEOMETRIA ---
            "formas": "Dica: Lembre-se dos prefixos gregos! Hexa = 6, Penta = 5, Octa = 8.",
            "area": "Dica: A área é o espaço interno. Tenha calma na hora de contar os quadrados.",
            "angulos": "Dica: Ângulo Reto = 90°, Linha Reta (Raso) = 180°. Triângulos somam 180°.",

            # --- FRAÇÕES ---
            "fracao_visual": "Dica: O número de baixo (Denominador) é em quantas partes o bloco foi cortado.",
            "simplificacao": "Dica: Para simplificar, procure dividir cima e baixo pela mesma tabuada.",
            "operacao_fracao": "Dica: Em somas de frações, lembre-se de analisar o denominador primeiro!",

            # --- PADRÃO CASO A CATEGORIA NÃO ESTEJA CADASTRADA ---
            "generico": "Dica: Continue praticando! O erro faz parte do aprendizado matemático."
        }

    def registrar_erro(self, categoria_erro):
        """Os jogos chamam essa função quando o jogador erra algo"""
        if categoria_erro not in self.erros:
            self.erros[categoria_erro] = 0
        self.erros[categoria_erro] += 1

    def obter_dica_final(self):
        """Gera a mensagem final com base no que o jogador mais errou"""
        # Se o dicionário de erros estiver vazio, ele não errou nada
        if not self.erros:
            return "Você não cometeu erros nesta rodada! Continue praticando e estudando"

        # Acha a categoria onde ele teve o MAIOR número de erros
        pior_categoria = max(self.erros, key=self.erros.get)

        if self.erros[pior_categoria] > 0:
            # Retorna a dica cadastrada, ou a genérica se alguém esquecer de cadastrar
            return self.banco_de_dicas.get(pior_categoria, self.banco_de_dicas["generico"])

        return "Perfeito! Você dominou o conteúdo!"