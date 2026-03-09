import os
import random
import math
import threading
from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.metrics import dp
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton, MDRaisedButton, MDFlatButton
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.textfield import MDTextField
from kivy.uix.modalview import ModalView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu

import banco_dados

# --- PALETA DE CORES (Tema Arquitetura/Blueprint) ---
COR_FUNDO = (0.94, 0.96, 0.98, 1)
COR_AZUL_BLUEPRINT = (0.1, 0.3, 0.6, 1)
COR_LARANJA = (1, 0.6, 0, 1)
COR_VERDE = (0.2, 0.7, 0.3, 1)
COR_VERMELHO = (0.9, 0.2, 0.2, 1)
COR_CINZA = (0.9, 0.9, 0.9, 1)
COR_TEXTO = (0.2, 0.2, 0.3, 1)
BRANCO = (1, 1, 1, 1)
CINZA_TXT = (0.5, 0.5, 0.5, 1)

# ============================================================================
# WIDGET 1: GRADE INTERATIVA (Fundamental)
# ============================================================================
class CelulaGrade(MDRaisedButton):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.ativa = False
        self.md_bg_color = COR_CINZA
        self.elevation = 0
        self.size_hint = (1, 1)
        self.text = ""

    def on_release(self):
        self.ativa = not self.ativa
        if self.ativa:
            self.md_bg_color = COR_AZUL_BLUEPRINT
            self.elevation = 3
        else:
            self.md_bg_color = COR_CINZA
            self.elevation = 0
        self.callback()

    def resetar(self):
        self.ativa = False
        self.md_bg_color = COR_CINZA
        self.elevation = 0

class GradeQuadriculada(MDGridLayout):
    def __init__(self, cols=5, rows=5, callback_mudanca=None, **kwargs):
        super().__init__(**kwargs)
        self.cols = cols
        self.rows = rows
        # Se for muito grande, diminui o espaçamento para caber na tela
        self.spacing = dp(4) if cols <= 5 else dp(2)
        self.padding = dp(10)
        self.callback = callback_mudanca
        self.celulas = []
        self.area_selecionada = 0

        for _ in range(cols * rows):
            c = CelulaGrade(self.atualizar_area)
            self.add_widget(c)
            self.celulas.append(c)

    def atualizar_area(self):
        self.area_selecionada = sum([1 for c in self.celulas if c.ativa])
        if self.callback:
            self.callback(self.area_selecionada)

# ============================================================================
# WIDGET 2: TRANSFERIDOR INTERATIVO (Médio)
# ============================================================================
class TransferidorWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.angulo_atual = 0
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.calcular_angulo(touch.pos)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self.calcular_angulo(touch.pos)
            return True
        return super().on_touch_move(touch)

    def calcular_angulo(self, touch_pos):
        cx = self.center_x
        cy = self.y + dp(10)

        dx = touch_pos[0] - cx
        dy = touch_pos[1] - cy

        rads = math.atan2(dy, dx)
        deg = math.degrees(rads)

        if deg < 0: deg = 0
        if deg > 180: deg = 180

        self.angulo_atual = int(deg)
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.clear()
        cx = self.center_x
        cy = self.y + dp(10)

        raio = min(self.width / 2, self.height) * 0.85

        with self.canvas:
            Color(0.85, 0.85, 0.85, 1)
            Ellipse(pos=(cx-raio, cy-raio), size=(raio*2, raio*2), angle_start=0, angle_end=180)

            Color(0, 0, 0, 1)
            Line(points=[cx-raio, cy, cx+raio, cy], width=dp(2))
            Line(ellipse=(cx-raio, cy-raio, raio*2, raio*2, 0, 180), width=dp(2))

            Color(*COR_AZUL_BLUEPRINT, 0.5)
            Ellipse(pos=(cx-raio, cy-raio), size=(raio*2, raio*2), angle_start=0, angle_end=self.angulo_atual)

            rad = math.radians(self.angulo_atual)
            px = cx + raio * math.cos(rad)
            py = cy + raio * math.sin(rad)

            Color(*COR_LARANJA)
            Line(points=[cx, cy, px, py], width=dp(4))

            Color(*COR_AZUL_BLUEPRINT)
            Ellipse(pos=(cx-dp(10), cy-dp(10)), size=(dp(20), dp(20)))

# ============================================================================
# TELA DO JOGO
# ============================================================================
class GeometriaGameScreen(Screen):
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
            radius=[15], md_bg_color=(1, 1, 1, 0.95), padding=dp(10), elevation=3
        )
        box = MDBoxLayout(spacing=dp(10))
        box.add_widget(MDIconButton(icon="arrow-left", on_release=self.voltar, pos_hint={'center_y': 0.5}))

        info_box = MDBoxLayout(orientation='vertical', pos_hint={'center_y': 0.5})
        self.lbl_titulo = MDLabel(text="GEOMETRIA", bold=True, theme_text_color="Custom", text_color=COR_AZUL_BLUEPRINT, font_style="Subtitle1")
        self.lbl_instrucao = MDLabel(text="...", font_style="Caption")
        info_box.add_widget(self.lbl_titulo)
        info_box.add_widget(self.lbl_instrucao)

        self.lbl_pts = MDLabel(text="0 PTS", halign="right", bold=True, theme_text_color="Custom", text_color=COR_VERDE, font_style="H6")

        box.add_widget(info_box)
        box.add_widget(self.lbl_pts)
        header.add_widget(box)
        self.game_area.add_widget(header)

        # CONTAINER DINÂMICO
        self.container = MDBoxLayout(
            orientation='vertical', size_hint=(0.95, 0.72),
            pos_hint={'center_x': 0.5, 'y': 0.05}, spacing=dp(10)
        )
        self.game_area.add_widget(self.container)
        self.main_box.add_widget(self.game_area)

        # BARRA INFERIOR (Sub-dificuldade)
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
        self.mostrar_dialogo_simples("Placar Atual", f"Modo: Geometria ({self.sub_dificuldade})\n\nPontos Totais: {self.pontuacao}\nAcertos: {self.acertos}\nErros: {self.erros}")

    def mostrar_dialogo_simples(self, tit, txt):
        self.dialog = MDDialog(title=tit, text=txt, buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()

    def usar_dica(self, instance):
        if self.dicas_disponiveis <= 0:
            self.mostrar_dialogo_simples("Atenção", "Você não tem mais dicas nesta partida!")
            return

        self.dicas_disponiveis -= 1

        if self.modo_jogo == "primario":
            # Desabilita uma alternativa errada
            erradas = [c for c in self.cards_opcoes if c.forma_nome != self.alvo_nome and not c.disabled]
            if erradas:
                alvo = random.choice(erradas)
                alvo.md_bg_color = COR_VERMELHO
                alvo.disabled = True

        elif self.modo_jogo == "fundamental":
            # Conta e avisa quantos faltam
            faltam = self.area_alvo - self.grade.area_selecionada
            if faltam > 0: msg = f"Faltam {faltam} quadrados!"
            elif faltam < 0: msg = f"Você pintou {abs(faltam)} quadrados a mais!"
            else: msg = "A área já está perfeita! É só confirmar."
            self.mostrar_dialogo_simples("Dica do Arquiteto", msg)

        else: # Medio
            self.mostrar_dialogo_simples("Dica Matemática", self.dica_matematica)

    # --- FLUXO PRINCIPAL ---
    def on_pre_enter(self):
        self.pergunta_atual = 1
        self.pontuacao = 0
        self.acertos = 0
        self.erros = 0
        self.dicas_disponiveis = 3
        self.lbl_pts.text = "0 PTS"
        self.gerar_fase()

    def atualizar_hud(self, titulo, instrucao):
        self.lbl_titulo.text = f"{titulo.upper()} ({self.sub_dificuldade.upper()})"
        self.lbl_instrucao.text = instrucao
        self.lbl_pts.text = f"{self.pontuacao} PTS"

    def gerar_fase(self):
        self.container.clear_widgets()
        self.container.disabled = False

        if self.pergunta_atual > self.total_perguntas:
            self.encerrar()
            return

        if self.modo_jogo == "primario":
            self.setup_primario()
        elif self.modo_jogo == "fundamental":
            self.setup_fundamental()
        else:
            self.setup_medio()

    # =========================================================================
    # JOGO 1: ENCAIXE A FORMA (PRIMÁRIO)
    # =========================================================================
    def setup_primario(self):
        formas_todas = [
            ("Triângulo", "triangle", 3), ("Quadrado", "square", 4),
            ("Pentágono", "pentagon", 5), ("Hexágono", "hexagon", 6),
            ("Círculo", "circle", 0), ("Losango", "rhombus", 4),
            ("Estrela", "star", 10), ("Octógono", "octagon", 8)
        ]

        if self.sub_dificuldade == "facil":
            opcoes_qtd = 4
            cols = 2
            pergunta_tipo = "nome"
        elif self.sub_dificuldade == "medio":
            opcoes_qtd = 6
            cols = 2
            pergunta_tipo = "nome"
        else:
            opcoes_qtd = 6
            cols = 2
            pergunta_tipo = "lados"

        opcoes = random.sample(formas_todas, opcoes_qtd)
        alvo = random.choice(opcoes)
        self.alvo_nome = alvo[0]

        if pergunta_tipo == "nome":
            self.atualizar_hud("Visão Espacial", f"Toque na forma: {self.alvo_nome.upper()}")
        else:
            txt_lado = "não possui lados retos" if alvo[2] == 0 else f"possui exatamente {alvo[2]} LADOS"
            self.atualizar_hud("Geometria", f"Toque na forma que {txt_lado}.")

        # 🔹 Grid maior
        grid = MDGridLayout(
            cols=cols,
            spacing=dp(20),
            padding=dp(20),
            size_hint=(1, 0.9)
        )

        self.cards_opcoes = []

        for f in opcoes:
            card = MDCard(
                orientation='vertical',
                padding=dp(20),
                radius=[25],
                elevation=6,
                ripple_behavior=True,
                md_bg_color=(1, 1, 1, 1),
                on_release=lambda x, nome=f[0]: self.verificar_primario(nome)
            )

            card.forma_nome = f[0]

            # 🔥 Ícone MUITO maior
            tamanho_fonte = "800sp" if opcoes_qtd == 4 else "240sp"

            icone = MDIcon(
                icon=f"{f[1]}-outline",
                halign="center",
                valign="middle",
                font_size=tamanho_fonte,
                theme_text_color="Custom",
                text_color=COR_AZUL_BLUEPRINT,
                size_hint_y=1
            )

            card.add_widget(icone)
            grid.add_widget(card)
            self.cards_opcoes.append(card)

        self.container.add_widget(grid)

    def verificar_primario(self, escolha):
        if escolha == self.alvo_nome:
            self.feedback(True, "Visualização e análise perfeitas!")
        else:
            self.feedback(False, f"Ops! Aquele era o {escolha}. O alvo era o {self.alvo_nome}.")

    # =========================================================================
    # JOGO 2: CONSTRUTOR DE ÁREA (FUNDAMENTAL)
    # =========================================================================
    def setup_fundamental(self):
        # Ajusta dificuldade
        if self.sub_dificuldade == "facil":
            grid_c, grid_r = 4, 4
            self.area_alvo = random.randint(4, 10)
        elif self.sub_dificuldade == "medio":
            grid_c, grid_r = 5, 5
            self.area_alvo = random.randint(10, 18)
        else:
            grid_c, grid_r = 6, 6
            self.area_alvo = random.randint(18, 30)

        self.atualizar_hud("Planta Baixa", f"Pinte exatos {self.area_alvo} metros quadrados (blocos).")

        card_grade = MDCard(
            size_hint=(0.9, 0.6), pos_hint={'center_x': 0.5},
            radius=[15], elevation=4, padding=dp(5), md_bg_color=(1,1,1,1)
        )
        self.grade = GradeQuadriculada(cols=grid_c, rows=grid_r, callback_mudanca=self.atualizar_contador_area)
        card_grade.add_widget(self.grade)

        self.container.add_widget(Widget(size_hint_y=0.05))
        self.container.add_widget(card_grade)

        box_botton = MDBoxLayout(orientation='vertical', size_hint_y=0.35, padding=dp(20), spacing=dp(10))
        self.lbl_contador = MDLabel(text="Área Atual: 0", halign="center", font_style="H4", theme_text_color="Custom", text_color=COR_LARANJA, bold=True)
        box_botton.add_widget(self.lbl_contador)

        btn = MDRaisedButton(
            text="CONFIRMAR PROJETO",
            size_hint_x=1, height=dp(50),
            md_bg_color=COR_AZUL_BLUEPRINT,
            font_size="18sp",
            on_release=self.verificar_fundamental
        )
        box_botton.add_widget(btn)
        self.container.add_widget(box_botton)

    def atualizar_contador_area(self, valor):
        self.lbl_contador.text = f"Área Atual: {valor}"
        if valor == self.area_alvo:
            self.lbl_contador.text_color = COR_VERDE
        else:
            self.lbl_contador.text_color = COR_LARANJA

    def verificar_fundamental(self, instance):
        if self.grade.area_selecionada == self.area_alvo:
            self.feedback(True, "Aprovação concedida! Área exata.")
        else:
            self.feedback(False, f"Erro no projeto. Você pintou {self.grade.area_selecionada} e eu pedi {self.area_alvo}.")

    # =========================================================================
    # JOGO 3: MESTRE DOS ÂNGULOS (MÉDIO)
    # =========================================================================
    def setup_medio(self):
        # Ajusta Dificuldade
        if self.sub_dificuldade == "facil":
            # Sem conta, apenas setar o ângulo visualmente
            self.angulo_alvo = random.choice([30, 45, 60, 90, 120, 150])
            self.atualizar_hud("Transferidor", f"Gire o ponteiro para medir exatos {self.angulo_alvo}°.")
            self.explicacao = f"Apenas medição visual direta."
            self.dica_matematica = "Olhe para a linha base preta e gire a linha laranja até a abertura parecer correta."

        elif self.sub_dificuldade == "medio":
            tipo = random.choice(["complemento", "suplemento"])
            if tipo == "complemento":
                base = random.choice([20, 30, 40, 45, 50, 60, 70])
                self.angulo_alvo = 90 - base
                self.atualizar_hud("Complementar", f"Marque o COMPLEMENTO de {base}°.")
                self.explicacao = f"Conta: 90° - {base}° = {self.angulo_alvo}°"
                self.dica_matematica = "Ângulos complementares somam 90 graus (um ângulo reto)."
            else:
                base = random.choice([45, 60, 90, 100, 120, 135, 150])
                self.angulo_alvo = 180 - base
                self.atualizar_hud("Suplementar", f"Marque o SUPLEMENTO de {base}°.")
                self.explicacao = f"Conta: 180° - {base}° = {self.angulo_alvo}°"
                self.dica_matematica = "Ângulos suplementares somam 180 graus (uma linha reta meia-lua inteira)."

        else:
            # Triângulos
            ang1 = random.choice([30, 40, 45, 50, 60])
            ang2 = random.choice([40, 50, 60, 70, 80])
            self.angulo_alvo = 180 - (ang1 + ang2)
            self.atualizar_hud("Triângulos", f"Um triângulo tem ângulos de {ang1}° e {ang2}°. Marque o 3º ângulo!")
            self.explicacao = f"Conta: 180° - ({ang1}° + {ang2}°) = {self.angulo_alvo}°"
            self.dica_matematica = "A soma de todos os ângulos internos de qualquer triângulo é sempre 180 graus."

        self.transferidor = TransferidorWidget(size_hint=(1, 0.5))
        self.container.add_widget(self.transferidor)

        self.lbl_angulo_atual = MDLabel(text="0°", halign="center", font_style="H2", bold=True, theme_text_color="Custom", text_color=COR_AZUL_BLUEPRINT)
        self.container.add_widget(self.lbl_angulo_atual)

        self.event_update = Clock.schedule_interval(self.atualizar_label_angulo, 0.05)

        box_btn = MDBoxLayout(padding=[dp(20), dp(10), dp(20), dp(30)], size_hint_y=0.2)
        btn = MDRaisedButton(
            text="CONFIRMAR MEDIDA",
            size_hint_x=1, height=dp(50),
            md_bg_color=COR_LARANJA,
            on_release=self.verificar_medio
        )
        box_btn.add_widget(btn)
        self.container.add_widget(box_btn)

    def atualizar_label_angulo(self, dt):
        if hasattr(self, 'transferidor'):
            self.lbl_angulo_atual.text = f"{self.transferidor.angulo_atual}°"

    def verificar_medio(self, instance):
        if hasattr(self, 'event_update'):
            self.event_update.cancel()

        diff = abs(self.transferidor.angulo_atual - self.angulo_alvo)

        if diff <= 5:
            self.feedback(True, f"Exato!\n{self.explicacao}")
        else:
            self.feedback(False, f"Incorreto. Você marcou {self.transferidor.angulo_atual}°.\n\n{self.explicacao}")

    # =========================================================================
    # FEEDBACK E NAVEGAÇÃO
    # =========================================================================
    def feedback(self, acertou, msg):
        self.container.disabled = True

        cor = COR_VERDE if acertou else COR_VERMELHO
        titulo = "SUCESSO!" if acertou else "ERROU..."

        if acertou:
            self.pontuacao += 100
            self.acertos += 1
        else:
            self.erros += 1

        self.lbl_pts.text = f"{self.pontuacao} PTS"

        content = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        content.add_widget(MDIcon(icon="check-circle" if acertou else "close-circle", halign="center", font_size="50sp", theme_text_color="Custom", text_color=cor))
        content.add_widget(MDLabel(text=titulo, halign="center", bold=True, font_style="H5", theme_text_color="Custom", text_color=cor))
        content.add_widget(MDLabel(text=msg, halign="center"))

        btn = MDRaisedButton(text="PRÓXIMO", pos_hint={'center_x': 0.5}, md_bg_color=cor, on_release=lambda x: self.fechar_modal())
        content.add_widget(btn)

        self.modal = ModalView(size_hint=(0.85, 0.45), auto_dismiss=False, background_color=(0,0,0,0.5))
        card = MDCard(radius=[20], md_bg_color=(1,1,1,1))
        card.add_widget(content)
        self.modal.add_widget(card)
        self.modal.open()

    def fechar_modal(self):
        self.modal.dismiss()
        self.pergunta_atual += 1
        self.gerar_fase()

    def encerrar(self):
        if self.manager.has_screen("fim_geometria"):
            screen = self.manager.get_screen("fim_geometria")
            screen.atualizar_stats(self.pontuacao, self.erros, "00:00", f"{self.modo_jogo} ({self.sub_dificuldade})")
            self.manager.current = "fim_geometria"
        else:
            self.voltar(None)

    def voltar(self, instance=None):
        if hasattr(self, 'event_update'): self.event_update.cancel()
        if self.dialog: self.dialog.dismiss()
        if self.manager: self.manager.current = "jogar"

# ============================================================================
# TELA DE FIM (Padronizada)
# ============================================================================
class TelaFimGeometria(Screen):
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

        self.titulo_lbl = MDLabel(text="PROJETO FINALIZADO", halign="center", font_style="H5", bold=True, theme_text_color="Custom", text_color=COR_AZUL_BLUEPRINT)

        self.resumo_box = MDBoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(80))
        self.acertos_lbl = MDLabel(text="Pontos: 0", halign="center", font_style="H5", theme_text_color="Custom", text_color=COR_VERDE)
        self.erros_lbl = MDLabel(text="Erros: 0", halign="center", font_style="Subtitle1", theme_text_color="Custom", text_color=COR_TEXTO)
        self.resumo_box.add_widget(self.acertos_lbl)
        self.resumo_box.add_widget(self.erros_lbl)

        self.input_nome = MDTextField(hint_text="Nome do Arquiteto", icon_right="account", size_hint_x=1, pos_hint={'center_x': 0.5})

        self.btn_salvar = MDRaisedButton(text="SALVAR RESULTADO", size_hint_x=1, height=dp(50), md_bg_color=COR_VERDE, on_release=self.acao_salvar)
        self.status_lbl = MDLabel(text="", halign="center", font_style="Caption", theme_text_color="Hint")

        btn_voltar = MDFlatButton(text="VOLTAR AO MENU", size_hint_x=1, theme_text_color="Custom", text_color=COR_AZUL_BLUEPRINT, on_release=self.voltar_menu)

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
            nome, "Escola Padrão", "Geometria",
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