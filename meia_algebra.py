import os
# Defina isso ANTES de importar o Kivy ou KivyMD
os.environ["KIVY_LOG_LEVEL"] = "info"
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen, SlideTransition, ScreenManager
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivymd.uix.button import MDIconButton, MDRectangleFlatButton, MDFillRoundFlatButton
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.slider import MDSlider
from kivy.uix.scrollview import ScrollView
import math
from kivymd.app import MDApp
from random import choice
from kivy.metrics import dp
import numpy as np
import matplotlib.pyplot as plt
from kivy_garden.matplotlib import FigureCanvasKivyAgg
import numpy as np

# Cores para padronizar os ícones (Paleta Material Design)
COR_AZUL = (0.2, 0.6, 1, 1)
COR_ROXA = (0.6, 0.4, 0.9, 1)
COR_LARANJA = (1, 0.6, 0.2, 1)
COR_VERDE = (0.3, 0.7, 0.4, 1)
COR_ROSA = (1, 0.3, 0.5, 1)
PRETO = (0, 0, 0, 1)
BRANCO_OFF = (0.98, 0.98, 0.98, 1)

# =================== TELA PRINCIPAL ÁLGEBRA ===================
class AlgebraTela(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # 1. Fundo
        try:
            fundo = Image(source="fundoapp.png", allow_stretch=True, keep_ratio=False, size_hint=(1, 1))
            layout.add_widget(fundo)
        except:
            pass

        # 2. Decoração de Fundo
        self.adicionar_decoracao_fundo(layout)

        # 3. Título e Boneco
        try:
            self.title_image = Image(
                source="Bonecos/titulo_algebra.webp",
                size_hint=(None, None),
                height=dp(80),
                width=dp(300),
                allow_stretch=True,
                keep_ratio=True,
                pos_hint={"center_x": 0.5, "top": 0.96},
            )
            layout.add_widget(self.title_image)

            boneco = Image(
                source="Bonecos/boneco_algebra.webp",
                size_hint=(0.45, 0.50),
                pos_hint={"center_x": 0.5, "center_y": 0.70}
            )
            layout.add_widget(boneco)
        except:
            pass # Se não tiver as imagens, o app não quebra

        # Botão voltar (Preto)
        self.back_button = MDIconButton(
            icon='arrow-left',
            pos_hint={'x': 0.02, 'top': 0.98},
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1), # Preto
            on_release=lambda x: self.voltar("conteudos")
        )
        layout.add_widget(self.back_button)

        # --- CARD CENTRAL ---
        card_principal = MDCard(
            size_hint=(0.9, 0.40),
            pos_hint={"center_x": 0.5, "y": 0.12},
            md_bg_color=(1, 1, 1, 0.3), # Fundo translúcido
            radius=[25],
            elevation=0,
            line_color=(0, 0, 0, 0.1), # Borda sutil preta
            line_width=1
        )

        container = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15)
        )

        # Subtítulo (Preto)
        container.add_widget(MDLabel(
            text="Escolha a atividade:",
            halign="center",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            font_style="Subtitle1",
            bold=True,
            size_hint_y=None,
            height=dp(30),
        ))

        # Botões Principais
        container.add_widget(self.create_icon_button(
            "Representações", "variable", lambda: self.ir_para("algebra_representacoes")
        ))

        container.add_widget(self.create_icon_button(
            "Definições", "book-open-variant", lambda: self.ir_para("algebra_definicoes")
        ))

        # Botão Jogar
        container.add_widget(self.create_icon_button(
            "Jogar", "gamepad-variant", lambda: self.ir_para("jogar")
        ))

        card_principal.add_widget(container)
        layout.add_widget(card_principal)

        self.add_widget(layout)

    # --- Funções Auxiliares ---
    def adicionar_decoracao_fundo(self, layout):
        """Ícones de álgebra escuros para preencher o vazio"""
        icones = ["variable", "function-variant", "sigma", "equal", "chart-bell-curve", "alpha", "beta"]
        positions = [
            {"x": 0.05, "y": 0.85}, {"x": 0.85, "y": 0.9},
            {"x": 0.1, "y": 0.6}, {"x": 0.85, "y": 0.6},
            {"x": 0.05, "y": 0.2}, {"x": 0.9, "y": 0.25}
        ]

        for pos in positions:
            icon = MDIconButton(
                icon=choice(icones),
                theme_text_color="Custom",
                text_color=(0, 0, 0, 0.08), # Preto marca d'água
                pos_hint=pos,
                icon_size=dp(45),
                disabled=True
            )
            layout.add_widget(icon)

    def create_icon_button(self, text, icon, callback):
        card = MDCard(
            size_hint=(1, None),
            height=dp(50),
            md_bg_color=(0.15, 0.25, 0.75, 0.9), # Azul padrão
            radius=[15],
            elevation=3,
            ripple_behavior=True,
            padding=[dp(15), 0, dp(10), 0]
        )

        row = BoxLayout(orientation="horizontal", spacing=dp(15))

        # Ícone Esquerdo
        row.add_widget(MDIconButton(
            icon=icon,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            pos_hint={'center_y': 0.5},
            disabled=True
        ))

        # Texto
        row.add_widget(MDLabel(
            text=text,
            halign="left",
            valign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            bold=True
        ))

        # Seta Direita
        row.add_widget(MDIconButton(
            icon="chevron-right",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 0.7),
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            pos_hint={'center_y': 0.5},
            disabled=True
        ))

        card.add_widget(row)
        card.on_release = lambda *a: callback()
        return card

    def ir_para(self, tela_nome):
        if self.manager:
            self.manager.transition = SlideTransition(direction="left", duration=0.4)
            self.manager.current = tela_nome

    def voltar(self, tela_nome):
        if self.manager:
            self.manager.transition = SlideTransition(direction="right", duration=0.4)
            self.manager.current = tela_nome

# =================== TELA REPRESENTAÇÕES ÁLGEBRA ===================
class AlgebraRepresentacoes(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        layout = FloatLayout()
        layout.add_widget(Image(source="fundoapp.png", allow_stretch=True, keep_ratio=False, size_hint=(1, 1)))

        # 2. Cabeçalho
        # Botão Voltar
        layout.add_widget(MDIconButton(
            icon="arrow-left",
            pos_hint={"x": 0.02, "center_y": 0.95},
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            on_release=self.voltar
        ))

        # Título da Tela
        layout.add_widget(MDLabel(
            text="FUNÇÕES",
            halign="center",
            pos_hint={"center_x": 0.5, "center_y": 0.95},
            font_style="H5",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            size_hint_y=None,
            height=dp(40)
        ))

        # 3. Card de Informações
        self.info_card = MDCard(
            size_hint=(0.95, 0.28),
            pos_hint={"center_x": 0.5, "top": 0.90},
            md_bg_color=(1, 1, 1, 0.95),
            radius=[15],
            padding=dp(10),
            elevation=4
        )

        box_info = BoxLayout(orientation="vertical", spacing=dp(5))

        self.lbl_equacao = MDLabel(
            text="f(x) = ...",
            halign="center",
            bold=True,
            font_style="H6",
            size_hint_y=None,
            height=dp(25),
            theme_text_color="Custom",
            text_color=(0.1, 0.3, 0.8, 1)
        )

        self.scroll_passos = ScrollView(do_scroll_x=False)
        self.lbl_passos = MDLabel(
            text="...",
            markup=True,
            size_hint_y=None,
            font_style="Body2",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 0.8)
        )
        self.lbl_passos.bind(texture_size=self.lbl_passos.setter('size'))

        self.scroll_passos.add_widget(self.lbl_passos)
        box_info.add_widget(self.lbl_equacao)
        box_info.add_widget(self.scroll_passos)

        self.info_card.add_widget(box_info)
        layout.add_widget(self.info_card)

        # 4. GRÁFICO MATPLOTLIB
        self.graph_box = BoxLayout(
            size_hint=(0.98, 0.38),
            pos_hint={"center_x": 0.5, "top": 0.61}
        )

        self.fig, self.ax = plt.subplots(dpi=100)
        self.fig.patch.set_alpha(0)
        self.ax.set_facecolor("#ffffffcc")
        self.ax.tick_params(axis='both', which='major', labelsize=16)

        self.graph_widget = FigureCanvasKivyAgg(self.fig)
        self.graph_box.add_widget(self.graph_widget)
        layout.add_widget(self.graph_box)

        # 5. Controles
        controls = BoxLayout(
            orientation="vertical",
            size_hint=(0.95, 0.22),
            pos_hint={"center_x": 0.5, "y": 0.01},
            spacing=dp(2)
        )

        # Botões de Tipo (1º e 2º Grau)
        btns = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(10))
        self.btn_1grau = MDFillRoundFlatButton(text="1º Grau", size_hint_x=0.5, on_release=lambda x: self.mudar_tipo("1grau"))
        self.btn_2grau = MDFillRoundFlatButton(text="2º Grau", size_hint_x=0.5, on_release=lambda x: self.mudar_tipo("2grau"))
        btns.add_widget(self.btn_1grau)
        btns.add_widget(self.btn_2grau)
        controls.add_widget(btns)

        # Sliders
        sliders = BoxLayout(orientation="vertical", spacing=dp(0))
        self.lbl_a = MDLabel(halign="center", font_style="Caption", size_hint_y=None, height=dp(15))
        self.slider_a = MDSlider(min=-5, max=5, value=1, step=0.5, size_hint_y=None, height=dp(20))

        self.lbl_b = MDLabel(halign="center", font_style="Caption", size_hint_y=None, height=dp(15))
        self.slider_b = MDSlider(min=-10, max=10, value=0, step=0.5, size_hint_y=None, height=dp(20))

        self.lbl_c = MDLabel(halign="center", font_style="Caption", opacity=0, size_hint_y=None, height=dp(15))
        self.slider_c = MDSlider(min=-10, max=10, value=0, step=0.5, disabled=True, opacity=0, size_hint_y=None, height=dp(20))

        for s in [self.slider_a, self.slider_b, self.slider_c]:
            s.bind(value=self.atualizar_grafico_bind)

        sliders.add_widget(self.lbl_a); sliders.add_widget(self.slider_a)
        sliders.add_widget(self.lbl_b); sliders.add_widget(self.slider_b)
        sliders.add_widget(self.lbl_c); sliders.add_widget(self.slider_c)
        controls.add_widget(sliders)

        # Botões Extras
        extras = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(5))

        self.btn_raizes = MDRectangleFlatButton(
            text="Raízes", size_hint_x=0.33,
            theme_text_color="Custom", text_color=(0, 0, 0, 1),
            line_color=(0, 0, 0, 1),
            on_release=self.mostrar_raizes
        )

        self.btn_inter = MDRectangleFlatButton(
            text="Intersec. Y", size_hint_x=0.33,
            theme_text_color="Custom", text_color=(0, 0, 0, 1),
            line_color=(0, 0, 0, 1),
            on_release=self.mostrar_interseccao
        )

        self.btn_vertice = MDRectangleFlatButton(
            text="Vértice", size_hint_x=0.33,
            theme_text_color="Custom", text_color=(0, 0, 0, 1),
            line_color=(0, 0, 0, 1),
            disabled=True, opacity=0,
            on_release=self.mostrar_vertice
        )

        extras.add_widget(self.btn_raizes)
        extras.add_widget(self.btn_inter)
        extras.add_widget(self.btn_vertice)
        controls.add_widget(extras)

        layout.add_widget(controls)
        self.add_widget(layout)

        self.tipo_atual = "1grau"
        self.mostrar_extras = []
        self.mudar_tipo("1grau")

    def mudar_tipo(self, tipo):
        self.tipo_atual = tipo
        self.mostrar_extras = []
        if tipo == "1grau":
            self.btn_1grau.md_bg_color = (0.2, 0.4, 0.9, 1); self.btn_2grau.md_bg_color = (0.6, 0.6, 0.6, 1)
            self.slider_c.disabled = True; self.slider_c.opacity = 0; self.lbl_c.opacity = 0
            self.btn_vertice.disabled = True; self.btn_vertice.opacity = 0
        else:
            self.btn_1grau.md_bg_color = (0.6, 0.6, 0.6, 1); self.btn_2grau.md_bg_color = (0.2, 0.4, 0.9, 1)
            self.slider_c.disabled = False; self.slider_c.opacity = 1; self.lbl_c.opacity = 1
            self.btn_vertice.disabled = False; self.btn_vertice.opacity = 1
        self.atualizar_grafico()

    def atualizar_grafico_bind(self, *args):
        Clock.unschedule(self.atualizar_grafico)
        Clock.schedule_once(self.atualizar_grafico, 0.05)

    def gerar_passo_a_passo(self, a, b, c):
        texto = ""
        # --- Lógica do 1º Grau ---
        if self.tipo_atual == "1grau":
            texto += f"[b]Função:[/b] {a:.2f}x + ({b:.2f}) = 0\n\n"
            if a == 0:
                texto += "Como a = 0, a função é constante.\nNão toca o eixo X."
            else:
                raiz = -b/a
                texto += f"1. Isolar o x:\n   {a:.2f}x = -({b:.2f})\n"
                texto += f"   {a:.2f}x = {-b:.2f}\n"
                texto += f"2. Dividir por a:\n   x = {-b:.2f} ÷ {a:.2f}\n"
                texto += f"   [b]x = {raiz:.2f}[/b]"

        # --- Lógica do 2º Grau ---
        else:
            if a == 0:
                return "[b]Atenção:[/b] Se a=0, não é função de 2º grau."

            # 1. Delta
            delta = b**2 - 4*a*c
            texto += f"[b]1. Delta (Δ):[/b]\n"
            texto += f"   Δ = b² - 4.a.c\n"
            texto += f"   Δ = ({b:.2f})² - 4 . ({a:.2f}) . ({c:.2f})\n"
            texto += f"   [b]Δ = {delta:.2f}[/b]\n\n"

            # 2. Bhaskara
            texto += f"[b]2. Bhaskara:[/b]\n"
            texto += f"   x = (-b ± √Δ) / 2a\n"

            if delta >= 0:
                raiz_delta = math.sqrt(delta)
                x1 = (-b + raiz_delta) / (2*a)
                x2 = (-b - raiz_delta) / (2*a)

                texto += f"   x' = {x1:.2f}\n"
                texto += f"   x'' = {x2:.2f}\n\n"
            else:
                texto += f"   Como Δ < 0, não existem raízes reais.\n\n"

            # 3. Vértice
            xv = -b / (2*a)
            yv = -delta / (4*a)
            texto += f"[b]3. Vértice:[/b]\n"
            texto += f"   Xv = {xv:.2f}\n"
            texto += f"   Yv = {yv:.2f}"
        return texto

    def atualizar_grafico(self, *args):
        self.ax.clear()
        self.ax.grid(True, linestyle="--", alpha=0.3)
        self.ax.axhline(0, color='black', linewidth=1.5)
        self.ax.axvline(0, color='black', linewidth=1.5)
        self.ax.tick_params(axis='both', which='major', labelsize=16)
        self.ax.set_xlim(-10, 10)
        self.ax.set_ylim(-10, 10)

        a, b, c = self.slider_a.value, self.slider_b.value, self.slider_c.value
        self.lbl_a.text = f"a={a:.2f}"; self.lbl_b.text = f"b={b:.2f}"; self.lbl_c.text = f"c={c:.2f}"

        x = np.linspace(-12, 12, 200)

        if self.tipo_atual == "1grau":
            y = a*x + b
            self.lbl_equacao.text = f"f(x) = {a:.2f}x + {b:.2f}"
            self.ax.set_title("Função Afim (1º Grau)", fontsize=22, fontweight='bold', pad=15)
        else:
            y = a*(x**2) + b*x + c
            self.lbl_equacao.text = f"f(x) = {a:.2f}x² + {b:.2f}x + {c:.2f}"
            self.ax.set_title("Função Quadrática", fontsize=22, fontweight='bold', pad=15)

        self.lbl_passos.text = self.gerar_passo_a_passo(a, b, c)
        self.ax.plot(x, y, label="f(x)", linewidth=2.5)

        if "raizes" in self.mostrar_extras:
            if self.tipo_atual == "1grau" and a!=0:
                self.ax.plot(-b/a, 0, 'ro', markersize=10, label="Raiz")
            elif self.tipo_atual == "2grau" and a!=0:
                delta = b**2 - 4*a*c
                if delta >= 0:
                    self.ax.plot((-b + np.sqrt(delta))/(2*a), 0, 'ro', markersize=10)
                    self.ax.plot((-b - np.sqrt(delta))/(2*a), 0, 'ro', markersize=10, label="Raízes")

        if "inter" in self.mostrar_extras:
            val = b if self.tipo_atual == "1grau" else c
            self.ax.plot(0, val, 'mo', markersize=10, label="Corta Y")

        if "vertice" in self.mostrar_extras and self.tipo_atual == "2grau" and a!=0:
            self.ax.plot(-b/(2*a), -(b**2-4*a*c)/(4*a), 'go', markersize=10, label="Vértice")

        self.ax.legend(fontsize=14, loc='upper right')
        self.graph_widget.draw()

    def mostrar_raizes(self, *args): self.mostrar_extras = ["raizes"]; self.atualizar_grafico()
    def mostrar_interseccao(self, *args): self.mostrar_extras = ["inter"]; self.atualizar_grafico()
    def mostrar_vertice(self, *args): self.mostrar_extras = ["vertice"]; self.atualizar_grafico()
    def voltar(self, *args): self.manager.transition.direction = "right"; self.manager.current = "algebra_tela"


# =================== TELA DEFINIÇÕES ÁLGEBRA (CORRIGIDA) ===================
class AlgebraDefinicoesTela(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 1. Estrutura Base
        layout = FloatLayout()
        
        try:
            fundo = Image(source="fundoapp.png", allow_stretch=True, keep_ratio=False, size_hint=(1, 1))
            layout.add_widget(fundo)
        except:
            pass 

        # 2. Cabeçalho
        header = MDBoxLayout(
            orientation="horizontal",
            size_hint=(1, None),
            height=dp(60),
            spacing=dp(10),
            padding=[dp(10), 0, dp(10), 0],
            pos_hint={"top": 1}
        )

        btn_voltar = MDIconButton(
            icon="arrow-left",
            theme_text_color="Custom",
            text_color=PRETO,
            on_release=self.voltar,
            pos_hint={'center_y': 0.5}
        )

        lbl_titulo = MDLabel(
            text="Definições de Álgebra",
            font_style="H5",
            bold=True,
            theme_text_color="Custom",
            text_color=PRETO,
            halign="left",
            valign="center",
            pos_hint={'center_y': 0.5}
        )

        header.add_widget(btn_voltar)
        header.add_widget(lbl_titulo)
        layout.add_widget(header)

        # 3. Área de Scroll (Conteúdo)
        scroll = ScrollView(
            size_hint=(1, 0.88),
            pos_hint={"top": 0.9, "center_x": 0.5},
            do_scroll_x=False,
            bar_width=0 
        )

        # Container vertical para os Cards
        self.container_conteudo = MDBoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(10), dp(20), dp(40)],
            spacing=dp(20),
            size_hint_y=None,
            adaptive_height=True
        )

        # --- ADICIONANDO OS CONTEÚDOS COM FÓRMULAS LEGÍVEIS ---
        
        self.adicionar_card_definicao(
            titulo="O que é Álgebra?",
            texto=("A Álgebra usa letras para representar números desconhecidos.\n\n"
                   "• [b]INCÓGNITA (x)[/b]: É o valor que queremos descobrir.\n"
                   "• [b]FUNÇÃO[/b]: Uma regra que relaciona cada valor de x a um resultado f(x)."),
            icone="variable-box",
            cor_icone=COR_AZUL
        )

        self.adicionar_card_definicao(
            titulo="Função de 1º Grau",
            texto=("É uma reta. A fórmula geral é:\n\n"
                   "   [size=20sp][b]f(x) = ax + b[/b][/size]\n\n"
                   "Para achar a raiz (onde corta o eixo X), basta igualar a zero e isolar o x."),
            icone="chart-line-variant",
            cor_icone=COR_VERDE
        )

        self.adicionar_card_definicao(
            titulo="Função de 2º Grau",
            texto=("O gráfico é uma curva chamada [b]Parábola[/b].\n"
                   "Fórmula Geral:\n\n"
                   "   [size=20sp][b]f(x) = ax² + bx + c[/b][/size]\n\n"
                   "• 'a' positivo: Sorriso (U)\n"
                   "• 'a' negativo: Triste (∩)"),
            icone="chart-bell-curve-cumulative",
            cor_icone=COR_LARANJA
        )

        # --- FÓRMULAS CORRIGIDAS (SEM LATEX) ---
        self.adicionar_card_definicao(
            titulo="Raízes (Bhaskara)",
            texto=("Usada para achar as raízes (onde a curva corta o eixo X).\n\n"
                   "1. [b]Delta (Δ)[/b]:\n"
                   "   Δ = b² - 4·a·c\n\n"
                   "2. [b]Fórmula de Bhaskara[/b]:\n"
                   "   [size=22sp]x = (-b ± √Δ) / 2a[/size]"), 
            icone="calculator-variant",
            cor_icone=COR_ROXA
        )

        self.adicionar_card_definicao(
            titulo="Vértice da Parábola",
            texto=("É o ponto de virada (máximo ou mínimo) da parábola.\n\n"
                   "• Coordenada X:\n"
                   "   [b]Xv = -b / 2a[/b]\n\n"
                   "• Coordenada Y:\n"
                   "   [b]Yv = -Δ / 4a[/b]"),
            icone="target",
            cor_icone=COR_ROSA
        )

        scroll.add_widget(self.container_conteudo)
        layout.add_widget(scroll)
        
        self.add_widget(layout)

    def voltar(self, instance):
        if self.manager:
            self.manager.transition = SlideTransition(direction="right", duration=0.4)
            self.manager.current = "algebra_tela"

    def adicionar_card_definicao(self, titulo, texto, icone, cor_icone):
        card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15),
            radius=[20],
            elevation=3,
            size_hint_y=None,
            adaptive_height=True,
            md_bg_color=BRANCO_OFF 
        )

        # Cabeçalho do Card (Ícone Colorido + Título)
        header_box = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(15),
            adaptive_height=True,
            size_hint_y=None
        )

        # Container do ícone
        icon_container = MDBoxLayout(
            size_hint=(None, None),
            size=(dp(42), dp(42)),
            md_bg_color=cor_icone,
            radius=[dp(21)],
            padding=dp(0),
        )

        # Ícone
        icon_btn = MDIconButton(
            icon=icone,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            icon_size=dp(22),
            size_hint=(1, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            disabled=True 
        )
        icon_container.add_widget(icon_btn)
        
        # Título
        lbl_titulo = MDLabel(
            text=titulo,
            font_style="Subtitle1",
            bold=True,
            theme_text_color="Custom", 
            text_color=PRETO, 
            valign="center",
            adaptive_height=True,
            pos_hint={"center_y": 0.5}
        )

        header_box.add_widget(icon_container)
        header_box.add_widget(lbl_titulo)

        # Corpo do Texto
        lbl_texto = MDLabel(
            text=texto,
            font_style="Body1", 
            theme_text_color="Custom",
            text_color=(0.2, 0.2, 0.2, 1), 
            adaptive_height=True,
            markup=True
        )

        card.add_widget(header_box)
        card.add_widget(lbl_texto)
        self.container_conteudo.add_widget(card)

