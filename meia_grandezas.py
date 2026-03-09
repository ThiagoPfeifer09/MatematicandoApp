from kivy.uix.screenmanager import Screen, SlideTransition, ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.utils import get_color_from_hex
from kivy.core.text import LabelBase
from random import choice
import os

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.slider import MDSlider
from kivy.uix.anchorlayout import AnchorLayout

# ================= REGISTRO DE FONTE =================
try:
    font_path = os.path.join(os.path.dirname(__file__), "Fontes", "Duo-Dunkel.ttf")
except NameError:
    font_path = os.path.join(os.getcwd(), "Fontes", "Duo-Dunkel.ttf")

NOME_FONTE_TITULO = "Roboto" 

if os.path.exists(font_path):
    LabelBase.register(name="BungeeShade", fn_regular=font_path)
    NOME_FONTE_TITULO = "BungeeShade"

# ================= CORES VIBRANTES =================
COR_VERDE = (0.3, 0.7, 0.3, 1)   # Comprimento
COR_ROXA = (0.6, 0.3, 0.9, 1)    # Massa
COR_AZUL = (0.1, 0.5, 0.9, 1)    # Volume
COR_LARANJA = (1, 0.6, 0.0, 1)   # Tempo
COR_VERMELHO = (0.9, 0.3, 0.3, 1)# Temperatura
BRANCO = (1, 1, 1, 1)
PRETO = (0, 0, 0, 1)
CINZA_TEXTO = (0.2, 0.2, 0.2, 1)
BRANCO_OFF = (0.98, 0.98, 0.98, 1)

# =================================================================================
# FUNÇÃO AUXILIAR PADRONIZADA (IGUAL ÀS OUTRAS TELAS)
# =================================================================================
def criar_card_definicao(titulo, texto, icone, cor_icone):
    """
    Cria um card com design padronizado: Ícone em círculo colorido + Título + Texto.
    """
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

    # Cabeçalho Horizontal
    header_box = MDBoxLayout(
        orientation="horizontal",
        spacing=dp(15),
        adaptive_height=True,
        size_hint_y=None
    )

    # Container do ícone (Círculo colorido)
    icon_container = MDBoxLayout(
        size_hint=(None, None),
        size=(dp(42), dp(42)),
        md_bg_color=cor_icone,
        radius=[dp(21)],
        padding=dp(0),
    )

    # Ícone Centralizado
    icon_btn = MDIconButton(
        icon=icone,
        theme_text_color="Custom",
        text_color=BRANCO,
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
        text_color=CINZA_TEXTO,
        adaptive_height=True,
        markup=True,
        line_height=1.3
    )

    card.add_widget(header_box)
    card.add_widget(lbl_texto)
    return card


# =================== TELA 1: MENU GRANDEZAS ===================
class GrandezasTela(Screen):
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
                source="Bonecos/titulo_grandezas.webp",
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
                source="Bonecos/Boneco_Grandezas.webp",
                size_hint=(0.47, 0.47),
                pos_hint={"center_x": 0.5, "center_y": 0.70}
            )
            layout.add_widget(boneco)
        except:
            pass

        # --- CARD CENTRAL ---
        card_principal = MDCard(
            size_hint=(0.9, 0.40),
            pos_hint={"center_x": 0.5, "y": 0.12},
            md_bg_color=(1, 1, 1, 0.3),
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

        # Subtítulo
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
            "Representações", "ruler", lambda: self.ir_para("grandezas_representacoes")
        ))

        container.add_widget(self.create_icon_button(
            "Definições", "scale-balance", lambda: self.ir_para("grandezas_definicoes")
        ))

        # Botão Jogar
        container.add_widget(self.create_icon_button(
            "Jogar", "gamepad-variant", lambda: self.ir_para("jogar")
        ))

        card_principal.add_widget(container)
        layout.add_widget(card_principal)

        self.add_widget(layout)

    def adicionar_decoracao_fundo(self, layout):
        icones = ["ruler", "scale-balance", "timer-outline", "thermometer", "tape-measure", "weight-kilogram"]
        positions = [{"x": 0.05, "y": 0.85}, {"x": 0.85, "y": 0.9}, {"x": 0.1, "y": 0.6}, {"x": 0.85, "y": 0.6}, {"x": 0.05, "y": 0.2}, {"x": 0.9, "y": 0.25}]
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
class GrandezasDefinicoesTela(Screen):
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
            text="Medidas e Conversões", 
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
            pos_hint={"bottom": 0, "center_x": 0.5},
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

        # --- ADICIONANDO OS CARDS PADRONIZADOS ---

        # Comprimento (Verde)
        self.container_conteudo.add_widget(criar_card_definicao(
            titulo="Comprimento",
            texto=("A unidade base é o [b]Metro (m)[/b].\n"
                   "Usamos base 10 para transformar.\n\n"
                   "[b]REGRA PRÁTICA:[/b]\n"
                   "• Maior p/ Menor (km → m): [b]× 1000[/b]\n"
                   "• Menor p/ Maior (m → km): [b]÷ 1000[/b]\n\n"
                   "[i]Ex: 1 km = 1.000 metros[/i]"),
            icone="ruler",
            cor_icone=COR_VERDE
        ))

        # Massa (Roxa)
        self.container_conteudo.add_widget(criar_card_definicao(
            titulo="Massa",
            texto=("Mede a quantidade de matéria. Unidade padrão: [b]Quilograma (kg)[/b].\n\n"
                   "[b]CONVERSÕES:[/b]\n"
                   "• 1 kg = 1.000 g (gramas)\n"
                   "• 1 tonelada = 1.000 kg\n\n"
                   "Para passar de kg para g, basta multiplicar por 1000."),
            icone="weight-kilogram",
            cor_icone=COR_ROXA
        ))

        # Volume (Azul)
        self.container_conteudo.add_widget(criar_card_definicao(
            titulo="Volume e Capacidade",
            texto=("Para líquidos, usamos o [b]Litro (L)[/b].\n\n"
                   "[b]PRINCIPAIS:[/b]\n"
                   "• 1 Litro = 1.000 ml (Mililitros)\n"
                   "• 1 m³ = 1.000 Litros\n\n"
                   "[i]Curiosidade: 1 litro de água ocupa um cubo de 10x10x10 cm.[/i]"),
            icone="cup-water",
            cor_icone=COR_AZUL
        ))

        # Tempo (Laranja)
        self.container_conteudo.add_widget(criar_card_definicao(
            titulo="Tempo",
            texto=("O tempo usa o sistema [b]sexagesimal[/b] (base 60), não decimal!\n\n"
                   "[b]TABELA:[/b]\n"
                   "• 1 Hora = 60 minutos\n"
                   "• 1 Minuto = 60 segundos\n\n"
                   "[b]Atenção:[/b] 1,5 horas são 1h e 30min, não 1h e 50min!"),
            icone="clock-time-four-outline",
            cor_icone=COR_LARANJA
        ))

        # Temperatura (Vermelho)
        self.container_conteudo.add_widget(criar_card_definicao(
            titulo="Temperatura",
            texto=("Mede a agitação das moléculas. No Brasil usamos [b]Celsius (°C)[/b].\n\n"
                   "[b]PONTOS CHAVE:[/b]\n"
                   "• 0°C: Congelamento da água\n"
                   "• 100°C: Ebulição (fervura)\n\n"
                   "Nos EUA, usa-se Fahrenheit (°F)."),
            icone="thermometer",
            cor_icone=COR_VERMELHO
        ))

        scroll.add_widget(self.container_conteudo)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def voltar(self, instance):
        if self.manager:
            self.manager.transition = SlideTransition(direction="right", duration=0.4)
            self.manager.current = "grandezas_tela"


# =================== TELA 3: REPRESENTAÇÕES (CONVERSOR) ===================
class GrandezasRepresentacoes(Screen):
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
            icon="arrow-left",
            pos_hint={"x": 0.02, "top": 0.98},
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            on_release=lambda x: self.voltar("grandezas_tela")
        ))

        self.title_label = Label(
            text="CONVERSOR",
            color=(0, 0, 0, 1),
            font_name=NOME_FONTE_TITULO,
            font_size="28sp",
            size_hint=(1, None),
            height=dp(60),
            pos_hint={"center_x": 0.5, "top": 0.96},
        )
        layout.add_widget(self.title_label)

        # 3. ÁREA VISUAL HERO
        self.hero_box = BoxLayout(
            orientation="vertical",
            size_hint=(1, 0.25),
            pos_hint={"center_x": 0.5, "top": 0.85},
            padding=[0, dp(10), 0, 0]
        )

        self.hero_icon = MDIconButton(
            icon="ruler",
            icon_size="90sp",
            pos_hint={"center_x": 0.5},
            theme_text_color="Custom",
            text_color=(0.2, 0.6, 0.4, 1),
            disabled=True
        )
        self.hero_box.add_widget(self.hero_icon)

        self.hero_value = MDLabel(
            text="10 m",
            halign="center",
            font_style="H3",
            theme_text_color="Custom",
            text_color=(0.2, 0.6, 0.4, 1),
            bold=True
        )
        self.hero_box.add_widget(self.hero_value)

        layout.add_widget(self.hero_box)

        # 4. CARD DE CONTROLE E RESULTADO
        self.panel_card = MDCard(
            orientation="vertical",
            size_hint=(0.92, 0.55),
            pos_hint={"center_x": 0.5, "y": 0.02},
            radius=[25],
            md_bg_color=(1, 1, 1, 0.95),
            elevation=6,
            padding=dp(20),
            spacing=dp(10)
        )

        lbl_slider = MDLabel(text="Ajuste o valor:", font_style="Caption", halign="center", size_hint_y=None, height=dp(20))
        self.panel_card.add_widget(lbl_slider)

        self.slider = MDSlider(
            min=0, max=100, value=10,
            color=(0.2, 0.6, 0.4, 1),
            size_hint_y=None,
            height=dp(40)
        )
        self.slider.bind(value=self.atualizar_interface)
        self.panel_card.add_widget(self.slider)

        self.scroll_res = ScrollView(size_hint=(1, 1))

        self.lbl_resultados = MDLabel(
            text="Selecione uma categoria...",
            halign="center",
            valign="top",
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1),
            font_style="Body1",
            markup=True,
            size_hint_y=None,
            padding=[0, dp(10)]
        )
        self.lbl_resultados.bind(texture_size=self.lbl_resultados.setter('size'))
        self.scroll_res.add_widget(self.lbl_resultados)
        self.panel_card.add_widget(self.scroll_res)

        box_botoes = MDBoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint=(1, None),
            height=dp(60),
            padding=[dp(5), dp(5)]
        )

        categorias = [
            ("Comprimento", "ruler", "#4CAF50"),
            ("Massa", "weight-kilogram", "#9C27B0"),
            ("Volume", "cup-water", "#2196F3"),
            ("Tempo", "clock-outline", "#FF9800"),
            ("Temperatura", "thermometer", "#F44336")
        ]

        self.btns_dict = {}
        for nome, icone, cor in categorias:
            wrapper = AnchorLayout(anchor_x='center', anchor_y='center')
            btn = MDIconButton(
                icon=icone,
                icon_size="26sp",
                theme_text_color="Custom",
                text_color=get_color_from_hex(cor),
                md_bg_color=(0.95, 0.95, 0.95, 1),
                size_hint=(None, None),
                size=(dp(48), dp(48)),
                on_release=lambda x, n=nome, c=cor, i=icone: self.mudar_categoria(n, c, i)
            )
            self.btns_dict[nome] = btn
            wrapper.add_widget(btn)
            box_botoes.add_widget(wrapper)

        self.panel_card.add_widget(box_botoes)

        layout.add_widget(self.panel_card)
        self.add_widget(layout)

        # Estado Inicial
        self.cat_atual = "Comprimento"
        self.cor_atual = "#4CAF50"
        self.mudar_categoria("Comprimento", "#4CAF50", "ruler")

    def adicionar_decoracao_fundo(self, layout):
        icones = ["ruler", "flask", "clock", "scale", "thermometer"]
        positions = [{"x": 0.1, "y": 0.8}, {"x": 0.9, "y": 0.85}, {"x": 0.15, "y": 0.2}, {"x": 0.85, "y": 0.25}]
        for pos in positions:
            layout.add_widget(MDIconButton(
                icon=choice(icones), theme_text_color="Custom",
                text_color=(0,0,0,0.05), pos_hint=pos,
                icon_size=dp(60), disabled=True
            ))

    def mudar_categoria(self, nome, cor_hex, icone):
        self.cat_atual = nome
        self.cor_atual = cor_hex
        rgba = get_color_from_hex(cor_hex)

        self.hero_icon.icon = icone
        self.hero_icon.text_color = rgba
        self.hero_value.text_color = rgba
        self.slider.color = rgba

        for n, btn in self.btns_dict.items():
            if n == nome:
                btn.md_bg_color = (rgba[0], rgba[1], rgba[2], 0.2)
                btn.icon_size = "34sp"
            else:
                btn.md_bg_color = (0.95, 0.95, 0.95, 1)
                btn.icon_size = "26sp"

        if nome == "Temperatura":
            self.slider.min = 0; self.slider.max = 100; self.slider.value = 25
        elif nome == "Tempo":
            self.slider.min = 1; self.slider.max = 120; self.slider.value = 60
        else:
            self.slider.min = 1; self.slider.max = 100; self.slider.value = 10

        self.atualizar_interface()

    def atualizar_interface(self, *args):
        val = int(self.slider.value)
        g = self.cat_atual
        texto = ""
        simbolo_base = ""

        if g == "Comprimento":
            simbolo_base = "m"
            cm = val * 100
            km = val / 1000
            texto = (
                f"[size=20][b]Conversões de Metro:[/b][/size]\n\n"
                f"[color={self.cor_atual}]• {cm} cm[/color] (Centímetros)\n"
                f"  [i](Multiplicamos por 100)[/i]\n\n"
                f"[color={self.cor_atual}]• {km:.3f} km[/color] (Quilômetros)\n"
                f"  [i](Dividimos por 1000)[/i]"
            )
        elif g == "Massa":
            simbolo_base = "kg"
            g_total = val * 1000
            t = val / 1000
            texto = (
                f"[size=20][b]Conversões de Massa:[/b][/size]\n\n"
                f"[color={self.cor_atual}]• {g_total} g[/color] (Gramas)\n"
                f"  [i](Multiplicamos por 1000)[/i]\n\n"
                f"[color={self.cor_atual}]• {t:.3f} t[/color] (Toneladas)\n"
                f"  [i](Dividimos por 1000)[/i]"
            )
        elif g == "Volume":
            simbolo_base = "L"
            ml = val * 1000
            texto = (
                f"[size=20][b]Conversões de Volume:[/b][/size]\n\n"
                f"[color={self.cor_atual}]• {ml} mL[/color] (Mililitros)\n"
                f"  [i](Multiplicamos por 1000)[/i]\n\n"
                f"[color={self.cor_atual}]• {val} dm³[/color] (Decímetros cúbicos)\n"
                f"  [i](É equivalente: 1 L = 1 dm³)[/i]"
            )
        elif g == "Tempo":
            simbolo_base = "min"
            seg = val * 60
            h = val // 60
            min_rest = val % 60
            texto = (
                f"[size=20][b]Conversões de Tempo:[/b][/size]\n\n"
                f"[color={self.cor_atual}]• {seg} s[/color] (Segundos)\n"
                f"  [i](Multiplicamos por 60)[/i]\n\n"
                f"[color={self.cor_atual}]• {h}h {min_rest}min[/color]\n"
                f"  [i](Sistema base 60)[/i]"
            )
        elif g == "Temperatura":
            simbolo_base = "°C"
            f = (val * 1.8) + 32
            k = val + 273.15
            texto = (
                f"[size=20][b]Escalas Termométricas:[/b][/size]\n\n"
                f"[color={self.cor_atual}]• {f:.1f} °F[/color] (Fahrenheit)\n"
                f"  [i](°C × 1.8 + 32)[/i]\n\n"
                f"[color={self.cor_atual}]• {k:.2f} K[/color] (Kelvin)\n"
                f"  [i](°C + 273.15)[/i]"
            )

        self.hero_value.text = f"{val} {simbolo_base}"
        self.lbl_resultados.text = texto

    def voltar(self, tela_anterior):
        self.manager.transition = SlideTransition(direction="right", duration=0.4)
        self.manager.current = tela_anterior