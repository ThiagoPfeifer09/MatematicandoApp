import random
from threading import Thread

from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.anchorlayout import MDAnchorLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.toast import toast
from kivy.core.window import Window

import banco_dados

# --- CORES ---
CORES_X = (0.4, 0.2, 0.8, 1)
CORES_O = (1, 0.6, 0.2, 1)
COR_DESTAKE = (0.2, 0.8, 0.4, 1)

CORES_LIGHT = {
    "fundo": (0.65, 0.85, 0.90, 1), 
    "tabuleiro_bg": (0.9, 0.9, 0.95, 1),
    "card_bg": (1, 1, 1, 1),
    "texto": (0.2, 0.3, 0.4, 1),
    "icone": (0.4, 0.4, 0.4, 1)
}

CORES_DARK = {
    "fundo": (0.12, 0.12, 0.12, 1),
    "tabuleiro_bg": (0.18, 0.18, 0.2, 1),
    "card_bg": (0.25, 0.25, 0.25, 1),
    "texto": (0.9, 0.9, 0.9, 1),
    "icone": (0.8, 0.8, 0.8, 1)
}

class PlacarWidget(MDCard):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (0.9, None)
        self.height = dp(60)
        self.radius = [dp(15)]
        self.elevation = 2
        self.pos_hint = {"center_x": 0.5}
        
        layout = MDBoxLayout(orientation="horizontal", padding=dp(10))
        self.lbl_jogador = MDLabel(text="Você: 0", halign="center", bold=True, theme_text_color="Custom", text_color=CORES_X, font_style="H6")
        self.lbl_pc = MDLabel(text="PC: 0", halign="center", bold=True, theme_text_color="Custom", text_color=CORES_O, font_style="H6")
        
        layout.add_widget(self.lbl_jogador)
        layout.add_widget(MDLabel(text="|", halign="center", size_hint_x=None, width=dp(10), theme_text_color="Hint"))
        layout.add_widget(self.lbl_pc)
        self.add_widget(layout)
        
    def atualizar(self, v, p):
        self.lbl_jogador.text = f"Você: {v}"
        self.lbl_pc.text = f"PC: {p}"

    def atualizar_tema(self, cores):
        self.md_bg_color = cores["card_bg"]

class BottomBarGame(MDCard):
    def __init__(self, callback_dica, callback_dif, callback_score, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (1, None)
        self.height = dp(70)
        self.radius = [dp(20), dp(20), 0, 0]
        self.elevation = 10
        layout = MDBoxLayout(orientation="horizontal", spacing=dp(10), padding=dp(5))
        
        self.btn_dica, self.lbl_dica = self.criar_botao("Dicas", "lightbulb-outline", callback_dica)
        self.btn_dif, self.lbl_dif = self.criar_botao("Dificuldade", "tune", callback_dif)
        self.btn_score, self.lbl_score = self.criar_botao("Score", "chart-bar", callback_score)
        
        layout.add_widget(self.empacotar(self.btn_dica, self.lbl_dica))
        layout.add_widget(self.empacotar(self.btn_dif, self.lbl_dif))
        layout.add_widget(self.empacotar(self.btn_score, self.lbl_score))
        self.add_widget(layout)

    def criar_botao(self, texto, icone, acao):
        btn = MDIconButton(icon=icone, pos_hint={"center_x": 0.5}, theme_text_color="Custom", on_release=lambda x: acao(x))
        lbl = MDLabel(text=texto, halign="center", font_style="Caption", theme_text_color="Custom")
        return btn, lbl

    def empacotar(self, btn, lbl):
        box = MDBoxLayout(orientation="vertical", spacing=dp(2))
        box.add_widget(btn)
        box.add_widget(lbl)
        return box

    def atualizar_tema(self, cores):
        self.md_bg_color = cores["card_bg"]
        for btn, lbl in [(self.btn_dica, self.lbl_dica), (self.btn_dif, self.lbl_dif), (self.btn_score, self.lbl_score)]:
            btn.text_color = cores["icone"]
            lbl.text_color = cores["icone"]

class CardTabuleiro(MDCard):
    def __init__(self, index, callback, **kwargs):
        super().__init__(**kwargs)
        self.index = index
        self.callback = callback
        self.equacao = ""
        self.resultado = 0
        self.estado = None 
        self.size_hint = (1, 1) 
        self.radius = [dp(12)]
        self.elevation = 2
        self.ripple_behavior = True
        self.padding = dp(5)
        
        self.label = MDLabel(text="", halign="center", valign="middle", theme_text_color="Custom", font_style="H5", bold=True)
        self.add_widget(self.label)
        self.bind(on_release=self.ao_clicar)

    def gerar_conta(self, dificuldade, cores_atuais):
        op = random.choice(['+', '-'])
        a, b = 0, 0
        if dificuldade == "Primario":
            if op == '+': a, b = random.randint(1, 10), random.randint(1, 10)
            else: a = random.randint(5, 15); b = random.randint(1, a)
        elif dificuldade == "Fundamental":
            op = random.choice(['+', '-', '*'])
            if op == '*': a, b = random.randint(2, 9), random.randint(2, 5)
            elif op == '+': a, b = random.randint(10, 50), random.randint(5, 40)
            else: a = random.randint(20, 60); b = random.randint(5, a)
        else: # Medio
            op = random.choice(['+', '-', '*', '/'])
            if op == '*': a, b = random.randint(4, 12), random.randint(3, 9)
            elif op == '/': 
                b = random.randint(2, 9); a = b * random.randint(2, 10)
            elif op == '+': a, b = random.randint(20, 100), random.randint(10, 80)
            else: a = random.randint(30, 100); b = random.randint(10, a)

        if op == '*': self.resultado = a * b
        elif op == '/': self.resultado = int(a / b)
        elif op == '+': self.resultado = a + b
        else: self.resultado = a - b
            
        sym = '÷' if op == '/' else 'x' if op == '*' else op
        self.equacao = f"{a} {sym} {b}"
        self.label.text = self.equacao
        self.label.font_size = "26sp" 
        self.estado = None
        self.elevation = 2
        self.atualizar_tema(cores_atuais)

    def atualizar_tema(self, cores):
        if self.estado is None:
            self.md_bg_color = cores["card_bg"]
            self.label.text_color = cores["texto"]

    def marcar(self, jogador):
        self.estado = jogador
        self.label.text = jogador
        self.label.font_style = "H3"
        self.label.font_size = "60sp" 
        self.elevation = 0
        self.md_bg_color = CORES_X if jogador == "X" else CORES_O
        self.label.text_color = (1, 1, 1, 1)

    def destacar_dica(self):
        orig_color = self.md_bg_color
        self.md_bg_color = COR_DESTAKE
        Clock.schedule_once(lambda dt: setattr(self, 'md_bg_color', orig_color), 1.5)

    def ao_clicar(self, *args):
        if self.estado is None: self.callback(self)

class JogoDaVelhaScreen(Screen):
    dialog_fim_jogo = None
    menu_dificuldade = None
    menu_score = None
    menu_dica = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cards = []
        self.game_active = True
        self.dificuldade_atual = "Primario" 
        self.stats = {"vitorias": 0, "derrotas": 0, "empates": 0}
        self.tema_atual = "Light" 
        self.cores = CORES_LIGHT
        
        # Variáveis de Tempo
        self.tempo_segundos = 0
        self.timer_event = None
        
        self.layout = MDBoxLayout(orientation="vertical")
        
        # TOPO
        topo = MDBoxLayout(size_hint_y=None, height=dp(60), padding=[dp(10), dp(5)])
        self.btn_voltar = MDIconButton(icon="arrow-left", on_release=self.voltar, theme_text_color="Custom")
        self.titulo = MDLabel(text="", halign="center", bold=True, font_style="H6", theme_text_color="Custom")
        
        box_acoes = MDBoxLayout(adaptive_width=True, spacing=dp(5), padding=dp(5))
        self.lbl_tempo = MDLabel(text="00:00", halign="center", valign="center", size_hint_x=None, width=dp(50), theme_text_color="Custom", bold=True)
        self.btn_tema = MDIconButton(icon="theme-light-dark", on_release=self.alternar_tema, theme_text_color="Custom")
        self.btn_reset = MDIconButton(icon="refresh", on_release=self.resetar_jogo, theme_text_color="Custom")
        
        box_acoes.add_widget(self.lbl_tempo)
        box_acoes.add_widget(self.btn_tema)
        box_acoes.add_widget(self.btn_reset)
        
        topo.add_widget(self.btn_voltar)
        topo.add_widget(self.titulo)
        topo.add_widget(box_acoes)
        self.layout.add_widget(topo)
        
        self.placar = PlacarWidget()
        box_placar = MDBoxLayout(size_hint_y=None, height=dp(70), padding=[dp(20), dp(5)])
        box_placar.add_widget(self.placar)
        self.layout.add_widget(box_placar)

        area_central = MDAnchorLayout(anchor_x='center', anchor_y='center')
        self.board_bg = MDCard(size_hint=(None, None), size=(dp(300), dp(300)), radius=[dp(20)], elevation=0, padding=dp(10))
        self.grid = MDGridLayout(cols=3, spacing=dp(8), size_hint=(1, 1))
        
        for i in range(9):
            card = CardTabuleiro(i, self.abrir_pergunta)
            self.cards.append(card)
            self.grid.add_widget(card)
            
        self.board_bg.add_widget(self.grid)
        area_central.add_widget(self.board_bg)
        self.layout.add_widget(area_central)
        
        self.lbl_status = MDLabel(text="Sua vez!", halign="center", size_hint_y=None, height=dp(30), theme_text_color="Custom", font_style="Caption")
        self.layout.add_widget(self.lbl_status)

        self.footer = BottomBarGame(self.acao_dica, self.acao_dificuldade, self.acao_score)
        self.layout.add_widget(self.footer)
        self.add_widget(self.layout)
        
        self.aplicar_tema()
        self.bind(size=self.atualizar_tamanho_board) 
        
        Clock.schedule_once(lambda dt: self.resetar_jogo())

    def start_timer(self):
        self.stop_timer()
        self.tempo_segundos = 0
        self.lbl_tempo.text = "00:00"
        self.timer_event = Clock.schedule_interval(self.atualizar_tempo, 1)

    def stop_timer(self):
        if self.timer_event:
            self.timer_event.cancel()
            self.timer_event = None

    def atualizar_tempo(self, dt):
        self.tempo_segundos += 1
        m, s = divmod(self.tempo_segundos, 60)
        self.lbl_tempo.text = f"{m:02d}:{s:02d}"

    def atualizar_tamanho_board(self, *args):
        altura = self.height - dp(270)
        largura = self.width - dp(40) 
        lado = min(largura, altura)
        if lado < dp(200): lado = dp(200)
        self.board_bg.size = (lado, lado)

    def alternar_tema(self, instance):
        if self.tema_atual == "Light":
            self.tema_atual = "Dark"
            self.cores = CORES_DARK
            MDApp.get_running_app().theme_cls.theme_style = "Dark"
        else:
            self.tema_atual = "Light"
            self.cores = CORES_LIGHT
            MDApp.get_running_app().theme_cls.theme_style = "Light"
        self.aplicar_tema()

    def aplicar_tema(self):
        self.layout.md_bg_color = self.cores["fundo"]
        self.board_bg.md_bg_color = self.cores["tabuleiro_bg"]
        self.titulo.text_color = self.cores["texto"]
        self.btn_voltar.text_color = self.cores["texto"]
        self.btn_tema.text_color = self.cores["texto"]
        self.btn_reset.text_color = self.cores["texto"]
        self.lbl_tempo.text_color = self.cores["texto"]
        self.placar.atualizar_tema(self.cores)
        self.footer.atualizar_tema(self.cores)
        self.lbl_status.text_color = self.cores["texto"]
        for card in self.cards:
            card.atualizar_tema(self.cores)

    def voltar(self, *args):
        self.stop_timer()
        if self.manager: self.manager.current = "jogar"

    def definir_dificuldade(self, nivel):
        nivel_limpo = nivel.lower()
        if "prim" in nivel_limpo: self.dificuldade_atual = "Primario"
        elif "fund" in nivel_limpo: self.dificuldade_atual = "Fundamental"
        elif "med" in nivel_limpo: self.dificuldade_atual = "Medio"
        else: self.dificuldade_atual = "Primario"
        self.resetar_jogo()

    def acao_dificuldade(self, caller_widget):
        menu_items = [
            {"text": "Fundamental I (Fácil)", "viewclass": "OneLineListItem", "on_release": lambda x="Primario": self.mudar_dif_menu(x)},
            {"text": "Fundamental II (Médio)", "viewclass": "OneLineListItem", "on_release": lambda x="Fundamental": self.mudar_dif_menu(x)},
            {"text": "Ensino Médio (Difícil)", "viewclass": "OneLineListItem", "on_release": lambda x="Medio": self.mudar_dif_menu(x)}
        ]
        self.menu_dificuldade = MDDropdownMenu(caller=caller_widget, items=menu_items, width_mult=4, max_height=dp(200))
        self.menu_dificuldade.open()

    def mudar_dif_menu(self, nivel):
        self.menu_dificuldade.dismiss()
        self.dificuldade_atual = nivel
        self.resetar_jogo()
        toast(f"Dificuldade: {nivel}")

    def acao_score(self, caller_widget):
        stats_items = [
            {"text": f"Vitórias: {self.stats['vitorias']}", "viewclass": "OneLineListItem", "on_release": lambda: self.menu_score.dismiss()},
            {"text": f"Derrotas: {self.stats['derrotas']}", "viewclass": "OneLineListItem", "on_release": lambda: self.menu_score.dismiss()},
            {"text": f"Empates:  {self.stats['empates']}", "viewclass": "OneLineListItem", "on_release": lambda: self.menu_score.dismiss()},
        ]
        self.menu_score = MDDropdownMenu(caller=caller_widget, items=stats_items, width_mult=3)
        self.menu_score.open()

    def acao_dica(self, caller_widget):
        if not self.game_active: return
        melhor_card = self.melhor_jogada_pc(simular_para="X")
        texto_dica = "Sem dicas óbvias agora!"
        if melhor_card:
            melhor_card.destacar_dica()
            texto_dica = f"Dica: O resultado é {melhor_card.resultado}!"
        self.menu_dica = MDDropdownMenu(caller=caller_widget, items=[{"text": texto_dica, "viewclass": "OneLineListItem", "on_release": lambda: self.menu_dica.dismiss()}], width_mult=4)
        self.menu_dica.open()

    def abrir_pergunta(self, card):
        if not self.game_active: return
        self.card_atual = card
        box = MDBoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None, height=dp(90))
        self.input_resp = MDTextField(hint_text="Resultado", helper_text="Digite e confirme", input_filter="int", halign="center", font_size="22sp")
        box.add_widget(self.input_resp)
        self.dialog = MDDialog(title=f"Quanto é {card.equacao}?", type="custom", content_cls=box,
                               buttons=[MDFlatButton(text="CANCELAR", on_release=lambda x: self.dialog.dismiss()),
                                        MDRaisedButton(text="OK", md_bg_color=CORES_X, on_release=self.verificar)])
        self.dialog.open()

    def verificar(self, *args):
        try:
            if not self.input_resp.text: return
            if int(self.input_resp.text) == self.card_atual.resultado:
                self.dialog.dismiss()
                self.card_atual.marcar("X")
                self.checar_estado("X")
            else:
                self.input_resp.error = True
        except: pass

    def checar_estado(self, last_player):
        if self.checar_vitoria(last_player):
            if last_player == "X":
                self.stats["vitorias"] += 1
                self.fim("Vitória!", True)
            else:
                self.stats["derrotas"] += 1
                self.fim("Derrota!", False)
            self.placar.atualizar(self.stats["vitorias"], self.stats["derrotas"])
        elif all(c.estado is not None for c in self.cards):
            self.stats["empates"] += 1
            self.fim("Velha (Empate)!", False)
        else:
            if last_player == "X":
                self.game_active = False
                self.lbl_status.text = "PC pensando..."
                Clock.schedule_once(self.jogada_pc, 0.8)
            else:
                self.game_active = True
                self.lbl_status.text = "Sua vez!"

    def jogada_pc(self, dt):
        card = self.melhor_jogada_pc(simular_para="O")
        if not card: card = self.melhor_jogada_pc(simular_para="X") 
        if not card: 
            livres = [c for c in self.cards if c.estado is None]
            if livres: card = random.choice(livres)
        if card:
            card.marcar("O")
            self.checar_estado("O")

    def melhor_jogada_pc(self, simular_para):
        livres = [c for c in self.cards if c.estado is None]
        for card in livres:
            card.estado = simular_para
            if self.checar_vitoria(simular_para):
                card.estado = None
                return card
            card.estado = None
        return None

    def checar_vitoria(self, j):
        wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
        return any(all(self.cards[i].estado == j for i in p) for p in wins)

    def formatar_tempo_str(self, segundos):
        m, s = divmod(segundos, 60)
        return f"{m:02d}:{s:02d}"

    def fim(self, msg, win):
        self.stop_timer() 
        self.game_active = False
        self.cor = CORES_X if win else CORES_O
        
        # --- ATUALIZAÇÃO SEGURA DO SAVE ---
        app = MDApp.get_running_app()
        user_id = getattr(app, 'user_id', None)
        
        vitoria = (msg == "Vitória!")
        derrota = (msg == "Derrota!")
        empate = ("Empate" in msg)
        tempo_txt = self.formatar_tempo_str(self.tempo_segundos)

        if user_id:
            print(f"[VELHA] Salvando para usuário {user_id}...")
            Thread(target=banco_dados.salvar_jogovelha, args=(user_id, vitoria, derrota, empate, self.dificuldade_atual, tempo_txt)).start()
        else:
            print("[AVISO] Jogo não salvo: Nenhum usuário logado.")
        # --------------------------------

        self.dialog_fim_jogo = MDDialog(
            title=msg, text=f"Tempo: {tempo_txt}\nO que deseja fazer?",
            buttons=[MDRaisedButton(text="NOVA PARTIDA", md_bg_color=self.cor, on_release=lambda x: (self.dialog_fim_jogo.dismiss(), self.resetar_jogo()))]
        )
        self.dialog_fim_jogo.open()

    def resetar_jogo(self, *args):
        self.start_timer() 
        self.game_active = True
        self.lbl_status.text = f"Nível: {self.dificuldade_atual} | Sua vez!"
        for c in self.cards: 
            c.gerar_conta(self.dificuldade_atual, self.cores)