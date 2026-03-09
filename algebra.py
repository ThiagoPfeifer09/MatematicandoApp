import os
import random
import threading
import math
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.card import MDCard
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivymd.uix.progressbar import MDProgressBar
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.button import MDIconButton, MDRaisedButton, MDFillRoundFlatButton, MDFlatButton
from kivymd.uix.slider import MDSlider
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, Line, Ellipse, Triangle
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.textfield import MDTextField
from kivy.uix.modalview import ModalView
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivy.uix.image import Image

import banco_dados

# --- PALETA DE CORES (Tema Cyber/Neon) ---
COR_FUNDO = (0.92, 0.94, 0.96, 1)
COR_PRIMARIA = (0.4, 0.2, 0.8, 1) # Roxo
COR_SECUNDARIA = (0.1, 0.6, 0.9, 1) # Azul Ciano
COR_DESTAQUE = (1.0, 0.3, 0.3, 1) # Vermelho/Rosa
COR_VERDE = (0.1, 0.8, 0.3, 1)
COR_TEXTO = (0.2, 0.2, 0.2, 1)
COR_CARD = (1, 1, 1, 0.95)
COR_BRANCO = (1, 1, 1, 1)
CINZA_TXT = (0.5, 0.5, 0.5, 1)

# ============================================================================
# WIDGET 1: BALANÇA MATEMÁTICA (Novo Nível Primário)
# ============================================================================
class BalancaAlgebrica(Widget):
    """Balança que calcula pesos reais e tomba se a matemática estiver errada."""
    def __init__(self, x_real, const_esq, const_dir, **kwargs):
        super().__init__(**kwargs)
        self.x_real = x_real # O valor escondido de X
        self.const_esq = const_esq # Número que acompanha o X
        self.const_dir = const_dir # Número do outro lado
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def aplicar_operacao(self, operador, valor):
        # Aplica a matemática nos dois lados
        if operador == '+':
            self.const_esq += valor
            self.const_dir += valor
        elif operador == '-':
            self.const_esq -= valor
            self.const_dir -= valor

        self.update_canvas()

        # Retorna se o X ficou isolado perfeitamente (x = valor)
        return self.const_esq == 0

    def update_canvas(self, *args):
        self.canvas.clear()
        cx, cy = self.center_x, self.center_y - dp(10)
        w = self.width
        largura_prancha = w * 0.75

        # Física da Balança (Verifica se os dois lados pesam igual)
        peso_real_esq = self.x_real + self.const_esq
        peso_real_dir = self.const_dir

        inclinacao = (peso_real_dir - peso_real_esq) * 2
        inclinacao = max(-20, min(20, inclinacao)) # Limite de tombo

        with self.canvas:
            # Base (Pivô)
            Color(0.4, 0.4, 0.4, 1)
            Triangle(points=[cx, cy, cx-dp(20), cy-dp(40), cx+dp(20), cy-dp(40)])

            rad = math.radians(inclinacao)
            p1_x = cx - (largura_prancha/2) * math.cos(rad)
            p1_y = cy + (largura_prancha/2) * math.sin(rad)
            p2_x = cx + (largura_prancha/2) * math.cos(rad)
            p2_y = cy - (largura_prancha/2) * math.sin(rad)

            # Prancha
            Color(0.2, 0.2, 0.2, 1)
            Line(points=[p1_x, p1_y, p2_x, p2_y], width=dp(4))

            # LADO ESQUERDO: Bloco [X] e Bloco [Constante]
            Color(*COR_PRIMARIA)
            Rectangle(pos=(p1_x + dp(10), p1_y + dp(2)), size=(dp(40), dp(40))) # Caixa X

            if self.const_esq != 0:
                cor_bloco = COR_SECUNDARIA if self.const_esq > 0 else COR_DESTAQUE
                Color(*cor_bloco)
                Rectangle(pos=(p1_x + dp(60), p1_y + (math.sin(rad)*dp(50)) + dp(2)), size=(dp(40), dp(40)))

            # LADO DIREITO: Bloco [Total]
            Color(*COR_SECUNDARIA if self.const_dir > 0 else COR_DESTAQUE)
            Rectangle(pos=(p2_x - dp(50), p2_y - (math.sin(rad)*dp(50)) + dp(2)), size=(dp(40), dp(40)))

        # Adiciona Textos por cima do Canvas
        self.clear_widgets()

        # Label do X
        lbl_x = MDLabel(text="X", bold=True, theme_text_color="Custom", text_color=COR_BRANCO, halign="center")
        lbl_x.size_hint = (None, None); lbl_x.size = (dp(40), dp(40))
        lbl_x.pos = (p1_x + dp(10), p1_y + dp(2))
        self.add_widget(lbl_x)

        # Label Constante Esquerda
        if self.const_esq != 0:
            sinal = "+" if self.const_esq > 0 else ""
            lbl_ce = MDLabel(text=f"{sinal}{self.const_esq}", bold=True, theme_text_color="Custom", text_color=COR_BRANCO, halign="center")
            lbl_ce.size_hint = (None, None); lbl_ce.size = (dp(40), dp(40))
            lbl_ce.pos = (p1_x + dp(60), p1_y + (math.sin(rad)*dp(50)) + dp(2))
            self.add_widget(lbl_ce)

        # Label Constante Direita
        lbl_cd = MDLabel(text=str(self.const_dir), bold=True, theme_text_color="Custom", text_color=COR_BRANCO, halign="center")
        lbl_cd.size_hint = (None, None); lbl_cd.size = (dp(40), dp(40))
        lbl_cd.pos = (p2_x - dp(50), p2_y - (math.sin(rad)*dp(50)) + dp(2))
        self.add_widget(lbl_cd)

# ============================================================================
# WIDGET 2: MIRA LASER LINEAR (Nível Médio)
# ============================================================================
class LaserPlotter(Widget):
    def __init__(self, alvo_x, alvo_y, **kwargs):
        super().__init__(**kwargs)
        self.alvo_x = alvo_x
        self.alvo_y = alvo_y
        self.slope = 1
        self.intercept = 0
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def set_params(self, a, b):
        self.slope = a
        self.intercept = b
        self.update_canvas()

    def verificar_acerto(self):
        y_calculado = (self.slope * self.alvo_x) + self.intercept
        return abs(y_calculado - self.alvo_y) <= 0.5

    def update_canvas(self, *args):
        self.canvas.clear()
        w, h = self.size
        x0, y0 = self.pos

        escala_x = w / 10
        escala_y = h / 10

        with self.canvas:
            Color(0.2, 0.2, 0.2, 1)
            Line(points=[x0, y0, x0, y0+h], width=dp(2))
            Line(points=[x0, y0, x0+w, y0], width=dp(2))

            pos_alvo_x = x0 + (self.alvo_x * escala_x)
            pos_alvo_y = y0 + (self.alvo_y * escala_y)
            Color(*COR_PRIMARIA)
            Ellipse(pos=(pos_alvo_x - dp(15), pos_alvo_y - dp(15)), size=(dp(30), dp(30)))
            Color(1,1,1,1)
            Ellipse(pos=(pos_alvo_x - dp(5), pos_alvo_y - dp(5)), size=(dp(10), dp(10)))

            p1_x = x0
            p1_y = y0 + (self.intercept * escala_y)
            p2_x = x0 + w
            p2_y = y0 + ((self.slope * 10 + self.intercept) * escala_y)

            Color(*COR_VERDE)
            Line(points=[p1_x, p1_y, p2_x, p2_y], width=dp(3))

# ============================================================================
# TELA PRINCIPAL DO JOGO
# ============================================================================
class AlgebraGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.modo_jogo = "balanca" # Determina QUAL mini-game rodar
        self.sub_dificuldade = "facil" # Determina a DIFICULDADE dentro do mini-game

        self.pergunta_atual = 1
        self.total_perguntas = 5
        self.acertos = 0
        self.erros = 0
        self.pontuacao = 0

        self.menu_dificuldade = None
        self.dialog = None

        self._setup_ui()

    def _setup_ui(self):
        self.main_box = MDBoxLayout(orientation="vertical", md_bg_color=COR_FUNDO)
        self.game_area = FloatLayout(size_hint_y=1)

        try:
            self.game_area.add_widget(Image(source='fundoapp.png', allow_stretch=True, keep_ratio=False))
        except: pass

        # CABEÇALHO
        header = MDCard(
            size_hint=(0.95, None), height=dp(70),
            pos_hint={'center_x': 0.5, 'top': 0.98},
            radius=[15], md_bg_color=COR_CARD, padding=dp(10), elevation=3
        )
        box_head = MDBoxLayout(spacing=dp(10))
        box_head.add_widget(MDIconButton(icon="arrow-left", on_release=self.voltar, pos_hint={'center_y': 0.5}))

        info_box = MDBoxLayout(orientation='vertical', pos_hint={'center_y': 0.5})
        self.lbl_titulo = MDLabel(text="ÁLGEBRA", bold=True, theme_text_color="Custom", text_color=COR_PRIMARIA, font_style="Subtitle1")
        self.lbl_instrucao = MDLabel(text="...", theme_text_color="Secondary", font_style="Caption")
        info_box.add_widget(self.lbl_titulo)
        info_box.add_widget(self.lbl_instrucao)

        self.lbl_pts = MDLabel(text="0 PTS", halign="right", bold=True, theme_text_color="Custom", text_color=COR_VERDE, font_style="H6")

        box_head.add_widget(info_box)
        box_head.add_widget(self.lbl_pts)
        header.add_widget(box_head)
        self.game_area.add_widget(header)

        # CONTAINER DINÂMICO DOS MINIGAMES
        self.container = MDBoxLayout(
            orientation='vertical', size_hint=(0.95, 0.72),
            pos_hint={'center_x': 0.5, 'y': 0.05}, spacing=dp(10)
        )
        self.game_area.add_widget(self.container)
        self.main_box.add_widget(self.game_area)

        # ==========================================
        # BARRA INFERIOR (Controle de Sub-dificuldade)
        # ==========================================
        self.bottom_bar = MDCard(orientation="horizontal", size_hint_y=None, height=dp(80), md_bg_color=COR_BRANCO, elevation=10, padding=dp(10))
        self.bottom_bar.add_widget(self.criar_item_barra("Dicas", "lightbulb-outline", self.usar_dica))
        self.bottom_bar.add_widget(self.criar_item_barra("Dificuldade", "tune", self.abrir_menu_dificuldade))
        self.bottom_bar.add_widget(self.criar_item_barra("Score", "chart-bar", self.mostrar_score))
        self.main_box.add_widget(self.bottom_bar)

        self.add_widget(self.main_box)

    def criar_item_barra(self, texto, icone, func_callback):
        box = MDCard(orientation="vertical", padding=dp(5), elevation=0, md_bg_color=(0,0,0,0), ripple_behavior=True, on_release=func_callback)
        box_interno = MDBoxLayout(orientation="vertical", spacing=dp(2), pos_hint={"center_x": .5, "center_y": .5})
        box_interno.add_widget(MDIcon(icon=icone, halign="center", theme_text_color="Custom", text_color=CINZA_TXT, pos_hint={"center_x": .5}))
        box_interno.add_widget(MDLabel(text=texto, halign="center", theme_text_color="Custom", text_color=CINZA_TXT, font_style="Caption"))
        box.add_widget(box_interno)
        return box

    # --- LÓGICA DA BARRA INFERIOR E SUB-DIFICULDADE ---
    def definir_dificuldade(self, diff):
        """Define o MODO DE JOGO quando entra na tela vindo do Menu Principal"""
        diff = diff.lower()
        if diff == "primario":
            self.modo_jogo = "balanca"
            self.sub_dificuldade = "facil"
        elif diff == "fundamental":
            self.modo_jogo = "operacoes"
            self.sub_dificuldade = "medio"
        else:
            self.modo_jogo = "laser"
            self.sub_dificuldade = "dificil"

    def abrir_menu_dificuldade(self, instance):
        """Abre menu para alterar a SUB-DIFICULDADE do jogo atual"""
        if not self.menu_dificuldade:
            opcoes = [
                {"text": "Fácil", "viewclass": "OneLineListItem", "on_release": lambda: self.mudar_sub_dificuldade("facil")},
                {"text": "Médio", "viewclass": "OneLineListItem", "on_release": lambda: self.mudar_sub_dificuldade("medio")},
                {"text": "Difícil", "viewclass": "OneLineListItem", "on_release": lambda: self.mudar_sub_dificuldade("dificil")},
            ]
            self.menu_dificuldade = MDDropdownMenu(caller=instance, items=opcoes, width_mult=3)
        self.menu_dificuldade.open()

    def mudar_sub_dificuldade(self, nova_sub):
        self.menu_dificuldade.dismiss()
        self.sub_dificuldade = nova_sub
        self.mostrar_dialogo_simples("Ajuste", f"O jogo atual foi ajustado para a dificuldade: {nova_sub.capitalize()}.")
        self.on_pre_enter() # Reinicia a fase com a nova dificuldade

    def mostrar_score(self, instance):
        self.mostrar_dialogo_simples("Seu Desempenho", f"Modo: {self.modo_jogo.capitalize()}\nNível: {self.sub_dificuldade.capitalize()}\n\nPontos Totais: {self.pontuacao}\nAcertos: {self.acertos}\nErros: {self.erros}")

    def mostrar_dialogo_simples(self, tit, txt):
        self.dialog = MDDialog(title=tit, text=txt, buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()

    def usar_dica(self, instance):
        self.mostrar_dialogo_simples("Dica Algébrica", "Lembre-se: Tudo que você faz de um lado do sinal de Igual (=), você OBRIGATORIAMENTE deve fazer do outro lado para manter o equilíbrio!")

    # --- FLUXO PRINCIPAL ---
    def on_pre_enter(self):
        self.pergunta_atual = 1
        self.pontuacao = 0
        self.acertos = 0
        self.erros = 0
        self.lbl_pts.text = "0 PTS"
        self.gerar_fase()

    def atualizar_hud(self, titulo, instrucao):
        # Exibe o título + a sub-dificuldade atual
        self.lbl_titulo.text = f"{titulo.upper()} ({self.sub_dificuldade.upper()})"
        self.lbl_instrucao.text = instrucao
        self.lbl_pts.text = f"{self.pontuacao} PTS"

    def gerar_fase(self):
        self.container.clear_widgets()
        self.container.disabled = False

        if self.pergunta_atual > self.total_perguntas:
            self.encerrar_jogo()
            return

        # Roteia baseado no MODO fixo, mas dentro da função usa a sub_dificuldade
        if self.modo_jogo == "balanca":
            self.setup_balanca_matematica()
        elif self.modo_jogo == "operacoes":
            self.setup_operacoes_passos()
        else:
            self.setup_mira_laser()

    # =========================================================================
    # JOGO 1: A BALANÇA MATEMÁTICA (Agora o usuário faz a conta)
    # =========================================================================
    def setup_balanca_matematica(self):
        """O aluno diz exatamente qual operação aplicar nos dois lados para isolar o X."""

        # Ajusta os números baseado na sub-dificuldade
        if self.sub_dificuldade == "facil":
            # x + a = b (positivos pequenos)
            a = random.randint(1, 9)
            x_val = random.randint(1, 9)
        elif self.sub_dificuldade == "medio":
            # x + a = b (números maiores)
            a = random.randint(10, 50)
            x_val = random.randint(10, 50)
        else:
            # x - a = b (envolve números negativos visuais)
            a = random.randint(-20, -1)
            x_val = random.randint(5, 30)

        b = x_val + a

        self.atualizar_hud("A Balança de Equações", "O que você deve fazer nos DOIS lados para deixar o X sozinho?")

        # Balança Customizada
        card_balanca = MDCard(orientation='vertical', radius=[15], padding=dp(10), size_hint=(1, 0.5), md_bg_color=COR_CARD)
        self.balanca = BalancaAlgebrica(x_real=x_val, const_esq=a, const_dir=b, size_hint=(1, 1))
        card_balanca.add_widget(self.balanca)
        self.container.add_widget(card_balanca)

        # Painel de Ação do Usuário
        painel_acao = MDCard(orientation='vertical', padding=dp(15), spacing=dp(10), size_hint=(1, 0.4), md_bg_color=COR_BRANCO)
        painel_acao.add_widget(MDLabel(text="Operação Simultânea:", halign="center", bold=True))

        box_input = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=0.5)

        # Botão de Toggle para + ou -
        self.btn_operador = MDRaisedButton(text="-", font_size="24sp", md_bg_color=COR_DESTAQUE, size_hint_x=0.3, on_release=self.toggle_operador)
        box_input.add_widget(self.btn_operador)

        # Campo para digitar o número
        self.input_numero = MDTextField(hint_text="Número", input_filter="int", font_size="24sp", halign="center", size_hint_x=0.7)
        box_input.add_widget(self.input_numero)

        painel_acao.add_widget(box_input)

        btn_aplicar = MDRaisedButton(text="APLICAR NOS DOIS LADOS", size_hint_x=1, md_bg_color=COR_PRIMARIA, on_release=self.aplicar_na_balanca)
        painel_acao.add_widget(btn_aplicar)

        self.container.add_widget(painel_acao)

    def toggle_operador(self, instance):
        if instance.text == "-":
            instance.text = "+"
            instance.md_bg_color = COR_VERDE
        else:
            instance.text = "-"
            instance.md_bg_color = COR_DESTAQUE

    def aplicar_na_balanca(self, instance):
        if not self.input_numero.text: return

        val = int(self.input_numero.text)
        op = self.btn_operador.text

        # A balança aplica a matemática. Se o X ficar sozinho (const_esq == 0), retorna True.
        x_isolado = self.balanca.aplicar_operacao(op, val)

        if x_isolado:
            # Se isolou corretamente E os dois lados baterem (a física da balança valida isso visualmente)
            self.feedback(True, f"Brilhante! Você isolou o X aplicando {op}{val} nos dois lados. X vale {self.balanca.const_dir}.")
        else:
            # Se não isolou, avisa para continuar tentando
            if self.balanca.const_esq != 0:
                # Não é erro fatal, o aluno pode tentar outro número, mas tira pontos no final se quiser
                self.input_numero.text = ""
                # Se desequilibrou visualmente (errou a conta na cabeça dele e o X real + const não bate com a direita)
                # Na verdade, como aplicamos a mesma operação dos dois lados, a equação NUNCA desequilibra.
                # Ela só fica "feia" se não isolar o X. Essa é a beleza da Álgebra.
                pass

    # =========================================================================
    # JOGO 2: OPERAÇÕES INVERSAS (FUNDAMENTAL)
    # =========================================================================
    def setup_operacoes_passos(self):
        # Ajusta dificuldade do Fundamental
        if self.sub_dificuldade == "facil":
            self.a = 1 # Sem multiplicação
            self.x_val = random.randint(2, 20)
            self.b = random.randint(1, 10)
        elif self.sub_dificuldade == "medio":
            self.a = random.randint(2, 5)
            self.x_val = random.randint(2, 10)
            self.b = random.randint(2, 15)
        else:
            self.a = random.randint(4, 9)
            self.x_val = random.randint(5, 15)
            self.b = random.randint(-15, -1) # Negativos

        sinal = '+' if self.b >= 0 else '' # Se for negativo, o sinal já vem no b
        self.c = (self.a * self.x_val) + self.b

        # Formatação bonita
        ax_str = f"{self.a}x" if self.a > 1 else "x"
        b_str = f"+ {self.b}" if self.b > 0 else f"- {abs(self.b)}"

        self.eq_atual = f"{ax_str} {b_str} = {self.c}"

        self.op_correta_passo1 = f"- {self.b}" if self.b > 0 else f"+ {abs(self.b)}"
        self.op_correta_passo2 = f"÷ {self.a}"

        self.passo = 1 if self.b != 0 else 2

        self.atualizar_hud("Isole o X", "Escolha a operação inversa para desmanchar a equação.")

        self.card_eq = MDCard(size_hint=(1, 0.4), radius=[20], elevation=2, md_bg_color=COR_CARD)
        self.lbl_eq = MDLabel(text=self.eq_atual, halign="center", font_style="H3", bold=True, theme_text_color="Custom", text_color=COR_PRIMARIA)
        self.card_eq.add_widget(self.lbl_eq)
        self.container.add_widget(self.card_eq)

        self.container.add_widget(MDLabel(text="PAINEL DE OPERAÇÕES:", halign="center", bold=True, size_hint_y=0.1))

        self.grid_ops = MDGridLayout(cols=2, spacing=dp(15), size_hint=(1, 0.5), padding=[dp(20), 0, dp(20), 0])
        self.gerar_botoes_operacao()
        self.container.add_widget(self.grid_ops)

    def gerar_botoes_operacao(self):
        self.grid_ops.clear_widgets()

        if self.passo == 1:
            opcoes = [self.op_correta_passo1, f"+ {abs(self.b)}", f"- {abs(self.b)}", f"x {self.a}"]
        else:
            opcoes = [self.op_correta_passo2, f"x {self.a}", f"- {self.a}", f"÷ {self.a+1}"]

        opcoes = list(set(opcoes))
        while len(opcoes) < 4:
            opcoes.append(f"+ {random.randint(1,9)}")
        random.shuffle(opcoes)

        for op in opcoes[:4]:
            btn = MDFillRoundFlatButton(
                text=op, size_hint=(1, 1), font_size="24sp",
                md_bg_color=COR_SECUNDARIA, text_color=COR_BRANCO,
                on_release=lambda x: self.verificar_operacao(x.text)
            )
            self.grid_ops.add_widget(btn)

    def verificar_operacao(self, escolha):
        if self.passo == 1:
            if escolha == self.op_correta_passo1:
                novo_valor = (self.a * self.x_val)
                ax_str = f"{self.a}x" if self.a > 1 else "x"
                self.lbl_eq.text = f"{ax_str} = {novo_valor}"

                if self.a == 1:
                    self.feedback(True, "Análise Perfeita! Você isolou e encontrou o X usando álgebra.")
                else:
                    self.passo = 2
                    self.gerar_botoes_operacao()
            else:
                self.feedback(False, f"Operação incorreta! Use o inverso matemático.")

        elif self.passo == 2:
            if escolha == self.op_correta_passo2:
                self.lbl_eq.text = f"x = {self.x_val}"
                self.lbl_eq.text_color = COR_VERDE
                self.feedback(True, "Análise Perfeita! Você isolou e encontrou o X usando álgebra.")
            else:
                self.feedback(False, "Quase lá! Para isolar o X na multiplicação, use a divisão.")

    # =========================================================================
    # JOGO 3: MIRA LASER (MÉDIO)
    # =========================================================================
    def setup_mira_laser(self):
        # Ajusta dificuldade do Médio
        if self.sub_dificuldade == "facil":
            tx, ty = random.randint(2, 5), random.randint(2, 5) # Alvo perto
            passo_a = 1 # Sliders só em inteiros
        elif self.sub_dificuldade == "medio":
            tx, ty = random.randint(5, 9), random.randint(5, 9)
            passo_a = 0.5 # Inclinação pode ser meio
        else:
            tx, ty = random.randint(2, 9), random.randint(1, 9)
            passo_a = 0.25 # Precisão alta exigida

        self.atualizar_hud("Laser", f"y = ax + b\nCruze o alvo roxo.")

        self.plotter = LaserPlotter(tx, ty, size_hint=(1, 0.45))
        self.container.add_widget(self.plotter)

        painel = MDCard(orientation='vertical', padding=dp(10), spacing=dp(5), radius=[15], size_hint=(1, 0.55), md_bg_color=COR_CARD)
        self.lbl_eq_laser = MDLabel(text="y = 1.0x + 0", halign="center", font_style="H5", bold=True, theme_text_color="Custom", text_color=COR_PRIMARIA)
        painel.add_widget(self.lbl_eq_laser)

        painel.add_widget(MDLabel(text="Inclinação (a):", font_style="Caption", bold=True))
        self.slider_a = MDSlider(min=-3, max=3, value=1, step=passo_a, color=COR_VERDE)
        self.slider_a.bind(value=self.atualizar_laser)
        painel.add_widget(self.slider_a)

        painel.add_widget(MDLabel(text="Altura (b):", font_style="Caption", bold=True))
        self.slider_b = MDSlider(min=-5 if self.sub_dificuldade=="dificil" else 0, max=10, value=0, step=1, color=COR_SECUNDARIA)
        self.slider_b.bind(value=self.atualizar_laser)
        painel.add_widget(self.slider_b)

        btn_fogo = MDRaisedButton(text="DISPARAR LASER", size_hint_x=1, md_bg_color=COR_DESTAQUE, on_release=self.verificar_laser)
        painel.add_widget(btn_fogo)

        self.container.add_widget(painel)
        self.atualizar_laser()

    def atualizar_laser(self, *args):
        a = self.slider_a.value
        b = self.slider_b.value
        sinal = "+" if b >= 0 else ""
        self.lbl_eq_laser.text = f"y = {a}x {sinal} {int(b)}"
        self.plotter.set_params(a, b)

    def verificar_laser(self, instance):
        if self.plotter.verificar_acerto():
            self.feedback(True, "Alvo Destruído! Belo cálculo de função linear.")
        else:
            self.feedback(False, "O laser errou o alvo. Modifique a inclinação ou a altura!")

    # =========================================================================
    # FEEDBACK & FIM DE JOGO
    # =========================================================================
    def feedback(self, acertou, msg):
        self.container.disabled = True
        cor = COR_VERDE if acertou else COR_DESTAQUE
        titulo = "SUCESSO!" if acertou else "ERRO LÓGICO!"

        if acertou:
            self.acertos += 1
            self.pontuacao += 100
        else:
            self.erros += 1

        self.lbl_pts.text = f"{self.pontuacao} PTS"

        content = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        content.add_widget(MDIcon(icon="check-circle" if acertou else "alert-circle", halign="center", font_size="50sp", theme_text_color="Custom", text_color=cor))
        content.add_widget(MDLabel(text=titulo, halign="center", bold=True, font_style="H5", theme_text_color="Custom", text_color=cor))
        content.add_widget(MDLabel(text=msg, halign="center"))
        btn_next = MDRaisedButton(text="CONTINUAR", pos_hint={'center_x': 0.5}, md_bg_color=cor, on_release=lambda x: self.fechar_modal())
        content.add_widget(btn_next)

        self.modal = ModalView(size_hint=(0.85, 0.4), auto_dismiss=False, background_color=(0,0,0,0.6))
        card = MDCard(radius=[20], md_bg_color=(1,1,1,1))
        card.add_widget(content)
        self.modal.add_widget(card)
        self.modal.open()

    def fechar_modal(self):
        self.modal.dismiss()
        self.pergunta_atual += 1
        self.gerar_fase()

    def encerrar_jogo(self):
        if self.manager.has_screen("fim_algebra"):
            screen = self.manager.get_screen("fim_algebra")
            screen.atualizar_stats(self.pontuacao, self.erros, "00:00", f"{self.modo_jogo} ({self.sub_dificuldade})")
            self.manager.current = "fim_algebra"
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
        try:
            layout.add_widget(Image(source='fundoapp.png', allow_stretch=True, keep_ratio=False))
        except: pass

        card = MDCard(
            size_hint=(0.85, 0.65), pos_hint={'center_x': 0.5, 'center_y': 0.5},
            elevation=8, radius=[25], orientation='vertical',
            padding=dp(25), spacing=dp(10), md_bg_color=(0.95, 0.95, 0.98, 1)
        )

        self.titulo_lbl = MDLabel(text="ANÁLISE CONCLUÍDA", halign="center", font_style="H5", bold=True, theme_text_color="Custom", text_color=COR_PRIMARIA)

        self.resumo_box = MDBoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(80))
        self.acertos_lbl = MDLabel(text="Pontos: 0", halign="center", font_style="H5", theme_text_color="Custom", text_color=COR_VERDE)
        self.erros_lbl = MDLabel(text="Erros: 0", halign="center", font_style="Subtitle1", theme_text_color="Custom", text_color=COR_TEXTO)
        self.resumo_box.add_widget(self.acertos_lbl)
        self.resumo_box.add_widget(self.erros_lbl)

        self.input_nome = MDTextField(hint_text="Seu Nome de Analista", icon_right="account", size_hint_x=1, pos_hint={'center_x': 0.5})

        self.btn_salvar = MDRaisedButton(text="SALVAR RESULTADO", size_hint_x=1, height=dp(50), md_bg_color=COR_VERDE, on_release=self.acao_salvar)
        self.status_lbl = MDLabel(text="", halign="center", font_style="Caption", theme_text_color="Hint")

        btn_voltar = MDFlatButton(text="VOLTAR AO MENU", size_hint_x=1, theme_text_color="Custom", text_color=COR_PRIMARIA, on_release=self.voltar_menu)

        card.add_widget(self.titulo_lbl)
        card.add_widget(self.resumo_box)
        card.add_widget(self.input_nome)
        card.add_widget(Widget(size_hint_y=0.1))
        card.add_widget(self.btn_salvar)
        card.add_widget(self.status_lbl)
        card.add_widget(btn_voltar)

        layout.add_widget(card)
        self.add_widget(layout)

    def atualizar_stats(self, pontos, erros, tempo, dificuldade):
        self.dados_partida = {"acertos": pontos, "erros": erros, "tempo": tempo, "dificuldade": dificuldade.capitalize()}
        self.acertos_lbl.text = f"Pontuação Final: {pontos}"
        self.erros_lbl.text = f"Erros Cometidos: {erros}"
        self.input_nome.text = ""
        self.status_lbl.text = ""
        self.btn_salvar.disabled = False
        self.btn_salvar.text = "SALVAR RESULTADO"

    def acao_salvar(self, instance):
        nome = self.input_nome.text.strip()
        if not nome:
            self.status_lbl.text = "Digite seu nome!"
            return
        self.btn_salvar.disabled = True
        self.status_lbl.text = "Enviando para a base..."
        threading.Thread(target=self._salvar_thread, args=(nome,)).start()

    def _salvar_thread(self, nome):
        sucesso, msg = banco_dados.salvar_partida(
            nome, "Escola Padrão", "Álgebra",
            self.dados_partida['dificuldade'],
            self.dados_partida['acertos'],
            self.dados_partida['erros'],
            self.dados_partida['tempo']
        )
        Clock.schedule_once(lambda dt: self._pos_salvar(True, "Salvo com sucesso!"))

    def _pos_salvar(self, sucesso, msg):
        self.status_lbl.text = msg
        if sucesso:
            self.btn_salvar.text = "SALVO!"
            self.btn_salvar.md_bg_color = (0.5, 0.5, 0.5, 1)
        else:
            self.btn_salvar.disabled = False

    def voltar_menu(self, instance):
        self.manager.current = "jogar"