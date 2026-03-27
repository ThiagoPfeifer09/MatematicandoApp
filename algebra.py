import os
import random
import threading
import math
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.card import MDCard
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.button import MDIconButton, MDRaisedButton, MDFlatButton
from kivymd.uix.slider import MDSlider
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.graphics import Color, Line, Ellipse, Rectangle, Triangle
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivy.uix.modalview import ModalView
from kivy.uix.image import Image
from kivymd.uix.textfield import MDTextField
from kivy.uix.behaviors import ButtonBehavior

# Tenta importar módulos locais. Mock se falhar para testar a UI.
try:
    from sistema_erros import GerenciadorErros
    import banco_dados
except ImportError:
    class GerenciadorErros:
        def registrar_erro(self, tipo): pass
        def obter_dica_final(self): return "Reveja o comportamento dos gráficos!"
    class banco_dados:
        @staticmethod
        def salvar_partida(*args): return True, "Salvo na Base (Mock)"

# --- PALETA DE CORES (Biohazard / Comic Book Era de Ouro) ---
COR_FUNDO = (0.05, 0.05, 0.08, 1) # Preto nanquim / sombras
COR_TOXICA = (0.2, 0.9, 0.2, 1) # Verde radioativo brilhante
COR_ALERTA = (0.9, 0.8, 0.1, 1) # Amarelo alerta
COR_PERIGO = (0.9, 0.1, 0.2, 1) # Vermelho sangue/emergência
COR_PAINEL = (0.12, 0.15, 0.18, 0.95) # Cinza azulado escuro
COR_BRANCO = (1, 1, 1, 1)
CINZA_TXT = (0.6, 0.7, 0.7, 1)
COR_SECUNDARIA = (1.0, 0.6, 0.1, 1) # Laranja
# ============================================================================
# WIDGET PRIMÁRIO: GOTA DE REAGENTE (Balança Interativa)
# ============================================================================
class GotaReagente(ButtonBehavior, Widget):
    def __init__(self, callback_remover, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(30), dp(30))
        self.callback_remover = callback_remover

        with self.canvas:
            Color(*COR_TOXICA)
            self.forma = Ellipse(pos=self.pos, size=self.size)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.forma.pos = self.pos
        self.forma.size = self.size

    def on_release(self):
        self.callback_remover(self)

# ============================================================================
# WIDGET FUNDAMENTAL: RADAR DO DRONE (Função Afim)
# ============================================================================
class RadarDrone(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player_a = 1.0
        self.player_b = 0.0
        self.alvos = [(2, 4), (5, 7)] # Pontos que a reta deve cruzar
        self.mostrar_dica = False
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def set_player_params(self, a, b):
        self.player_a = a
        self.player_b = b
        self.update_canvas()

    def set_alvos(self, p1, p2):
        self.alvos = [p1, p2]
        self.update_canvas()

    def verificar_acerto(self):
        acertos = 0
        for x, y in self.alvos:
            y_calc = self.player_a * x + self.player_b
            if abs(y_calc - y) <= 0.1:
                acertos += 1

        if acertos == 2:
            return True, "Rota confirmada! O drone resgatou os sobreviventes."
        elif acertos == 1:
            return False, "O drone bateu! A inclinação (a) ou a altura inicial (b) estão descalibradas."
        else:
            return False, "Rota totalmente fora! O drone colidiu com as paredes do laboratório."

    def _coord(self, x_cart, y_cart, w, h, x0, y0):
        # Escala: X de 0 a 10, Y de 0 a 10
        escala_x = w / 10
        escala_y = h / 10
        return x0 + (x_cart * escala_x), y0 + (y_cart * escala_y)

    def update_canvas(self, *args):
        self.canvas.clear()
        w, h = self.size
        x0, y0 = self.pos

        with self.canvas:
            # Grid / Fundo
            Color(0.1, 0.2, 0.1, 0.3)
            Rectangle(pos=self.pos, size=self.size)
            Color(0.2, 0.4, 0.2, 0.5)
            for i in range(11):
                Line(points=[x0 + i*(w/10), y0, x0 + i*(w/10), y0 + h], width=1)
                Line(points=[x0, y0 + i*(h/10), x0 + w, y0 + i*(h/10)], width=1)

            # Sobreviventes (Alvos)
            Color(*COR_ALERTA)
            for ax, ay in self.alvos:
                px, py = self._coord(ax, ay, w, h, x0, y0)
                Ellipse(pos=(px-dp(10), py-dp(10)), size=(dp(20), dp(20)))

            # Dica visual (Triângulo retângulo da inclinação)
            if self.mostrar_dica:
                Color(1, 1, 0, 0.3)
                p1, p2 = self.alvos
                px1, py1 = self._coord(p1[0], p1[1], w, h, x0, y0)
                px2, py2 = self._coord(p2[0], p2[1], w, h, x0, y0)
                Line(points=[px1, py1, px2, py1], width=dp(2), dash_length=5, dash_offset=5) # Cateto X
                Line(points=[px2, py1, px2, py2], width=dp(2), dash_length=5, dash_offset=5) # Cateto Y

            # Rota do Drone (Reta do Jogador)
            Color(*COR_BRANCO)
            x_ini, y_ini = self._coord(0, self.player_b, w, h, x0, y0)
            x_fim, y_fim = self._coord(10, self.player_a * 10 + self.player_b, w, h, x0, y0)
            Line(points=[x_ini, y_ini, x_fim, y_fim], width=dp(2))

# ============================================================================
# WIDGET MÉDIO: ESCUDO PARABÓLICO (Função Quadrática)
# ============================================================================
class RadarParabola(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.player_a = -1.0
        self.player_b = 10.0
        self.player_c = -16.0
        self.raiz1 = 2
        self.raiz2 = 8
        self.vertice_y = 9
        self.mostrar_dica = False
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def set_player_params(self, a, b, c):
        self.player_a = a
        self.player_b = b
        self.player_c = c
        self.update_canvas()

    def set_ameaca(self, r1, r2, vy):
        self.raiz1 = r1
        self.raiz2 = r2
        self.vertice_y = vy
        self.update_canvas()

    def verificar_acerto(self):
        # A equação ideal
        a_ideal = -self.vertice_y / (((self.raiz2 - self.raiz1)/2)**2)
        b_ideal = -a_ideal * (self.raiz1 + self.raiz2)
        c_ideal = a_ideal * self.raiz1 * self.raiz2

        # Validação com tolerância
        ok_a = abs(self.player_a - a_ideal) <= 0.2
        ok_b = abs(self.player_b - b_ideal) <= 0.5
        ok_c = abs(self.player_c - c_ideal) <= 0.5

        if ok_a and ok_b and ok_c:
            return True, "Escudo ativado! A radiação foi contida com sucesso."
        elif self.player_a >= 0:
            return False, "O escudo está invertido! A concavidade (coeficiente 'a') deve ser negativa para cobrir a área."
        else:
            return False, "Vazamento detectado! As bases do escudo não alinham com a zona de radiação."

    def _coord(self, x_cart, y_cart, w, h, x0, y0):
        escala_x = w / 10
        escala_y = h / 10
        return x0 + (x_cart * escala_x), y0 + (y_cart * escala_y)

    def update_canvas(self, *args):
        self.canvas.clear()
        w, h = self.size
        x0, y0 = self.pos

        with self.canvas:
            Color(0.1, 0.1, 0.15, 1)
            Rectangle(pos=self.pos, size=self.size)

            # Área de Radiação (Ameaça)
            Color(*COR_PERIGO, 0.4)
            r1x, r1y = self._coord(self.raiz1, 0, w, h, x0, y0)
            r2x, r2y = self._coord(self.raiz2, 0, w, h, x0, y0)
            vx, vy = self._coord((self.raiz1+self.raiz2)/2, self.vertice_y, w, h, x0, y0)
            # Desenha um triângulo tosco para representar a mancha
            Triangle(points=[r1x, r1y, r2x, r2y, vx, vy])

            # Dica (Marca as raízes desejadas)
            if self.mostrar_dica:
                Color(1, 1, 0, 0.8)
                Ellipse(pos=(r1x-dp(5), r1y-dp(5)), size=(dp(10), dp(10)))
                Ellipse(pos=(r2x-dp(5), r2y-dp(5)), size=(dp(10), dp(10)))
                Ellipse(pos=(vx-dp(5), vy-dp(5)), size=(dp(10), dp(10)))

            # Escudo do Jogador (Parábola)
            Color(*COR_SECUNDARIA)
            pontos_parabola = []
            for i in range(0, 101):
                x = i / 10.0
                y = self.player_a * (x**2) + self.player_b * x + self.player_c
                # Trava visual se for muito para baixo
                if y >= -2:
                    px, py = self._coord(x, y, w, h, x0, y0)
                    pontos_parabola.extend([px, py])

            if len(pontos_parabola) >= 4:
                Line(points=pontos_parabola, width=dp(2.5))

# ============================================================================
# TELA PRINCIPAL: FUGA DO LABORATÓRIO (BIO-ESCAPE)
# ============================================================================
class AlgebraGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nivel_acesso = "primario" # primario, fundamental, medio
        self.pergunta_atual = 1
        self.total_perguntas = 3
        self.acertos = 0
        self.erros = 0
        self.pontuacao = 0
        self.tentativas_fase = 0
        self.dicas_disponiveis = 3

        self.menu_niveis = None
        self.dialog = None
        self._setup_ui()

    def _setup_ui(self):
        self.layout = FloatLayout()

        self.main_box = MDBoxLayout(orientation="vertical", padding=[dp(10), dp(35), dp(10), dp(10)], spacing=dp(10))

        # CABEÇALHO (HUD)
        header = MDCard(size_hint_y=None, height=dp(70), radius=[15], md_bg_color=COR_PAINEL, padding=dp(10), elevation=4)
        box_head = MDBoxLayout(spacing=dp(10))
        box_head.add_widget(MDIconButton(icon="arrow-left", theme_text_color="Custom", text_color=COR_BRANCO, on_release=self.voltar, pos_hint={'center_y': 0.5}))

        info_box = MDBoxLayout(orientation='vertical', pos_hint={'center_y': 0.5})
        self.lbl_titulo = MDLabel(text="SISTEMA DE SEGURANÇA", bold=True, theme_text_color="Custom", text_color=COR_TOXICA, font_style="Subtitle1")
        self.lbl_instrucao = MDLabel(text="Aguardando comandos...", theme_text_color="Custom", text_color=CINZA_TXT, font_style="Caption")
        info_box.add_widget(self.lbl_titulo)
        info_box.add_widget(self.lbl_instrucao)

        self.lbl_pts = MDLabel(text="0 PTS", halign="right", bold=True, theme_text_color="Custom", text_color=COR_ALERTA, font_style="H6", size_hint_x=0.4)

        box_head.add_widget(info_box)
        box_head.add_widget(self.lbl_pts)
        header.add_widget(box_head)
        self.main_box.add_widget(header)

        # CONTAINER CENTRAL (Onde os minigames aparecem)
        self.container = MDBoxLayout(orientation='vertical', spacing=dp(10))
        self.main_box.add_widget(self.container)

        # BARRA INFERIOR (Ferramentas)
        self.bottom_bar = MDCard(orientation="horizontal", size_hint_y=None, height=dp(70), md_bg_color=COR_PAINEL, elevation=10, padding=dp(5), radius=[15])
        self.bottom_bar.add_widget(self.criar_item_barra("Hackear Dica", "help-network-outline", self.usar_dica, COR_ALERTA))
        self.bottom_bar.add_widget(self.criar_item_barra("Nível de Acesso", "folder-key-network", self.abrir_menu_niveis, COR_BRANCO))
        self.bottom_bar.add_widget(self.criar_item_barra("Diagnóstico", "chart-timeline-variant", self.mostrar_score, CINZA_TXT))
        self.main_box.add_widget(self.bottom_bar)

        self.layout.add_widget(self.main_box)
        self.add_widget(self.layout)

    def criar_item_barra(self, texto, icone, func_callback, cor):
        box = MDCard(orientation="vertical", padding=dp(2), elevation=0, md_bg_color=(0,0,0,0), ripple_behavior=True, on_release=func_callback)
        box_interno = MDBoxLayout(orientation="vertical", spacing=0, pos_hint={"center_x": .5, "center_y": .5})
        box_interno.add_widget(MDIcon(icon=icone, halign="center", theme_text_color="Custom", text_color=cor, pos_hint={"center_x": .5}))
        box_interno.add_widget(MDLabel(text=texto, halign="center", theme_text_color="Custom", text_color=cor, font_style="Caption"))
        box.add_widget(box_interno)
        return box

    def abrir_menu_niveis(self, instance):
        if not self.menu_niveis:
            opcoes = [
                {"text": "Primário (Centrífuga)", "viewclass": "OneLineListItem", "on_release": lambda: self.mudar_nivel("primario")},
                {"text": "Fundamental (Drone)", "viewclass": "OneLineListItem", "on_release": lambda: self.mudar_nivel("fundamental")},
                {"text": "Médio (Escudo)", "viewclass": "OneLineListItem", "on_release": lambda: self.mudar_nivel("medio")},
            ]
            self.menu_niveis = MDDropdownMenu(caller=instance, items=opcoes, width_mult=4, background_color=COR_PAINEL)
        self.menu_niveis.open()

    def mudar_nivel(self, novo_nivel):
        self.menu_niveis.dismiss()
        self.nivel_acesso = novo_nivel
        self.on_pre_enter()

    def mostrar_score(self, instance):
        self.mostrar_dialogo_simples("Status Biológico", f"Pontos de Sobrevivência: {self.pontuacao}\nAmeaças contidas: {self.acertos}\nFalhas Críticas: {self.erros}")

    def mostrar_dialogo_simples(self, tit, txt):
        self.dialog = MDDialog(title=tit, text=txt, md_bg_color=COR_PAINEL, buttons=[MDFlatButton(text="FECHAR", theme_text_color="Custom", text_color=COR_TOXICA, on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()

    def usar_dica(self, instance):
        if self.dicas_disponiveis <= 0:
            self.mostrar_dialogo_simples("Erro de Sistema", "Sem energia para o assistente IA!")
            return

        self.dicas_disponiveis -= 1

        if self.nivel_acesso == "primario":
            self.mostrar_dialogo_simples("Dica da IA", "Lembre-se da Equivalência: Retire a MESMA quantidade de gotas dos dois lados da centrífuga para manter o equilíbrio.")
        elif self.nivel_acesso == "fundamental":
            self.radar_drone.mostrar_dica = True
            self.radar_drone.update_canvas()
            self.mostrar_dialogo_simples("Dica da IA", "Analise as linhas amarelas no mapa. A inclinação (a) é o quanto você sobe dividido por quanto você anda para o lado (Variação de Y / Variação de X).")
        elif self.nivel_acesso == "medio":
            self.radar_parabola.mostrar_dica = True
            self.radar_parabola.update_canvas()
            self.mostrar_dialogo_simples("Dica da IA", "As luzes amarelas indicam as Raízes (onde o escudo toca o chão) e o Vértice (altura máxima). Use a forma fatorada: a*(x - r1)*(x - r2) para descobrir os coeficientes!")

    def on_pre_enter(self):
        self.pergunta_atual = 1
        self.pontuacao = 0
        self.acertos = 0
        self.erros = 0
        self.dicas_disponiveis = 3
        self.lbl_pts.text = "0 PTS"
        self.gerenciador_erros = GerenciadorErros()
        self.gerar_fase()

    def gerar_fase(self):
        self.container.clear_widgets()
        self.container.disabled = False
        self.tentativas_fase = 0

        if self.pergunta_atual > self.total_perguntas:
            self.encerrar_jogo()
            return

        self.lbl_titulo.text = f"SALA DE RISCO {self.pergunta_atual}/{self.total_perguntas}"

        if self.nivel_acesso == "primario":
            self.setup_primario()
        elif self.nivel_acesso == "fundamental":
            self.setup_fundamental()
        elif self.nivel_acesso == "medio":
            self.setup_medio()

    # --- NÍVEL 1: PRIMÁRIO (Balança Visual / Manipulação Direta) ---
    def setup_primario(self):
        self.lbl_instrucao.text = "Equilibre a centrífuga tocando nas gotas para extraí-las."

        val_x = random.randint(2, 5)
        gotas_esq = random.randint(1, 4)
        gotas_dir = val_x + gotas_esq

        card = MDCard(orientation='vertical', radius=[15], padding=dp(10), md_bg_color=COR_PAINEL)

        self.lbl_eq_prim = MDLabel(text="X = ?", halign="center", font_style="H4", bold=True, theme_text_color="Custom", text_color=COR_TOXICA, size_hint_y=0.2)
        card.add_widget(self.lbl_eq_prim)

        box_pratos = MDBoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=0.6)

        # Lado Esquerdo
        self.grid_esq = MDGridLayout(cols=2, adaptive_size=True, pos_hint={'center_x': 0.5, 'center_y': 0.5}, spacing=dp(5))
        self.grid_esq.add_widget(MDIcon(icon="flask-outline", theme_text_color="Custom", text_color=COR_ALERTA, font_size="50sp"))
        for _ in range(gotas_esq):
            self.grid_esq.add_widget(GotaReagente(self.remover_gota_esq))

        # Pivo
        pivo = MDBoxLayout(size_hint_x=0.2)
        pivo.add_widget(MDIcon(icon="scale-balance", font_size="50sp", pos_hint={'center_y': 0.5}, theme_text_color="Custom", text_color=CINZA_TXT))

        # Lado Direito
        self.grid_dir = MDGridLayout(cols=3, adaptive_size=True, pos_hint={'center_x': 0.5, 'center_y': 0.5}, spacing=dp(5))
        for _ in range(gotas_dir):
            self.grid_dir.add_widget(GotaReagente(self.remover_gota_dir))

        box_pratos.add_widget(self.grid_esq)
        box_pratos.add_widget(pivo)
        box_pratos.add_widget(self.grid_dir)
        card.add_widget(box_pratos)

        btn = MDRaisedButton(text="INICIAR SÍNTESE", size_hint_x=1, md_bg_color=COR_TOXICA, on_release=self.validar_primario)
        card.add_widget(btn)

        self.container.add_widget(card)

    def remover_gota_esq(self, widget):
        self.grid_esq.remove_widget(widget)
        self.atualizar_label_primario()

    def remover_gota_dir(self, widget):
        self.grid_dir.remove_widget(widget)
        self.atualizar_label_primario()

    def atualizar_label_primario(self):
        # Apenas visual. A lógica real verifica se tem frasco do lado esquerdo sem gotas, e conta as da direita.
        q_esq = len(self.grid_esq.children) - 1 # subtrai o icone do frasco
        q_dir = len(self.grid_dir.children)
        self.lbl_eq_prim.text = f"X + {q_esq} = {q_dir}" if q_esq > 0 else f"X = {q_dir}"

    def validar_primario(self, instance):
        q_esq = len(self.grid_esq.children) - 1
        q_dir = len(self.grid_dir.children)

        # A situação didática espera que o aluno zere as gotas esquerdas
        if q_esq == 0:
            self.feedback(True, f"Equilíbrio Perfeito! O frasco X pesa exatamente {q_dir} gotas.")
        else:
            self.gerenciador_erros.registrar_erro("equivalencia")
            self.feedback(False, "Balança desequilibrada! Você deve isolar o frasco (X) retirando as mesmas quantidades dos dois lados.")

    # --- NÍVEL 2: FUNDAMENTAL (Rota Linear do Drone) ---
    def setup_fundamental(self):
        self.lbl_instrucao.text = "Trace a reta y=ax+b para o drone de resgate."

        # Gera pontos fáceis (inteiros)
        ax = random.randint(1, 4)
        ay = random.randint(1, 4)
        bx = random.randint(6, 9)
        by = ay + random.randint(-2, 3)
        if by < 1: by = 1
        if by > 9: by = 9

        self.radar_drone = RadarDrone(size_hint=(1, 0.5))
        self.radar_drone.set_alvos((ax, ay), (bx, by))
        self.container.add_widget(self.radar_drone)

        painel = MDCard(orientation='vertical', padding=dp(10), spacing=dp(5), radius=[15], size_hint=(1, 0.5), md_bg_color=COR_PAINEL)

        self.lbl_eq_drone = MDLabel(text="y = 1.0x + 0.0", halign="center", font_style="H5", bold=True, theme_text_color="Custom", text_color=COR_BRANCO)
        painel.add_widget(self.lbl_eq_drone)

        painel.add_widget(MDLabel(text="Inclinação (a):", font_style="Caption", theme_text_color="Custom", text_color=CINZA_TXT))
        self.sld_a = MDSlider(min=-3, max=3, value=1.0, step=0.5, color=COR_ALERTA)
        self.sld_a.bind(value=self.atualizar_drone)
        painel.add_widget(self.sld_a)

        painel.add_widget(MDLabel(text="Ponto Inicial (b):", font_style="Caption", theme_text_color="Custom", text_color=CINZA_TXT))
        self.sld_b = MDSlider(min=0, max=10, value=0.0, step=1.0, color=COR_TOXICA)
        self.sld_b.bind(value=self.atualizar_drone)
        painel.add_widget(self.sld_b)

        btn = MDRaisedButton(text="ENVIAR ROTA", size_hint_x=1, md_bg_color=COR_ALERTA, text_color=(0,0,0,1), on_release=self.validar_fundamental)
        painel.add_widget(btn)

        self.container.add_widget(painel)
        self.atualizar_drone()

    def atualizar_drone(self, *args):
        a = self.sld_a.value
        b = self.sld_b.value
        sinal = "+" if b >= 0 else ""
        self.lbl_eq_drone.text = f"y = {a}x {sinal} {b}"
        self.radar_drone.set_player_params(a, b)

    def validar_fundamental(self, instance):
        acertou, msg = self.radar_drone.verificar_acerto()
        if acertou:
            self.feedback(True, msg)
        else:
            self.tentativas_fase += 1
            self.gerenciador_erros.registrar_erro("funcao_afim")
            if self.tentativas_fase >= 2:
                self.feedback(False, msg + "\nUse a Dica da IA para ver o cálculo do triângulo!")
            else:
                self.lbl_instrucao.text = msg
                self.lbl_instrucao.text_color = COR_PERIGO

    # --- NÍVEL 3: MÉDIO (Escudo Parabólico) ---
    def setup_medio(self):
        self.lbl_instrucao.text = "Gere uma parábola y=ax²+bx+c para cobrir a área."

        raizes = [(2, 8), (1, 9), (3, 7)]
        r1, r2 = random.choice(raizes)
        vy = random.randint(5, 9)

        self.radar_parabola = RadarParabola(size_hint=(1, 0.45))
        self.radar_parabola.set_ameaca(r1, r2, vy)
        self.container.add_widget(self.radar_parabola)

        painel = MDCard(orientation='vertical', padding=dp(10), spacing=dp(5), radius=[15], size_hint=(1, 0.55), md_bg_color=COR_PAINEL)

        self.lbl_eq_para = MDLabel(text="y = -1.0x² + 0.0x + 0.0", halign="center", font_style="Subtitle1", bold=True, theme_text_color="Custom", text_color=COR_BRANCO)
        painel.add_widget(self.lbl_eq_para)

        # Sliders a, b, c
        self.sld_pa = MDSlider(min=-3, max=3, value=-1.0, step=0.25, color=COR_PERIGO)
        self.sld_pa.bind(value=self.atualizar_parabola)
        box_a = MDBoxLayout(size_hint_y=None, height=dp(30))
        box_a.add_widget(MDLabel(text="a:", size_hint_x=0.1, theme_text_color="Custom", text_color=CINZA_TXT))
        box_a.add_widget(self.sld_pa)
        painel.add_widget(box_a)

        self.sld_pb = MDSlider(min=-20, max=20, value=0.0, step=1.0, color=COR_ALERTA)
        self.sld_pb.bind(value=self.atualizar_parabola)
        box_b = MDBoxLayout(size_hint_y=None, height=dp(30))
        box_b.add_widget(MDLabel(text="b:", size_hint_x=0.1, theme_text_color="Custom", text_color=CINZA_TXT))
        box_b.add_widget(self.sld_pb)
        painel.add_widget(box_b)

        self.sld_pc = MDSlider(min=-30, max=30, value=0.0, step=1.0, color=COR_TOXICA)
        self.sld_pc.bind(value=self.atualizar_parabola)
        box_c = MDBoxLayout(size_hint_y=None, height=dp(30))
        box_c.add_widget(MDLabel(text="c:", size_hint_x=0.1, theme_text_color="Custom", text_color=CINZA_TXT))
        box_c.add_widget(self.sld_pc)
        painel.add_widget(box_c)

        btn = MDRaisedButton(text="ACIONAR ESCUDO ESTRUTURAL", size_hint_x=1, md_bg_color=COR_TOXICA, on_release=self.validar_medio)
        painel.add_widget(btn)

        self.container.add_widget(painel)
        self.atualizar_parabola()

    def atualizar_parabola(self, *args):
        a = self.sld_pa.value
        b = self.sld_pb.value
        c = self.sld_pc.value
        sb = "+" if b >= 0 else ""
        sc = "+" if c >= 0 else ""
        self.lbl_eq_para.text = f"y = {a}x² {sb} {b}x {sc} {c}"
        self.radar_parabola.set_player_params(a, b, c)

    def validar_medio(self, instance):
        acertou, msg = self.radar_parabola.verificar_acerto()
        if acertou:
            self.feedback(True, msg)
        else:
            self.tentativas_fase += 1
            self.gerenciador_erros.registrar_erro("funcao_quadratica")
            if self.tentativas_fase >= 3:
                self.feedback(False, msg + "\nContaminação alta! Tente usar o Hack de IA na próxima vez.")
            else:
                self.lbl_instrucao.text = msg
                self.lbl_instrucao.text_color = COR_PERIGO

    # --- COMUNS ---
    def feedback(self, acertou, msg):
        self.container.disabled = True
        cor = COR_TOXICA if acertou else COR_PERIGO
        titulo = "SUCESSO!" if acertou else "SISTEMA COMPROMETIDO!"

        if acertou:
            self.acertos += 1
            self.pontuacao += 100 if self.tentativas_fase == 0 else 50
        else:
            self.erros += 1

        self.lbl_pts.text = f"{self.pontuacao} PTS"

        content = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        content.add_widget(MDIcon(icon="shield-check" if acertou else "biohazard", halign="center", font_size="60sp", theme_text_color="Custom", text_color=cor))
        content.add_widget(MDLabel(text=titulo, halign="center", bold=True, font_style="H5", theme_text_color="Custom", text_color=cor))
        content.add_widget(MDLabel(text=msg, halign="center", theme_text_color="Custom", text_color=COR_BRANCO))
        btn_next = MDRaisedButton(text="AVANÇAR", pos_hint={'center_x': 0.5}, md_bg_color=cor, text_color=(0,0,0,1), on_release=lambda x: self.fechar_modal())
        content.add_widget(btn_next)

        self.modal = ModalView(size_hint=(0.85, 0.4), auto_dismiss=False, background_color=(0,0,0,0.8))
        card = MDCard(radius=[20], md_bg_color=COR_PAINEL)
        card.add_widget(content)
        self.modal.add_widget(card)
        self.modal.open()

    def fechar_modal(self):
        self.modal.dismiss()
        self.pergunta_atual += 1
        self.gerar_fase()

    def encerrar_jogo(self):
        if self.manager.has_screen("fim_bioescape"):
            mensagem_dica = self.gerenciador_erros.obter_dica_final()
            screen = self.manager.get_screen("fim_bioescape")
            screen.atualizar_stats(self.pontuacao, self.erros, "00:00", f"BioEscape ({self.nivel_acesso})", mensagem_dica)
            self.manager.current = "fim_bioescape"
        else:
            self.voltar()

    def voltar(self, instance=None):
        if self.dialog: self.dialog.dismiss()
        if self.manager: self.manager.current = "jogar"

# ============================================================================
# TELA DE FIM
# ============================================================================
class TelaFimAlgebra(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dados_partida = {}
        self._construir_interface()

    def _construir_interface(self):
        layout = FloatLayout()

        card = MDCard(
            size_hint=(0.85, 0.65), pos_hint={'center_x': 0.5, 'center_y': 0.5},
            elevation=8, radius=[25], orientation='vertical',
            padding=dp(25), spacing=dp(10), md_bg_color=COR_PAINEL
        )

        self.titulo_lbl = MDLabel(text="RELATÓRIO DE FUGA", halign="center", font_style="H5", bold=True, theme_text_color="Custom", text_color=COR_TOXICA)

        self.resumo_box = MDBoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(100))
        self.acertos_lbl = MDLabel(text="Pontos: 0", halign="center", font_style="H5", theme_text_color="Custom", text_color=COR_ALERTA)
        self.erros_lbl = MDLabel(text="Falhas: 0", halign="center", font_style="Subtitle1", theme_text_color="Custom", text_color=COR_PERIGO)
        self.dica_lbl = MDLabel(text="", halign="center", font_style="Caption", bold=True, theme_text_color="Custom", text_color=COR_BRANCO)

        self.resumo_box.add_widget(self.acertos_lbl)
        self.resumo_box.add_widget(self.erros_lbl)
        self.resumo_box.add_widget(self.dica_lbl)

        self.input_nome = MDTextField(hint_text="Identificação do Cientista", icon_right="flask", size_hint_x=1, pos_hint={'center_x': 0.5}, text_color_normal=COR_BRANCO)

        self.btn_salvar = MDRaisedButton(text="SALVAR REGISTO", size_hint_x=1, height=dp(50), md_bg_color=COR_TOXICA, text_color=(0,0,0,1), on_release=self.acao_salvar)
        self.status_lbl = MDLabel(text="", halign="center", font_style="Caption", theme_text_color="Custom", text_color=CINZA_TXT)

        btn_voltar = MDFlatButton(text="RETORNAR AO MENU", size_hint_x=1, theme_text_color="Custom", text_color=CINZA_TXT, on_release=self.voltar_menu)

        card.add_widget(self.titulo_lbl)
        card.add_widget(self.resumo_box)
        card.add_widget(self.input_nome)
        card.add_widget(Widget(size_hint_y=0.1))
        card.add_widget(self.btn_salvar)
        card.add_widget(self.status_lbl)
        card.add_widget(btn_voltar)

        layout.add_widget(card)
        self.add_widget(layout)

    def atualizar_stats(self, pontos, erros, tempo, dificuldade, mensagem_dica=""):
        self.dados_partida = {"acertos": pontos, "erros": erros, "tempo": tempo, "dificuldade": dificuldade}
        self.acertos_lbl.text = f"Pontuação de Sobrevivência: {pontos}"
        self.erros_lbl.text = f"Danos Contabilizados: {erros}"
        self.dica_lbl.text = mensagem_dica
        self.input_nome.text = ""
        self.status_lbl.text = ""
        self.btn_salvar.disabled = False
        self.btn_salvar.text = "SALVAR REGISTO"

    def acao_salvar(self, instance):
        nome = self.input_nome.text.strip()
        if not nome:
            self.status_lbl.text = "É obrigatório inserir o nome!"
            return
        self.btn_salvar.disabled = True
        self.status_lbl.text = "A transmitir dados..."
        threading.Thread(target=self._salvar_thread, args=(nome,)).start()

    def _salvar_thread(self, nome):
        try:
            sucesso, msg = banco_dados.salvar_partida(nome, "Lab Bio", "Fuga", self.dados_partida['dificuldade'], self.dados_partida['acertos'], self.dados_partida['erros'], self.dados_partida['tempo'])
        except:
            sucesso, msg = True, "Modo Offline: Dados locais"
        Clock.schedule_once(lambda dt: self._pos_salvar(sucesso, msg))

    def _pos_salvar(self, sucesso, msg):
        self.status_lbl.text = msg
        if sucesso:
            self.btn_salvar.text = "DADOS GUARDADOS!"
            self.btn_salvar.md_bg_color = (0.3, 0.3, 0.3, 1)
        else:
            self.btn_salvar.disabled = False

    def voltar_menu(self, instance):
        self.manager.current = "jogar"