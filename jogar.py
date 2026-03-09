from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFillRoundFlatIconButton, MDFlatButton
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.tab import MDTabs, MDTabsBase
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp, sp
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.widget import MDWidget
from kivy.core.text import LabelBase
from kivy.animation import Animation
from kivy.properties import NumericProperty, StringProperty
from random import randint, choice
import os
from kivy.uix.label import Label
from kivymd.uix.dialog import MDDialog

# ======================================================================
# Configuração da Fonte
# ======================================================================
font_path = os.path.join(os.path.dirname(__file__), "Fontes", "Duo-Dunkel.ttf")
if os.path.exists(font_path):
    LabelBase.register(name="BungeeShade", fn_regular=font_path)

# ======================================================================
# CLASSE DO JOGO DE BOLICHE MATEMÁTICO
# ======================================================================
class BolicheMatematicoScreen(Screen):
    pontos = NumericProperty(0)
    dificuldade = StringProperty("Primario")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.add_widget(self.layout)
        self.pinos = []
        self.bola_ativa = False

    def on_enter(self):
        self.layout.clear_widgets()
        self.pontos = 0
        self.setup_ui()
        self.gerar_rodada()

    def definir_dificuldade(self, diff):
        self.dificuldade = diff

    def setup_ui(self):
        self.layout.add_widget(Image(source='fundoapp.png', allow_stretch=True, keep_ratio=False))

        self.lbl_pontos = MDLabel(
            text=f"PONTOS: {self.pontos}", halign="center", font_style="H5",
            pos_hint={"center_x": 0.5, "top": 0.95}, bold=True
        )
        self.layout.add_widget(self.lbl_pontos)

        back_btn = MDIconButton(
            icon="arrow-left", pos_hint={"x": 0.02, "top": 0.98},
            on_release=self.voltar, icon_size=dp(36)
        )
        self.layout.add_widget(back_btn)

    def gerar_rodada(self):
        for p in self.pinos:
            self.layout.remove_widget(p)
        self.pinos = []

        if self.dificuldade == "Primario":
            self.alvo = randint(5, 20)
        elif self.dificuldade == "Fundamental":
            self.alvo = randint(20, 100)
        else:
            self.alvo = choice([12, 15, 20, 25])

        self.criar_bola()

        # Posições em Arco
        pos_x = [0.15, 0.32, 0.5, 0.68, 0.85]
        pos_y = [0.65, 0.73, 0.78, 0.73, 0.65]
        indice_correto = randint(0, 4)

        for i in range(5):
            is_correto = (i == indice_correto)
            exp, res = self.gerar_expressao(self.alvo if is_correto else None)

            pino = MDLabel(
                text=exp, size_hint=(None, None), size=(dp(80), dp(50)),
                pos_hint={"center_x": pos_x[i], "center_y": pos_y[i]},
                halign="center", md_bg_color=(1, 1, 1, 0.9),
                radius=[dp(10)], bold=True
            )
            pino.resultado = res
            self.pinos.append(pino)
            self.layout.add_widget(pino)

    def gerar_expressao(self, valor_fixo):
        v = valor_fixo if valor_fixo is not None else randint(1, 150)
        if self.dificuldade == "Primario":
            return (f"{v-2}+2", v) if randint(0,1) else (f"{v+3}-3", v)
        elif self.dificuldade == "Fundamental":
            return (f"{v//2}x2", v) if v%2==0 else (f"{v}+0", v)
        else:
            return (f"√{v*v}", v)

    def criar_bola(self):
        if hasattr(self, 'bola'): self.layout.remove_widget(self.bola)
        if hasattr(self, 'lbl_bola'): self.layout.remove_widget(self.lbl_bola)

        self.bola = Image(
            source='matemas.webp', size_hint=(None, None), size=(dp(80), dp(80)),
            pos_hint={"center_x": 0.5, "y": 0.1}
        )
        self.lbl_bola = MDLabel(
            text=str(self.alvo), halign="center", font_style="H4",
            pos_hint={"center_x": 0.5, "center_y": 0.16}, bold=True
        )
        self.layout.add_widget(self.bola)
        self.layout.add_widget(self.lbl_bola)
        self.bola_ativa = True

    def on_touch_down(self, touch):
        if self.bola.collide_point(*touch.pos) and self.bola_ativa:
            touch.grab(self)
            self.touch_start_y = touch.y
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            if touch.y > self.touch_start_y + dp(30):
                self.lancar_bola()
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)

    def lancar_bola(self):
        self.bola_ativa = False
        anim = Animation(pos_hint={"center_y": 0.8}, duration=0.5, t="out_quad")
        anim.bind(on_progress=self.checar_colisao)
        anim.bind(on_complete=lambda *a: self.gerar_rodada())
        anim.start(self.bola)
        Animation(pos_hint={"center_y": 0.86}, duration=0.5).start(self.lbl_bola)

    def checar_colisao(self, anim, widget, progress):
        for p in self.pinos[:]:
            if widget.collide_widget(p):
                if p.resultado == self.alvo:
                    p.md_bg_color = (0, 1, 0, 1)
                    self.pontos += 10
                    self.lbl_pontos.text = f"PONTOS: {self.pontos}"
                else:
                    p.md_bg_color = (1, 0, 0, 1)
                self.layout.remove_widget(p)
                self.pinos.remove(p)

    def voltar(self, *args):
        self.manager.current = "jogar"

# ======================================================================
# CLASSES DE JOGOS
# ======================================================================
class JogosPrimario:
    @staticmethod
    def get():
        return [
            {"nome": "Boliche Matemático", "imagem": "Jogos/boliche_icon.webp", "tela": "boliche_matematico"},
            {"nome": "Pac-Man Matemático", "imagem": "Jogos/pacman.webp", "tela": "pacman_matematico"},
            {"nome": "Operações", "imagem": "Jogos/matematicando.webp", "tela": "primario"},
            {"nome": "Chuva Numérica", "imagem": "Jogos/chuva.webp", "tela": "chuva_numeros"},
            {"nome": "Frações", "imagem": "Jogos/fracoes.webp", "tela": "fracoes_info"},
            {"nome": "Álgebra", "imagem": "Jogos/algebra.webp", "tela": "algebra"},
            {"nome": "Cruzadinha", "imagem": "Jogos/cross.webp", "tela": "cross_p"},
            {"nome": "Sudoku", "imagem": "Jogos/sudoku.webp", "tela": "sudoku"},
            {"nome": "Geometria", "imagem": "Jogos/geometria.webp", "tela": "jogo_geometria"},
            {"nome": "Jogo da Velha", "imagem": "Jogos/velha.webp", "tela": "velha"},
            {"nome": "Estatistica", "imagem": "Jogos/estatistica.webp", "tela": "jogo_estatistica"},
        ]

class JogosFundamental:
    @staticmethod
    def get():
        return [
            {"nome": "Boliche Matemático", "imagem": "Jogos/boliche_icon.webp", "tela": "boliche_matematico"},
            {"nome": "Pac-Man Matemático", "imagem": "Jogos/pacman.webp", "tela": "pacman_matematico"},
            {"nome": "Operações", "imagem": "Jogos/matematicando.webp", "tela": "fundamental"},
            {"nome": "Chuva Numérica", "imagem": "Jogos/chuva.png", "tela": "chuva_numeros"},
            {"nome": "Álgebra", "imagem": "Jogos/algebra.webp", "tela": "algebra"},
            {"nome": "Frações", "imagem": "Jogos/fracoes.webp", "tela": "fracoes_info"},
            {"nome": "Cruzadinha", "imagem": "Jogos/cross.webp", "tela": "cross_f"},
            {"nome": "Sudoku", "imagem": "Jogos/sudoku.webp", "tela": "sudoku"},
            {"nome": "Geometria", "imagem": "Jogos/geometria.webp", "tela": "jogo_geometria"},
            {"nome": "Jogo da Velha", "imagem": "Jogos/velha.webp", "tela": "velha"},
            {"nome": "Estatistica", "imagem": "Jogos/estatistica.webp", "tela": "jogo_estatistica"},
        ]

class JogosMedio:
    @staticmethod
    def get():
        return [
            {"nome": "Boliche Matemático", "imagem": "Jogos/boliche_icon.webp", "tela": "boliche_matematico"},
            {"nome": "Pac-Man Matemático", "imagem": "Jogos/pacman.webp", "tela": "pacman_matematico"},
            {"nome": "Operações", "imagem": "Jogos/matematicando.webp", "tela": "medio"},
            {"nome": "Chuva Numérica", "imagem": "Jogos/chuva.png", "tela": "chuva_numeros"},
            {"nome": "Álgebra", "imagem": "Jogos/algebra.webp", "tela": "algebra"},
            {"nome": "Frações", "imagem": "Jogos/fracoes.webp", "tela": "fracoes_info"},
            {"nome": "Cruzadinha", "imagem": "Jogos/cross.webp", "tela": "cross"},
            {"nome": "Sudoku", "imagem": "Jogos/sudoku.webp", "tela": "sudoku"},
            {"nome": "Geometria", "imagem": "Jogos/geometria.webp", "tela": "jogo_geometria"},
            {"nome": "Jogo da Velha", "imagem": "Jogos/velha.webp", "tela": "velha"},
            {"nome": "Estatistica", "imagem": "Jogos/estatistica.webp", "tela": "jogo_estatistica"},
        ]

# ======================================================================
# TELA PRINCIPAL (JOGAR)
# ======================================================================
class TelaJogar(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.categoria_atual = "Fundamental I"

        self.add_widget(Image(source='fundoapp.png', allow_stretch=True, keep_ratio=False))

        main_layout = MDBoxLayout(orientation="vertical")
        self.add_widget(main_layout)

        top_layout = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(90), padding=[dp(10), dp(20), dp(10), dp(5)])

        back_btn = MDIconButton(icon="arrow-left", icon_size=dp(36), on_release=self.voltar)
        top_layout.add_widget(back_btn)

        font_name = "BungeeShade" if os.path.exists(font_path) else "Roboto"
        title = Label(text="SELECIONE O JOGO", font_name=font_name, font_size="22sp", color=(0,0,0,1))

        top_layout.add_widget(title)
        top_layout.add_widget(MDWidget())
        main_layout.add_widget(top_layout)

        self.content_area = MDBoxLayout()
        main_layout.add_widget(self.content_area)

        self.bottom_bar = BottomBar(self.trocar_aba)
        main_layout.add_widget(self.bottom_bar)
        self.mostrar_jogos("Fundamental I")

    def trocar_aba(self, nome):
        self.mostrar_jogos(nome)

    def mostrar_jogos(self, categoria):
        self.categoria_atual = categoria
        self.content_area.clear_widgets()

        jogos = JogosPrimario.get() if categoria == "Fundamental I" else \
            JogosFundamental.get() if categoria == "Fundamental II" else JogosMedio.get()

        scroll = ScrollView(bar_width=dp(4))
        # Ajustei o spacing e padding para os cards respirarem melhor
        grid = MDGridLayout(cols=3, spacing=dp(15), padding=dp(15), adaptive_height=True)

        for jogo in jogos:
            # O Card principal
            card = MDCard(
                size_hint=(1, None),
                height=dp(140), # Reduzi um pouco a altura para focar no ícone
                radius=[18],
                elevation=4,
                on_release=lambda inst, j=jogo: self.aciona_jogo(j)
            )

            # Removemos o padding interno para a imagem poder crescer
            box = MDBoxLayout(orientation="vertical", padding=dp(0), spacing=dp(0))

            try:
                # Criando um layout para a imagem centralizar e crescer livremente
                img_box = FloatLayout(size_hint=(1, 0.75)) # Imagem ocupa 75% da altura do card
                img = Image(
                    source=jogo["imagem"],
                    allow_stretch=True, # Permite esticar
                    keep_ratio=True,    # Mas mantém a proporção
                    size_hint=(0.8, 0.8), # A imagem ocupa 80% do FloatLayout (aumente se quiser maior)
                    pos_hint={"center_x": 0.5, "center_y": 0.5} # Centraliza
                )
                img_box.add_widget(img)
                box.add_widget(img_box)
            except:
                # Se não achar a imagem, coloca um ícone padrão grande
                fallback = MDIconButton(icon="gamepad-variant", font_size="50sp", halign="center", size_hint_y=0.75)
                box.add_widget(fallback)

            # O Texto (ocupa os 25% restantes da altura)
            box.add_widget(MDLabel(
                text=jogo["nome"],
                halign="center",
                font_size="13sp",
                bold=True,
                size_hint_y=0.25
            ))

            card.add_widget(box)
            grid.add_widget(card)

        scroll.add_widget(grid)
        self.content_area.add_widget(scroll)

    def aciona_jogo(self, jogo):
        nome_tela = jogo["tela"]
        dificuldade = "Primario" if self.categoria_atual == "Fundamental I" else \
            "Fundamental" if self.categoria_atual == "Fundamental II" else "Medio"

        try:
            screen = self.manager.get_screen(nome_tela)
            if hasattr(screen, 'definir_dificuldade'):
                screen.definir_dificuldade(dificuldade)
            elif hasattr(screen, 'define_dificul'):
                screen.define_dificul(dificuldade)
        except: pass
        self.manager.current = nome_tela

    def voltar(self, instance):
        self.manager.current = "inicial"

# ======================================================================
# BOTTOM BAR
# ======================================================================
class BottomBar(MDBoxLayout):
    def __init__(self, on_change, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(70)
        self.padding = [dp(0), dp(5), dp(0), dp(5)]
        self.spacing = dp(0)
        self.md_bg_color = (1, 1, 1, 1)
        self.radius = [20, 20, 0, 0]
        self.on_change = on_change
        self.buttons = {}

        abas = [("Fundamental I", "school"), ("Fundamental II", "book-open-variant"), ("Médio", "chart-bar")]

        for nome, icon in abas:
            btn = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(2),
                padding=dp(0),
                size_hint=(1, 1),
                on_touch_down=self._make_callback(nome)
            )

            btn.add_widget(MDWidget())

            ic = MDIconButton(
                icon=icon,
                theme_text_color="Custom",
                text_color=(0.6, 0.6, 0.6, 1),
                icon_size=dp(26),
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                pos_hint={"center_y": 0.5}
            )
            btn.add_widget(ic)

            text_box = MDBoxLayout(
                orientation="vertical",
                size_hint=(None, None),
                width=dp(115),
                height=dp(34),
                pos_hint={"center_y": 0.5},
                spacing=dp(0)
            )

            lbl_top = Label(
                text="Ensino",
                halign="left",
                valign="bottom",
                font_size="11sp",
                color=(0.6, 0.6, 0.6, 1),
                size_hint=(1, None),
                height=dp(14)
            )
            lbl_top.bind(size=lbl_top.setter('text_size'))

            lbl_bottom = Label(
                text=nome,
                halign="left",
                valign="top",
                font_size="13sp",
                bold=True,
                color=(0.6, 0.6, 0.6, 1),
                size_hint=(1, None),
                height=dp(20)
            )
            lbl_bottom.bind(size=lbl_bottom.setter('text_size'))

            text_box.add_widget(lbl_top)
            text_box.add_widget(lbl_bottom)
            btn.add_widget(text_box)

            btn.add_widget(MDWidget())

            self.add_widget(btn)
            self.buttons[nome] = (ic, lbl_top, lbl_bottom)

        self.selecionar("Fundamental I")

    def selecionar(self, nome):
        cinza = (0.6, 0.6, 0.6, 1)
        azul = (0.0, 0.4, 0.8, 1)

        for ic, t1, t2 in self.buttons.values():
            ic.text_color = cinza
            t1.color = cinza
            t2.color = cinza

        if nome in self.buttons:
            ic, t1, t2 = self.buttons[nome]
            ic.text_color = azul
            t1.color = azul
            t2.color = azul

    def _make_callback(self, nome):
        def callback(instance, touch):
            if instance.collide_point(*touch.pos):
                self.selecionar(nome)
                self.on_change("Medio" if nome == "Médio" else nome)
                return True
        return callback

from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFillRoundFlatIconButton
from kivymd.uix.card import MDCard
from kivy.uix.image import Image
from kivy.metrics import dp, sp # Importante para tamanhos corretos
from kivy.app import App
from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
# =======================================================================================================================
# Tela de seleção da operação e rodadas do matematicando
class TelaEscolhaNivel(MDScreen):
    def __init__(self, dificuldade, titulo, tela_voltar, **kwargs):
        super().__init__(**kwargs)
        self.dificuldade = dificuldade
        self.tela_voltar = tela_voltar
        self.dialog = None # Variável para guardar o pop-up

        # Layout principal
        layout = FloatLayout()

        # Imagem de fundo
        try:
            self.bg_image = Image(source='fundoapp.png', allow_stretch=True, keep_ratio=False)
            layout.add_widget(self.bg_image)
        except:
            pass

        # --- TÍTULO PRINCIPAL ---
        title = MDLabel(
            text=titulo,
            halign="center",
            # font_name="BungeeShade", # Descomente se tiver a fonte
            font_style="H4",
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            pos_hint={"center_x": 0.5, "top": 0.95},
            size_hint=(1, None),
            height=dp(50)
        )
        layout.add_widget(title)

        # --- CARD DE FUNDO ---
        card_bg = MDCard(
            size_hint=(0.9, 0.65),
            pos_hint={"center_x": 0.5, "center_y": 0.55},
            radius=[20, 20, 20, 20],
            md_bg_color=(1, 1, 1, 0.8),
            elevation=2
        )
        layout.add_widget(card_bg)

        # --- COLUNA ESQUERDA: RODADAS ---
        rodadas_label = MDLabel(
            text="Rodadas",
            halign="center",
            font_size="22sp",
            bold=True,
            theme_text_color="Custom",
            text_color=(0, 0, 0, 0.8),
            pos_hint={"center_x": 0.28, "top": 0.85},
            size_hint=(0.4, None),
            height=dp(30)
        )
        layout.add_widget(rodadas_label)

        # --- NOVO: BOTÃO DE AJUDA (?) ---
        self.btn_help = MDIconButton(
            icon="help-circle-outline",
            theme_text_color="Custom",
            text_color=(0.2, 0.4, 0.8, 1), # Azul destaque
            icon_size="26sp",
            pos_hint={"center_x": 0.42, "center_y": 0.835}, # Posicionado ao lado do texto "Rodadas"
            on_release=self.mostrar_info_rodadas
        )
        layout.add_widget(self.btn_help)
        # --------------------------------

        # Botões de Rodadas
        self.button_3 = self.create_rodada_button("3", 0.75, 3, "numeric-3-circle")
        self.button_6 = self.create_rodada_button("6", 0.65, 6, "numeric-6-circle")
        self.button_10 = self.create_rodada_button("10", 0.55, 10, "numeric-10-circle")

        for btn in [self.button_3, self.button_6, self.button_10]:
            layout.add_widget(btn)

        # --- COLUNA DIREITA: OPERAÇÕES ---
        operacoes_label = MDLabel(
            text="Operação",
            halign="center",
            font_size="22sp",
            bold=True,
            theme_text_color="Custom",
            text_color=(0, 0, 0, 0.8),
            pos_hint={"center_x": 0.72, "top": 0.85},
            size_hint=(0.4, None),
            height=dp(30)
        )
        layout.add_widget(operacoes_label)

        # Botões de Operação
        self.op_soma = self.create_operacao_button("Soma", 0.75, "soma", "plus")
        self.op_subtracao = self.create_operacao_button("Subtração", 0.65, "subtracao", "minus")
        self.op_multiplicacao = self.create_operacao_button("Mult.", 0.55, "multiplicacao", "close")
        self.op_divisao = self.create_operacao_button("Divisão", 0.45, "divisao", "division")

        for btn in [self.op_soma, self.op_subtracao, self.op_multiplicacao, self.op_divisao]:
            layout.add_widget(btn)

        # --- RODAPÉ: BOTÕES DE AÇÃO ---
        self.calculos_button = MDRaisedButton(
            text="INICIAR PARTIDA",
            size_hint=(0.6, None),
            height=dp(55),
            font_size="20sp",
            pos_hint={"center_x": 0.5, "center_y": 0.15},
            on_release=self.iniciar_jogo,
            md_bg_color=(0.8, 0.8, 0.8, 1),
            text_color=(1, 1, 1, 1),
            elevation=3,
            disabled=True
        )
        layout.add_widget(self.calculos_button)

        voltar_button = MDRaisedButton(
            text="Voltar",
            size_hint=(0.3, None),
            height=dp(40),
            font_size="16sp",
            pos_hint={"center_x": 0.5, "center_y": 0.06},
            on_release=self.voltar_tela_inicial,
            md_bg_color=(0.8, 0.4, 0.4, 1),
            text_color=(1, 1, 1, 1),
            elevation=1
        )
        layout.add_widget(voltar_button)

        self.add_widget(layout)

        self.botao_selecionado = None
        self.operacao_selecionada = None

    # --- NOVO: FUNÇÃO DO POP-UP ---
    def mostrar_info_rodadas(self, instance):
        if not self.dialog:
            self.dialog = MDDialog(
                title="Como funcionam as Rodadas?",
                text="As rodadas funcionam como um [b]Saldo de Pontos[/b].\n\n"
                     "• Se você escolher [b]3[/b], você precisa acumular [b]3 acertos a mais[/b] que erros para passar de nível.\n"
                     "• Errar diminui seu saldo.\n\n"
                     "Exemplo: Se tiver 3 acertos e 1 erro, seu saldo é 2.",
                buttons=[
                    MDFlatButton(
                        text="ENTENDI",
                        theme_text_color="Custom",
                        text_color=(0.2, 0.4, 0.8, 1),
                        on_release=lambda x: self.dialog.dismiss()
                    )
                ],
            )
        self.dialog.open()

    # --- FUNÇÕES DE CRIAÇÃO VISUAL ---

    def on_enter(self):
        self.mostrar_info_rodadas

    def create_rodada_button(self, text, center_y, rodadas_value, icon_name):
        return MDFillRoundFlatIconButton(
            text=f"{text} Rounds",
            icon=icon_name,
            size_hint=(0.40, None),
            height=dp(50),
            font_size="16sp",
            pos_hint={"center_x": 0.28, "center_y": center_y},
            on_release=lambda x: self.definir_rodadas(rodadas_value),
            md_bg_color=(0.2, 0.6, 0.8, 1),
            text_color=(1, 1, 1, 1),
            icon_color=(1, 1, 1, 1)
        )

    def create_operacao_button(self, text, center_y, operacao_value, icon_name):
        return MDFillRoundFlatIconButton(
            text=text,
            icon=icon_name,
            size_hint=(0.40, None),
            height=dp(50),
            font_size="16sp",
            pos_hint={"center_x": 0.72, "center_y": center_y},
            on_release=lambda x: self.definir_operacao(operacao_value),
            md_bg_color=(0.4, 0.4, 0.6, 1),
            text_color=(1, 1, 1, 1),
            icon_color=(1, 1, 1, 1)
        )

    # --- LÓGICA ---

    def voltar_tela_inicial(self, instance):
        self.manager.current = self.tela_voltar

    def definir_rodadas(self, rodadas_value):
        self.valor_rodadas = rodadas_value
        mapa_botoes = {3: self.button_3, 6: self.button_6, 10: self.button_10}
        self.botao_selecionado = mapa_botoes[rodadas_value]

        for btn in mapa_botoes.values():
            btn.md_bg_color = (0.2, 0.6, 0.8, 1)
            btn.elevation = 1

        self.botao_selecionado.md_bg_color = (0, 0.7, 0, 1)
        self.botao_selecionado.elevation = 4
        self.verificar_pronto()

    def definir_operacao(self, operacao_value):
        self.operacao_selecionada = operacao_value
        botoes = {"soma": self.op_soma, "subtracao": self.op_subtracao, "multiplicacao": self.op_multiplicacao, "divisao": self.op_divisao}

        for btn in botoes.values():
            btn.md_bg_color = (0.4, 0.4, 0.6, 1)
            btn.elevation = 1

        botoes[operacao_value].md_bg_color = (0, 0.7, 0, 1)
        botoes[operacao_value].elevation = 4
        self.verificar_pronto()

    def verificar_pronto(self):
        if hasattr(self, 'valor_rodadas') and self.operacao_selecionada:
            self.calculos_button.disabled = False
            self.calculos_button.md_bg_color = (0, 0.6, 0, 1)
            self.calculos_button.text_color = (1, 1, 1, 1)

    def iniciar_jogo(self, instance):
        app = App.get_running_app()
        sm = app.root
        sm.current = "game1"
        game1 = sm.get_screen("game1")

        game1.define_dificul(self.dificuldade)
        game1.confirma_rodadas(self.valor_rodadas)
        game1.escolha_modo("normal")
        game1.define_operacao(self.operacao_selecionada.lower())
        game1.inicia_nivel(1)