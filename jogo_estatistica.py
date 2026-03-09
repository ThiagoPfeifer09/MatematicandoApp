import os
import threading
import random
import statistics
import math

os.environ["KIVY_LOG_LEVEL"] = "info"

from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, Line, Ellipse
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

import banco_dados

# --- CORES GERAIS DO APP ---
CORAL = (1, 0.44, 0.26, 1)
LILAS = (0.65, 0.55, 0.98, 1)
PRETO = (0, 0, 0, 1)
BRANCO = (1, 1, 1, 1)
CINZA_TXT = (0.5, 0.5, 0.5, 1)

# --- CORES ESPECÍFICAS DOS JOGOS (Tema Laboratório/Estatística) ---
COR_FUNDO = (0.96, 0.96, 0.98, 1)
COR_ROXO = (0.4, 0.2, 0.6, 1)
COR_VERDE = (0.2, 0.7, 0.3, 1)
COR_VERMELHO = (0.9, 0.3, 0.3, 1)
COR_AZUL = (0.2, 0.6, 0.8, 1)
COR_AMARELO = (1, 0.8, 0, 1)
COR_CINZA = (0.9, 0.9, 0.9, 1)
COR_LARANJA = (1, 0.6, 0, 1)

COR_PRIMARIA = COR_ROXO
COR_DESTAQUE = COR_AMARELO
COR_VERDE_SUCESSO = COR_VERDE
COR_TEXTO = (0.2, 0.2, 0.2, 1)
COR_CARD = (1, 1, 1, 0.95)

# ============================================================================
# WIDGET AUXILIAR 1: BARRA DE FREQUÊNCIA (Para o nível Primário)
# ============================================================================
class BarraFrequencia(MDBoxLayout):
    def __init__(self, icone, cor, max_val, callback_slider=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.spacing = dp(10)
        self.size_hint_y = None
        self.height = dp(40)
        self.icone_nome = icone
        self.valor_atual = 0
        self.callback_slider = callback_slider

        self.icon_widget = MDIcon(icon=icone, theme_text_color="Custom", text_color=cor, size_hint_x=0.15, font_size="28sp", pos_hint={'center_y': 0.5})
        self.add_widget(self.icon_widget)

        self.slider = MDSlider(min=0, max=max_val, value=0, step=1, color=cor, size_hint_x=0.7)
        self.slider.bind(value=self.on_slider_value)
        self.add_widget(self.slider)

        self.lbl_valor = MDLabel(text="0", bold=True, size_hint_x=0.15, halign="center", font_style="H6", pos_hint={'center_y': 0.5})
        self.add_widget(self.lbl_valor)

    def on_slider_value(self, instance, value):
        self.valor_atual = int(value)
        self.lbl_valor.text = str(self.valor_atual)
        if self.callback_slider:
            self.callback_slider()

    def set_value(self, val):
        self.slider.value = val

# ============================================================================
# WIDGET AUXILIAR 2: TUBOS DE ENSAIO (Para o nível Fundamental)
# ============================================================================
class TuboEnsaioWidget(Widget):
    def __init__(self, valor_inicial, max_val, callback_mudanca, **kwargs):
        super().__init__(**kwargs)
        self.valor = valor_inicial
        self.max_val = max_val
        self.callback = callback_mudanca
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.register_event_type('on_touch_down')
        self.register_event_type('on_touch_move')

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.ajustar_nivel(touch.y)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            self.ajustar_nivel(touch.y)
            return True
        return super().on_touch_move(touch)

    def ajustar_nivel(self, touch_y):
        h_util = self.height * 0.8
        base_y = self.y + (self.height * 0.1)
        pct = (touch_y - base_y) / h_util
        pct = max(0, min(1, pct))
        novo_valor = int(pct * self.max_val)
        if novo_valor != self.valor:
            self.valor = novo_valor
            self.update_canvas()
            self.callback(self)

    def update_canvas(self, *args):
        self.canvas.clear()
        x, y = self.pos
        w, h = self.size
        w_tubo = w * 0.6
        x_tubo = x + (w - w_tubo) / 2
        y_base = y + (h * 0.1)
        h_tubo = h * 0.8
        h_liq = (self.valor / self.max_val) * h_tubo if self.max_val > 0 else 0

        with self.canvas:
            Color(0.9, 0.9, 0.95, 0.5)
            Rectangle(pos=(x_tubo, y_base), size=(w_tubo, h_tubo))
            Color(*COR_ROXO)
            Rectangle(pos=(x_tubo, y_base), size=(w_tubo, h_liq))
            Color(0.3, 0.3, 0.3, 1)
            Line(rectangle=(x_tubo, y_base, w_tubo, h_tubo), width=dp(2))
            Color(0, 0, 0, 0.15)
            step = h_tubo / 10
            for i in range(1, 10):
                ly = y_base + (i * step)
                Line(points=[x_tubo, ly, x_tubo+w_tubo, ly], width=1)

# ============================================================================
# WIDGET AUXILIAR 3: ROLETA DE PROBABILIDADE (Para o nível Médio)
# ============================================================================
class RoletaWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fatias = [33, 33, 34]
        self.cores = [COR_VERMELHO, COR_VERDE, COR_AZUL]
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def set_fatias(self, lista_pct):
        self.fatias = lista_pct
        self.update_canvas()

    def update_canvas(self, *args):
        self.canvas.clear()
        cx, cy = self.center_x, self.center_y
        raio = min(self.width, self.height) * 0.45
        angle_start = 0

        with self.canvas:
            for i, pct in enumerate(self.fatias):
                if pct <= 0: continue
                angle_size = (pct / 100) * 360
                Color(*self.cores[i % len(self.cores)])
                Ellipse(pos=(cx-raio, cy-raio), size=(raio*2, raio*2),
                        angle_start=angle_start, angle_end=angle_start+angle_size)
                angle_start += angle_size

            # Centro da Roleta
            Color(1, 1, 1, 1)
            Ellipse(pos=(cx-dp(10), cy-dp(10)), size=(dp(20), dp(20)))
            Color(0.2, 0.2, 0.2, 1)
            Line(ellipse=(cx-dp(10), cy-dp(10), dp(20), dp(20)), width=1.5)

# ============================================================================
# TELA PRINCIPAL DO JOGO
# ============================================================================
class EstatisticaGameScreen(Screen):
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
            radius=[15], md_bg_color=COR_CARD, padding=dp(10), elevation=3
        )
        box = MDBoxLayout(spacing=dp(10))
        box.add_widget(MDIconButton(icon="arrow-left", on_release=self.voltar, pos_hint={'center_y': 0.5}))

        info_box = MDBoxLayout(orientation='vertical', pos_hint={'center_y': 0.5})
        self.lbl_titulo = MDLabel(text="ESTATÍSTICA", bold=True, theme_text_color="Custom", text_color=COR_PRIMARIA, font_style="Subtitle1")
        self.lbl_instrucao = MDLabel(text="...", font_style="Caption")
        info_box.add_widget(self.lbl_titulo)
        info_box.add_widget(self.lbl_instrucao)

        self.lbl_pts = MDLabel(text="0 PTS", halign="right", bold=True, theme_text_color="Custom", text_color=COR_VERDE_SUCESSO, font_style="H6")

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

        # BARRA INFERIOR (Sub-dificuldade e Dicas)
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

    # --- LÓGICA DA BARRA INFERIOR E ROTAS ---
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
        self.mostrar_dialogo_simples("Seu Desempenho", f"Modo: Estatística ({self.sub_dificuldade})\n\nPontos Totais: {self.pontuacao}\nAcertos: {self.acertos}\nErros: {self.erros}")

    def mostrar_dialogo_simples(self, tit, txt):
        self.dialog = MDDialog(title=tit, text=txt, buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()

    def usar_dica(self, instance):
        if self.dicas_disponiveis <= 0:
            self.mostrar_dialogo_simples("Atenção", "Você não tem mais dicas nesta partida!")
            return

        self.dicas_disponiveis -= 1

        if self.modo_jogo == "primario":
            # Força o slider da categoria certa a subir um pouco para mostrar o caminho
            cat = list(self.dados_alvo.keys())[0]
            self.barras_freq[cat].set_value(self.dados_alvo[cat])
            self.mostrar_dialogo_simples("Dica de Analista", f"A categoria '{cat}' possui exatamente {self.dados_alvo[cat]} itens na caixa. Ajuste o restante!")

        elif self.modo_jogo == "fundamental":
            self.mostrar_dialogo_simples("Dica de Laboratório", "MÉDIA: Some todos os valores que aparecem embaixo dos tubos e divida pela quantidade de tubos.")

        else: # Medio
            self.mostrar_dialogo_simples("Dica de Probabilidade", "A Roleta inteira é 100%. Se você quer que o Verde tenha 50%, ele precisa ocupar METADE do círculo.")

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
    # JOGO 1: CONSTRUTOR DE GRÁFICO (PRIMÁRIO) - Corrigido e Operacional
    # =========================================================================
    def setup_primario(self):
        # Ajusta dificuldade
        num_cats = 3 if self.sub_dificuldade in ["facil", "medio"] else 4
        max_itens = 5 if self.sub_dificuldade == "facil" else 8

        opcoes = [
            ("apple", COR_VERMELHO),
            ("leaf", COR_VERDE),
            ("star", COR_AMARELO),
            ("water", COR_AZUL)
        ]
        escolhidos = random.sample(opcoes, num_cats)

        # Garante uma moda clara
        qtds = [random.randint(1, max_itens-2) for _ in range(num_cats)]
        qtds[0] = max_itens
        random.shuffle(qtds)

        self.dados_alvo = {escolhidos[i][0]: qtds[i] for i in range(num_cats)}
        self.maior_valor = max(qtds)

        self.atualizar_hud("Organizador de Dados", "Conte os itens na caixa e monte o gráfico com os sliders!")

        # 1. CAIXA BAGUNÇADA
        card_caixa = MDCard(orientation='vertical', size_hint=(1, 0.45), radius=[15], padding=dp(10), md_bg_color=COR_CINZA)
        card_caixa.add_widget(MDLabel(text="DADOS COLETADOS:", bold=True, size_hint_y=None, height=dp(20)))

        grid_icones = MDGridLayout(cols=6 if num_cats==3 else 7, spacing=dp(5), padding=dp(5))

        lista_baguncada = [(ic, cor) for ic, cor in escolhidos for _ in range(self.dados_alvo[ic])]
        random.shuffle(lista_baguncada)

        for ic, cor in lista_baguncada:
            grid_icones.add_widget(MDIcon(icon=ic, theme_text_color="Custom", text_color=cor, font_size="32sp", halign="center"))

        # Completa espaços vazios
        while len(grid_icones.children) < (24 if num_cats==3 else 28):
            grid_icones.add_widget(Widget())

        card_caixa.add_widget(grid_icones)
        self.container.add_widget(card_caixa)

        # 2. CONSTRUTOR DE GRÁFICO (Sliders)
        card_grafico = MDCard(orientation='vertical', size_hint=(1, 0.55), radius=[15], padding=dp(15), spacing=dp(5), md_bg_color=BRANCO)
        card_grafico.add_widget(MDLabel(text="MONTE O GRÁFICO DE BARRAS:", bold=True, size_hint_y=None, height=dp(20)))

        self.barras_freq = {}
        for ic, cor in escolhidos:
            barra = BarraFrequencia(icone=ic, cor=cor, max_val=max_itens)
            self.barras_freq[ic] = barra
            card_grafico.add_widget(barra)

        btn = MDRaisedButton(text="ANALISAR GRÁFICO", size_hint_x=1, height=dp(45), md_bg_color=COR_PRIMARIA, on_release=self.verificar_primario)
        card_grafico.add_widget(btn)

        self.container.add_widget(card_grafico)

    def verificar_primario(self, instance):
        erros_contagem = 0
        for icone, barra in self.barras_freq.items():
            if barra.valor_atual != self.dados_alvo[icone]:
                erros_contagem += 1

        if erros_contagem == 0:
            msg = f"Gráfico Perfeito!\nA barra maior representa a MODA.\nNeste caso, a Moda teve {self.maior_valor} votos."
            self.feedback(True, msg)
        else:
            self.feedback(False, "O gráfico não bate com os dados da caixa. Volte e conte os itens com cuidado!")

    # =========================================================================
    # JOGO 2: LABORATÓRIO DE MÉDIA (FUNDAMENTAL)
    # =========================================================================
    def setup_fundamental(self):
        num_tubos = 3 if self.sub_dificuldade == "facil" else 4 if self.sub_dificuldade == "medio" else 5
        self.pede_mediana = (self.sub_dificuldade == "dificil")

        vals = [random.randint(10, 50) for _ in range(num_tubos)]

        if not self.pede_mediana:
            soma = sum(vals)
            vals[0] -= soma % num_tubos # Ajusta pra divisão ser exata
            self.resposta_calc = sum(vals) // num_tubos
            titulo = "Cálculo de Média"
            instrucao = "Some os valores dos tubos, divida pela quantidade e digite o resultado."
        else:
            self.resposta_calc = int(statistics.median(vals))
            titulo = "Cálculo de Mediana"
            instrucao = "Ordene os valores dos tubos do menor pro maior e ache o do meio (Mediana)."

        self.atualizar_hud(titulo, instrucao)

        box_tubos = MDBoxLayout(spacing=dp(10), padding=dp(10), size_hint=(1, 0.6))
        self.lbls_tubos = {}

        for v in vals:
            col_tubo = MDBoxLayout(orientation='vertical')
            t = TuboEnsaioWidget(valor_inicial=v, max_val=100, callback_mudanca=self.atualizar_lbl_tubo)
            lbl = MDLabel(text=str(v), halign="center", font_style="H6", bold=True, size_hint_y=0.2, theme_text_color="Custom", text_color=COR_ROXO)
            self.lbls_tubos[t] = lbl

            col_tubo.add_widget(t)
            col_tubo.add_widget(lbl)
            box_tubos.add_widget(col_tubo)

        self.container.add_widget(box_tubos)

        painel_resp = MDCard(orientation='horizontal', size_hint=(1, 0.4), padding=dp(20), spacing=dp(20), md_bg_color=BRANCO)

        txt_dica = "Qual a MÉDIA exata?" if not self.pede_mediana else "Qual a MEDIANA?"
        self.in_calc = MDTextField(hint_text=txt_dica, input_filter="int", font_size="24sp", halign="center", pos_hint={'center_y': 0.5})

        btn = MDRaisedButton(text="RESPONDER", height=dp(50), md_bg_color=COR_PRIMARIA, pos_hint={'center_y': 0.5}, on_release=self.verificar_fundamental)

        painel_resp.add_widget(self.in_calc)
        painel_resp.add_widget(btn)

        self.container.add_widget(painel_resp)

    def atualizar_lbl_tubo(self, tubo_instance):
        self.lbls_tubos[tubo_instance].text = str(tubo_instance.valor)

    def verificar_fundamental(self, instance):
        try:
            resp_usuario = int(self.in_calc.text.strip())

            if resp_usuario == self.resposta_calc:
                nome_calc = "Mediana" if self.pede_mediana else "Média"
                self.feedback(True, f"Matemática pura! A {nome_calc} é exatamente {self.resposta_calc}.")
            else:
                self.feedback(False, f"A resposta correta era {self.resposta_calc}. Tente refazer o cálculo mentalmente.")
        except:
            self.mostrar_dialogo_simples("Erro", "Digite um número válido!")

    # =========================================================================
    # JOGO 3: ROLETA DE PROBABILIDADE (MÉDIO) - De volta com os Sliders
    # =========================================================================
    def setup_medio(self):
        """Mecânica: O aluno deve visualizar o Target na Roleta ajustando os % das cores"""

        if self.sub_dificuldade == "facil":
            self.target_prob = random.choice([25, 50, 75])
            self.target_cor_nome = "VERDE"
            self.target_cor_hex = COR_VERDE

        elif self.sub_dificuldade == "medio":
            self.target_prob = random.choice([20, 30, 40, 60, 80])
            self.target_cor_nome = "VERMELHO"
            self.target_cor_hex = COR_VERMELHO

        else:
            self.target_prob = random.choice([10, 15, 35, 45, 85])
            self.target_cor_nome = "AZUL"
            self.target_cor_hex = COR_AZUL

        self.atualizar_hud("Criador de Probabilidade", f"Construa uma roleta onde a cor {self.target_cor_nome} tenha {self.target_prob}% de chance.")

        # O Widget visual da Roleta
        self.roleta = RoletaWidget(size_hint=(1, 0.45))
        self.container.add_widget(self.roleta)

        # Painel de Controle (Sliders)
        painel_ctrl = MDCard(orientation='vertical', size_hint=(1, 0.55), padding=dp(15), spacing=dp(5), md_bg_color=BRANCO)

        # Slider Verde
        box_v = MDBoxLayout(orientation='horizontal')
        box_v.add_widget(MDLabel(text="Verde", size_hint_x=0.3, font_style="Caption", bold=True, theme_text_color="Custom", text_color=COR_VERDE))
        self.sl_verde = MDSlider(min=0, max=100, value=33, step=1, color=COR_VERDE)
        self.sl_verde.bind(value=self.atualizar_roleta)
        box_v.add_widget(self.sl_verde)
        self.lbl_v = MDLabel(text="33%", size_hint_x=0.2, halign="center")
        box_v.add_widget(self.lbl_v)
        painel_ctrl.add_widget(box_v)

        # Slider Vermelho
        box_r = MDBoxLayout(orientation='horizontal')
        box_r.add_widget(MDLabel(text="Vermelho", size_hint_x=0.3, font_style="Caption", bold=True, theme_text_color="Custom", text_color=COR_VERMELHO))
        self.sl_verm = MDSlider(min=0, max=100, value=33, step=1, color=COR_VERMELHO)
        self.sl_verm.bind(value=self.atualizar_roleta)
        box_r.add_widget(self.sl_verm)
        self.lbl_r = MDLabel(text="33%", size_hint_x=0.2, halign="center")
        box_r.add_widget(self.lbl_r)
        painel_ctrl.add_widget(box_r)

        # Azul (Restante Automático para fechar 100%)
        self.lbl_azul = MDLabel(text="Azul (Restante): 34%", halign="center", font_style="Caption", bold=True, theme_text_color="Custom", text_color=COR_AZUL)
        painel_ctrl.add_widget(self.lbl_azul)

        # A Entrada extra de confirmação
        painel_ctrl.add_widget(MDLabel(text=f"Ajuste para {self.target_cor_nome} = {self.target_prob}%", halign="center", theme_text_color="Custom", text_color=self.target_cor_hex, bold=True))

        btn = MDRaisedButton(text="VALIDAR ROLETA", size_hint_x=1, md_bg_color=COR_PRIMARIA, on_release=self.verificar_medio)
        painel_ctrl.add_widget(btn)

        self.container.add_widget(painel_ctrl)
        self.atualizar_roleta()

    def atualizar_roleta(self, *args):
        v = int(self.sl_verde.value)
        r = int(self.sl_verm.value)

        # Garante que a soma não ultrapasse 100
        if v + r > 100:
            fator = 100 / (v + r)
            v = int(v * fator)
            r = int(r * fator)

            # Trava visualmente o slider no limite pra não confundir
            self.sl_verde.value = v
            self.sl_verm.value = r

        a = 100 - (v + r)

        self.lbl_v.text = f"{v}%"
        self.lbl_r.text = f"{r}%"
        self.lbl_azul.text = f"Azul (Restante): {a}%"

        # fatias = [Vermelho, Verde, Azul]
        self.roleta.set_fatias([r, v, a])

        # Guarda os valores atuais para a verificação
        self.dict_valores_roleta = {"VERDE": v, "VERMELHO": r, "AZUL": a}

    def verificar_medio(self, instance):
        valor_jogador = self.dict_valores_roleta[self.target_cor_nome]

        # Margem de erro visual
        if abs(valor_jogador - self.target_prob) <= 2:
            self.feedback(True, f"Montagem Perfeita! A cor {self.target_cor_nome} ficou com a área exigida.")
        else:
            self.feedback(False, f"Incorreto. Você deixou a cor {self.target_cor_nome} com {valor_jogador}%.\nO objetivo era {self.target_prob}%.")

    # =========================================================================
    # FEEDBACK E NAVEGAÇÃO
    # =========================================================================
    def feedback(self, acertou, msg):
        self.container.disabled = True

        cor = COR_VERDE_SUCESSO if acertou else COR_VERMELHO
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
        if self.manager.has_screen("fim_estatistica"):
            screen = self.manager.get_screen("fim_estatistica")
            screen.atualizar_stats(self.pontuacao, self.erros, "00:00", f"{self.modo_jogo} ({self.sub_dificuldade})")
            self.manager.current = "fim_estatistica"
        else:
            self.voltar(None)

    def voltar(self, instance=None):
        if self.dialog: self.dialog.dismiss()
        if self.manager: self.manager.current = "jogar"

# ============================================================================
# TELA DE FIM (Padronizada)
# ============================================================================
class TelaFimEstatistica(Screen):
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

        self.titulo_lbl = MDLabel(text="RELATÓRIO FINAL", halign="center", font_style="H5", bold=True, theme_text_color="Custom", text_color=COR_PRIMARIA)

        self.resumo_box = MDBoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(80))
        self.acertos_lbl = MDLabel(text="Pontos: 0", halign="center", font_style="H5", theme_text_color="Custom", text_color=COR_VERDE)
        self.erros_lbl = MDLabel(text="Erros: 0", halign="center", font_style="Subtitle1", theme_text_color="Custom", text_color=COR_TEXTO)
        self.resumo_box.add_widget(self.acertos_lbl)
        self.resumo_box.add_widget(self.erros_lbl)

        self.input_nome = MDTextField(hint_text="Nome do Estatístico", icon_right="account", size_hint_x=1, pos_hint={'center_x': 0.5})

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
            nome, "Escola Padrão", "Estatística",
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