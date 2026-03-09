import math
from random import randint, choice

# Kivy Imports
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Ellipse
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout  # <--- O IMPORT QUE FALTAVA ESTÁ AQUI

# KivyMD Imports
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.menu import MDDropdownMenu

# ======================================================================
# WIDGETS AUXILIARES (BOLA, PINO, TEXTO)
# ======================================================================
class BolaWidget(MDFloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(110), dp(110))
        self.pos_hint = {'center_x': 0.5, 'y': 0.22} 
        
        with self.canvas.before:
            Color(1, 1, 1, 1) # Branco
            self.shape = Ellipse(size=self.size, pos=self.pos)
        
        self.bind(pos=self.atualizar_shape, size=self.atualizar_shape)

        self.lbl_numero = MDLabel(
            text="0", halign="center", valign="center", font_style="H3", bold=True,
            theme_text_color="Custom", text_color=(0.2, 0.2, 0.2, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.add_widget(self.lbl_numero)

    def atualizar_shape(self, *args):
        self.shape.pos = self.pos
        self.shape.size = self.size

class PinoCard(MDCard):
    def __init__(self, texto, resultado, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(90), dp(55))
        self.radius = [dp(12)]
        self.elevation = 4
        self.md_bg_color = (1, 1, 1, 1)
        self.resultado = resultado
        self.ativo = True

        self.lbl = MDLabel(
            text=texto, halign="center", valign="center", bold=True, font_style="H6",
            theme_text_color="Custom", text_color=(0.2, 0.2, 0.2, 1)
        )
        self.add_widget(self.lbl)

class FloatingText(MDLabel):
    def __init__(self, text, pos_center, color=(0, 0.8, 0, 1), **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.bold = True
        self.font_style = "H5"
        self.theme_text_color = "Custom"
        self.text_color = color
        self.halign = "center"
        self.size_hint = (None, None)
        self.size = (dp(150), dp(50))
        self.pos = (pos_center[0] - self.width/2, pos_center[1])
        
        anim = Animation(y=self.y + dp(80), opacity=0, duration=1.0, t='out_quad')
        anim.bind(on_complete=self.remover)
        anim.start(self)

    def remover(self, *args):
        if self.parent: self.parent.remove_widget(self)

# ======================================================================
# TELA DO JOGO (MAIN SCREEN)
# ======================================================================
class BolicheMatematicoScreen(Screen):
    pontos = NumericProperty(0)
    vidas = NumericProperty(3)
    dificuldade = StringProperty("Fundamental")
    em_movimento = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Camada 1: Elementos do Jogo (Fundo, Bola, Pinos)
        self.game_layer = FloatLayout()
        self.add_widget(self.game_layer)
        
        # Camada 2: Interface (Botões, Barras e Overlay de Início)
        self.ui_layer = FloatLayout()
        self.add_widget(self.ui_layer)
        
        self.pinos = []
        self.bola = None
        self.bola_start_pos = (0, 0)
        self.lbl_score_nav = None
        self.menu_diff = None
        self.menu_dicas = None
        self.start_overlay = None # Controle da tela de "Iniciar Jogo"

    def on_enter(self):
        """Chamado quando a tela abre"""
        self.game_layer.clear_widgets()
        self.ui_layer.clear_widgets()
        
        self.pontos = 0
        self.vidas = 3
        self.em_movimento = False
        self.start_overlay = None
        
        # 1. Carrega o visual base
        self.setup_background()
        self.setup_ui() 
        
        # 2. Mostra o botão de INICIAR (Bloqueia o jogo até clicar)
        self.mostrar_tela_inicio()

    # --- TELA DE INÍCIO (OVERLAY) ---
    def mostrar_tela_inicio(self):
        self.start_overlay = FloatLayout()
        
        # Fundo escurecido semi-transparente
        fundo = MDCard(md_bg_color=(0, 0, 0, 0.6), size_hint=(1, 1))
        self.start_overlay.add_widget(fundo)
        
        # Card Central
        card = MDCard(
            size_hint=(None, None), size=(dp(280), dp(220)),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            radius=[dp(20)], elevation=10, orientation="vertical",
            padding=dp(20), spacing=dp(20), md_bg_color=(1, 1, 1, 1)
        )
        
        card.add_widget(MDLabel(text="BOLICHE\nMATEMÁTICO", halign="center", font_style="H5", bold=True, theme_text_color="Primary"))
        card.add_widget(MDLabel(text="Arraste a bola para acertar\na resposta correta!", halign="center", font_style="Caption", theme_text_color="Secondary"))
        
        btn = MDRaisedButton(
            text="INICIAR JOGO", font_size="18sp", pos_hint={'center_x': 0.5},
            size_hint_x=1, md_bg_color=(0.2, 0.6, 1, 1),
            on_release=self.iniciar_partida
        )
        card.add_widget(btn)
        
        self.start_overlay.add_widget(card)
        self.ui_layer.add_widget(self.start_overlay)

    def iniciar_partida(self, instance):
        # Remove a tela de início
        if self.start_overlay:
            self.ui_layer.remove_widget(self.start_overlay)
            self.start_overlay = None
        
        # Cria a bola e os pinos
        self.setup_game_elements()
        self.gerar_rodada()

    # --- CONFIGURAÇÃO VISUAL ---
    def setup_background(self):
        try:
            # Certifique-se que a imagem existe na pasta
            self.game_layer.add_widget(Image(source='fundoapp.png', allow_stretch=True, keep_ratio=False))
        except:
            pass

    def setup_ui(self):
        # Barra Superior
        top_bar = MDBoxLayout(size_hint=(1, None), height=dp(70), padding=[dp(10), dp(5)], spacing=dp(10), pos_hint={"top": 1})
        
        btn_back = MDIconButton(icon="arrow-left", theme_text_color="Custom", text_color=(0.2, 0.2, 0.2, 1), on_release=self.voltar, pos_hint={"center_y": 0.5})
        top_bar.add_widget(btn_back)
        
        box_vidas = MDBoxLayout(adaptive_size=True, spacing=dp(5), pos_hint={"center_y": 0.5})
        box_vidas.add_widget(MDIconButton(icon="heart", theme_text_color="Custom", text_color=(1, 0.3, 0.3, 1), icon_size=dp(28), ripple_scale=0))
        self.lbl_vidas_txt = MDLabel(text="x3", bold=True, theme_text_color="Error", font_style="H6", adaptive_size=True, pos_hint={"center_y": 0.5})
        box_vidas.add_widget(self.lbl_vidas_txt)
        top_bar.add_widget(box_vidas)

        top_bar.add_widget(MDBoxLayout()) # Espaçador

        box_bateria = MDBoxLayout(orientation="vertical", size_hint_x=None, width=dp(140), spacing=dp(2), pos_hint={"center_y": 0.5})
        box_bateria.add_widget(MDLabel(text="CRITICO", font_style="Overline", halign="right", theme_text_color="Primary"))
        self.progress = MDProgressBar(value=0, color=(0.6, 0.2, 1, 1), size_hint_y=None, height=dp(8), radius=[dp(4)])
        box_bateria.add_widget(self.progress)
        top_bar.add_widget(box_bateria)
        
        self.ui_layer.add_widget(top_bar)

        # Barra Inferior
        bottom_card = MDCard(size_hint=(1, None), height=dp(100), radius=[dp(30), dp(30), 0, 0], md_bg_color=(1, 1, 1, 1), elevation=15, pos_hint={"bottom": 1})
        
        # AQUI O GRIDLAYOUT AGORA VAI FUNCIONAR COM O IMPORT CORRETO
        nav_grid = GridLayout(cols=3, size_hint=(1, 1), padding=[dp(0), dp(5)])
        
        nav_grid.add_widget(self.create_nav_button("lightbulb-outline", "Dicas", self.abrir_menu_dicas))
        nav_grid.add_widget(self.create_nav_button("tune", "Dificuldade", self.abrir_menu_dificuldade))
        nav_grid.add_widget(self.create_nav_button("chart-bar", "Score", lambda x: None, is_score=True))
        
        bottom_card.add_widget(nav_grid)
        self.ui_layer.add_widget(bottom_card)

    def create_nav_button(self, icon_name, text_label, callback, is_score=False):
        wrapper = AnchorLayout(anchor_x='center', anchor_y='center')
        container = MDBoxLayout(orientation="vertical", spacing=dp(4), adaptive_height=True, adaptive_width=True)
        
        icon = MDIconButton(icon=icon_name, pos_hint={"center_x": 0.5}, theme_text_color="Custom", text_color=(0.4, 0.4, 0.4, 1), icon_size=dp(30), on_release=callback, ripple_scale=0 if is_score else 1)
        container.add_widget(icon)
        
        lbl = MDLabel(text=text_label, halign="center", font_style="Caption", theme_text_color="Custom", text_color=(0.4, 0.4, 0.4, 1), valign="top", adaptive_height=True)
        container.add_widget(lbl)
        
        if is_score:
            lbl.text = "Score"
            self.lbl_score_nav = MDLabel(text="0", halign="center", font_style="H6", bold=True, theme_text_color="Primary", adaptive_height=True)
            container.add_widget(self.lbl_score_nav)
        
        wrapper.add_widget(container)
        return wrapper

    # --- LÓGICA DE JOGO (BOLA E PINOS) ---
    def setup_game_elements(self):
        self.bola = BolaWidget()
        self.game_layer.add_widget(self.bola)

    def gerar_rodada(self):
        for p in self.pinos:
            if p.parent: self.game_layer.remove_widget(p)
        self.pinos = []

        # Define Alvo
        if self.dificuldade == "Primario": self.alvo = randint(5, 20)
        elif self.dificuldade == "Fundamental": self.alvo = randint(15, 50)
        else: self.alvo = randint(30, 100)

        self.bola.lbl_numero.text = str(self.alvo)
        self.resetar_bola_posicao_instantaneo()

        # Posiciona Pinos
        centro_x_tela = 0.5
        raio_x = 0.35; raio_y = 0.55; centro_y_arco = 0.25 
        angulos = [150, 120, 90, 60, 30]
        indice_certo = randint(0, 4)

        for i, angulo in enumerate(angulos):
            rad = math.radians(angulo)
            px = centro_x_tela + (raio_x * math.cos(rad))
            py = centro_y_arco + (raio_y * math.sin(rad))
            
            is_certo = (i == indice_certo)
            texto, res = self.gerar_conta(self.alvo if is_certo else None)
            
            pino = PinoCard(texto, res)
            pino.pos_hint = {'center_x': px, 'center_y': py}
            self.pinos.append(pino)
            self.game_layer.add_widget(pino)
        
        # Traz bola pra frente
        if self.bola.parent: self.game_layer.remove_widget(self.bola)
        self.game_layer.add_widget(self.bola)

    def gerar_conta(self, target):
        limit = 20 if self.dificuldade == "Primario" else 50 if self.dificuldade == "Fundamental" else 100
        v = target if target is not None else randint(1, limit)
        while v == self.alvo and target is None: v = randint(1, limit)
        
        ops = ['+', '-', 'x']
        if self.dificuldade == "Primario": ops = ['+', '-']
        op = choice(ops)
        
        if op == '+':
            n = randint(1, v-1) if v > 1 else 0
            return (f"{v-n} + {n}", v)
        elif op == '-':
            n = randint(1, 10)
            return (f"{v+n} - {n}", v)
        elif op == 'x':
            if v % 2 == 0: return (f"{v//2} x 2", v)
            return (f"{v} x 1", v)
        return (f"{v}", v)

    # --- FÍSICA E TOQUES ---
    def resetar_bola_posicao_instantaneo(self):
        Animation.cancel_all(self.bola)
        self.em_movimento = False
        self.bola.pos_hint = {'center_x': 0.5, 'y': 0.22}
        if self.bola.parent: self.bola.parent.do_layout()

    def resetar_bola_animado(self, *args):
        Animation.cancel_all(self.bola)
        self.em_movimento = False
        target_y = self.game_layer.height * 0.22
        target_x = self.game_layer.center_x - (self.bola.width / 2)
        anim = Animation(x=target_x, y=target_y, duration=0.5, t='out_back')
        anim.bind(on_complete=self.travar_bola_base)
        anim.start(self.bola)

    def travar_bola_base(self, *args):
        self.bola.pos_hint = {'center_x': 0.5, 'y': 0.22}

    def on_touch_down(self, touch):
        # Bloqueia toque no jogo se estiver no menu de start
        if self.start_overlay: return super().on_touch_down(touch)
        
        if self.em_movimento: return super().on_touch_down(touch)

        if self.bola and self.bola.collide_point(*touch.pos):
            touch.grab(self)
            self.bola_start_pos = (touch.x, touch.y)
            self.bola.pos_hint = {} 
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            self.bola.center_x = touch.x
            self.bola.center_y = touch.y
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            diff_y = touch.y - self.bola_start_pos[1]
            diff_x = touch.x - self.bola_start_pos[0]
            if diff_y > dp(30): self.lancar_bola(diff_x, diff_y)
            else: self.resetar_bola_animado()
            return True
        return super().on_touch_up(touch)

    def lancar_bola(self, diff_x, diff_y):
        self.em_movimento = True
        start_x = self.bola.center_x
        start_y = self.bola.center_y
        distancia_y_total = self.height - start_y + dp(100)
        fator = distancia_y_total / diff_y
        target_x_abs = start_x + (diff_x * fator)
        
        final_hint_x = target_x_abs / self.width
        final_hint_x = max(-0.5, min(1.5, final_hint_x))

        anim = Animation(pos_hint={'center_x': final_hint_x, 'top': 1.2}, duration=0.7)
        anim.bind(on_progress=self.checar_colisoes)
        anim.bind(on_complete=self.fim_lancamento)
        anim.start(self.bola)

    def checar_colisoes(self, anim, widget, progress):
        bx, by = self.bola.center
        raio_bola = self.bola.width / 2
        for p in self.pinos:
            if p.ativo:
                px, py = p.center
                raio_pino = p.width / 2
                dist = math.sqrt((bx - px)**2 + (by - py)**2)
                margem = dp(25)
                if dist < (raio_bola + raio_pino - margem):
                    anim.stop(widget)
                    Animation.cancel_all(widget)
                    self.processar_acerto(p)
                    Clock.schedule_once(self.resetar_bola_animado, 0.1)
                    Clock.schedule_once(lambda dt: self.gerar_rodada(), 0.8)
                    break

    def processar_acerto(self, pino):
        pino.ativo = False
        if pino.resultado == self.alvo:
            pino.md_bg_color = (0.3, 0.9, 0.3, 1) # Verde
            self.pontos += 10
            self.progress.value += 20
            self.game_layer.add_widget(FloatingText("+10!", pino.center))
        else:
            pino.md_bg_color = (1, 0.3, 0.3, 1) # Vermelho
            self.vidas -= 1
            self.lbl_vidas_txt.text = f"x{self.vidas}"
            self.game_layer.add_widget(FloatingText("Errou!", pino.center, color=(1,0,0,1)))
        
        if self.lbl_score_nav: self.lbl_score_nav.text = str(self.pontos)
        anim = Animation(opacity=0, size=(0, 0), duration=0.2)
        anim.start(pino)

    def fim_lancamento(self, anim, widget):
        if self.vidas <= 0:
            # GAME OVER: Reseta valores e mostra a tela de INÍCIO de novo
            self.pontos = 0
            self.vidas = 3
            self.lbl_vidas_txt.text = "x3"
            self.progress.value = 0
            if self.lbl_score_nav: self.lbl_score_nav.text = "0"
            
            self.game_layer.clear_widgets()
            self.setup_background()
            self.mostrar_tela_inicio()
            
        self.resetar_bola_animado()

    # --- MENUS ---
    def abrir_menu_dificuldade(self, instance):
        menu_items = [
            {"text": "Fácil", "viewclass": "OneLineListItem", "on_release": lambda x="Primario": self.callback_dificuldade(x)},
            {"text": "Médio", "viewclass": "OneLineListItem", "on_release": lambda x="Fundamental": self.callback_dificuldade(x)},
            {"text": "Difícil", "viewclass": "OneLineListItem", "on_release": lambda x="Medio": self.callback_dificuldade(x)}
        ]
        self.menu_diff = MDDropdownMenu(caller=instance, items=menu_items, width_mult=3, max_height=dp(150), background_color=(1, 1, 1, 1))
        self.menu_diff.open()

    def callback_dificuldade(self, nova_dificuldade):
        self.menu_diff.dismiss()
        self.dificuldade = nova_dificuldade
        self.game_layer.add_widget(FloatingText(f"Nível: {nova_dificuldade}", (self.width/2, self.height/2)))
        self.gerar_rodada()

    def abrir_menu_dicas(self, instance):
        menu_items = [
            {"text": "Eliminar 1 (-10 pts)", "viewclass": "OneLineListItem", "on_release": lambda: self.callback_dicas("eliminar")},
            {"text": "Mostrar Alvo (-20 pts)", "viewclass": "OneLineListItem", "on_release": lambda: self.callback_dicas("mostrar")}
        ]
        self.menu_dicas = MDDropdownMenu(caller=instance, items=menu_items, width_mult=4, background_color=(1, 1, 1, 1))
        self.menu_dicas.open()

    def callback_dicas(self, tipo):
        self.menu_dicas.dismiss()
        if self.pontos < 10 and tipo == "eliminar":
            self.game_layer.add_widget(FloatingText("Pontos Insuficientes!", (self.width/2, self.height/2), color=(1,0,0,1)))
            return
        if self.pontos < 20 and tipo == "mostrar":
            self.game_layer.add_widget(FloatingText("Pontos Insuficientes!", (self.width/2, self.height/2), color=(1,0,0,1)))
            return

        if tipo == "eliminar":
            encontrou = False
            for p in self.pinos:
                if p.ativo and p.resultado != self.alvo:
                    anim = Animation(opacity=0, size=(0, 0), duration=0.2)
                    anim.start(p)
                    p.ativo = False
                    self.pontos -= 10
                    self.game_layer.add_widget(FloatingText("-10 Pts", (self.width/2, self.height/2), color=(1,0.5,0,1)))
                    encontrou = True
                    break
            if not encontrou: self.game_layer.add_widget(FloatingText("Nada para eliminar!", (self.width/2, self.height/2)))
        elif tipo == "mostrar":
             self.game_layer.add_widget(FloatingText(f"Alvo: {self.alvo}", (self.width/2, self.height/2 + dp(50))))
             self.pontos -= 20
        if self.lbl_score_nav: self.lbl_score_nav.text = str(self.pontos)

    def voltar(self, instance):
        self.manager.current = "jogar"