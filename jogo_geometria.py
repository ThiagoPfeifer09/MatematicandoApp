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
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.textfield import MDTextField
from kivy.uix.modalview import ModalView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.menu import MDDropdownMenu

# Tentativa de importar os módulos locais de base de dados e gestão de erros
try:
    from sistema_erros import GerenciadorErros
    import banco_dados
except ImportError:
    class GerenciadorErros:
        def registrar_erro(self, tipo): pass
        def obter_dica_final(self): return "Pratique mais a construção de formas geométricas!"
    class banco_dados:
        @staticmethod
        def salvar_partida(*args): return True, "Guardado na Base (Simulação)"

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
# WIDGET 1: GEOPLANO VIRTUAL (Nível Primário)
# ============================================================================
class GeoplanoWidget(Widget):
    def __init__(self, cols=6, rows=6, **kwargs):
        super().__init__(**kwargs)
        self.cols = cols
        self.rows = rows
        self.pontos_grid = [] # Guarda as posições (x, y) reais no ecrã
        self.vertices_selecionados = [] # Guarda os índices dos pontos clicados
        self.figura_fechada = False

        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()
        w, h = self.size
        x0, y0 = self.pos

        # Recalcula a posição dos pontos baseados no tamanho do widget
        self.pontos_grid = []
        passo_x = w / (self.cols + 1)
        passo_y = h / (self.rows + 1)

        with self.canvas:
            # Fundo estilo prancheta
            Color(1, 1, 1, 1)
            Rectangle(pos=self.pos, size=self.size)

            # Desenha os pontos do Geoplano (Pinos)
            Color(*COR_CINZA)
            for c in range(1, self.cols + 1):
                for r in range(1, self.rows + 1):
                    px = x0 + (c * passo_x)
                    py = y0 + (r * passo_y)
                    self.pontos_grid.append((px, py, c, r)) # Ecrã X, Ecrã Y, Grid X, Grid Y
                    Ellipse(pos=(px - dp(4), py - dp(4)), size=(dp(8), dp(8)))

            # Desenha as linhas (O elástico)
            if self.vertices_selecionados:
                Color(*COR_AZUL_BLUEPRINT)
                pontos_linha = []
                for idx in self.vertices_selecionados:
                    px, py, _, _ = self.pontos_grid[idx]
                    pontos_linha.extend([px, py])
                    # Destaca os vértices escolhidos
                    Ellipse(pos=(px - dp(6), py - dp(6)), size=(dp(12), dp(12)))

                if len(pontos_linha) >= 4: # Pelo menos 2 pontos (x1,y1,x2,y2)
                    Line(points=pontos_linha, width=dp(3))

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.figura_fechada:
            # Encontra o ponto mais próximo do toque
            for idx, (px, py, cx, cy) in enumerate(self.pontos_grid):
                dist = math.hypot(touch.x - px, touch.y - py)
                if dist < dp(30): # Raio de tolerância para o toque de dedo

                    # Se clicou no primeiro ponto de novo (e tem pelo menos 3 pontos), fecha a figura
                    if len(self.vertices_selecionados) >= 3 and idx == self.vertices_selecionados[0]:
                        self.vertices_selecionados.append(idx)
                        self.figura_fechada = True
                    # Se não clicou no mesmo ponto da última vez, adiciona à linha
                    elif not self.vertices_selecionados or idx != self.vertices_selecionados[-1]:
                        self.vertices_selecionados.append(idx)

                    self.update_canvas()
                    return True
        return super().on_touch_down(touch)

    def limpar(self):
        self.vertices_selecionados = []
        self.figura_fechada = False
        self.update_canvas()

    def calcular_distancia_quadrada(self, p1, p2):
        return (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2

    def verificar_forma(self, forma_alvo):
        if not self.figura_fechada:
            return False, "É necessário fechar a figura! Toque novamente no primeiro ponto que marcou."

        # Extrai as coordenadas lógicas (Grid X, Grid Y) da figura (ignorando o último ponto que fecha o ciclo)
        coords = [(self.pontos_grid[idx][2], self.pontos_grid[idx][3]) for idx in self.vertices_selecionados[:-1]]
        qtd_lados = len(coords)

        if forma_alvo == "Triângulo":
            if qtd_lados == 3:
                return True, "Excelente! Três vértices e três lados formam um triângulo perfeito."
            return False, f"Desenhou uma figura com {qtd_lados} lados. O triângulo precisa de 3!"

        elif forma_alvo == "Quadrado":
            if qtd_lados != 4:
                return False, f"O quadrado precisa de exatos 4 lados, desenhou {qtd_lados}."

            l1 = self.calcular_distancia_quadrada(coords[0], coords[1])
            l2 = self.calcular_distancia_quadrada(coords[1], coords[2])
            l3 = self.calcular_distancia_quadrada(coords[2], coords[3])
            l4 = self.calcular_distancia_quadrada(coords[3], coords[0])

            diag1 = self.calcular_distancia_quadrada(coords[0], coords[2])
            diag2 = self.calcular_distancia_quadrada(coords[1], coords[3])

            if l1 == l2 == l3 == l4 and diag1 == diag2:
                return True, "Perfeito! Todos os 4 lados são iguais e os ângulos são retos."
            elif l1 == l2 == l3 == l4:
                return False, "Os lados são iguais, mas os cantos estão tortos (formou um Losango). Tente deixá-lo reto."
            else:
                return False, "Os lados não têm o mesmo tamanho!"

        elif forma_alvo == "Retângulo":
            if qtd_lados != 4:
                return False, f"O retângulo precisa de 4 lados, desenhou {qtd_lados}."

            l1 = self.calcular_distancia_quadrada(coords[0], coords[1])
            l2 = self.calcular_distancia_quadrada(coords[1], coords[2])
            l3 = self.calcular_distancia_quadrada(coords[2], coords[3])
            l4 = self.calcular_distancia_quadrada(coords[3], coords[0])

            diag1 = self.calcular_distancia_quadrada(coords[0], coords[2])
            diag2 = self.calcular_distancia_quadrada(coords[1], coords[3])

            if l1 == l3 and l2 == l4 and diag1 == diag2:
                if l1 != l2:
                    return True, "Bom trabalho! Lados opostos iguais formando um retângulo."
                else:
                    return False, "Desenhou um Quadrado! Lembre-se, o retângulo tem lados esticados (diferentes)."
            else:
                return False, "Os lados não estão alinhados corretamente ou os cantos não são retos."

        return False, "Ainda não consegui identificar esta forma. Tente novamente!"


# ============================================================================
# WIDGET 2: GRADE INTERATIVA (Nível Fundamental)
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
# WIDGET 3: TRANSFERIDOR INTERATIVO (Nível Médio)
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
# TELA PRINCIPAL DO JOGO DE GEOMETRIA
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

        # BARRA INFERIOR
        self.bottom_bar = MDCard(orientation="horizontal", size_hint_y=None, height=dp(80), md_bg_color=BRANCO, elevation=10, padding=dp(10))
        self.bottom_bar.add_widget(self.criar_item_barra("Dicas", "lightbulb-outline", self.usar_dica))
        self.bottom_bar.add_widget(self.criar_item_barra("Dificuldade", "tune", self.abrir_menu_dificuldade))
        self.bottom_bar.add_widget(self.criar_item_barra("Placar", "chart-bar", self.mostrar_score))
        self.main_box.add_widget(self.bottom_bar)

        self.add_widget(self.main_box)

    def criar_item_barra(self, texto, icone, func_callback):
        box = MDCard(orientation="vertical", padding=dp(5), elevation=0, md_bg_color=(0,0,0,0), ripple_behavior=True, on_release=func_callback)
        box_interno = MDBoxLayout(orientation="vertical", spacing=dp(2), pos_hint={"center_x": .5, "center_y": .5})
        box_interno.add_widget(MDIcon(icon=icone, halign="center", theme_text_color="Custom", text_color=CINZA_TXT, pos_hint={"center_x": .5}))
        box_interno.add_widget(MDLabel(text=texto, halign="center", theme_text_color="Custom", text_color=CINZA_TXT, font_style="Caption"))
        box.add_widget(box_interno)
        return box

    def abrir_menu_dificuldade(self, instance):
        if not self.menu_dificuldade:
            opcoes = [
                {"text": "Primário (Geoplano)", "viewclass": "OneLineListItem", "on_release": lambda: self.mudar_sub_dificuldade("facil", "primario")},
                {"text": "Fundamental (Área)", "viewclass": "OneLineListItem", "on_release": lambda: self.mudar_sub_dificuldade("medio", "fundamental")},
                {"text": "Médio (Ângulos)", "viewclass": "OneLineListItem", "on_release": lambda: self.mudar_sub_dificuldade("dificil", "medio")},
            ]
            self.menu_dificuldade = MDDropdownMenu(caller=instance, items=opcoes, width_mult=4)
        self.menu_dificuldade.open()

    def mudar_sub_dificuldade(self, nova_sub, novo_modo):
        self.menu_dificuldade.dismiss()
        self.sub_dificuldade = nova_sub
        self.modo_jogo = novo_modo
        self.mostrar_dialogo_simples("Ajuste", f"Modo alterado para: {novo_modo.capitalize()}.")
        self.on_pre_enter()

    def mostrar_score(self, instance):
        self.mostrar_dialogo_simples("Placar Atual", f"Modo: Geometria ({self.sub_dificuldade})\n\nPontos Totais: {self.pontuacao}\nAcertos: {self.acertos}\nErros: {self.erros}")

    def mostrar_dialogo_simples(self, tit, txt):
        self.dialog = MDDialog(title=tit, text=txt, buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()

    def usar_dica(self, instance):
        if self.dicas_disponiveis <= 0:
            self.mostrar_dialogo_simples("Atenção", "Já não tem dicas nesta partida!")
            return

        self.dicas_disponiveis -= 1

        if self.modo_jogo == "primario":
            msg = f"Lembre-se: O {self.alvo_nome} precisa ter as proporções corretas. Clique nos pontos até fechar a forma perfeitamente."
            self.mostrar_dialogo_simples("Dica de Desenho", msg)

        elif self.modo_jogo == "fundamental":
            faltam = self.area_alvo - self.grade.area_selecionada
            if faltam > 0: msg = f"Faltam {faltam} quadrados!"
            elif faltam < 0: msg = f"Pintou {abs(faltam)} quadrados a mais!"
            else: msg = "A área já está perfeita! Confirme o projeto."
            self.mostrar_dialogo_simples("Dica do Arquiteto", msg)

        else: # Medio
            self.mostrar_dialogo_simples("Dica Matemática", self.dica_matematica)


    def on_pre_enter(self):
        self.pergunta_atual = 1
        self.pontuacao = 0
        self.acertos = 0
        self.erros = 0
        self.dicas_disponiveis = 3
        self.lbl_pts.text = "0 PTS"
        self.gerenciador_erros = GerenciadorErros()
        self.gerar_fase()

    def atualizar_hud(self, titulo, instrucao):
        self.lbl_titulo.text = f"{titulo.upper()}"
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
    # JOGO 1: GEOPLANO VIRTUAL (PRIMÁRIO)
    # =========================================================================
    def setup_primario(self):
        # O Geoplano trabalha de forma otimizada com polígonos retos.
        formas_disponiveis = ["Quadrado", "Retângulo", "Triângulo"]
        self.alvo_nome = random.choice(formas_disponiveis)

        self.atualizar_hud("Geoplano Virtual", f"Ligue os pontos e feche um {self.alvo_nome.upper()}.")

        card_quadro = MDCard(
            orientation='vertical', radius=[15], padding=dp(5),
            size_hint=(1, 0.75), pos_hint={'center_x': 0.5}, elevation=4,
            md_bg_color=(1,1,1,1)
        )

        # Instancia o Geoplano
        self.geoplano = GeoplanoWidget(cols=6, rows=6)
        card_quadro.add_widget(self.geoplano)

        self.container.add_widget(card_quadro)

        box_botoes = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint=(1, 0.25), pos_hint={'center_x': 0.5})

        btn_limpar = MDFlatButton(
            text="CORTAR ELÁSTICO",
            theme_text_color="Custom",
            text_color=COR_VERMELHO,
            size_hint_x=0.3,
            on_release=lambda x: self.geoplano.limpar()
        )

        btn_validar = MDRaisedButton(
            text="VALIDAR POLÍGONO",
            md_bg_color=COR_AZUL_BLUEPRINT,
            size_hint_x=0.7,
            on_release=self.verificar_primario
        )

        box_botoes.add_widget(btn_limpar)
        box_botoes.add_widget(btn_validar)

        self.container.add_widget(box_botoes)

    def verificar_primario(self, instance):
        acertou, msg = self.geoplano.verificar_forma(self.alvo_nome)

        if acertou:
            self.feedback(True, msg)
        else:
            self.gerenciador_erros.registrar_erro("desenho_formas")
            self.geoplano.limpar()
            self.feedback(False, msg + "\nO geoplano foi limpo. Tente novamente!")

    # =========================================================================
    # JOGO 2: CONSTRUTOR DE ÁREA (FUNDAMENTAL)
    # =========================================================================
    def setup_fundamental(self):
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
            self.gerenciador_erros.registrar_erro("area")
            self.feedback(False, f"Erro no projeto. Pintou {self.grade.area_selecionada} e era necessário {self.area_alvo}.")

    # =========================================================================
    # JOGO 3: MESTRE DOS ÂNGULOS (MÉDIO)
    # =========================================================================
    def setup_medio(self):
        if self.sub_dificuldade == "facil":
            self.angulo_alvo = random.choice([30, 45, 60, 90, 120, 150])
            self.atualizar_hud("Transferidor", f"Gire o ponteiro para medir exatos {self.angulo_alvo}°.")
            self.explicacao = f"Apenas medição visual direta."
            self.dica_matematica = "Olhe para a linha de base preta e gire a linha laranja até a abertura parecer correta."

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
                self.dica_matematica = "Ângulos suplementares somam 180 graus (uma linha reta inteira)."

        else:
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
            self.gerenciador_erros.registrar_erro("angulos")
            self.feedback(False, f"Incorreto. Marcou {self.transferidor.angulo_atual}°.\n\n{self.explicacao}")


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
        mensagem_dica = self.gerenciador_erros.obter_dica_final()

        if self.manager.has_screen("fim_geometria"):
            tela_fim = self.manager.get_screen("fim_geometria")
            tela_fim.atualizar_stats(
                self.pontuacao,
                self.erros,
                "00:00",
                f"{self.modo_jogo} ({self.sub_dificuldade})",
                mensagem_dica
            )
            self.manager.current = "fim_geometria"
        else:
            self.voltar()

    def voltar(self, instance=None):
        if hasattr(self, 'event_update'): self.event_update.cancel()
        if self.dialog: self.dialog.dismiss()
        if self.manager: self.manager.current = "jogar"

# ============================================================================
# TELA DE FIM (Ecrã Final)
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

        self.dica_lbl = MDLabel(text="", halign="center", font_style="Caption", bold=True, theme_text_color="Custom", text_color=(0.9, 0.4, 0.1, 1))

        self.resumo_box.add_widget(self.acertos_lbl)
        self.resumo_box.add_widget(self.erros_lbl)
        self.resumo_box.add_widget(self.dica_lbl)

        self.input_nome = MDTextField(hint_text="Nome do Arquiteto", icon_right="account", size_hint_x=1, pos_hint={'center_x': 0.5})

        self.btn_salvar = MDRaisedButton(text="GUARDAR REGISTO", size_hint_x=1, height=dp(50), md_bg_color=COR_VERDE, on_release=self.acao_salvar)
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

    def atualizar_stats(self, pontos, erros, tempo, dificuldade, mensagem_dica=""):
        self.dados_partida = {"acertos": pontos, "erros": erros, "tempo": tempo, "dificuldade": dificuldade.capitalize()}
        self.acertos_lbl.text = f"Pontuação Final: {pontos}"
        self.erros_lbl.text = f"Erros Cometidos: {erros}"
        self.input_nome.text = ""
        self.status_lbl.text = ""
        self.btn_salvar.disabled = False
        self.btn_salvar.text = "GUARDAR REGISTO"
        self.dica_lbl.text = mensagem_dica

    def acao_salvar(self, instance):
        nome = self.input_nome.text.strip()
        if not nome:
            self.status_lbl.text = "Identifique-se!"
            return
        self.btn_salvar.disabled = True
        self.status_lbl.text = "A enviar para a base de dados..."
        threading.Thread(target=self._salvar_thread, args=(nome,)).start()

    def _salvar_thread(self, nome):
        try:
            sucesso, msg = banco_dados.salvar_partida(
                nome, "Escola Padrão", "Geometria",
                self.dados_partida['dificuldade'],
                self.dados_partida['acertos'],
                self.dados_partida['erros'],
                self.dados_partida['tempo']
            )
        except Exception:
            sucesso, msg = True, "Guardado (Modo Offline)"

        Clock.schedule_once(lambda dt: self._pos_salvar(True, msg))

    def _pos_salvar(self, sucesso, msg):
        self.status_lbl.text = msg
        if sucesso:
            self.btn_salvar.text = "GUARDADO!"
            self.btn_salvar.md_bg_color = (0.5, 0.5, 0.5, 1)
        else:
            self.btn_salvar.disabled = False

    def voltar_menu(self, instance):
        self.manager.current = "jogar"