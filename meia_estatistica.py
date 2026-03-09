from kivy.uix.screenmanager import Screen, SlideTransition, ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.utils import get_color_from_hex, get_hex_from_color
from kivy.clock import Clock
from kivy.core.text import LabelBase
from random import choice, randint
from collections import Counter
import os

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton, MDFillRoundFlatButton
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

# ================= CORES VIBRANTES (PADRÃO) =================
COR_ROXA = (0.6, 0.3, 0.9, 1)    # Média
COR_AZUL = (0.1, 0.5, 0.9, 1)    # Mediana
COR_VERDE = (0.3, 0.7, 0.3, 1)   # Moda
COR_LARANJA = (1, 0.6, 0.0, 1)   # Probabilidade
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


# =================== TELA 1: MENU ESTATÍSTICA ===================
class EstatisticaTela(Screen):
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
                source="Bonecos/titulo_estatistica.webp",
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
                source="Bonecos/boneco_estatistica.webp",
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
            "Representações", "chart-bar", lambda: self.ir_para("estatistica_representacoes")
        ))

        container.add_widget(self.create_icon_button(
            "Definições", "book-open-variant", lambda: self.ir_para("estatistica_definicoes")
        ))

        # Botão Jogar
        container.add_widget(self.create_icon_button(
            "Jogar", "gamepad-variant", lambda: self.ir_para("jogar")
        ))

        card_principal.add_widget(container)
        layout.add_widget(card_principal)

        self.add_widget(layout)

    def adicionar_decoracao_fundo(self, layout):
        icones = ["chart-bar", "chart-pie", "sigma", "percent", "dice-5"]
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


# =================== TELA 2: DEFINIÇÕES (ESTILO PADRONIZADO) ===================
class EstatisticaDefinicoesTela(Screen):
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
            orientation="horizontal", size_hint=(1, None), height=dp(70),
            spacing=dp(10), padding=[dp(10), dp(10), dp(10), 0], pos_hint={"top": 1}
        )

        btn_voltar = MDIconButton(
            icon="arrow-left", theme_text_color="Custom", text_color=PRETO,
            on_release=self.voltar, pos_hint={'center_y': 0.5}
        )

        lbl_titulo = MDLabel(
            text="Estatística Básica", font_style="H5", bold=True,
            theme_text_color="Custom", text_color=PRETO,
            halign="left", valign="center", pos_hint={'center_y': 0.5}
        )

        header.add_widget(btn_voltar)
        header.add_widget(lbl_titulo)
        layout.add_widget(header)

        # 3. Área de Scroll
        scroll = ScrollView(
            size_hint=(1, None), size_hint_y=0.88,
            pos_hint={"bottom": 0, "center_x": 0.5},
            do_scroll_x=False, bar_width=0
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

        # Média (Roxo)
        self.container_conteudo.add_widget(criar_card_definicao(
            titulo="Média Aritmética",
            texto=("O valor que equilibra os dados. Somamos tudo e dividimos pela quantidade.\n\n"
                   "[b]Exemplo:[/b] Notas 6, 7 e 8\n"
                   "1. Soma: 6 + 7 + 8 = 21\n"
                   "2. Quantidade: 3 números\n"
                   "3. Média: 21 ÷ 3 = [b]7[/b]"),
            icone="chart-bar",
            cor_icone=COR_ROXA
        ))

        # Mediana (Azul)
        self.container_conteudo.add_widget(criar_card_definicao(
            titulo="Mediana",
            texto=("É o valor que está exatamente no [b]meio[/b] da lista quando ela está ordenada.\n\n"
                   "[b]Exemplo:[/b] {2, 5, [b]8[/b], 10, 12}\n"
                   "A mediana é 8.\n\n"
                   "Se houver dois números no meio, somamos e dividimos por 2."),
            icone="format-align-center",
            cor_icone=COR_AZUL
        ))

        # Moda (Verde)
        self.container_conteudo.add_widget(criar_card_definicao(
            titulo="Moda",
            texto=("É o valor que mais se repete (que está na moda!).\n\n"
                   "[b]Exemplo:[/b] {2, 3, 5, 5, 5, 8, 9}\n"
                   "O número 5 aparece 3 vezes.\n"
                   "Logo, a Moda = [b]5[/b]."),
            icone="star-circle",
            cor_icone=COR_VERDE
        ))

        # Probabilidade (Laranja)
        self.container_conteudo.add_widget(criar_card_definicao(
            titulo="Probabilidade",
            texto=("A chance de algo acontecer.\n"
                   "[b]P = (Favoráveis) ÷ (Total)[/b]\n\n"
                   "[b]Exemplo:[/b] Lançar um dado e sair 4.\n"
                   "• Favorável: 1 face (o número 4)\n"
                   "• Total: 6 faces\n"
                   "• P = 1/6 (aprox. 16%)"),
            icone="dice-5",
            cor_icone=COR_LARANJA
        ))

        scroll.add_widget(self.container_conteudo)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def voltar(self, instance):
        if self.manager:
            self.manager.transition = SlideTransition(direction="right", duration=0.4)
            self.manager.current = "estatistica_tela"


# =================== TELA 3: REPRESENTAÇÕES (SIMULADOR ATUALIZADO) ===================
class EstatisticaRepresentacoes(Screen):
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
            on_release=lambda x: self.voltar("estatistica_tela")
        ))

        self.title_label = Label(
            text="DADOS",
            color=(0, 0, 0, 1),
            font_name=NOME_FONTE_TITULO, 
            font_size="28sp",
            size_hint=(1, None),
            height=dp(60),
            pos_hint={"center_x": 0.5, "top": 0.96},
        )
        layout.add_widget(self.title_label)

        # 3. CARD DOS NÚMEROS (LISTA ATUAL)
        self.hero_box = BoxLayout(
            orientation="vertical",
            size_hint=(0.9, 0.20),
            pos_hint={"center_x": 0.5, "top": 0.85},
            padding=[0, dp(10), 0, 0]
        )

        self.hero_label = MDLabel(
            text="Lista: [ ]",
            halign="center",
            font_style="H5",
            theme_text_color="Custom",
            text_color=(0.2, 0.4, 0.8, 1),
            bold=True
        )
        self.hero_box.add_widget(self.hero_label)
        layout.add_widget(self.hero_box)

        # 4. CARD DE RESULTADOS E CONTROLES
        self.panel_card = MDCard(
            orientation="vertical",
            size_hint=(0.92, 0.60),
            pos_hint={"center_x": 0.5, "y": 0.02},
            radius=[25],
            md_bg_color=(1, 1, 1, 0.95),
            elevation=6,
            padding=dp(20),
            spacing=dp(10)
        )

        # Botões de Ação
        btn_box = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        
        btn_add = MDFillRoundFlatButton(
            text="Adicionar Número",
            md_bg_color=(0.2, 0.6, 0.4, 1),
            size_hint_x=0.7,
            on_release=self.adicionar_numero
        )
        
        btn_reset = MDIconButton(
            icon="refresh",
            theme_text_color="Custom",
            text_color=(0.8, 0.2, 0.2, 1),
            on_release=self.resetar_lista
        )

        btn_box.add_widget(btn_add)
        btn_box.add_widget(btn_reset)
        self.panel_card.add_widget(btn_box)

        # Área de Resultados
        self.scroll_res = ScrollView(size_hint=(1, 1))
        self.lbl_resultados = MDLabel(
            text="Adicione números para ver as estatísticas.",
            halign="center",
            valign="top",
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1),
            font_style="Body1",
            markup=True,
            size_hint_y=None
        )
        self.lbl_resultados.bind(texture_size=self.lbl_resultados.setter('size'))
        self.scroll_res.add_widget(self.lbl_resultados)
        self.panel_card.add_widget(self.scroll_res)

        layout.add_widget(self.panel_card)
        self.add_widget(layout)

        # Dados
        self.lista_numeros = []

    def adicionar_decoracao_fundo(self, layout):
        pass

    def adicionar_numero(self, instance):
        # Adiciona um número aleatório entre 1 e 10 para simular
        novo_num = randint(1, 10)
        self.lista_numeros.append(novo_num)
        self.atualizar_interface()

    def resetar_lista(self, instance):
        self.lista_numeros = []
        self.atualizar_interface()

    def atualizar_interface(self):
        if not self.lista_numeros:
            self.hero_label.text = "Lista: [ Vazia ]"
            self.lbl_resultados.text = "Adicione números..."
            return

        # Ordena para exibir bonito
        lista_sorted = sorted(self.lista_numeros)
        self.hero_label.text = f"Lista: {str(lista_sorted)}"

        # Cálculos
        soma = sum(self.lista_numeros)
        qtd = len(self.lista_numeros)
        media = soma / qtd

        # Mediana
        if qtd % 2 == 1:
            mediana = lista_sorted[qtd // 2]
        else:
            mediana = (lista_sorted[qtd // 2 - 1] + lista_sorted[qtd // 2]) / 2

        # Moda
        counts = Counter(self.lista_numeros)
        max_freq = max(counts.values())
        modas = [k for k, v in counts.items() if v == max_freq]
        
        if max_freq == 1:
            texto_moda = "Amodal (nenhum repete)"
        elif len(modas) == 1:
            texto_moda = str(modas[0])
        else:
            texto_moda = f"Multimodal {modas}"

        # Cores para o texto
        hex_roxa = get_hex_from_color(COR_ROXA)
        hex_azul = get_hex_from_color(COR_AZUL)
        hex_verde = get_hex_from_color(COR_VERDE)

        texto = (
            f"[b]Análise dos Dados:[/b]\n\n"
            f"[color={hex_roxa}]• Média:[/color] {media:.2f}\n"
            f"  [size=14](Soma {soma} ÷ {qtd})[/size]\n\n"
            f"[color={hex_azul}]• Mediana:[/color] {mediana}\n"
            f"  [size=14](Valor central)[/size]\n\n"
            f"[color={hex_verde}]• Moda:[/color] {texto_moda}\n"
            f"  [size=14](Mais frequente)[/size]"
        )
        
        self.lbl_resultados.text = texto

    def voltar(self, tela_anterior):
        self.manager.transition = SlideTransition(direction="right", duration=0.4)
        self.manager.current = tela_anterior

