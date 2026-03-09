from manim import *

config.background_color = "#1E1E1E"
# Não precisamos de MathTex.set_default aqui

class ResolverEquacaoLinear(Scene):
    def construct(self):
        # Usando Text em vez de Tex/MathTex
        titulo = Text("Resolvendo a Equação", font_size=60)
        equacao_generica = Text("ax = b - c", font_size=72)
        VGroup(titulo, equacao_generica).arrange(DOWN, buff=1)

        self.play(Write(titulo))
        self.play(FadeIn(equacao_generica, shift=DOWN))
        self.wait(2)

        self.play(FadeOut(titulo), FadeOut(equacao_generica))
        self.wait(1)

        exemplo_titulo = Text("Exemplo:", font_size=48).to_edge(UP)
        equacao_inicial = Text("2x = 17 - 7", font_size=72)

        self.play(Write(exemplo_titulo))
        self.play(Write(equacao_inicial))
        self.wait(2)

        passo1_texto = Text("Passo 1: Simplificar", font_size=36).next_to(exemplo_titulo, DOWN, buff=0.5)
        self.play(Write(passo1_texto))

        # Para transformar, precisamos recriar os objetos
        equacao_simplificada = Text("2x = 10", font_size=72)
        self.play(ReplacementTransform(equacao_inicial, equacao_simplificada), FadeOut(passo1_texto))
        self.wait(2)

        passo2_texto = Text("Passo 2: Isolar 'x'", font_size=36).next_to(exemplo_titulo, DOWN, buff=0.5)
        self.play(Write(passo2_texto))

        # Como não temos frações bonitas, vamos mostrar a divisão de forma simples
        equacao_dividindo = Text("x = 10 / 2", font_size=72)
        self.play(ReplacementTransform(equacao_simplificada, equacao_dividindo))
        self.wait(2)

        solucao = Text("x = 5", font_size=72)
        self.play(FadeOut(passo2_texto), ReplacementTransform(equacao_dividindo, solucao))

        caixa_solucao = SurroundingRectangle(solucao, color=GREEN, buff=0.3)
        self.play(Create(caixa_solucao))
        self.wait(3)