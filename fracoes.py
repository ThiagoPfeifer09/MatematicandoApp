import os
import random
from fractions import Fraction
import threading
import math

os.environ["KIVY_LOG_LEVEL"] = "info"

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, Line
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton, MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.slider import MDSlider
from kivy.uix.widget import Widget
from kivy.uix.modalview import ModalView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu

from sistema_erros import GerenciadorErros
import banco_dados

# --- PALETA DE CORES ---
COR_FUNDO = (0.94, 0.96, 0.98, 1)
COR_PRIMARIA = (0.1, 0.5, 0.8, 1) # Azul principal
COR_SECUNDARIA = (1.0, 0.6, 0.1, 1) # Laranja
COR_VERDE = (0.2, 0.7, 0.3, 1)
COR_VERMELHO = (0.9, 0.2, 0.2, 1)
COR_CINZA = (0.85, 0.85, 0.85, 1)
COR_TEXTO = (0.2, 0.2, 0.2, 1)
BRANCO = (1, 1, 1, 1)
CINZA_TXT = (0.5, 0.5, 0.5, 1)

# ============================================================================
# WIDGET 1: BLOCO CLICÁVEL (Primário)
# ============================================================================
class BlocoFracao(MDCard):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.ativo = False
        self.md_bg_color = COR_CINZA
        self.radius = [10]
        self.elevation = 1
        self.ripple_behavior = True

    def on_release(self):
        self.ativo = not self.ativo
        if self.ativo:
            self.md_bg_color = COR_SECUNDARIA
            self.elevation = 4
        else:
            self.md_bg_color = COR_CINZA
            self.elevation = 1
        self.callback()

    def revelar_dica(self):
        if not self.ativo:
            self.md_bg_color = COR_VERDE
            Clock.schedule_once(lambda dt: self._voltar_cor(), 1.5)

    def _voltar_cor(self):
        if not self.ativo:
            self.md_bg_color = COR_CINZA

# ============================================================================
# WIDGET 2: BARRA DE FRAÇÃO NATIVA (Fundamental e Médio)
# ============================================================================
class BarraFracaoWidget(Widget):
    def __init__(self, n=0, d=1, cor_fundo=COR_SECUNDARIA, is_impropria=False, **kwargs):
        super().__init__(**kwargs)
        self.n = n
        self.d = d if d > 0 else 1
        self.cor_fundo = cor_fundo
        self.is_impropria = is_impropria
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def set_fracao(self, n, d):
        self.n = n
        self.d = d if d > 0 else 1
        self.update_canvas()

    def destacar_dica(self):
        cor_original = self.cor_fundo
        self.cor_fundo = COR_VERDE
        self.update_canvas()
        Clock.schedule_once(lambda dt: self._remover_destaque(cor_original), 1.5)

    def _remover_destaque(self, cor_original):
        self.cor_fundo = cor_original
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size

        # Se for imprópria visualmente, a barra base inteira é o "d", mas pode pintar além.
        # Caso contrário, limita no máximo d.
        max_visual_n = self.n if self.is_impropria else min(self.n, self.d)
        largura_preenchida = (w / self.d) * max_visual_n if self.d > 0 else 0

        # Limita visual para não sair da tela do app, mesmo se for mais que o dobro
        largura_preenchida = min(largura_preenchida, w * 1.5)

        with self.canvas:
            # Fundo base (1 inteiro)
            Color(0.9, 0.9, 0.9, 1)
            Rectangle(pos=(x, y), size=(w, h))

            # Se passar de 1 inteiro, desenha o fundo extra
            if largura_preenchida > w:
                Color(0.85, 0.85, 0.85, 1)
                Rectangle(pos=(x+w+dp(5), y), size=(w, h))

            if self.n > 0:
                Color(*self.cor_fundo)
                # Preenche até 1 inteiro
                if largura_preenchida <= w:
                    Rectangle(pos=(x, y), size=(largura_preenchida, h))
                else:
                    # Preenche 1 inteiro todo
                    Rectangle(pos=(x, y), size=(w, h))
                    # Preenche a sobra na segunda barra
                    sobra = largura_preenchida - w
                    Rectangle(pos=(x+w+dp(5), y), size=(sobra, h))

            Color(0.3, 0.3, 0.3, 1)
            Line(rectangle=(x, y, w, h), width=dp(2))

            if largura_preenchida > w:
                Line(rectangle=(x+w+dp(5), y, w, h), width=dp(2))

            if self.d > 1:
                step = w / self.d
                for i in range(1, self.d):
                    Line(points=[x + (i * step), y, x + (i * step), y + h], width=dp(1.5))
                # Réguas na barra extra se existir
                if largura_preenchida > w:
                    for i in range(1, self.d):
                        Line(points=[x + w + dp(5) + (i * step), y, x + w + dp(5) + (i * step), y + h], width=dp(1.5))

# ============================================================================
# TELA DO JOGO PRINCIPAL
# ============================================================================
class FracoesGameScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.modo_jogo = "primario"
        self.sub_dificuldade = "facil"
        self.pergunta_atual = 1
        self.total_perguntas = 5
        self.acertos = 0
        self.erros = 0
        self.pontuacao = 0
        self.dicas_disponiveis = 3
        self.menu_dificuldade = None
        self.dialog = None

        # Inicializa o gerenciador aqui para evitar erros de atributo
        self.gerenciador_erros = GerenciadorErros()

        self._setup_ui()

    def _setup_ui(self):
        self.main_box = MDBoxLayout(orientation="vertical", md_bg_color=COR_FUNDO)
        self.game_area = FloatLayout(size_hint_y=1)

        try:
            self.game_area.add_widget(Image(source='fundoapp.png', allow_stretch=True, keep_ratio=False))
        except: pass

        # CABEÇALHO / HUD
        header = MDCard(
            size_hint=(0.95, None), height=dp(70),
            pos_hint={'center_x': 0.5, 'top': 0.98},
            radius=[15], md_bg_color=(1, 1, 1, 0.95), padding=dp(10), elevation=4
        )
        box_head = MDBoxLayout(spacing=dp(10))
        box_head.add_widget(MDIconButton(icon="arrow-left", on_release=self.voltar, pos_hint={'center_y': 0.5}))

        info_box = MDBoxLayout(orientation='vertical', pos_hint={'center_y': 0.5})
        self.lbl_titulo = MDLabel(text="FRAÇÕES", bold=True, theme_text_color="Custom", text_color=COR_PRIMARIA, font_style="Subtitle1")
        self.lbl_instrucao = MDLabel(text="...", theme_text_color="Secondary", font_style="Caption")
        info_box.add_widget(self.lbl_titulo)
        info_box.add_widget(self.lbl_instrucao)

        self.lbl_pts = MDLabel(text="0 PTS", halign="right", bold=True, theme_text_color="Custom", text_color=COR_VERDE, font_style="H6")

        box_head.add_widget(info_box)
        box_head.add_widget(self.lbl_pts)
        header.add_widget(box_head)
        self.game_area.add_widget(header)

        # CONTAINER DINÂMICO
        self.container = MDBoxLayout(
            orientation='vertical', size_hint=(0.95, 0.72),
            pos_hint={'center_x': 0.5, 'y': 0.05}, spacing=dp(10)
        )
        self.game_area.add_widget(self.container)
        self.main_box.add_widget(self.game_area)

        # BARRA INFERIOR
        self.bottom_bar = MDCard(orientation="horizontal", size_hint_y=None, height=dp(80), md_bg_color=BRANCO, elevation=10, padding=dp(10))
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

    # --- LÓGICA DA BARRA INFERIOR ---
    def definir_dificuldade(self, diff):
        diff = diff.lower()
        if diff == "primario":
            self.modo_jogo = "primario"
            self.sub_dificuldade = "facil"
        elif diff == "fundamental":
            self.modo_jogo = "fundamental"
            self.sub_dificuldade = "medio"
        else:
            self.modo_jogo = "medio"
            self.sub_dificuldade = "dificil"

    def abrir_menu_dificuldade(self, instance):
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
        self.mostrar_dialogo_simples("Ajuste", f"A dificuldade foi alterada para: {nova_sub.capitalize()}.")
        self.on_pre_enter()

    def mostrar_score(self, instance):
        self.mostrar_dialogo_simples("Placar Atual", f"Modo: Frações ({self.sub_dificuldade})\n\nPontos Totais: {self.pontuacao}\nAcertos: {self.acertos}\nErros: {self.erros}")

    def mostrar_dialogo_simples(self, tit, txt):
        self.dialog = MDDialog(title=tit, text=txt, buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()

    def usar_dica(self, instance):
        if self.dicas_disponiveis <= 0:
            self.mostrar_dialogo_simples("Atenção", "Você não tem mais dicas para esta partida.")
            return

        self.dicas_disponiveis -= 1

        if self.modo_jogo == "primario":
            blocos_faltando = [b for b in self.blocos if not b.ativo]
            marcados = sum([1 for b in self.blocos if b.ativo])
            n_alvo = self.fracao_alvo[0]
            if marcados < n_alvo and blocos_faltando:
                blocos_faltando[0].revelar_dica()
        elif self.modo_jogo == "fundamental":
            self.mostrar_dialogo_simples("Dica", f"Procure dividir os dois números (numerador e denominador) por um divisor comum. Pense na tabuada!")
        else: # medio
            if hasattr(self, 'bar1'):
                self.bar1.destacar_dica()
                self.mostrar_dialogo_simples("Dica", "O tamanho total que você precisa cobrir é igual à área verde que piscou!")

    # --- FLUXO PRINCIPAL DO JOGO ---
    def on_pre_enter(self):
        self.pergunta_atual = 1
        self.pontuacao = 0
        self.acertos = 0
        self.erros = 0
        self.dicas_disponiveis = 3
        self.lbl_pts.text = "0 PTS"

        # Reinicia o banco de erros da rodada atual
        self.gerenciador_erros = GerenciadorErros()

        self.gerar_fase()

    def atualizar_hud(self, titulo, instrucao):
        self.lbl_titulo.text = f"{titulo.upper()} ({self.sub_dificuldade.upper()})"
        self.lbl_instrucao.text = instrucao
        self.lbl_pts.text = f"{self.pontuacao} PTS"

    def gerar_fase(self):
        self.container.clear_widgets()
        self.container.disabled = False

        if self.pergunta_atual > self.total_perguntas:
            self.encerrar_jogo()
            return

        if self.modo_jogo == "primario":
            self.setup_primario()
        elif self.modo_jogo == "fundamental":
            self.setup_fundamental()
        else:
            self.setup_medio()

    # =========================================================================
    # JOGO 1: CONSTRUTOR DE BLOCOS (PRIMÁRIO)
    # =========================================================================
    def setup_primario(self):
        if self.sub_dificuldade == "facil":
            d = random.randint(2, 4)
            n = random.randint(1, d)
        elif self.sub_dificuldade == "medio":
            d = random.randint(5, 8)
            n = random.randint(1, d - 1)
        else:
            # Frações Impróprias (N > D)
            d = random.randint(3, 5)
            n = random.randint(d + 1, d * 2 - 1)

        self.fracao_alvo = (n, d)

        txt_dica = "Pinte mais de um inteiro!" if n > d else f"Pinte os blocos para formar {n}/{d}"
        self.atualizar_hud("Construtor", txt_dica)

        card_tela = MDCard(orientation='vertical', padding=dp(20), spacing=dp(15), radius=[15], md_bg_color=(1,1,1,0.9))
        card_tela.add_widget(MDLabel(text=f"{n} / {d}", halign="center", font_style="H2", bold=True, theme_text_color="Custom", text_color=COR_PRIMARIA))

        self.blocos = []

        # Se for imprópria, mostra 2 blocos de D (2 inteiros)
        total_blocos = d * 2 if n > d else d
        cols = d # Colunas é igual ao Denominador, assim a quebra de linha forma os inteiros visuais

        grid = MDGridLayout(cols=cols, spacing=dp(5), adaptive_size=True, pos_hint={'center_x': 0.5})

        for i in range(total_blocos):
            bloco = BlocoFracao(callback=self.atualizar_contador_primario, size_hint=(None, None), size=(dp(45), dp(45)))
            self.blocos.append(bloco)
            grid.add_widget(bloco)

        card_tela.add_widget(grid)

        self.lbl_contador = MDLabel(text="0 selecionados", halign="center", theme_text_color="Secondary", font_style="Subtitle1")
        card_tela.add_widget(self.lbl_contador)

        btn_confirmar = MDRaisedButton(
            text="CONFIRMAR", size_hint_x=1, height=dp(50),
            md_bg_color=COR_PRIMARIA, on_release=self.verificar_primario
        )
        card_tela.add_widget(btn_confirmar)
        self.container.add_widget(card_tela)

    def atualizar_contador_primario(self):
        marcados = sum([1 for b in self.blocos if b.ativo])
        self.lbl_contador.text = f"{marcados} selecionados"

    def verificar_primario(self, instance):
        marcados = sum([1 for b in self.blocos if b.ativo])
        n_alvo, d_alvo = self.fracao_alvo

        if marcados == n_alvo:
            self.feedback(True, f"Perfeito! Você construiu a fração {n_alvo}/{d_alvo}.")
        else:
            # REGISTRA ERRO: Categoria Visual
            self.gerenciador_erros.registrar_erro("fracao_visual")
            self.feedback(False, f"Você selecionou {marcados} partes. O pedido era {n_alvo}.")

    # =========================================================================
    # JOGO 2: SIMPLIFICADOR VISUAL (FUNDAMENTAL)
    # =========================================================================
    def setup_fundamental(self):
        if self.sub_dificuldade == "facil":
            pares = [(2,4), (4,8), (2,6), (3,6), (5,10), (2,10)] # Pares / Divisiveis obvios
            self.forcar_irredutivel = False
        elif self.sub_dificuldade == "medio":
            pares = [(6,9), (4,12), (6,8), (8,12), (9,12), (6,15)]
            self.forcar_irredutivel = False
        else:
            pares = [(8,16), (6,12), (4,16), (10,15), (12,18)]
            self.forcar_irredutivel = True # Exige que chegue na fração mínima possível

        n_alvo, d_alvo = random.choice(pares)
        self.alvo_f = Fraction(n_alvo, d_alvo)
        self.alvo_d_original = d_alvo

        if self.forcar_irredutivel:
            txt_instrucao = "Simplifique a fração ao MÁXIMO possível."
        else:
            txt_instrucao = "Ajuste N e D para criar uma fração IGUAL, mas simplificada."

        self.atualizar_hud("Simplifique", txt_instrucao)

        painel = MDCard(orientation='vertical', padding=dp(15), spacing=dp(10), radius=[15], md_bg_color=(1,1,1,0.95))

        box_alvo = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=0.2)
        box_alvo.add_widget(MDLabel(text=f"{n_alvo}\n—\n{d_alvo}", halign="center", size_hint_x=0.2, bold=True))
        barra_alvo = BarraFracaoWidget(n=n_alvo, d=d_alvo, cor_fundo=COR_VERMELHO)
        box_alvo.add_widget(barra_alvo)
        painel.add_widget(box_alvo)

        painel.add_widget(MDBoxLayout(size_hint_y=None, height=dp(2), md_bg_color=COR_CINZA))

        self.box_jog = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=0.2)
        self.lbl_jog = MDLabel(text="0\n—\n1", halign="center", size_hint_x=0.2, bold=True, theme_text_color="Custom", text_color=COR_PRIMARIA)
        self.barra_jog = BarraFracaoWidget(n=0, d=1, cor_fundo=COR_SECUNDARIA)
        self.box_jog.add_widget(self.lbl_jog)
        self.box_jog.add_widget(self.barra_jog)
        painel.add_widget(self.box_jog)

        box_sliders = MDBoxLayout(orientation='vertical', size_hint_y=0.4, spacing=dp(5))
        box_sliders.add_widget(MDLabel(text="Numerador (Cima):", font_style="Caption", bold=True))
        self.slider_n = MDSlider(min=0, max=10, value=0, step=1, color=COR_SECUNDARIA)
        self.slider_n.bind(value=self.atualizar_barra_fundamental)
        box_sliders.add_widget(self.slider_n)

        box_sliders.add_widget(MDLabel(text="Denominador (Baixo):", font_style="Caption", bold=True))
        self.slider_d = MDSlider(min=1, max=10, value=1, step=1, color=COR_PRIMARIA)
        self.slider_d.bind(value=self.atualizar_barra_fundamental)
        box_sliders.add_widget(self.slider_d)
        painel.add_widget(box_sliders)

        btn = MDRaisedButton(text="TESTAR EQUIVALÊNCIA", size_hint_x=1, md_bg_color=COR_PRIMARIA, on_release=self.verificar_fundamental)
        painel.add_widget(btn)
        self.container.add_widget(painel)

    def atualizar_barra_fundamental(self, *args):
        n = int(self.slider_n.value)
        d = int(self.slider_d.value)
        self.lbl_jog.text = f"{n}\n—\n{d}"
        self.barra_jog.set_fracao(n, d)

    def verificar_fundamental(self, instance):
        n = int(self.slider_n.value)
        d = int(self.slider_d.value)
        if d == 0: d = 1
        f_jogador = Fraction(n, d)

        if f_jogador == self.alvo_f:
            if self.forcar_irredutivel:
                if f_jogador.denominator == d and f_jogador.numerator == n:
                    self.feedback(True, f"Perfeito! {n}/{d} é a forma irredutível.")
                else:
                    # REGISTRA ERRO: Simplificação (chegou perto mas não reduziu tudo)
                    self.gerenciador_erros.registrar_erro("simplificacao")
                    self.feedback(False, f"São equivalentes, mas {n}/{d} AINDA dá pra simplificar mais!")
            else:
                if d < self.alvo_d_original:
                    self.feedback(True, f"Genial! {n}/{d} é equivalente e está simplificada.")
                else:
                    # REGISTRA ERRO: Simplificação (não diminuiu o denominador)
                    self.gerenciador_erros.registrar_erro("simplificacao")
                    self.feedback(False, "Elas são equivalentes, mas você não simplificou.")
        else:
            # REGISTRA ERRO: Simplificação/Equivalência (errou o cálculo básico)
            self.gerenciador_erros.registrar_erro("simplificacao")
            self.feedback(False, "Os volumes visuais não batem. As frações não são equivalentes.")

    # =========================================================================
    # JOGO 3: LABORATÓRIO DE OPERAÇÕES (MÉDIO)
    # =========================================================================
    def setup_medio(self):
        if self.sub_dificuldade == "facil":
            # Mesmos denominadores
            d = random.randint(3, 6)
            n1 = random.randint(1, d-1)
            n2 = random.randint(1, d-1)
            op = '+' if (n1+n2) <= d else '-'
            if op == '-': n1, n2 = max(n1,n2), min(n1,n2)
            n1_alvo, d1_alvo, n2_alvo, d2_alvo = n1, d, n2, d

        elif self.sub_dificuldade == "medio":
            # Denominadores diferentes, mas múltiplos
            operacoes = [(1,2, '+', 1,4), (1,2, '-', 1,4), (1,3, '+', 1,6), (2,3, '-', 1,6), (1,2, '+', 1,8)]
            n1_alvo, d1_alvo, op, n2_alvo, d2_alvo = random.choice(operacoes)

        else:
            # Difícil: Pode gerar frações > 1 (Soma) ou denominadores chatos
            operacoes = [(3,4, '+', 1,2), (2,3, '+', 1,2), (3,5, '-', 1,2), (1,3, '+', 1,4)]
            n1_alvo, d1_alvo, op, n2_alvo, d2_alvo = random.choice(operacoes)

        f1 = Fraction(n1_alvo, d1_alvo)
        f2 = Fraction(n2_alvo, d2_alvo)
        if op == '+': self.f_resp = f1 + f2
        else: self.f_resp = f1 - f2

        self.atualizar_hud("Operações", f"Resolva a operação e ajuste a barra de resposta.")

        painel = MDCard(orientation='vertical', padding=dp(10), spacing=dp(5), radius=[15], md_bg_color=(1,1,1,0.95))

        box_conta = MDBoxLayout(orientation='horizontal', spacing=dp(5), size_hint_y=0.25)
        self.bar1 = BarraFracaoWidget(n1_alvo, d1_alvo, COR_PRIMARIA, size_hint_x=0.4)
        lbl_op = MDLabel(text=op, halign="center", font_style="H4", size_hint_x=0.1, bold=True)
        bar2 = BarraFracaoWidget(n2_alvo, d2_alvo, COR_SECUNDARIA, size_hint_x=0.4)

        box_conta.add_widget(self.bar1)
        box_conta.add_widget(lbl_op)
        box_conta.add_widget(bar2)
        painel.add_widget(box_conta)

        painel.add_widget(MDLabel(text=f"({n1_alvo}/{d1_alvo})   {op}   ({n2_alvo}/{d2_alvo})   =   ?", halign="center", bold=True, size_hint_y=0.15))

        self.box_resp = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=0.2)
        self.lbl_resp = MDLabel(text="0\n—\n1", halign="center", size_hint_x=0.2, bold=True, theme_text_color="Custom", text_color=COR_VERDE)

        # Se for dificil, ativa o modo de desenho pra fração impropria
        is_impropria = self.sub_dificuldade == "dificil"
        self.barra_resp = BarraFracaoWidget(n=0, d=1, cor_fundo=COR_VERDE, is_impropria=is_impropria)

        self.box_resp.add_widget(self.lbl_resp)
        self.box_resp.add_widget(self.barra_resp)
        painel.add_widget(self.box_resp)

        box_sliders = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=0.3)
        box_n = MDBoxLayout(orientation='vertical')
        box_n.add_widget(MDLabel(text="Numerador:", font_style="Caption", halign="center"))
        max_n_slider = 16 if is_impropria else 12
        self.slider_resp_n = MDSlider(min=0, max=max_n_slider, value=0, step=1, color=COR_VERDE)
        self.slider_resp_n.bind(value=self.atualizar_barra_medio)
        box_n.add_widget(self.slider_resp_n)

        box_d = MDBoxLayout(orientation='vertical')
        box_d.add_widget(MDLabel(text="Denominador:", font_style="Caption", halign="center"))
        self.slider_resp_d = MDSlider(min=1, max=12, value=1, step=1, color=COR_VERDE)
        self.slider_resp_d.bind(value=self.atualizar_barra_medio)
        box_d.add_widget(self.slider_resp_d)

        box_sliders.add_widget(box_n)
        box_sliders.add_widget(box_d)
        painel.add_widget(box_sliders)

        btn = MDRaisedButton(text="CONFIRMAR RESULTADO", size_hint_x=1, md_bg_color=COR_VERDE, on_release=self.verificar_medio)
        painel.add_widget(btn)
        self.container.add_widget(painel)

    def atualizar_barra_medio(self, *args):
        n = int(self.slider_resp_n.value)
        d = int(self.slider_resp_d.value)
        self.lbl_resp.text = f"{n}\n—\n{d}"
        self.barra_resp.set_fracao(n, d)

    def verificar_medio(self, instance):
        n = int(self.slider_resp_n.value)
        d = int(self.slider_resp_d.value)
        f_jogador = Fraction(n, d)

        if f_jogador == self.f_resp:
            self.feedback(True, f"Matemática Perfeita! A resposta é {self.f_resp.numerator}/{self.f_resp.denominator}.")
        else:
            # REGISTRA ERRO: Operação com Fração
            self.gerenciador_erros.registrar_erro("operacao_fracao")
            self.feedback(False, f"Incorreto. A resposta exata era {self.f_resp.numerator}/{self.f_resp.denominator}.")

    # =========================================================================
    # FEEDBACK & FIM DE JOGO
    # =========================================================================
    def feedback(self, acertou, msg):
        self.container.disabled = True
        cor = COR_VERDE if acertou else COR_VERMELHO
        titulo = "EXCELENTE!" if acertou else "ATENÇÃO!"

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
        btn_next = MDRaisedButton(text="PRÓXIMO", pos_hint={'center_x': 0.5}, md_bg_color=cor, on_release=lambda x: self.fechar_modal())
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
        # PEGA A DICA BASEADA NO QUE MAIS ERROU
        mensagem_dica = self.gerenciador_erros.obter_dica_final()

        tela_fim = self.manager.get_screen("fim_fracoes")

        # Passa a dica para a tela final
        tela_fim.atualizar_stats(
            self.pontuacao,
            self.erros,
            "00:00",
            f"{self.modo_jogo} ({self.sub_dificuldade})",
            mensagem_dica
        )
        self.manager.current = "fim_fracoes"

    def voltar(self, instance=None):
        if self.dialog: self.dialog.dismiss()
        self.manager.current = "jogar"

# ============================================================================
# TELA DE FIM (Padronizada)
# ============================================================================
class TelaFimFracoes(Screen):
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

        self.titulo_lbl = MDLabel(text="FRAÇÕES CONCLUÍDAS", halign="center", font_style="H5", bold=True, theme_text_color="Custom", text_color=COR_PRIMARIA)

        self.resumo_box = MDBoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(80))
        self.acertos_lbl = MDLabel(text="Pontos: 0", halign="center", font_style="H5", theme_text_color="Custom", text_color=COR_VERDE)
        self.erros_lbl = MDLabel(text="Erros: 0", halign="center", font_style="Subtitle1", theme_text_color="Custom", text_color=COR_TEXTO)

        self.dica_lbl = MDLabel(text="", halign="center", font_style="Caption", bold=True, theme_text_color="Custom", text_color=(0.9, 0.4, 0.1, 1))

        self.resumo_box.add_widget(self.acertos_lbl)
        self.resumo_box.add_widget(self.erros_lbl)
        self.resumo_box.add_widget(self.dica_lbl)

        self.input_nome = MDTextField(hint_text="Seu Nome para o Ranking", icon_right="account", size_hint_x=1, pos_hint={'center_x': 0.5})

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

    def atualizar_stats(self, pontos, erros, tempo, dificuldade, mensagem_dica=""):
        self.dados_partida = {"acertos": pontos, "erros": erros, "tempo": tempo, "dificuldade": dificuldade.capitalize()}
        self.acertos_lbl.text = f"Pontuação Final: {pontos}"
        self.erros_lbl.text = f"Erros Cometidos: {erros}"
        self.input_nome.text = ""
        self.status_lbl.text = ""
        self.btn_salvar.disabled = False
        self.btn_salvar.text = "SALVAR RESULTADO"
        self.dica_lbl.text = mensagem_dica

    def atualizar_stats(self, pontos, erros, tempo, dificuldade, mensagem_dica=""):
        self.dados_partida = {"acertos": pontos, "erros": erros, "tempo": tempo, "dificuldade": dificuldade.capitalize()}
        self.acertos_lbl.text = f"Pontuação Final: {pontos}"
        self.erros_lbl.text = f"Erros Cometidos: {erros}"

        # MOSTRA A DICA NA TELA
        self.dica_lbl.text = mensagem_dica

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
            nome, "Escola Padrão", "Frações",
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