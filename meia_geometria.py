from kivy.uix.screenmanager import Screen, SlideTransition, ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Line
from kivy.graphics.vertex_instructions import Rectangle
from kivy.core.text import Label as CoreLabel
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.slider import MDSlider

import math
from random import choice

# ================= CORES VIBRANTES (PADRONIZADAS) =================
COR_AZUL_SOLIDO = (0.2, 0.6, 1, 1)
COR_VERDE_SOLIDO = (0.3, 0.7, 0.4, 1)
COR_LARANJA_SOLIDO = (1, 0.6, 0.2, 1)
COR_ROXA_SOLIDO = (0.6, 0.4, 0.9, 1)
COR_ROSA_SOLIDO = (1, 0.3, 0.5, 1)
BRANCO = (1, 1, 1, 1)
PRETO = (0, 0, 0, 1)
CINZA_TEXTO = (0.2, 0.2, 0.2, 1)
BRANCO_OFF = (0.98, 0.98, 0.98, 1)

# =================== TELA 1: MENU GEOMETRIA ===================
class GeometriaTela(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # 1. Fundo
        try:
            fundo = Image(source="fundoapp.png", allow_stretch=True, keep_ratio=False, size_hint=(1, 1))
            layout.add_widget(fundo)
        except:
            pass

        self.adicionar_decoracao_fundo(layout)

        try:
            self.title_image = Image(
                source="Bonecos/titulo_geometria.webp",
                size_hint=(None, None),
                height=dp(80),
                width=dp(300),
                allow_stretch=True,
                keep_ratio=True,
                pos_hint={"center_x": 0.5, "top": 0.96},
            )
            layout.add_widget(self.title_image)
        except:
            pass

        # Botão Voltar
        self.back_button = MDIconButton(
            icon='arrow-left',
            pos_hint={'x': 0.02, 'top': 0.98},
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1), 
            on_release=lambda x: self.voltar("conteudos")
        )
        layout.add_widget(self.back_button)

        # Boneco
        try:
            boneco = Image(
                source="Bonecos/boneco_geometria.webp",
                size_hint=(0.45, 0.50),
                pos_hint={"center_x": 0.5, "center_y": 0.70}
            )
            layout.add_widget(boneco)
        except:
            pass

        # --- CARD CENTRAL ---
        card_principal = MDCard(
            size_hint=(0.9, 0.40),
            pos_hint={"center_x": 0.5, "y": 0.12},
            md_bg_color=(1, 1, 1, 0.3), # Fundo translúcido
            radius=[25],
            elevation=0,
            line_color=(0, 0, 0, 0.1),
            line_width=1
        )

        container = BoxLayout(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15)
        )

        # Subtítulo do Card
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
            "Representações", "shape-outline", lambda: self.ir_para("geometria_representacoes")
        ))

        container.add_widget(self.create_icon_button(
            "Definições", "ruler-square", lambda: self.ir_para("geometria_definicoes")
        ))

        # Botão Jogar
        container.add_widget(self.create_icon_button(
            "Jogar", "gamepad-variant", lambda: self.ir_para("jogar")
        ))

        card_principal.add_widget(container)
        layout.add_widget(card_principal)

        self.add_widget(layout)

    def adicionar_decoracao_fundo(self, layout):
        icones = [
            "hexagon-outline", "triangle-outline", "square-outline",
            "circle-outline", "ruler", "protractor", "vector-square"
        ]
        positions = [
            {"x": 0.05, "y": 0.85}, {"x": 0.85, "y": 0.9},
            {"x": 0.1, "y": 0.6}, {"x": 0.85, "y": 0.6},
            {"x": 0.05, "y": 0.2}, {"x": 0.9, "y": 0.25}
        ]
        for pos in positions:
            icon = MDIconButton(
                icon=choice(icones),
                theme_text_color="Custom",
                text_color=(0, 0, 0, 0.08),
                pos_hint=pos,
                icon_size=dp(45),
                disabled=True
            )
            layout.add_widget(icon)

    def create_icon_button(self, text, icon, callback):
        card = MDCard(
            size_hint=(1, None),
            height=dp(50),
            md_bg_color=(0.15, 0.25, 0.75, 0.9),
            radius=[15],
            elevation=3,
            ripple_behavior=True,
            padding=[dp(15), 0, dp(10), 0]
        )

        row = BoxLayout(orientation="horizontal", spacing=dp(15))

        row.add_widget(MDIconButton(
            icon=icon,
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(dp(24), dp(24)),
            pos_hint={'center_y': 0.5},
            disabled=True
        ))

        row.add_widget(MDLabel(
            text=text,
            halign="left",
            valign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            bold=True
        ))

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


# =================== TELA 2: DEFINIÇÕES (PADRONIZADA) ===================
class GeometriaDefinicoesTela(Screen):
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
            text="Áreas e Perímetros",
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

        # 3. Área de Scroll
        scroll = ScrollView(
            size_hint=(1, 0.88),
            pos_hint={"top": 0.9, "center_x": 0.5},
            do_scroll_x=False,
            bar_width=0
        )

        # Container vertical
        self.container_conteudo = MDBoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(10), dp(20), dp(40)],
            spacing=dp(20),
            size_hint_y=None,
            adaptive_height=True
        )

        # --- CONTEÚDOS PADRONIZADOS ---

        # Quadrado (Azul)
        self.adicionar_card_definicao(
            titulo="Quadrado",
            texto=("Figura com 4 lados iguais e ângulos de 90°.\n"
                   "Lado = [b]L[/b]\n\n"
                   "[b]ÁREA (Preenchimento):[/b]\n"
                   "   A = L × L  ou  [b]L²[/b]\n\n"
                   "[b]PERÍMETRO (Contorno):[/b]\n"
                   "   P = 4 × L"),
            icone="square-rounded",
            cor_fundo=COR_AZUL_SOLIDO
        )

        # Retângulo (Verde)
        self.adicionar_card_definicao(
            titulo="Retângulo",
            texto=("Lados opostos iguais e paralelos.\n"
                   "Base = [b]b[/b], Altura = [b]h[/b]\n\n"
                   "[b]ÁREA:[/b]\n"
                   "   A = b × h\n\n"
                   "[b]PERÍMETRO:[/b]\n"
                   "   P = 2·b + 2·h"),
            icone="rectangle",
            cor_fundo=COR_VERDE_SOLIDO
        )

        # Triângulo (Laranja)
        self.adicionar_card_definicao(
            titulo="Triângulo",
            texto=("Polígono de 3 lados.\n\n"
                   "[b]ÁREA:[/b]\n"
                   "   A = (Base × Altura) / 2\n\n"
                   "[b]PERÍMETRO:[/b]\n"
                   "   P = Soma dos 3 lados"),
            icone="triangle",
            cor_fundo=COR_LARANJA_SOLIDO
        )

        # Círculo (Roxo)
        self.adicionar_card_definicao(
            titulo="Círculo",
            texto=("Definido pelo Raio ([b]r[/b]).\n"
                   "Considere π ≈ 3,14\n\n"
                   "[b]ÁREA:[/b]\n"
                   "   A = π × r²\n\n"
                   "[b]CIRCUNFERÊNCIA:[/b]\n"
                   "   C = 2 × π × r"),
            icone="circle",
            cor_fundo=COR_ROXA_SOLIDO
        )

        # Trapézio (Rosa)
        self.adicionar_card_definicao(
            titulo="Trapézio",
            texto=("Possui duas bases paralelas.\n"
                   "B = Base Maior, b = Base Menor, h = Altura\n\n"
                   "[b]ÁREA:[/b]\n"
                   "   A = ((B + b) × h) / 2\n\n"
                   "[b]PERÍMETRO:[/b]\n"
                   "   P = Soma dos 4 lados"),
            icone="vector-polygon",
            cor_fundo=COR_ROSA_SOLIDO
        )

        scroll.add_widget(self.container_conteudo)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def voltar(self, instance):
        if self.manager:
            self.manager.transition = SlideTransition(direction="right", duration=0.4)
            self.manager.current = "geometria_tela"

    def adicionar_card_definicao(self, titulo, texto, icone, cor_fundo):
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

        # Cabeçalho
        header_box = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(15),
            adaptive_height=True,
            size_hint_y=None
        )

        # Container do ícone (Círculo colorido)
        icon_container = MDCard(
            size_hint=(None, None),
            size=(dp(42), dp(42)),
            radius=[dp(21)], 
            md_bg_color=cor_fundo,
            elevation=0,
            padding=0,
        )

        # FloatLayout para centralização perfeita
        icon_wrapper = FloatLayout(size_hint=(1, 1))

        icon_widget = MDIcon(
            icon=icone,
            theme_text_color="Custom",
            text_color=BRANCO,
            font_size=dp(24),
            halign="center",
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        icon_wrapper.add_widget(icon_widget)
        icon_container.add_widget(icon_wrapper)

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

        # Texto
        lbl_texto = MDLabel(
            text=texto,
            font_style="Body1",
            theme_text_color="Custom",
            text_color=CINZA_TEXTO,
            adaptive_height=True,
            markup=True,
            line_height=1.3
        )

        card.add_widget(header_box)
        card.add_widget(lbl_texto)
        self.container_conteudo.add_widget(card)


# =================== TELA 3: REPRESENTAÇÕES (SIMULADOR) ===================
class GeometriaRepresentacoes(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # 1. Fundo
        try:
            fundo = Image(source="fundoapp.png", allow_stretch=True, keep_ratio=False, size_hint=(1, 1))
            layout.add_widget(fundo)
        except:
            pass
        self.adicionar_decoracao_fundo(layout)

        # 2. Cabeçalho
        layout.add_widget(MDIconButton(
            icon="arrow-left", pos_hint={"x": 0.02, "top": 0.98},
            theme_text_color="Custom", text_color=(0, 0, 0, 1),
            on_release=lambda x: self.voltar("geometria_tela")
        ))

        # Título
        self.title_label = Label(
            text="GEOMETRIA", color=(0, 0, 0, 1),
            font_size="28sp", size_hint=(1, None), height=dp(60),
            pos_hint={"center_x": 0.5, "top": 0.96},
            bold=True
        )
        layout.add_widget(self.title_label)

        # 3. CARD DE INFORMAÇÕES
        self.info_card = MDCard(
            size_hint=(0.95, 0.28),
            pos_hint={"center_x": 0.5, "top": 0.88},
            md_bg_color=(1, 1, 1, 0.95), radius=[15], elevation=4,
            orientation="vertical", padding=[dp(15), dp(5)]
        )

        self.lbl_titulo_forma = MDLabel(
            text="Selecione uma forma", halign="center", theme_text_color="Custom",
            text_color=(0, 0, 0, 1), font_style="H6", bold=True, size_hint_y=None, height=dp(30)
        )
        self.info_card.add_widget(self.lbl_titulo_forma)

        self.scroll_passos = ScrollView(size_hint=(1, 1))
        self.lbl_passos = MDLabel(
            text="...", halign="left", valign="top", theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1), font_style="Body1",
            size_hint_y=None, markup=True
        )
        self.lbl_passos.bind(texture_size=self.lbl_passos.setter('size'))
        self.scroll_passos.add_widget(self.lbl_passos)
        self.info_card.add_widget(self.scroll_passos)
        layout.add_widget(self.info_card)

        # 4. ÁREA DE DESENHO
        self.drawing_container = MDCard(
            size_hint=(0.9, 0.28),
            pos_hint={"center_x": 0.5, "top": 0.58},
            md_bg_color=(1, 1, 1, 1), radius=[15], elevation=2
        )
        self.drawing_area = Widget()
        self.drawing_container.add_widget(self.drawing_area)
        layout.add_widget(self.drawing_container)

        # 5. CONTROLES INFERIORES
        controls_layout = BoxLayout(
            orientation="vertical", size_hint=(0.95, 0.28),
            pos_hint={"center_x": 0.5, "y": 0.01}, spacing=dp(5)
        )

        # Container dos Sliders
        self.sliders_container = BoxLayout(
            orientation="vertical", size_hint_y=0.65,
            padding=[dp(5), 0], spacing=dp(2)
        )
        controls_layout.add_widget(self.sliders_container)

        # Botões de Seleção
        shapes_box = BoxLayout(orientation="horizontal", spacing=dp(15), size_hint_y=0.35, padding=[0, dp(5)])

        formas = [
            ("Quadrado", "square-outline", "square"),
            ("Retângulo", "rectangle-outline", "rectangle"),
            ("Triângulo", "triangle-outline", "triangle"),
            ("Círculo", "circle-outline", "circle")
        ]

        for nome, icone, id_forma in formas:
            btn = MDIconButton(
                icon=icone, theme_text_color="Custom", text_color=(1, 1, 1, 1),
                md_bg_color=(0.2, 0.4, 0.9, 1), icon_size="28sp",
                size_hint=(None, None), size=(dp(45), dp(45)),
                pos_hint={"center_y": 0.5},
                on_release=lambda x, f=id_forma: self.selecionar_forma(f)
            )
            shapes_box.add_widget(btn)

        # Trapézio
        btn_trap = MDIconButton(
            icon="vector-square", theme_text_color="Custom", text_color=(1, 1, 1, 1),
            md_bg_color=(0.2, 0.4, 0.9, 1), icon_size="28sp",
            size_hint=(None, None), size=(dp(45), dp(45)), pos_hint={"center_y": 0.5},
            on_release=lambda x: self.selecionar_forma("trapezoid")
        )
        shapes_box.add_widget(btn_trap)

        controls_layout.add_widget(shapes_box)
        layout.add_widget(controls_layout)
        self.add_widget(layout)

        # Estado Inicial
        self.forma_atual = None
        self.sliders_refs = {}
        Clock.schedule_once(lambda dt: self.selecionar_forma("square"), 0.1)

    def adicionar_decoracao_fundo(self, layout):
        pass 

    def selecionar_forma(self, forma):
        self.forma_atual = forma
        self.sliders_container.clear_widgets()
        self.sliders_refs = {}

        configs = {
            "circle": [("Raio", 10, 50, 30)],
            "square": [("Lado", 20, 80, 50)],
            "rectangle": [("Base", 20, 100, 60), ("Altura", 20, 80, 40)],
            "triangle": [("Base", 20, 100, 60), ("Altura", 20, 80, 50)],
            "trapezoid": [("Base Maior", 30, 100, 70), ("Base Menor", 15, 60, 40), ("Altura", 20, 60, 40)]
        }

        for nome, min_v, max_v, val_inicial in configs[forma]:
            card_slider = MDCard(
                orientation="horizontal", size_hint_y=None, height=dp(35),
                radius=[10], md_bg_color=(1, 1, 1, 0.9), elevation=1, padding=[dp(10), 0]
            )
            lbl = MDLabel(text=f"{nome}: {val_inicial}", size_hint_x=0.45, theme_text_color="Custom", text_color=(0,0,0,1), bold=True, font_style="Caption")
            sld = MDSlider(min=min_v, max=max_v, value=val_inicial, step=1, size_hint_x=0.55, color=(0.2, 0.4, 0.9, 1))
            sld.bind(value=lambda instance, v, n=nome, l=lbl: self.atualizar_valores(n, v, l))
            card_slider.add_widget(lbl); card_slider.add_widget(sld)
            self.sliders_container.add_widget(card_slider)
            self.sliders_refs[nome] = sld

        traducoes = {"circle": "Círculo", "square": "Quadrado", "rectangle": "Retângulo", "triangle": "Triângulo", "trapezoid": "Trapézio"}
        self.lbl_titulo_forma.text = traducoes.get(forma, forma)
        self.desenhar_forma()

    def atualizar_valores(self, nome, valor, label):
        label.text = f"{nome}: {int(valor)}"
        self.desenhar_forma()

    def desenhar_texto_canvas(self, texto, x, y):
        label = CoreLabel(text=texto, font_size=20, color=(0, 0, 0, 1), bold=True)
        label.refresh()
        texture = label.texture
        if texture:
            Color(1, 1, 1, 0.6)
            Rectangle(pos=(x, y), size=texture.size)
            Color(0, 0, 0, 1)
            Rectangle(texture=texture, pos=(x, y), size=texture.size)

    def desenhar_forma(self):
        self.drawing_area.canvas.clear()
        cx, cy = self.drawing_area.center_x, self.drawing_area.center_y
        vals = {k: v.value for k, v in self.sliders_refs.items()}

        ZOOM = 4.5
        texto_passo = ""
        fmt = lambda x: f"{x:.0f}"

        with self.drawing_area.canvas:
            Color(0.2, 0.4, 0.9, 1) # Azul

            if self.forma_atual == "circle":
                r = vals["Raio"]
                r_vis = r * ZOOM
                Line(circle=(cx, cy, r_vis), width=2.5)
                Color(1, 0, 0, 1)
                Line(points=[cx, cy, cx + r_vis, cy], width=2)
                self.desenhar_texto_canvas(f"R: {fmt(r)}", cx + r_vis/2 - 15, cy + 8)
                texto_passo = f"[b]Círculo:[/b]\nA = π.r² = 3,14 x {fmt(r)}² = [b]{math.pi * r**2:.1f}[/b]\nC = 2.π.r = [b]{2 * math.pi * r:.1f}[/b]"

            elif self.forma_atual == "square":
                l = vals["Lado"]
                l_vis = l * ZOOM
                Line(rectangle=(cx - l_vis/2, cy - l_vis/2, l_vis, l_vis), width=2.5)
                self.desenhar_texto_canvas(f"L: {fmt(l)}", cx - l_vis/2 - 30, cy)
                texto_passo = f"[b]Quadrado:[/b]\nA = L² = {fmt(l)}² = [b]{l**2:.0f}[/b]\nP = 4 x L = [b]{4*l:.0f}[/b]"

            elif self.forma_atual == "rectangle":
                b, h = vals["Base"], vals["Altura"]
                b_vis, h_vis = b * ZOOM, h * ZOOM
                Line(rectangle=(cx - b_vis/2, cy - h_vis/2, b_vis, h_vis), width=2.5)
                self.desenhar_texto_canvas(f"{fmt(b)}", cx, cy - h_vis/2 - 25)
                self.desenhar_texto_canvas(f"{fmt(h)}", cx + b_vis/2 + 10, cy)
                texto_passo = f"[b]Retângulo:[/b]\nA = b x h = {fmt(b)} x {fmt(h)} = [b]{b*h:.0f}[/b]\nP = 2b + 2h = [b]{2*b + 2*h:.0f}[/b]"

            elif self.forma_atual == "triangle":
                b, h = vals["Base"], vals["Altura"]
                b_vis, h_vis = b * ZOOM, h * ZOOM
                pts = [cx - b_vis/2, cy - h_vis/2, cx + b_vis/2, cy - h_vis/2, cx, cy + h_vis/2, cx - b_vis/2, cy - h_vis/2]
                Line(points=pts, width=2.5)
                Color(0.5, 0.5, 0.5, 1)
                Line(points=[cx, cy + h_vis/2, cx, cy - h_vis/2], width=1.5, dash_length=5)
                self.desenhar_texto_canvas(f"h:{fmt(h)}", cx + 5, cy)
                self.desenhar_texto_canvas(f"b:{fmt(b)}", cx, cy - h_vis/2 - 25)
                area = (b * h) / 2
                lado = math.sqrt((b/2)**2 + h**2)
                texto_passo = f"[b]Triângulo:[/b]\nA = (b x h)/2 = [b]{area:.1f}[/b]\nP ≈ {fmt(b)} + {lado:.1f} + {lado:.1f} = [b]{b + 2*lado:.1f}[/b]"

            elif self.forma_atual == "trapezoid":
                B, b_menor, h = vals["Base Maior"], vals["Base Menor"], vals["Altura"]
                B_vis, b_vis, h_vis = B*ZOOM, b_menor*ZOOM, h*ZOOM
                pts = [cx - B_vis/2, cy - h_vis/2, cx + B_vis/2, cy - h_vis/2, cx + b_vis/2, cy + h_vis/2, cx - b_vis/2, cy + h_vis/2, cx - B_vis/2, cy - h_vis/2]
                Line(points=pts, width=2.5)
                self.desenhar_texto_canvas(f"b:{fmt(b_menor)}", cx, cy + h_vis/2 + 5)
                self.desenhar_texto_canvas(f"B:{fmt(B)}", cx, cy - h_vis/2 - 25)
                self.desenhar_texto_canvas(f"h:{fmt(h)}", cx + B_vis/4, cy)
                area = ((B + b_menor) * h) / 2
                lado = math.sqrt(((B-b_menor)/2)**2 + h**2)
                texto_passo = f"[b]Trapézio:[/b]\nA = ((B+b)xh)/2 = [b]{area:.1f}[/b]\nP ≈ [b]{B + b_menor + 2*lado:.1f}[/b]"

        self.lbl_passos.text = texto_passo

    def ir_para(self, tela_nome):
        if self.manager:
            self.manager.transition = SlideTransition(direction="left", duration=0.4)
            self.manager.current = tela_nome

    def voltar(self, tela_nome):
        if self.manager:
            self.manager.transition = SlideTransition(direction="right", duration=0.4)
            self.manager.current = tela_nome

