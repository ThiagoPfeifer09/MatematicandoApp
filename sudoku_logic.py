import random
from threading import Thread

from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu 
from kivymd.uix.card import MDCard 

# --- IMPORT DO BANCO DE DADOS ---
import banco_dados 

# ====================== LÓGICA DO SUDOKU ======================

class SudokuGenerator:
    def __init__(self):
        self.tabuleiro = [[0] * 9 for _ in range(9)]
        self.solucao = None

    def _e_valido(self, tabuleiro, num, pos):
        for j in range(9):
            if tabuleiro[pos[0]][j] == num and pos[1] != j:
                return False
        for i in range(9):
            if tabuleiro[i][pos[1]] == num and pos[0] != i:
                return False
        box_x, box_y = pos[1] // 3, pos[0] // 3
        for i in range(box_y * 3, box_y * 3 + 3):
            for j in range(box_x * 3, box_x * 3 + 3):
                if tabuleiro[i][j] == num and (i, j) != pos:
                    return False
        return True

    def _encontrar_vazio(self, tabuleiro):
        for i in range(9):
            for j in range(9):
                if tabuleiro[i][j] == 0:
                    return (i, j)
        return None

    def resolver(self, tabuleiro=None):
        if tabuleiro is None:
            tabuleiro = self.tabuleiro
        encontrar = self._encontrar_vazio(tabuleiro)
        if not encontrar:
            return True
        linha, coluna = encontrar
        numeros = list(range(1, 10))
        random.shuffle(numeros)
        for num in numeros:
            if self._e_valido(tabuleiro, num, (linha, coluna)):
                tabuleiro[linha][coluna] = num
                if self.resolver(tabuleiro):
                    return True
                tabuleiro[linha][coluna] = 0
        return False

    def gerar_tabuleiro(self, dificuldade="medio"):
        self.tabuleiro = [[0] * 9 for _ in range(9)]
        self._preencher_diagonal()
        self.resolver()
        self.solucao = [row[:] for row in self.tabuleiro]
        
        if "facil" in dificuldade:
            remocoes = 30
        elif "medio" in dificuldade:
            remocoes = 45
        else: 
            remocoes = 55
            
        current_board = [row[:] for row in self.solucao]
        while remocoes > 0:
            row, col = random.randint(0, 8), random.randint(0, 8)
            if current_board[row][col] != 0:
                current_board[row][col] = 0
                remocoes -= 1
        self.tabuleiro = current_board
        return self.tabuleiro

    def _preencher_bloco(self, i, j):
        nums = list(range(1, 10))
        random.shuffle(nums)
        for r in range(3):
            for c in range(3):
                self.tabuleiro[i + r][j + c] = nums.pop()

    def _preencher_diagonal(self):
        for i in range(0, 9, 3):
            self._preencher_bloco(i, i)

    def verificar_vitoria(self, tabuleiro_atual):
        for i in range(9):
            for j in range(9):
                if tabuleiro_atual[i][j] == 0:
                    return False
                if tabuleiro_atual[i][j] != self.solucao[i][j]:
                    return False
        return True


# ====================== WIDGET: CÉLULA ======================

class CelulaSudoku(ButtonBehavior, MDLabel):
    def __init__(self, row, col, fixed, start_value=0, **kwargs):
        super().__init__(**kwargs)
        self.row, self.col, self.fixed, self.value = row, col, fixed, start_value
        self.halign, self.valign = 'center', 'middle'
        self.font_style = 'H5'
        self.theme_text_color = 'Custom'
        
        self.is_wrong = False 
        self.is_match_state = False       
        self.is_selected_state = False    
        self.is_highlighted_state = False 

        self.paleta = {
            "Light": {
                "base": (1, 1, 1, 1),
                "fixed": (0.9, 0.9, 0.9, 1),
                "selected": (0.4, 0.7, 0.9, 1),
                "match": (0.6, 0.8, 1.0, 1),
                "highlight": (0.85, 0.95, 0.85, 1),
                "conflict": (1, 0.8, 0.8, 1),
                "text_fixed": (0, 0, 0, 1),
                "text_input": (0.2, 0.2, 0.8, 1),
                "text_error": (0.8, 0, 0, 1)
            },
            "Dark": {
                "base": (0.18, 0.18, 0.18, 1),
                "fixed": (0.25, 0.25, 0.25, 1),
                "selected": (0.1, 0.4, 0.5, 1),
                "match": (0.2, 0.5, 0.7, 1),
                "highlight": (0.2, 0.3, 0.2, 1),
                "conflict": (0.6, 0.2, 0.2, 1),
                "text_fixed": (0.9, 0.9, 0.9, 1),
                "text_input": (0.4, 0.8, 1, 1),
                "text_error": (1, 0.4, 0.4, 1)
            }
        }
        
        with self.canvas.before:
            self.cor_rect = Color(1, 1, 1, 1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self._update_rect, size=self._update_rect)
        
        self.atualizar_tema()

    def _update_rect(self, *args):
        if hasattr(self, 'rect'):
            self.rect.pos, self.rect.size = self.pos, self.size

    def atualizar_tema(self):
        app = MDApp.get_running_app()
        tema_atual = app.theme_cls.theme_style
        self.cores_atuais = self.paleta[tema_atual]
        self.set_visual_state(self.is_selected_state, self.is_highlighted_state, self.is_match_state)

    def set_visual_state(self, is_selected=False, is_highlighted=False, is_match=False):
        self.is_selected_state = is_selected
        self.is_highlighted_state = is_highlighted
        self.is_match_state = is_match

        cores = self.cores_atuais

        if is_selected:
            bg = cores["selected"]
        elif self.is_wrong:
            bg = cores["conflict"]
        elif is_match:
            bg = cores["match"]
        elif is_highlighted:
            bg = cores["highlight"]
        elif self.fixed:
            bg = cores["fixed"]
        else:
            bg = cores["base"]

        if self.is_wrong:
            txt = cores["text_error"]
        elif self.fixed:
            txt = cores["text_fixed"]
        else:
            txt = cores["text_input"]

        self.cor_rect.rgba = bg
        self.text_color = txt
        self.text = str(self.value) if self.value != 0 else ""

    def update_text(self):
        self.text = str(self.value) if self.value != 0 else ""

    def on_release(self):
        app_root = App.get_running_app().root
        if app_root:
            tela_sudoku = app_root.get_screen('sudoku')
            tela_sudoku.selecionar_celula(self.row, self.col)

# ====================== WIDGET: BOTÃO DE MENU INFERIOR ======================

class BotaoMenuInferior(ButtonBehavior, BoxLayout):
    def __init__(self, icon_name, text_label, action_id, parent_screen, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.action_id = action_id 
        self.parent_screen = parent_screen
        self.padding = dp(2)
        
        self.icon = MDIconButton(
            icon=icon_name, pos_hint={'center_x': 0.5}, icon_size=dp(26),
            theme_text_color="Custom", text_color=(0.5, 0.5, 0.5, 1) 
        )
        self.icon.on_release = self.on_release 
        
        self.label = MDLabel(
            text=text_label, halign="center", theme_text_color="Custom",
            text_color=(0.5, 0.5, 0.5, 1), font_style="Caption"
        )
        
        self.add_widget(self.icon)
        self.add_widget(self.label)

    def on_release(self):
        self.parent_screen.gerenciar_menu_inferior(self.action_id, self)
        
    def atualizar_cor(self, cor_texto):
        self.icon.text_color = cor_texto
        self.label.text_color = cor_texto


# ====================== TELA: DEFINIÇÃO DO JOGO ======================

class TelaDefinicaoSudoku(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'definicao_sudoku'
        self.card_bg_color = None
        self.labels_texto = [] 
        self._build_ui()

    def _build_ui(self):
        layout = FloatLayout()
        with layout.canvas.before:
            self.layout_bg_color = Color(0.65, 0.85, 0.90, 1) 
            self.rect_bg = Rectangle(pos=layout.pos, size=layout.size)
        layout.bind(pos=self._update_bg_rect, size=self._update_bg_rect)

        header = MDBoxLayout(orientation='horizontal', size_hint=(1, 0.08), pos_hint={'top': 1}, padding=dp(10), spacing=dp(10))
        btn_voltar = MDIconButton(icon="arrow-left", theme_text_color="Custom", text_color=(0.5, 0.5, 0.5, 1), on_release=self.voltar_jogo)
        lbl_titulo = MDLabel(text="Manual do Jogador", halign="left", valign="center", font_style="H6", theme_text_color="Custom", text_color=(0.5, 0.5, 0.5, 1))
        header.add_widget(btn_voltar)
        header.add_widget(lbl_titulo)
        layout.add_widget(header)

        scroll = ScrollView(size_hint=(1, 0.92), pos_hint={'top': 0.92}, do_scroll_x=False)
        box_central = MDBoxLayout(orientation='vertical', adaptive_height=True, padding=[dp(20), dp(10), dp(20), dp(40)], spacing=dp(20))

        card = MDCard(orientation='vertical', padding=dp(20), spacing=dp(15), size_hint_y=None, adaptive_height=True, size_hint_x=0.9, pos_hint={'center_x': 0.5}, radius=[dp(12)], elevation=2)
        self.card_ref = card 
        
        self.add_section_title(card, "O Objetivo", "flag-checkered")
        self.add_body_text(card, "O Sudoku é jogado em uma grade 9x9. O objetivo é simples: preencher todas as células vazias com números de 1 a 9.")
        self.add_section_title(card, "As 3 Regras de Ouro", "alert-decagram-outline")
        self.add_body_text(card, "Para vencer, você nunca pode repetir um número nas seguintes situações:")
        self.add_bullet_point(card, "Linhas Horizontais", "Cada linha deve ter os números 1-9 sem repetição.")
        self.add_bullet_point(card, "Colunas Verticais", "Cada coluna deve ter os números 1-9 sem repetição.")
        self.add_bullet_point(card, "Quadrantes (3x3)", "Cada bloco quadrado marcado por linhas grossas deve ter os números 1-9.")
        self.add_section_title(card, "Estratégias Básicas", "lightbulb-on-outline")
        self.add_subtitle(card, "1. O Último Solteiro")
        self.add_body_text(card, "Se em uma linha, coluna ou bloco já existem 8 números preenchidos, o nono número é óbvio! É o que está faltando.")
        self.add_subtitle(card, "2. Varredura (Scanning)")
        self.add_body_text(card, "Escolha um número (ex: 5). Olhe para os blocos 3x3 e veja onde o 5 NÃO pode entrar por causa das linhas e colunas vizinhas.")
        self.add_subtitle(card, "3. Anotações (Notas)")
        self.add_body_text(card, "Se você não tem certeza, não chute! Use a lógica para eliminar possibilidades.")

        box_central.add_widget(card)
        lbl_footer = MDLabel(text="Divirta-se exercitando seu cérebro!", halign="center", theme_text_color="Hint", font_style="Caption")
        box_central.add_widget(lbl_footer)
        scroll.add_widget(box_central)
        layout.add_widget(scroll)
        self.add_widget(layout)
        self.atualizar_tema_conteudo()

    def _update_bg_rect(self, instance, value):
        self.rect_bg.pos = instance.pos
        self.rect_bg.size = instance.size

    def add_section_title(self, layout, text, icon):
        box = MDBoxLayout(orientation='horizontal', spacing=dp(10), adaptive_height=True)
        ico = MDIconButton(icon=icon, theme_text_color="Custom", text_color=(0.2, 0.6, 1, 1), pos_hint={'center_y': 0.5})
        lbl = MDLabel(text=text, font_style="H6", bold=True, adaptive_height=True, pos_hint={'center_y': 0.5}, theme_text_color="Custom")
        self.labels_texto.append(lbl)
        box.add_widget(ico)
        box.add_widget(lbl)
        layout.add_widget(box)

    def add_subtitle(self, layout, text):
        lbl = MDLabel(text=text, font_style="Subtitle1", bold=True, theme_text_color="Custom", adaptive_height=True)
        self.labels_texto.append(lbl)
        layout.add_widget(lbl)

    def add_body_text(self, layout, text):
        lbl = MDLabel(text=text, font_style="Body2", theme_text_color="Custom", adaptive_height=True, markup=True)
        self.labels_texto.append(lbl)
        layout.add_widget(lbl)

    def add_bullet_point(self, layout, title, desc):
        box = MDBoxLayout(orientation='vertical', adaptive_height=True, padding=[dp(10), 0, 0, dp(5)])
        lbl_title = MDLabel(text=f"• {title}", font_style="Subtitle2", bold=True, theme_text_color="Custom", adaptive_height=True)
        lbl_desc = MDLabel(text=desc, font_style="Caption", theme_text_color="Custom", adaptive_height=True)
        self.labels_texto.append(lbl_title)
        self.labels_texto.append(lbl_desc)
        box.add_widget(lbl_title)
        box.add_widget(lbl_desc)
        layout.add_widget(box)

    def on_enter(self):
        self.atualizar_tema_conteudo()

    def atualizar_tema_conteudo(self):
        app = MDApp.get_running_app()
        is_dark = app.theme_cls.theme_style == "Dark"
        bg_screen = (0.05, 0.05, 0.05, 1) if is_dark else (0.65, 0.85, 0.90, 1)
        bg_card = (0.15, 0.15, 0.15, 1) if is_dark else (1, 1, 1, 1)
        txt_primary = (0.9, 0.9, 0.9, 1) if is_dark else (0.2, 0.2, 0.2, 1)
        self.layout_bg_color.rgba = bg_screen
        self.card_ref.md_bg_color = bg_card
        for lbl in self.labels_texto:
            lbl.text_color = txt_primary

    def voltar_jogo(self, instance):
        if self.manager:
            self.manager.transition = SlideTransition(direction="right")
            self.manager.current = 'sudoku'


# ====================== TELA: SUDOKU (PRINCIPAL) ======================

class TelaSudoku(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'sudoku'
        self.generator = SudokuGenerator()
        self.cells, self.tabuleiro_logico = {}, None
        self.celula_selecionada = None
        
        self.dificuldade = "medio"
        
        self.erros = 0
        self.max_erros = 5
        self.dicas_restantes = 3
        
        self.tempo_segundos = 0 
        self.timer_event = None
        self.dialog = None
        
        # Referências de Cores
        self.layout_bg_color = None
        self.barra_inferior_bg_color = None
        self.botoes_menu = []
        
        self.menu_dificuldade = None
        self.menu_dicas = None
        self.menu_score = None 
        
        self.lista_dicas = [
            "Varredura Visual: Escolha um número e veja onde ele está nos blocos.",
            "Único Candidato: Pergunte 'Quais números NÃO podem estar aqui?'.",
            "Linhas e Colunas: Se falta só um número na linha, é ele!",
            "Blocos: Verifique se um número elimina linhas inteiras no bloco.",
            "Comece pelo Básico: Preencha onde tem mais números."
        ]
        
        self._build_ui()

    def _build_ui(self):
        layout = FloatLayout()
        
        with layout.canvas.before:
            self.layout_bg_color = Color(0.65, 0.85, 0.90, 1) 
            self.bg_rect = Rectangle(pos=layout.pos, size=layout.size)
            
        layout.bind(pos=self._update_bg_rect, size=self._update_bg_rect)
        
        # HEADER
        header_layout = BoxLayout(orientation='horizontal', size_hint=(0.94, 0.08), pos_hint={'center_x': 0.5, 'top': 0.99}, spacing=dp(5))
        
        self.lbl_erros = MDLabel(text="Erros: 0/5", halign="left", valign="center", size_hint_x=0.35, theme_text_color="Custom", text_color=(0.2, 0.2, 0.2, 1))
        self.lbl_tempo = MDLabel(text="00:00", halign="center", valign="center", size_hint_x=0.25, font_style="H6", theme_text_color="Custom", text_color=(0.1, 0.1, 0.1, 1))
        
        self.btn_tema = MDIconButton(icon="weather-night", icon_size=dp(30), theme_text_color="Custom", text_color=(0.2, 0.2, 0.2, 1), pos_hint={'center_y': 0.5}, on_release=self.trocar_tema)
        self.btn_pause = MDIconButton(icon="pause", icon_size=dp(36), theme_text_color="Custom", text_color=(0.1, 0.1, 0.1, 1), pos_hint={'center_y': 0.5}, on_release=self.pausar_jogo)
        
        header_layout.add_widget(self.lbl_erros)
        header_layout.add_widget(self.lbl_tempo)
        header_layout.add_widget(self.btn_tema)
        header_layout.add_widget(self.btn_pause)
        layout.add_widget(header_layout)

        # Grade
        self.grade_9x9 = GridLayout(cols=9, rows=9, spacing=dp(2), size_hint=(0.94, 0.52), pos_hint={'center_x': 0.5, 'center_y': 0.61})
        self.grade_9x9.bind(pos=self.desenhar_linhas_grade, size=self.desenhar_linhas_grade)
        layout.add_widget(self.grade_9x9)
        
        teclado = self._criar_teclado()
        layout.add_widget(teclado)
        
        barra_inferior = self._criar_barra_inferior()
        layout.add_widget(barra_inferior)
        
        self.add_widget(layout)
        Clock.schedule_once(lambda dt: self._update_bg_rect(layout, None), 0)

    def _update_bg_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def _criar_barra_inferior(self):
        container = GridLayout(cols=3, size_hint=(1, 0.08), pos_hint={'x': 0, 'bottom': 1}, spacing=dp(5))
        
        with container.canvas.before:
            self.barra_inferior_bg_color = Color(1, 1, 1, 1)
            Rectangle(pos=container.pos, size=container.size)
            Color(0.8, 0.8, 0.8, 1)
            Line(points=[container.x, container.top, container.right, container.top], width=1)
        
        self.btn_dicas = BotaoMenuInferior("lightbulb-outline", "Dicas", "dicas", self)
        self.btn_dif = BotaoMenuInferior("tune", "Dificuldade", "dificuldade", self)
        self.btn_score = BotaoMenuInferior("chart-bar", "Score", "score", self)
        self.botoes_menu = [self.btn_dicas, self.btn_dif, self.btn_score]
        
        container.add_widget(self.btn_dicas)
        container.add_widget(self.btn_dif)
        container.add_widget(self.btn_score)
        
        container.bind(pos=lambda c, v: self._update_bg(c), size=lambda c, v: self._update_bg(c))
        return container

    def _update_bg(self, widget):
        widget.canvas.before.clear()
        with widget.canvas.before:
            if self.barra_inferior_bg_color:
                Color(self.barra_inferior_bg_color.r, self.barra_inferior_bg_color.g, self.barra_inferior_bg_color.b, 1)
            else:
                Color(1, 1, 1, 1)
            Rectangle(pos=widget.pos, size=widget.size)
            Color(0.8, 0.8, 0.8, 1)
            Line(points=[widget.x, widget.top, widget.right, widget.top], width=1)

    def trocar_tema(self, instance):
        app = MDApp.get_running_app()
        novo_tema = "Dark" if app.theme_cls.theme_style == "Light" else "Light"
        app.theme_cls.theme_style = novo_tema
        is_dark = (novo_tema == "Dark")
        
        cor_fundo = (0.05, 0.05, 0.05, 1) if is_dark else (0.65, 0.85, 0.90, 1)
        cor_texto = (0.9, 0.9, 0.9, 1) if is_dark else (0.2, 0.2, 0.2, 1)
        cor_barra = (0.1, 0.1, 0.1, 1) if is_dark else (1, 1, 1, 1)
        
        self.layout_bg_color.rgba = cor_fundo
        self.barra_inferior_bg_color.rgba = cor_barra
        self.lbl_erros.text_color = cor_texto
        self.lbl_tempo.text_color = cor_texto
        self.btn_tema.text_color = cor_texto
        self.btn_pause.text_color = cor_texto
        self.btn_tema.icon = "weather-sunny" if is_dark else "weather-night"
        
        cor_menu_txt = (0.7, 0.7, 0.7, 1) if is_dark else (0.5, 0.5, 0.5, 1)
        for btn in self.botoes_menu:
            btn.atualizar_cor(cor_menu_txt)
        
        for cell in self.cells.values():
            cell.atualizar_tema()
            
        self.desenhar_linhas_grade()
        self._update_bg(self.btn_dicas.parent)

    def gerenciar_menu_inferior(self, action_id, widget_caller):
        if action_id == "dicas":
            self.abrir_menu_dicas(widget_caller)
        elif action_id == "dificuldade":
            self.abrir_menu_dificuldade(widget_caller)
        elif action_id == "score":
            self.abrir_menu_score(widget_caller)

    def abrir_menu_dificuldade(self, caller_widget):
        menu_items = [
            {"text": "Fundamental I (Fácil)", "viewclass": "OneLineListItem", "on_release": lambda x="facil": self.mudar_dificuldade_menu(x), "height": dp(64)},
            {"text": "Fundamental II (Médio)", "viewclass": "OneLineListItem", "on_release": lambda x="medio": self.mudar_dificuldade_menu(x), "height": dp(64)},
            {"text": "Ensino Médio (Difícil)", "viewclass": "OneLineListItem", "on_release": lambda x="dificil": self.mudar_dificuldade_menu(x), "height": dp(64)}
        ]
        self.menu_dificuldade = MDDropdownMenu(caller=caller_widget, items=menu_items, width_mult=5)
        self.menu_dificuldade.open()

    def mudar_dificuldade_menu(self, nivel):
        self.menu_dificuldade.dismiss()
        if self.dificuldade != nivel:
            self.dificuldade = nivel
            self.reiniciar(None)

    def abrir_menu_dicas(self, caller_widget):
        dicas_txt = f"Revelar Número ({self.dicas_restantes})"
        menu_items = [
            {"text": "Definição Jogo", "viewclass": "OneLineListItem", "on_release": lambda: self.executar_dica("texto"), "height": dp(64)},
            {"text": dicas_txt, "viewclass": "OneLineListItem", "on_release": lambda: self.executar_dica("revelar"), "height": dp(64)}
        ]
        self.menu_dicas = MDDropdownMenu(caller=caller_widget, items=menu_items, width_mult=5)
        self.menu_dicas.open()

    def executar_dica(self, tipo):
        self.menu_dicas.dismiss()
        if tipo == "texto":
            if self.manager:
                self.manager.transition = SlideTransition(direction="left")
                self.manager.current = 'definicao_sudoku'
        elif tipo == "revelar":
            self.usar_dica_revelar()

    def usar_dica_revelar(self):
        if not self.celula_selecionada:
            self.dialog = MDDialog(title="Ops!", text="Selecione uma célula vazia primeiro.", buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
            self.dialog.open()
            return
        if self.dicas_restantes <= 0:
            self.dialog = MDDialog(title="Sem Dicas", text="Você não tem mais dicas de revelação.", buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
            self.dialog.open()
            return

        r, c = self.celula_selecionada
        cell = self.cells[(r, c)]
        if cell.fixed or cell.value == self.generator.solucao[r][c]:
            return

        self.dicas_restantes -= 1
        self.inserir_numero(self.generator.solucao[r][c])

    def abrir_menu_score(self, caller_widget):
        tempo_gasto = self.tempo_segundos
        m, s = divmod(tempo_gasto, 60)
        str_nivel = f"Nível: {self.dificuldade.capitalize()}"
        str_erros = f"Erros: {self.erros}/{self.max_erros}"
        str_tempo = f"Tempo Jogado: {m:02d}:{s:02d}"

        menu_items = [
            {"text": str_nivel, "viewclass": "OneLineListItem", "height": dp(56)},
            {"text": str_erros, "viewclass": "OneLineListItem", "height": dp(56)},
            {"text": str_tempo, "viewclass": "OneLineListItem", "height": dp(56)}
        ]
        self.menu_score = MDDropdownMenu(caller=caller_widget, items=menu_items, width_mult=4, position="top", border_margin=dp(24))
        self.menu_score.open()

    def desenhar_linhas_grade(self, *args):
        grid = self.grade_9x9
        grid.canvas.after.clear()
        
        app = MDApp.get_running_app()
        is_dark = app.theme_cls.theme_style == "Dark"
        cor_borda = (0.4, 0.4, 0.4, 1) if is_dark else (0, 0, 0, 1)
        
        with grid.canvas.after:
            w, h = grid.width, grid.height
            x, y = grid.x, grid.y
            espessura = dp(2.5)

            Color(1.0, 0.7, 0.0, 1.0) 
            Line(points=[x + w/3, y, x + w/3, y + h], width=espessura, cap='square')
            Line(points=[x + 2*w/3, y, x + 2*w/3, y + h], width=espessura, cap='square')
            
            Color(1.0, 0.3, 0.3, 1.0)
            Line(points=[x, y + h/3, x + w, y + h/3], width=espessura, cap='square')
            Line(points=[x, y + 2*h/3, x + w, y + 2*h/3], width=espessura, cap='square')
            
            Color(*cor_borda)
            Line(rectangle=(x, y, w, h), width=dp(2))

    def _criar_teclado(self):
        teclado_layout = GridLayout(cols=1, rows=2, size_hint=(0.94, 0.18), pos_hint={'center_x': 0.5, 'center_y': 0.23}, spacing=dp(6))
        
        linha_superior = GridLayout(cols=5, spacing=dp(8))
        for i in range(1, 6):
            btn = MDRaisedButton(text=str(i), size_hint=(1, 1), elevation=2, on_release=lambda btn, n=i: self.inserir_numero(n))
            linha_superior.add_widget(btn)

        linha_inferior = GridLayout(cols=5, spacing=dp(8))
        for i in range(6, 10):
            btn = MDRaisedButton(text=str(i), size_hint=(1, 1), elevation=2, on_release=lambda btn, n=i: self.inserir_numero(n))
            linha_inferior.add_widget(btn)
            
        btn_x = MDRaisedButton(text="X", size_hint=(1, 1), elevation=2, md_bg_color=(0.8, 0.2, 0.2, 1), theme_text_color="Custom", text_color=(1, 1, 1, 1), on_release=lambda btn: self.inserir_numero(0))
        linha_inferior.add_widget(btn_x)

        teclado_layout.add_widget(linha_superior)
        teclado_layout.add_widget(linha_inferior)
        return teclado_layout

    def on_enter(self, *args):
        if not self.tabuleiro_logico:
            Thread(target=self.iniciar_novo_jogo).start()

    def iniciar_novo_jogo(self):
        self.erros = 0
        self.dicas_restantes = 3
        self.tempo_segundos = 0
        self.stop_timer()
        self.tabuleiro_logico = self.generator.gerar_tabuleiro(self.dificuldade)
        Clock.schedule_once(self._montar_grade, 0)
        Clock.schedule_once(self.start_timer, 0)

    def _montar_grade(self, dt):
        self.grade_9x9.clear_widgets()
        self.cells.clear()
        self.lbl_erros.text = f"Erros: 0/{self.max_erros}"
        self.lbl_erros.theme_text_color = "Custom"
        app = MDApp.get_running_app()
        cor_erro = (0.9, 0.9, 0.9, 1) if app.theme_cls.theme_style == "Dark" else (0.2, 0.2, 0.2, 1)
        self.lbl_erros.text_color = cor_erro

        for r in range(9):
            for c in range(9):
                valor = self.tabuleiro_logico[r][c]
                cell = CelulaSudoku(r, c, valor != 0, valor)
                self.grade_9x9.add_widget(cell)
                self.cells[(r, c)] = cell
        Clock.schedule_once(self.desenhar_linhas_grade, 0.1)

    def start_timer(self, dt=None):
        self.stop_timer()
        self.timer_event = Clock.schedule_interval(self.atualizar_tempo, 1)

    def stop_timer(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

    def atualizar_tempo(self, dt):
        self.tempo_segundos += 1
        m, s = divmod(self.tempo_segundos, 60)
        self.lbl_tempo.text = f"{m:02d}:{s:02d}"

    def pausar_jogo(self, instance):
        self.stop_timer()
        self.dialog = MDDialog(
            title="Pausado", 
            text="Continuar jogando?", 
            buttons=[
                MDFlatButton(text="SAIR", on_release=self.voltar), 
                MDFlatButton(text="CONTINUAR", on_release=self.retomar_jogo)
            ], 
            auto_dismiss=False
        )
        self.dialog.open()

    def retomar_jogo(self, inst):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = None
        self.start_timer()

    def selecionar_celula(self, row, col):
        self.celula_selecionada = (row, col)
        valor_selecionado = self.cells[(row, col)].value
        block_r = row // 3
        block_c = col // 3
        
        for (r, c), cell in self.cells.items():
            is_selected = (r == row and c == col)
            in_cross = (r == row) or (c == col)
            in_block = (r // 3 == block_r and c // 3 == block_c)
            is_match = (cell.value == valor_selecionado) and (valor_selecionado != 0) and not is_selected
            is_highlighted = (in_cross or in_block) and not is_selected
            
            cell.set_visual_state(is_selected=is_selected, is_highlighted=is_highlighted, is_match=is_match)

    def inserir_numero(self, num):
        if not self.celula_selecionada: return
        r, c = self.celula_selecionada
        cell = self.cells[(r, c)]
        if cell.fixed: return
        
        if num == 0:
            self.tabuleiro_logico[r][c] = 0
            cell.value = 0
            cell.is_wrong = False
            cell.update_text()
        else:
            valor_correto = self.generator.solucao[r][c]
            if num == valor_correto:
                self.tabuleiro_logico[r][c] = num
                cell.value = num
                cell.is_wrong = False
                cell.update_text()
                if self.generator.verificar_vitoria(self.tabuleiro_logico): self.game_finished(win=True)
            else:
                self.erros += 1
                self.lbl_erros.text = f"Erros: {self.erros}/{self.max_erros}"
                self.lbl_erros.theme_text_color = "Error"
                cell.value = num
                cell.is_wrong = True
                cell.update_text()
                if self.erros >= self.max_erros: self.game_finished(win=False)
        
        self.selecionar_celula(r, c)

    def contar_acertos(self):
        corretos = 0
        for r in range(9):
            for c in range(9):
                cell = self.cells[(r, c)]
                if cell.value != 0 and cell.value == self.generator.solucao[r][c]:
                    corretos += 1
        return corretos

    def formatar_tempo_str(self, segundos):
        m, s = divmod(segundos, 60)
        return f"{m:02d}:{s:02d}"

    def game_finished(self, win, timeout=False):
        self.stop_timer()
        titulo = "Parabéns!" if win else "Game Over"
        
        app = MDApp.get_running_app()
        user_id = getattr(app, 'user_id', None)
        
        # --- ATUALIZAÇÃO SEGURA: Só salva se tiver usuário ---
        if user_id:
            acertos = 81 if win else self.contar_acertos()
            base_points = {"facil": 1000, "medio": 2000, "dificil": 3000}
            pontos = base_points.get(self.dificuldade, 1000)
            pontos_finais = max(0, pontos - (self.erros * 100) - (self.tempo_segundos * 1))
            
            tempo_txt = self.formatar_tempo_str(self.tempo_segundos)
            msg = f"Pontos: {pontos_finais}\nTempo: {tempo_txt}"
            
            print(f"[SUDOKU] Salvando para usuário {user_id}...")
            Thread(target=banco_dados.salvar_sudoku, args=(
                user_id, 
                pontos_finais, 
                self.erros, 
                acertos, 
                self.dificuldade, 
                tempo_txt,
                win
            )).start()
        else:
            msg = "Pontos não salvos (Usuário não identificado)"
            print("[AVISO] Jogo não salvo: Nenhum usuário logado.")
        # ----------------------------------------------------

        self.dialog = MDDialog(
            title=titulo, 
            text=msg, 
            buttons=[
                MDFlatButton(text="SAIR", on_release=self.voltar), 
                MDFlatButton(text="NOVO", on_release=self.reiniciar)
            ], 
            auto_dismiss=False
        )
        self.dialog.open()

    def reiniciar(self, inst):
        if self.dialog: self.dialog.dismiss()
        self.dialog = None
        Thread(target=self.iniciar_novo_jogo).start()

    def voltar(self, *args):
        if self.dialog: self.dialog.dismiss()
        if self.manager:
            self.manager.transition = SlideTransition(direction="right")
            self.manager.current = 'jogar'