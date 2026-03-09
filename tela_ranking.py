from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import MDList, ThreeLineListItem
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.button import MDIconButton, MDFillRoundFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.spinner import MDSpinner
from kivy.metrics import dp
from kivy.clock import Clock
import banco_dados

class TelaRanking(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "ranking"

        layout = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        # --- CABEÇALHO ---
        header = MDBoxLayout(size_hint_y=None, height=dp(50))
        btn_back = MDIconButton(icon="arrow-left", on_release=self.voltar)
        lbl = MDLabel(text="Ranking Global (XP)", halign="center", font_style="H5", bold=True)
        header.add_widget(btn_back)
        header.add_widget(lbl)
        layout.add_widget(header)

        # --- BOTÃO DE ATUALIZAR ---
        filtros = MDBoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10), adaptive_width=True, pos_hint={'center_x': .5})
        btn_atualizar = MDFillRoundFlatButton(
            text="Atualizar", 
            icon="refresh",
            on_release=lambda x: self.carregar_dados()
        )
        filtros.add_widget(btn_atualizar)
        layout.add_widget(filtros)

        # --- LOADING ---
        self.spinner = MDSpinner(
            size_hint=(None, None), 
            size=(dp(46), dp(46)), 
            pos_hint={'center_x': .5, 'center_y': .5}, 
            active=False,
            palette=[[0.2, 0.6, 1, 1]]
        )
        layout.add_widget(self.spinner)

        # --- LISTA DE JOGADORES ---
        scroll = MDScrollView()
        self.lista_rank = MDList()
        scroll.add_widget(self.lista_rank)
        layout.add_widget(scroll)

        self.add_widget(layout)

    def on_enter(self):
        self.carregar_dados()

    def carregar_dados(self):
        self.lista_rank.clear_widgets()
        self.spinner.active = True
        # Executa em background para não travar a tela
        Clock.schedule_once(self._buscar_api, 0.5)

    def _buscar_api(self, dt):
        # Chama a função que traz o total de TODOS os jogos
        dados = banco_dados.obter_ranking_unificado()
        self.spinner.active = False

        if not dados:
            self.lista_rank.add_widget(ThreeLineListItem(
                text="Sem dados ou Offline", 
                secondary_text="Verifique sua conexão",
                tertiary_text="Jogue para aparecer aqui!"
            ))
            return

        for i, item in enumerate(dados):
            nome = item.get('nome', 'Anônimo')
            xp_total = item.get('xp', 0)
            detalhes = item.get('detalhes', {})

            # --- EXTRAINDO PONTOS DE CADA JOGO ---
            # Jogos Básicos
            p_chuva = detalhes.get('chuva', 0)
            p_ops = detalhes.get('operacoes', 0)
            p_frac = detalhes.get('fracoes', 0)
            
            # Jogos de Lógica/Avançados
            p_sudoku = detalhes.get('sudoku', 0)
            p_velha = detalhes.get('velha', 0)
            p_geo = detalhes.get('geometria', 0)
            p_alg = detalhes.get('algebra', 0)
            p_cruz = detalhes.get('cruzadinha', 0)
            p_est = detalhes.get('estatistica', 0)

            # --- FORMATAÇÃO VISUAL (EMOJIS) ---
            # Linha 2: Jogos mais dinâmicos
            linha2 = f"🌧️{p_chuva} | ➗{p_ops} | 🍰{p_frac} | 🧩{p_sudoku}"
            
            # Linha 3: Jogos mais complexos
            linha3 = f"⭕{p_velha} | 📐{p_geo} | ✖️{p_alg} | 📝{p_cruz} | 📊{p_est}"

            # Ícone de Medalha
            medalha = f"{i+1}º"
            if i == 0: medalha = "🥇 1º"
            elif i == 1: medalha = "🥈 2º"
            elif i == 2: medalha = "🥉 3º"

            # Cria o item da lista
            list_item = ThreeLineListItem(
                text=f"{medalha} {nome} - [b]{xp_total} XP Total[/b]",
                secondary_text=linha2,
                tertiary_text=linha3,
                theme_text_color="Custom",
                text_color=(0, 0, 0, 1) # Texto preto
            )
            self.lista_rank.add_widget(list_item)

    def voltar(self, instance):
        if self.manager:
            # Certifique-se que o nome da tela principal no seu ScreenManager é 'menu_principal'
            self.manager.current = "menu_principal"