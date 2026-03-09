import os
from random import choice, randint
import math

from kivy.core.text import LabelBase
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse
from kivy.uix.screenmanager import Screen, SlideTransition, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivy.uix.carousel import Carousel 

# Importações KivyMD
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDIconButton, MDFillRoundFlatButton, MDRectangleFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.slider import MDSlider

# ================= REGISTRO DE FONTE =================
try:
    font_path = os.path.join(os.path.dirname(__file__), "Fontes", "Duo-Dunkel.ttf")
except NameError:
    font_path = os.path.join(os.getcwd(), "Fontes", "Duo-Dunkel.ttf")

NOME_FONTE_TITULO = "Roboto" 

if os.path.exists(font_path):
    NOME_FONTE_TITULO = "BungeeShade"


# ================= CORES PADRONIZADAS =================
COR_AZUL = (0.2, 0.6, 1, 1)
COR_ROXA = (0.6, 0.4, 0.9, 1)
COR_LARANJA = (1, 0.6, 0.2, 1)
COR_VERDE = (0.3, 0.7, 0.4, 1)
COR_ROSA = (1, 0.3, 0.5, 1)
PRETO = (0, 0, 0, 1)
CINZA_TEXTO = (0.2, 0.2, 0.2, 1) # Texto mais suave para leitura
BRANCO_OFF = (0.98, 0.98, 0.98, 1)


# =================================================================================
# FUNÇÃO AUXILIAR PADRONIZADA (IGUAL À DE ÁLGEBRA)
# =================================================================================
def criar_card_definicao(titulo, texto, icone, cor_icone):
    """
    Cria um card com design padronizado: Ícone em círculo colorido + Título + Texto formatado.
    """
    card = MDCard(
        orientation="vertical",
        padding=dp(20),
        spacing=dp(15),
        radius=[20],
        elevation=3,
        size_hint_y=None,
        adaptive_height=True,
        md_bg_color=BRANCO_OFF 
    )

    # Cabeçalho do Card (Ícone Colorido + Título)
    header_box = MDBoxLayout(
        orientation="horizontal",
        spacing=dp(15),
        adaptive_height=True,
        size_hint_y=None
    )

    # Container do ícone (Círculo colorido)
    icon_container = MDBoxLayout(
        size_hint=(None, None),
        size=(dp(42), dp(42)),
        md_bg_color=cor_icone,
        radius=[dp(21)],
        padding=dp(0),
    )

    # Ícone Centralizado
    icon_btn = MDIconButton(
        icon=icone,
        theme_text_color="Custom",
        text_color=(1, 1, 1, 1),
        icon_size=dp(22),
        size_hint=(1, 1), 
        pos_hint={"center_x": 0.5, "center_y": 0.5},
        disabled=True 
    )
    icon_container.add_widget(icon_btn)
    
    # Título
    lbl_titulo = MDLabel(
        text=titulo,
        font_style="Subtitle1",
        bold=True,
        theme_text_color="Custom", 
        text_color=PRETO, 
        valign="center",
        adaptive_height=True,
        pos_hint={"center_y": 0.5}
    )

    header_box.add_widget(icon_container)
    header_box.add_widget(lbl_titulo)

    # Corpo do Texto
    lbl_texto = MDLabel(
        text=texto,
        font_style="Body1",
        theme_text_color="Custom",
        text_color=CINZA_TEXTO,
        adaptive_height=True,
        markup=True
    )

    card.add_widget(header_box)
    card.add_widget(lbl_texto)
    return card


# =================================================================================
# COMPONENTE DE GRÁFICO NATIVO (MANTIDO)
# =================================================================================
class GraficoNativo(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.atualizar_canvas, size=self.atualizar_canvas)
        self.dados_funcao = {"tipo": "1grau", "a": 1, "b": 0, "c": 0, "extras": []}

    def definir_dados(self, tipo, a, b, c, extras):
        self.dados_funcao = {"tipo": tipo, "a": a, "b": b, "c": c, "extras": extras}
        self.atualizar_canvas()

    def atualizar_canvas(self, *args):
        self.canvas.clear()
        
        cx, cy = self.center_x, self.center_y
        w, h = self.width, self.height
        escala = dp(20) 

        with self.canvas:
            Color(0, 0, 0, 1) 
            Line(points=[self.x, cy, self.right, cy], width=1.2)
            Line(points=[cx, self.y, cx, self.top], width=1.2)

            Color(0.2, 0.4, 0.8, 1) 
            pontos = []
            
            passo = 0.2 
            inicio_x = - (w / 2) / escala
            fim_x = (w / 2) / escala
            
            x_calc = inicio_x
            while x_calc <= fim_x:
                try:
                    if self.dados_funcao["tipo"] == "1grau":
                        y_calc = self.dados_funcao["a"] * x_calc + self.dados_funcao["b"]
                    else:
                        y_calc = (self.dados_funcao["a"] * (x_calc**2)) + (self.dados_funcao["b"] * x_calc) + self.dados_funcao["c"]
                    
                    px = cx + (x_calc * escala)
                    py = cy + (y_calc * escala)
                    
                    if self.y - 100 <= py <= self.top + 100:
                        pontos.extend([px, py])
                except:
                    pass
                x_calc += passo

            if len(pontos) > 2:
                Line(points=pontos, width=2)

            a = self.dados_funcao["a"]
            b = self.dados_funcao["b"]
            c = self.dados_funcao["c"]
            extras = self.dados_funcao["extras"]

            if "inter" in extras:
                val_y = b if self.dados_funcao["tipo"] == "1grau" else c
                py = cy + (val_y * escala)
                Color(1, 0, 1, 1) 
                Ellipse(pos=(cx - dp(4), py - dp(4)), size=(dp(8), dp(8)))

            if "raizes" in extras and a != 0:
                Color(1, 0, 0, 1) 
                if self.dados_funcao["tipo"] == "1grau":
                    root = -b/a
                    px = cx + (root * escala)
                    Ellipse(pos=(px - dp(4), cy - dp(4)), size=(dp(8), dp(8)))
                else: 
                    delta = b**2 - 4*a*c
                    if delta >= 0:
                        x1 = (-b + math.sqrt(delta))/(2*a)
                        x2 = (-b - math.sqrt(delta))/(2*a)
                        px1 = cx + (x1 * escala)
                        px2 = cx + (x2 * escala)
                        Ellipse(pos=(px1 - dp(4), cy - dp(4)), size=(dp(8), dp(8)))
                        Ellipse(pos=(px2 - dp(4), cy - dp(4)), size=(dp(8), dp(8)))

            if "vertice" in extras and self.dados_funcao["tipo"] == "2grau" and a != 0:
                xv = -b/(2*a)
                delta = b**2 - 4*a*c
                yv = -delta/(4*a)
                px = cx + (xv * escala)
                py = cy + (yv * escala)
                Color(0, 0.8, 0, 1) 
                Ellipse(pos=(px - dp(4), py - dp(4)), size=(dp(8), dp(8)))


# =================== TELA 1: MENU OPERAÇÕES (MeiaTela) ===================
class MeiaTela(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # Fundo
        try:
            fundo = Image(source="fundoapp.png", allow_stretch=True, keep_ratio=False, size_hint=(1, 1))
            layout.add_widget(fundo)
        except:
            pass

        self.adicionar_decoracao_fundo(layout)

        try:
            self.title_image = Image(source="Bonecos/titulo_operacoes.webp", size_hint=(None, None), height=dp(80), width=dp(300), allow_stretch=True, keep_ratio=True, pos_hint={"center_x": 0.5, "top": 0.96})
            layout.add_widget(self.title_image)
            
            boneco = Image(source="Bonecos/boneco_operacao.webp", size_hint=(0.45, 0.50), pos_hint={"center_x": 0.5, "center_y": 0.70})
            layout.add_widget(boneco)
        except:
            pass

        # Botão Voltar
        layout.add_widget(MDIconButton(
            icon="arrow-left", 
            theme_text_color="Custom", 
            text_color=(0, 0, 0, 1), 
            pos_hint={"x": 0.02, "top": 0.98}, 
            on_release=lambda x: self.voltar("conteudos")
        ))

        # Card Principal do Menu
        card_principal = MDCard(
            size_hint=(0.9, 0.40), 
            pos_hint={"center_x": 0.5, "y": 0.12}, 
            md_bg_color=(1, 1, 1, 0.3), 
            radius=[25], 
            elevation=0, 
            line_color=(0, 0, 0, 0.1), 
            line_width=1
        )
        
        container = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))

        container.add_widget(MDLabel(
            text="Escolha a atividade:", 
            halign="center", 
            theme_text_color="Custom", 
            text_color=(0, 0, 0, 1), 
            font_style="Subtitle1", 
            bold=True, 
            size_hint_y=None, 
            height=dp(30)
        ))
        
        container.add_widget(self.create_icon_button("Representações", "image-outline", "representacoes"))
        container.add_widget(self.create_icon_button("Definições", "book-open-variant", "definicoes"))
        container.add_widget(self.create_icon_button("Jogar", "gamepad-variant", "jogar"))

        card_principal.add_widget(container)
        layout.add_widget(card_principal)
        self.add_widget(layout)

    def adicionar_decoracao_fundo(self, layout):
        icones = ["plus", "minus", "division", "percent", "calculator", "function"]
        positions = [{"x": 0.05, "y": 0.85}, {"x": 0.85, "y": 0.9}, {"x": 0.1, "y": 0.6}, {"x": 0.85, "y": 0.6}, {"x": 0.05, "y": 0.2}, {"x": 0.9, "y": 0.25}]
        for pos in positions:
            layout.add_widget(MDIconButton(icon=choice(icones), theme_text_color="Custom", text_color=(0, 0, 0, 0.08), pos_hint=pos, icon_size=dp(45), disabled=True))

    def create_icon_button(self, text, icon, screen_name):
        card = MDCard(size_hint=(1, None), height=dp(50), md_bg_color=(0.15, 0.25, 0.75, 0.9), radius=[15], elevation=3, ripple_behavior=True, padding=[dp(15), 0, dp(10), 0])
        row = BoxLayout(orientation="horizontal", spacing=dp(15))
        row.add_widget(MDIconButton(icon=icon, theme_text_color="Custom", text_color=(1, 1, 1, 1), size_hint=(None, None), size=(dp(24), dp(24)), pos_hint={'center_y': 0.5}, disabled=True))
        row.add_widget(MDLabel(text=text, halign="left", valign="center", theme_text_color="Custom", text_color=(1, 1, 1, 1), bold=True))
        row.add_widget(MDIconButton(icon="chevron-right", theme_text_color="Custom", text_color=(1, 1, 1, 0.7), size_hint=(None, None), size=(dp(24), dp(24)), pos_hint={'center_y': 0.5}, disabled=True))
        card.add_widget(row)
        card.on_release = lambda *a: self.ir_para(screen_name)
        return card

    def ir_para(self, screen_name):
        if self.manager:
            self.manager.transition = SlideTransition(direction="left", duration=0.4)
            self.manager.current = screen_name

    def voltar(self, screen_name):
        if self.manager:
            self.manager.current = screen_name


# =================== TELA 2: SIMULADOR (TelaRepresentacoes) ===================
class TelaRepresentacoes(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        
        try:
            fundo = Image(source="fundoapp.png", allow_stretch=True, keep_ratio=False, size_hint=(1, 1))
            layout.add_widget(fundo)
        except:
            pass

        self.adicionar_decoracao_fundo(layout)

        # Header
        layout.add_widget(MDIconButton(
            icon="arrow-left", pos_hint={"x": 0.02, "top": 0.98}, 
            theme_text_color="Custom", text_color=(0, 0, 0, 1), 
            on_release=self.voltar
        ))
        
        layout.add_widget(Label(
            text="SIMULADOR", 
            color=(0, 0, 0, 1), 
            font_name=NOME_FONTE_TITULO, 
            font_size="28sp", 
            size_hint=(1, None), 
            height=dp(60), 
            pos_hint={"center_x": 0.5, "top": 0.96}
        ))

        # Card de Resultado
        card_resultado = MDCard(
            size_hint=(0.85, 0.25), 
            pos_hint={"center_x": 0.5, "top": 0.82}, 
            md_bg_color=(1, 1, 1, 0.9), 
            radius=[20], 
            elevation=4, 
            orientation="vertical", 
            padding=dp(10)
        )
        self.conta_label = MDLabel(text="5 + 5 = 10", halign="center", valign="center", theme_text_color="Custom", text_color=(0, 0, 0, 1), font_style="H4", bold=True)
        self.info_label = MDLabel(text="Parcela + Parcela = Soma", halign="center", theme_text_color="Custom", text_color=(0.5, 0.5, 0.5, 1), font_style="Subtitle1")
        card_resultado.add_widget(self.conta_label)
        card_resultado.add_widget(self.info_label)
        layout.add_widget(card_resultado)

        # Sliders
        sliders_box = BoxLayout(orientation="vertical", size_hint=(0.8, 0.35), pos_hint={"center_x": 0.5, "y": 0.22}, spacing=dp(10))
        
        self.label_s1 = MDLabel(text="Valor 1: 5", halign="center", bold=True, theme_text_color="Custom", text_color=(0, 0, 0, 1))
        sliders_box.add_widget(self.label_s1)
        self.slider1 = MDSlider(min=1, max=20, value=5, step=1, color=(0.2, 0.4, 0.8, 1))
        self.slider1.bind(value=self.atualizar_calculo)
        sliders_box.add_widget(self.slider1)

        self.label_s2 = MDLabel(text="Valor 2: 5", halign="center", bold=True, theme_text_color="Custom", text_color=(0, 0, 0, 1))
        sliders_box.add_widget(self.label_s2)
        self.slider2 = MDSlider(min=1, max=20, value=5, step=1, color=(0.2, 0.4, 0.8, 1))
        self.slider2.bind(value=self.atualizar_calculo)
        sliders_box.add_widget(self.slider2)
        layout.add_widget(sliders_box)

        # Botões de Operação
        ops_box = BoxLayout(orientation="horizontal", size_hint=(0.9, 0.12), pos_hint={"center_x": 0.5, "y": 0.05}, spacing=dp(15), padding=dp(5))
        self.botoes_op = {}
        operacoes = [("+", "plus", "soma"), ("-", "minus", "subtracao"), ("×", "close", "multiplicacao"), ("÷", "division", "divisao")]
        for simbolo, icone, id_op in operacoes:
            btn = MDIconButton(icon=icone, theme_text_color="Custom", text_color=(1, 1, 1, 1), md_bg_color=(0.2, 0.4, 0.9, 1), icon_size="32sp", size_hint=(None, None), size=(dp(56), dp(56)), pos_hint={"center_y": 0.5})
            btn.bind(on_release=lambda x, op=id_op: self.mudar_operacao(op))
            ops_box.add_widget(btn)
            self.botoes_op[id_op] = btn
        layout.add_widget(ops_box)
        self.add_widget(layout)

        self.op_atual = "soma"
        self.atualizar_visual_botoes()
        self.atualizar_calculo()

    def adicionar_decoracao_fundo(self, layout):
        icones = ["calculator", "plus", "minus", "percent"]; positions = [{"x": 0.05, "y": 0.85}, {"x": 0.85, "y": 0.9}, {"x": 0.1, "y": 0.15}, {"x": 0.9, "y": 0.2}]
        for pos in positions: layout.add_widget(MDIconButton(icon=choice(icones), theme_text_color="Custom", text_color=(0, 0, 0, 0.05), pos_hint=pos, icon_size=dp(50), disabled=True))

    def mudar_operacao(self, nova_op): self.op_atual = nova_op; self.atualizar_visual_botoes(); self.atualizar_calculo()
    def atualizar_visual_botoes(self):
        for op, btn in self.botoes_op.items(): btn.md_bg_color = (1, 0.5, 0, 1) if op == self.op_atual else (0.2, 0.4, 0.9, 1)

    def atualizar_calculo(self, *args):
        val1 = int(self.slider1.value); val2 = int(self.slider2.value)
        if self.op_atual == "soma":
            self.label_s1.text = f"Parcela 1: {val1}"; self.label_s2.text = f"Parcela 2: {val2}"; res = val1 + val2; self.conta_label.text = f"{val1} + {val2} = {res}"; self.info_label.text = "Soma (Total)"
        elif self.op_atual == "subtracao":
            self.label_s1.text = f"Minuendo: {val1}"; self.label_s2.text = f"Subtraendo: {val2}"; res = val1 - val2; self.conta_label.text = f"{val1} - {val2} = {res}"; self.info_label.text = "Resultado Negativo" if res < 0 else "Diferença"
        elif self.op_atual == "multiplicacao":
            self.label_s1.text = f"Fator 1: {val1}"; self.label_s2.text = f"Fator 2: {val2}"; res = val1 * val2; self.conta_label.text = f"{val1} × {val2} = {res}"; self.info_label.text = "Produto"
        elif self.op_atual == "divisao":
            divisor = val2 if val2 > 0 else 1; dividendo = val1; self.label_s1.text = f"Dividendo: {dividendo}"; self.label_s2.text = f"Divisor: {divisor}"; res = dividendo / divisor; res_formatado = f"{int(res)}" if res.is_integer() else f"{res:.2f}".replace('.', ','); self.conta_label.text = f"{dividendo} ÷ {divisor} = {res_formatado}"; self.info_label.text = "Quociente (Decimal)"

    def voltar(self, *args):
        if self.manager:
            self.manager.transition = SlideTransition(direction="right", duration=0.4)
            self.manager.current = "tela"


# =================== TELA 3: DEFINIÇÕES DE OPERAÇÕES (PADRONIZADA) ===================
class OperacoesDefinicoesTela(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # 1. Estrutura Base
        layout = FloatLayout()
        
        try:
            fundo = Image(source="fundoapp.png", allow_stretch=True, keep_ratio=False, size_hint=(1, 1))
            layout.add_widget(fundo)
        except:
            pass

        # 2. Cabeçalho
        header = MDBoxLayout(
            orientation="horizontal", 
            size_hint=(1, None), 
            height=dp(60), 
            spacing=dp(10), 
            padding=[dp(10), 0, dp(10), 0], 
            pos_hint={"top": 1}
        )
        
        btn_voltar = MDIconButton(
            icon="arrow-left", 
            theme_text_color="Custom", 
            text_color=PRETO, 
            on_release=self.voltar, 
            pos_hint={'center_y': 0.5}
        )
        
        lbl_titulo = MDLabel(
            text="Definições Básicas", 
            font_style="H5", 
            bold=True, 
            theme_text_color="Custom", 
            text_color=PRETO, 
            halign="left", 
            valign="center", 
            pos_hint={'center_y': 0.5}
        )
        
        header.add_widget(btn_voltar)
        header.add_widget(lbl_titulo)
        layout.add_widget(header)

        # 3. Área de Scroll
        scroll = ScrollView(
            size_hint=(1, 0.88), 
            pos_hint={"top": 0.9, "center_x": 0.5}, 
            do_scroll_x=False, 
            bar_width=0
        )
        
        self.container_conteudo = MDBoxLayout(
            orientation="vertical", 
            padding=[dp(20), dp(10), dp(20), dp(40)], 
            spacing=dp(20), 
            size_hint_y=None, 
            adaptive_height=True
        )

        # === ADIÇÃO ===
        self.container_conteudo.add_widget(criar_card_definicao(
            titulo="Adição (+)", 
            texto=(
                "[b]Conceito:[/b] Agrupar duas ou mais quantidades.\n\n"
                "[b]Termos:[/b]\n"
                "   12  (Parcela)\n"
                " + 34  (Parcela)\n"
                "  -----\n"
                "   46  (Soma ou Total)\n\n"
                "[b]Propriedades:[/b]\n"
                "• [i]Comutativa:[/i] A ordem não altera a soma.\n"
                "   2 + 3 = 3 + 2\n"
                "• [i]Neutro:[/i] O zero não altera o valor.\n"
                "   5 + 0 = 5"
            ), 
            icone="plus", 
            cor_icone=COR_AZUL
        ))
        
        # === SUBTRAÇÃO ===
        self.container_conteudo.add_widget(criar_card_definicao(
            titulo="Subtração (-)", 
            texto=(
                "[b]Conceito:[/b] Tirar uma quantidade de outra para ver a diferença.\n\n"
                "[b]Termos:[/b]\n"
                "   50  (Minuendo)\n"
                " - 20  (Subtraendo)\n"
                "  -----\n"
                "   30  (Resto ou Diferença)\n\n"
                "[b]Dica:[/b] É o inverso da adição.\n"
                "Resto + Subtraendo = Minuendo"
            ), 
            icone="minus", 
            cor_icone=COR_LARANJA
        ))

        # === MULTIPLICAÇÃO ===
        self.container_conteudo.add_widget(criar_card_definicao(
            titulo="Multiplicação (×)", 
            texto=(
                "[b]Conceito:[/b] Forma rápida de somar várias vezes o mesmo número.\n"
                "Ex: 4 + 4 + 4 = 3 x 4\n\n"
                "[b]Termos:[/b]\n"
                "    5   (Fator)\n"
                "  x 6   (Fator)\n"
                "  -----\n"
                "   30   (Produto)\n\n"
                "[b]Regras:[/b]\n"
                "• Multiplicar por 0 dá sempre 0.\n"
                "• Multiplicar por 1 mantém o valor."
            ), 
            icone="close", 
            cor_icone=COR_ROXA
        ))

        # === DIVISÃO ===
        self.container_conteudo.add_widget(criar_card_definicao(
            titulo="Divisão (÷)", 
            texto=(
                "[b]Conceito:[/b] Repartir uma quantidade em partes iguais.\n\n"
                "[b]Estrutura:[/b]\n"
                "  20  (Dividendo) ÷ 4 (Divisor)\n"
                "   = 5 (Quociente)\n\n"
                "[b]Exemplo:[/b] 20 balas para 4 pessoas dá 5 para cada.\n\n"
                "[b]Atenção:[/b] Jamais dividirás por Zero!"
            ), 
            icone="division", 
            cor_icone=COR_VERDE
        ))
        
        scroll.add_widget(self.container_conteudo)
        layout.add_widget(scroll)
        self.add_widget(layout)

    def voltar(self, instance):
        if self.manager:
            self.manager.transition = SlideTransition(direction="right", duration=0.4)
            self.manager.current = "tela"
