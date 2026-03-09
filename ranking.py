from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList, ThreeLineIconListItem, IconLeftWidget
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDIconButton, MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.card import MDCard
from kivymd.uix.fitimage import FitImage
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.utils import get_color_from_hex
import threading

# Import do banco
import banco_dados

# --- PALETA DE CORES "ARCADE" ---
COR_BOARD_BG = get_color_from_hex("#2196F3")   # Azul vibrante
COR_BOARD_BORDER = get_color_from_hex("#0D47A1") # Azul escuro
COR_RIBBON_GREEN = get_color_from_hex("#4CAF50") # Verde
COR_TEXTO_BRANCO = (1, 1, 1, 1)
COR_TEXTO_AMARELO = (1, 1, 0, 1)
COR_OURO = (1, 0.84, 0, 1)
COR_PRATA = (0.9, 0.9, 0.9, 1)
COR_BRONZE = (0.8, 0.5, 0.2, 1)
COR_PRETO = (0, 0, 0, 1)

# --- KV Lang para o Item da Lista ---
# Define um item de lista personalizado com estilo "Pixel/Arcade"
KV_RANKING_ITEM = """
<RankingItemPixel@ThreeLineIconListItem>:
    theme_text_color: "Custom"
    text_color: 1, 1, 1, 1
    secondary_theme_text_color: "Custom"
    secondary_text_color: 0.9, 0.9, 0.9, 1
    tertiary_theme_text_color: "Custom"
    tertiary_text_color: 1, 1, 0, 1  
    bg_color: 0, 0, 0, 0
    divider: "Inset"
    divider_color: 1, 1, 1, 0.3
    font_style: "H6" 
"""
Builder.load_string(KV_RANKING_ITEM)

class TelaRanking(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.filtro_jogo = None
        self.filtro_dificuldade = None

        # 1. Imagem de Fundo
        try:
            self.bg_image = FitImage(source="fundoapp.png")
            self.add_widget(self.bg_image)
        except:
            pass

        # Layout Principal
        layout_principal = MDBoxLayout(
            orientation='vertical',
            padding=[dp(15), dp(30), dp(15), dp(15)],
            spacing=dp(10),
            md_bg_color=[0,0,0,0]
        )

        # 2. Cabeçalho
        header = MDBoxLayout(size_hint_y=None, height=dp(60))

        btn_back = MDIconButton(
            icon="arrow-left",
            theme_text_color="Custom",
            text_color=COR_PRETO,
            icon_size=dp(35),
            on_release=self.voltar,
            pos_hint={'center_y': .5}
        )

        lbl_titulo = MDLabel(
            text="Ranking Global",
            halign="center",
            font_style="H4",
            bold=True,
            theme_text_color="Custom",
            text_color=COR_PRETO,
            pos_hint={'center_y': .5}
        )

        header.add_widget(btn_back)
        header.add_widget(lbl_titulo)
        header.add_widget(MDLabel(size_hint_x=None, width=dp(40))) # Espaçador
        layout_principal.add_widget(header)

        # 3. Filtros
        filtros_layout = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))

        self.btn_jogo = MDFillRoundFlatButton(
            text="JOGO",
            font_style="Button",
            md_bg_color=COR_RIBBON_GREEN,
            text_color=COR_TEXTO_BRANCO,
            size_hint_x=0.45,
            on_release=self.abrir_menu_jogo
        )
        self.btn_jogo.radius = [dp(6), dp(6), dp(6), dp(6)]

        self.btn_nivel = MDFillRoundFlatButton(
            text="NIVEL",
            font_style="Button",
            md_bg_color=COR_RIBBON_GREEN,
            text_color=COR_TEXTO_BRANCO,
            size_hint_x=0.45,
            on_release=self.abrir_menu_nivel
        )
        self.btn_nivel.radius = [dp(6), dp(6), dp(6), dp(6)]

        btn_limpar = MDIconButton(
            icon="delete",
            theme_text_color="Custom",
            text_color=COR_TEXTO_BRANCO,
            md_bg_color=(1, 0, 0, 0.6),
            on_release=self.limpar_filtros,
            pos_hint={'center_y': .5}
        )

        filtros_layout.add_widget(self.btn_jogo)
        filtros_layout.add_widget(self.btn_nivel)
        filtros_layout.add_widget(btn_limpar)
        layout_principal.add_widget(filtros_layout)

        self.menu_jogo = None
        self.menu_nivel = None

        # 4. O "Board" Azul (Lista)
        card_lista = MDCard(
            radius=[dp(12),],
            md_bg_color=COR_BOARD_BG,
            line_color=COR_BOARD_BORDER,
            line_width=dp(3),
            padding=dp(4),
            elevation=6
        )

        layout_lista_interna = MDBoxLayout(orientation='vertical')

        # Container do Spinner (Carregamento)
        from kivy.uix.floatlayout import FloatLayout
        self.spinner_container = FloatLayout(size_hint_y=None, height=0)

        self.spinner = MDSpinner(
            size_hint=(None, None),
            size=(dp(46), dp(46)),
            pos_hint={'center_x': .5, 'center_y': .5},
            palette=[COR_TEXTO_AMARELO, COR_TEXTO_BRANCO],
            active=False
        )
        self.spinner_container.add_widget(self.spinner)
        layout_lista_interna.add_widget(self.spinner_container)

        scroll = MDScrollView()
        self.lista_rank = MDList(padding=[dp(5), dp(10), dp(5), dp(20)])
        scroll.add_widget(self.lista_rank)
        layout_lista_interna.add_widget(scroll)

        card_lista.add_widget(layout_lista_interna)
        layout_principal.add_widget(card_lista)

        self.add_widget(layout_principal)

        self._criar_menus()

    # --- Funções de Menu ---
    def _criar_menus(self):
        opcoes_jogo = ["Cálculo", "Álgebra", "Frações", "Geometria", "Estatística", "Operações"]
        items_jogo = [
            {
                "text": jogo.upper(),
                "viewclass": "OneLineListItem",
                "height": dp(48),
                "on_release": lambda x=jogo: self.selecionar_jogo(x),
            } for jogo in opcoes_jogo
        ]
        self.menu_jogo = MDDropdownMenu(
            caller=self.btn_jogo,
            items=items_jogo,
            width_mult=3.5,
            md_bg_color=COR_TEXTO_BRANCO,
        )

        opcoes_nivel = ["Primário", "Fundamental", "Médio"]
        items_nivel = [
            {
                "text": nivel.upper(),
                "viewclass": "OneLineListItem",
                "height": dp(48),
                "on_release": lambda x=nivel: self.selecionar_nivel(x),
            } for nivel in opcoes_nivel
        ]
        self.menu_nivel = MDDropdownMenu(
            caller=self.btn_nivel,
            items=items_nivel,
            width_mult=3.5,
            md_bg_color=COR_TEXTO_BRANCO,
        )

    def abrir_menu_jogo(self, instance):
        self.menu_jogo.open()

    def abrir_menu_nivel(self, instance):
        self.menu_nivel.open()

    def selecionar_jogo(self, jogo_escolhido):
        print(f"[DEBUG] Jogo selecionado: {jogo_escolhido}")
        self.filtro_jogo = jogo_escolhido
        self.btn_jogo.text = jogo_escolhido.upper()
        self.menu_jogo.dismiss()
        self.carregar_dados()

    def selecionar_nivel(self, nivel_escolhido):
        print(f"[DEBUG] Nível selecionado: {nivel_escolhido}")
        self.filtro_dificuldade = nivel_escolhido
        self.btn_nivel.text = nivel_escolhido.upper()
        self.menu_nivel.dismiss()
        self.carregar_dados()

    def limpar_filtros(self, instance):
        print("[DEBUG] Limpando filtros")
        self.filtro_jogo = None
        self.filtro_dificuldade = None
        self.btn_jogo.text = "JOGO"
        self.btn_nivel.text = "NIVEL"
        self.carregar_dados()

    def on_enter(self):
        self.carregar_dados()

    def carregar_dados(self):
        self.lista_rank.clear_widgets()
        self.spinner_container.height = dp(100)
        self.spinner.active = True

        # Thread para não travar a UI enquanto busca na internet
        threading.Thread(target=self._buscar_api_thread).start()

    def _buscar_api_thread(self):
        print(f"[DEBUG] Buscando API -> Jogo: {self.filtro_jogo}, Dif: {self.filtro_dificuldade}")
        try:
            dados = banco_dados.buscar_ranking(
                jogo=self.filtro_jogo,
                dificuldade=self.filtro_dificuldade
            )
        except Exception as e:
            print(f"[ERRO] Falha ao buscar ranking: {e}")
            dados = []

        # Atualiza a UI na thread principal
        Clock.schedule_once(lambda dt: self._atualizar_lista(dados))

    def _atualizar_lista(self, dados):
        self.spinner.active = False
        self.spinner_container.height = 0

        if not dados:
            aviso = Factory.RankingItemPixel(
                text="SEM DADOS",
                secondary_text="TENTE LIMPAR OS FILTROS",
                tertiary_text=""
            )
            icon_widget = IconLeftWidget(icon="alert-box", theme_text_color="Custom", text_color=COR_TEXTO_BRANCO)
            aviso.add_widget(icon_widget)
            self.lista_rank.add_widget(aviso)
            return

        for i, item in enumerate(dados):
            # Extraindo Dados de forma segura com .get()
            # Isso impede o erro KeyError se o campo não existir
            nome = item.get('nome', 'PLAYER').upper()

            # Tenta pegar 'acertos', se não tiver, tenta 'xp', senão 0
            # Isso resolve o seu erro original
            pontos = item.get('acertos', item.get('xp', 0))

            game = item.get('jogo', 'JOGO').upper()
            tempo = item.get('tempo', '--:--')
            dificuldade = item.get('dificuldade', 'Normal')
            escola = item.get('escola', 'Escola Padrão')

            # Limita tamanho da escola
            if len(escola) > 25:
                escola = escola[:22] + "..."

            # Ícones de Posição
            icone_nome = "numeric-" + str(i+1) + "-box"
            cor_icone = COR_TEXTO_BRANCO

            if i == 0:
                icone_nome = "trophy"
                cor_icone = COR_OURO
            elif i == 1:
                icone_nome = "medal"
                cor_icone = COR_PRATA
            elif i == 2:
                icone_nome = "medal-outline"
                cor_icone = COR_BRONZE

            # --- ORGANIZAÇÃO DAS LINHAS ---
            sec_text = f"{game} • {dificuldade} • {pontos} pts"
            ter_text = f"{escola} | Tempo: {tempo}"

            list_item = Factory.RankingItemPixel(
                text=f"{i+1}. {nome}",
                secondary_text=sec_text,
                tertiary_text=ter_text,
            )

            icon_widget = IconLeftWidget(
                icon=icone_nome,
                theme_text_color="Custom",
                text_color=cor_icone
            )

            list_item.add_widget(icon_widget)
            self.lista_rank.add_widget(list_item)

    def voltar(self, instance):
        if self.manager:
            self.manager.current = "inicial" # Voltando para a tela inicial