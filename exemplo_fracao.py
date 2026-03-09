from manim import *

class IntroducaoFracao(Scene):
    def construct(self):
        # Título
        titulo = Text("Como resolver soma de frações:", font_size=44)
        self.play(Write(titulo))
        self.wait(1)

        self.play(titulo.animate.to_edge(UP))

        # Criação das pizzas
        fracao1 = self.criar_pizza(2, 5).shift(LEFT * 3)
        fracao2 = self.criar_pizza(3, 2).shift(RIGHT * 3)

        label1 = Text("2/5", font_size=36).next_to(fracao1, DOWN)
        label2 = Text("3/2", font_size=36).next_to(fracao2, DOWN)

        self.play(Create(fracao1), Create(fracao2), Write(label1), Write(label2))
        self.wait(3)

        # Transição para a próxima etapa (ou cena)
        self.play(FadeOut(fracao1, fracao2, label1, label2, titulo))
        self.wait()

    def criar_pizza(self, numerador, denominador, raio=1.5):
        group = VGroup()
        angle_per_slice = 360 / denominador
        for i in range(denominador):
            cor = BLUE if i < numerador else GRAY
            fatia = Sector(
                start_angle=PI * i * angle_per_slice / 180,
                angle=PI * angle_per_slice / 180,
                outer_radius=raio,
                fill_opacity=0.8,
                fill_color=cor,
                stroke_color=BLACK
            )
            group.add(fatia)
        return group
