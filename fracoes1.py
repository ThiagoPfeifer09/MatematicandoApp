from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.properties import NumericProperty
from kivy.metrics import dp
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.slider import MDSlider
from kivy.uix.image import Image
import math
from kivy.graphics import Color, Rectangle, Line, Ellipse, Triangle

# =============================================================================
# MIXIN DE TEMA (Fundo)
# =============================================================================
class ThemeManagerMixin:
    def setup_background_and_theme_button(self, layout):
        try:
            self.bg_image = Image(
                source='fundoapp.png',
                allow_stretch=True,
                keep_ratio=False,
                size_hint=(1, 1),
                pos_hint={'x': 0, 'y': 0},
                fit_mode='fill'
            )
            layout.add_widget(self.bg_image, index=len(layout.children))
        except:
            pass # Se não tiver imagem, fica fundo padrão

# =============================================================================
# TELA 1: PROPRIEDADES E DEFINIÇÕES
# =============================================================================
class TelaFracoesPropriedades(Screen, ThemeManagerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = FloatLayout()
        self.setup_background_and_theme_button(main_layout)

        content_box = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15),
                                size_hint=(0.95, 0.92), pos_hint={'center_x': 0.5, 'center_y': 0.46})

        content_box.add_widget(
            MDLabel(
                text=" DEFINIÇÕES: A ESTRUTURA DA FRAÇÃO",
                halign="center",
                font_style="H5",
                size_hint_y=None,
                height=dp(30),
                theme_text_color="Custom",
                text_color=(1, 0.95, 0.8, 1)
            )
        )

        card_terminologia = MDCard(
            orientation='vertical',
            size_hint_y=0.35,
            padding=dp(20),
            spacing=dp(15),
            md_bg_color=(1, 1, 1, 0.95),
            radius=[15],
            elevation=10,
        )

        card_terminologia.add_widget(
            MDLabel(
                text="[b]PARTES FUNDAMENTAIS[/b]: NUMERADOR E DENOMINADOR",
                halign="center",
                font_style="Subtitle1",
                markup=True,
                theme_text_color="Custom",
                text_color=(0.1, 0.1, 0.1, 1)
            )
        )

        self.terminologia_display = InteractiveFractionDisplay(
            numerator=1, denominator=3, size_hint_y=0.4
        )
        card_terminologia.add_widget(self.terminologia_display)

        card_terminologia.add_widget(
            MDLabel(
                text="O [color=ff3333][b]NUMERADOR[/b][/color] (topo) é quantas partes tomamos. O [color=0099ff][b]DENOMINADOR[/b][/color] (base) é em quantas partes [b]iguais[/b] o TODO foi dividido.",
                halign='center',
                font_style='Body2',
                markup=True,
                size_hint_y=0.4,
                theme_text_color="Custom",
                text_color=(0.1, 0.1, 0.1, 1)
            )
        )
        content_box.add_widget(card_terminologia)

        card_tipos = MDCard(
            orientation='vertical',
            size_hint_y=0.55,
            padding=dp(20),
            spacing=dp(15),
            md_bg_color=(0, 0, 0, 0.75),
            radius=[15],
            elevation=12,
        )

        card_tipos.add_widget(
            MDLabel(
                text="[b]TIPOS DE FRAÇÕES[/b]: PRÓPRIAS E IMPRÓPRIAS",
                halign="center",
                font_style="H6",
                markup=True,
                theme_text_color="Custom",
                text_color=(1, 0.95, 0.8, 1)
            )
        )

        self.multi_bar_display = MultiBarFractionDisplay(size_hint_y=0.4)
        card_tipos.add_widget(self.multi_bar_display)

        self.fraction_label_tipos = MDLabel(
            text="[color=ff3333][b]1[/b][/color] / [color=0099ff][b]2[/b][/color] - PRÓPRIA",
            halign='center',
            font_style='H6',
            markup=True,
            size_hint_y=None,
            height=dp(30),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
        card_tipos.add_widget(self.fraction_label_tipos)

        control_sliders_container = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(70), spacing=dp(20))

        denom_vert_box = BoxLayout(orientation='vertical', size_hint_x=0.5, padding=(dp(5), 0))
        denom_vert_box.add_widget(MDLabel(text="DENOMINADOR:", theme_text_color="Custom", text_color=(1, 1, 1, 1), halign='center', size_hint_y=None, height=dp(20)))

        self.denominator_slider = MDSlider(min=2, max=6, step=1, value=3, color=[1, 0.8, 0, 1])

        denom_vert_box.add_widget(self.denominator_slider)
        control_sliders_container.add_widget(denom_vert_box)

        num_vert_box = BoxLayout(orientation='vertical', size_hint_x=0.5, padding=(dp(5), 0))
        num_vert_box.add_widget(MDLabel(text="NUMERADOR:", theme_text_color="Custom", text_color=(1, 1, 1, 1), halign='center', size_hint_y=None, height=dp(20)))

        self.numerator_slider = MDSlider(min=0, max=6, step=1, value=1, color=[1, 0.8, 0, 1])

        num_vert_box.add_widget(self.numerator_slider)
        control_sliders_container.add_widget(num_vert_box)

        card_tipos.add_widget(control_sliders_container)
        content_box.add_widget(card_tipos)

        main_layout.add_widget(content_box)

        back_button = MDIconButton(
            icon='arrow-left',
            pos_hint={'x': 0, 'top': 1},
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            on_release=self.voltar_para_informacoes,
            font_size="40sp"
        )
        main_layout.add_widget(back_button)

        self.denominator_slider.bind(value=self.update_fraction_values)
        self.numerator_slider.bind(value=self.update_fraction_values)
        self.update_fraction_values(None, None)

        self.add_widget(main_layout)

    def update_fraction_values(self, instance, value):
        denom_val = int(self.denominator_slider.value)
        num_val = int(self.numerator_slider.value)

        self.numerator_slider.max = max(denom_val * 3, 6)

        self.terminologia_display.denominator = denom_val
        self.terminologia_display.numerator = min(num_val, denom_val)

        self.multi_bar_display.denominator = denom_val
        self.multi_bar_display.numerator = num_val

        tipo_texto = ""
        misto_text = ""

        if num_val < denom_val:
            tipo_texto = "PRÓPRIA (Valor < 1)"
            tipo_cor = "00ff00"
        elif num_val == denom_val or (denom_val != 0 and num_val % denom_val == 0):
            tipo_texto = "APARENTE (Valor = Inteiro)"
            tipo_cor = "00ffff"
            misto_text = f" (= {num_val // denom_val})"
        else:
            tipo_texto = "IMPRÓPRIA (Valor > 1)"
            tipo_cor = "ff3333"
            inteiro = num_val // denom_val
            resto = num_val % denom_val
            misto_text = f" ({inteiro} e {resto}/{denom_val})"


        self.fraction_label_tipos.text = (
            f"[color=ff3333][b]{num_val}[/b][/color] / [color=0099ff][b]{denom_val}[/b][/color] "
            f"[color={tipo_cor}]{tipo_texto}{misto_text}[/color]"
        )

    def voltar_para_informacoes(self, instance):
        self.manager.transition = SlideTransition(direction="right", duration=0.4)
        self.manager.current = "fracoes_info"

# =============================================================================
# TELA 2: REPRESENTAÇÕES VISUAIS
# =============================================================================
class TelaFracoesRepresentacoes(Screen, ThemeManagerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = FloatLayout()
        self.setup_background_and_theme_button(main_layout)

        main_layout.add_widget(
            MDLabel(
                text="2. REPRESENTAÇÕES: Barra, Pizza e Conjunto",
                halign="center",
                font_style="H5",
                pos_hint={"center_x": 0.5, "top": 0.95},
                theme_text_color="Custom",
                text_color=(1, 0.95, 0.8, 1)
            )
        )

        content_box = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10),
                                size_hint=(0.95, 0.85), pos_hint={'center_x': 0.5, 'center_y': 0.45})

        viz_card = MDCard(
            orientation='vertical',
            size_hint_y=0.65,
            padding=dp(15),
            spacing=dp(10),
            md_bg_color=(1, 1, 1, 0.95),
            radius=[15],
            elevation=10,
        )

        viz_card.add_widget(MDLabel(text="EM BARRA (LINEAR)", halign="center", font_style="Body2", size_hint_y=None, height=dp(20), theme_text_color="Primary"))
        self.bar_display = InteractiveFractionDisplay(size_hint_y=0.2)
        viz_card.add_widget(self.bar_display)

        viz_card.add_widget(MDLabel(text="EM PIZZA (CIRCULAR)", halign="center", font_style="Body2", size_hint_y=None, height=dp(20), theme_text_color="Primary"))
        self.circle_display = CircularFractionDisplay(size_hint_y=0.4)
        viz_card.add_widget(self.circle_display)

        viz_card.add_widget(MDLabel(text="EM CONJUNTO DE OBJETOS", halign="center", font_style="Body2", size_hint_y=None, height=dp(20), theme_text_color="Primary"))
        self.set_display = SetFractionDisplay(size_hint_y=0.4)
        viz_card.add_widget(self.set_display)

        content_box.add_widget(viz_card)

        control_card = MDCard(
            orientation='vertical',
            size_hint_y=0.3,
            padding=dp(15),
            spacing=dp(10),
            md_bg_color=(0, 0, 0, 0.75),
            radius=[15],
            elevation=12,
        )

        self.fraction_label = MDLabel(
            text="[color=ff3333][b]1[/b][/color] / [color=0099ff][b]4[/b][/color]",
            halign='center',
            font_style='H6',
            markup=True,
            size_hint_y=None,
            height=dp(40),
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1)
        )
        control_card.add_widget(self.fraction_label)

        denom_box = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(10))
        denom_box.add_widget(MDLabel(text="PARTES TOTAIS (DENOMINADOR):", theme_text_color="Custom", text_color=(1, 1, 1, 1), size_hint_x=0.4))
        self.denominator_slider = MDSlider(min=2, max=8, step=1, value=4, color=[0.2, 0.6, 1, 1])
        denom_box.add_widget(self.denominator_slider)
        control_card.add_widget(denom_box)

        num_box = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(10))
        num_box.add_widget(MDLabel(text="PARTES SELECIONADAS (NUMERADOR):", theme_text_color="Custom", text_color=(1, 1, 1, 1), size_hint_x=0.4))
        self.numerator_slider = MDSlider(min=0, max=4, step=1, value=1, color=[1, 0.4, 0.4, 1])
        num_box.add_widget(self.numerator_slider)
        control_card.add_widget(num_box)

        content_box.add_widget(control_card)

        main_layout.add_widget(content_box)

        back_button = MDIconButton(
            icon='arrow-left',
            pos_hint={'x': 0, 'top': 1},
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            on_release=self.voltar_para_informacoes,
            font_size="40sp"
        )
        main_layout.add_widget(back_button)

        self.denominator_slider.bind(value=self.update_fraction_values)
        self.numerator_slider.bind(value=self.update_fraction_values)
        self.update_fraction_values(None, None)

        self.add_widget(main_layout)

    def update_fraction_values(self, instance, value):
        new_max = int(self.denominator_slider.value)

        self.numerator_slider.max = new_max
        if self.numerator_slider.value > new_max:
            self.numerator_slider.value = new_max

        num_val = int(self.numerator_slider.value)
        denom_val = new_max

        self.fraction_label.text = f"[color=ff3333][b]{num_val}[/b][/color] / [color=0099ff][b]{denom_val}[/b][/color]"

        self.bar_display.denominator = denom_val
        self.bar_display.numerator = num_val

        self.circle_display.denominator = denom_val
        self.circle_display.numerator = num_val

        self.set_display.denominator = denom_val
        self.set_display.numerator = num_val


    def voltar_para_informacoes(self, instance):
        self.manager.transition = SlideTransition(direction="right", duration=0.4)
        self.manager.current = "fracoes_info"

# =============================================================================
# TELA 3: EXPLICAÇÕES DETALHADAS
# =============================================================================
class TelaFracoesExplicacoes(Screen, ThemeManagerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        main_layout = FloatLayout()
        self.setup_background_and_theme_button(main_layout)

        back_button = MDIconButton(
            icon='arrow-left',
            pos_hint={'x': 0, 'top': 1},
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            on_release=self.voltar_para_informacoes,
            font_size="40sp"
        )
        main_layout.add_widget(back_button)

        main_layout.add_widget(
            MDLabel(
                text="3. EXPLICAÇÕES: O Mundo das Frações",
                halign="center",
                font_style="H5",
                pos_hint={"center_x": 0.5, "top": 0.95},
                theme_text_color="Custom",
                text_color=(1, 0.95, 0.8, 1)
            )
        )

        content_card = MDCard(
            orientation='vertical',
            size_hint=(0.95, 0.82),
            pos_hint={'center_x': 0.5, 'center_y': 0.45},
            padding=dp(15),
            spacing=dp(10),
            md_bg_color=(1, 1, 1, 0.98),
            radius=[15],
            elevation=12,
        )

        scroll_view = ScrollView()
        content_box = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(5), size_hint_y=None)
        content_box.bind(minimum_height=content_box.setter('height'))

        content_box.add_widget(self._create_section_title("Conceito Fundamental", color=(0.8, 0.2, 0.2, 1)))
        content_box.add_widget(self._create_content_label(
            "[b]O que é?[/b] É a parte de um todo dividido em [color=ff3333]partes iguais[/color]. "
            "Representa a divisão de um Numerador (a) pelo Denominador (b)."
        ))

        content_box.add_widget(self._create_subsection_title("Partes da Fração (a/b)", color=(0.1, 0.5, 0.8, 1)))

        content_box.add_widget(self._create_content_label(
            "   [b][color=ff3333]NUMERADOR (a)[/color][/b]: As partes [b]selecionadas/tomadas[/b]."
        ))
        content_box.add_widget(self._create_content_label(
            "   [b][color=0099ff]DENOMINADOR (b)[/color][/b]: O [b]total de partes iguais[/b] em que o todo foi dividido."
        ))

        content_box.add_widget(self._create_section_title("Tipos de Frações", color=(0.8, 0.5, 0.1, 1)))

        content_box.add_widget(self._create_content_label(
            "[b]1. PRÓPRIA[/b]: O numerador é menor que o denominador ([b]a < b[/b]). Valor menor que 1. Ex: [b]1/2[/b]"
        ))
        content_box.add_widget(self._create_content_label(
            "[b]2. IMPRÓPRIA[/b]: O numerador é maior que o denominador ([b]a > b[/b]). Valor maior que 1. Ex: [b]5/3[/b]"
        ))
        content_box.add_widget(self._create_content_label(
            "[b]3. APARENTE[/b]: O numerador é múltiplo do denominador ([b]a = n * b[/b]). "
            "Valor igual a um número inteiro. Ex: [b]6/3 = 2[/b]"
        ))

        content_box.add_widget(self._create_section_title("Equivalência e Redução", color=(0.2, 0.6, 0.2, 1)))
        content_box.add_widget(self._create_content_label(
            "[b]EQUIVALENTES[/b]: Representam a mesma quantidade. "
            "Obtidas multiplicando (ampliação) ou dividindo (simplificação) o numerador e o denominador pelo mesmo número. Ex: [b]1/2[/b] = [b]2/4[/b]."
        ))

        content_box.add_widget(self._create_section_title("Números Mistos", color=(0.5, 0.2, 0.8, 1)))
        content_box.add_widget(self._create_content_label(
            "[b]O que são?[/b] Forma de representar frações impróprias, combinando uma [color=552288]parte inteira[/color] e uma [color=552288]parte fracionária[/color].\n"
            "Ex: [b]5/3[/b] (Imprópria) é equivalente a [b]1 e 2/3[/b] (Número Misto)."
        ))

        content_box.add_widget(self._create_section_title("Simplificação (Forma Irredutível)", color=(0.8, 0.5, 0.1, 1)))
        content_box.add_widget(self._create_content_label(
            "[b]Como simplificar?[/b] Dividindo o Numerador e o Denominador pelo [color=cc6600]Máximo Divisor Comum (MDC)[/color] até que não haja mais divisores em comum.\n"
            "Ex: Simplificar [b]6/8[/b] por 2 resulta em [b]3/4[/b] (Forma Irredutível)."
        ))

        content_box.add_widget(self._create_section_title("Visão Geral das Operações", color=(0.2, 0.2, 0.8, 1)))

        content_box.add_widget(self._create_content_label(
            "[b]SOMA / SUBTRAÇÃO:[/b] Só podem ser feitas diretamente se os denominadores forem [color=3333cc]iguais[/color]. Se forem diferentes, use o [color=3333cc]MMC[/color] para encontrar um denominador comum."
        ))
        content_box.add_widget(self._create_content_label(
            "[b]MULTIPLICAÇÃO:[/b] Multiplique [color=3333cc]numerador por numerador[/color] e [color=3333cc]denominador por denominador[/color]. Simplifique o resultado."
        ))
        content_box.add_widget(self._create_content_label(
            "[b]DIVISÃO:[/b] [color=3333cc]Mantenha a primeira fração[/color] e [color=3333cc]multiplique pelo inverso da segunda[/color]. Ex: [b]a/b[/b] dividido por [b]c/d[/b] = [b]a/b * d/c[/b]."
        ))

        content_box.add_widget(FloatLayout(size_hint_y=None, height=dp(20)))

        scroll_view.add_widget(content_box)
        content_card.add_widget(scroll_view)
        main_layout.add_widget(content_card)

        self.add_widget(main_layout)

    def _create_section_title(self, text, color):
        return MDLabel(
            text=f"[b][color={self._rgb_to_hex(color)}]{text.upper()}[/color][/b]",
            halign="left",
            font_style="H5",
            markup=True,
            size_hint_y=None,
            height=dp(35),
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1)
        )

    def _create_subsection_title(self, text, color):
        return MDLabel(
            text=f"[b][color={self._rgb_to_hex(color)}]{text}[/color][/b]",
            halign="left",
            font_style="Subtitle1",
            markup=True,
            size_hint_y=None,
            height=dp(30),
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1)
        )

    def _create_content_label(self, text):
        return MDLabel(
            text=text,
            halign="left",
            font_style="Body2",
            markup=True,
            size_hint_y=None,
            height=dp(80),
            theme_text_color="Custom",
            text_color=(0.1, 0.1, 0.1, 1)
        )

    def _rgb_to_hex(self, rgb):
        r = int(rgb[0] * 255)
        g = int(rgb[1] * 255)
        b = int(rgb[2] * 255)
        return f"{r:02x}{g:02x}{b:02x}"

    def voltar_para_informacoes(self, instance):
        self.manager.transition = SlideTransition(direction="right", duration=0.4)
        self.manager.current = "fracoes_info"

# =============================================================================
# TELA 4: MENU DE FRAÇÕES (INFO E SELEÇÃO)
# =============================================================================
class TelaFracoesInfo(Screen, ThemeManagerMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.dificuldade = "Primario" # Padrão

        layout = FloatLayout()
        self.setup_background_and_theme_button(layout)

        layout.add_widget(
            MDLabel(
                text="FRAÇÕES: INTRODUÇÃO",
                halign="center",
                font_style="H6",
                pos_hint={"center_x": 0.5, "top": 0.92},
                theme_text_color="Custom",
                text_color=(1, 0.95, 0.8, 1)
            )
        )

        button_container = BoxLayout(
            orientation='vertical',
            size_hint=(0.7, 0.5),
            pos_hint={'center_x': 0.5, 'center_y': 0.28},
            spacing='20dp',
            padding='10dp'
        )

        topics = [
            ("Definições", "fracoes_propriedades"),
            ("Representações", "fracoes_representacoes"),
            ("Explicações", "fracoes_explicacoes"),
            ("JOGAR!", "fracoes"),
        ]

        for text, destino in topics:
            btn = MDRaisedButton(
                text=text,
                size_hint_y=None,
                height="80dp",
                # Cor vermelha para o botão de jogar, azul para info
                md_bg_color=(0.1, 0.5, 0.8, 1) if destino != "fracoes" else (0.8, 0.1, 0.2, 1),
                on_release=lambda x, d=destino: self.navegar_para_destino(d),
                font_style="H5"
            )
            button_container.add_widget(btn)

        layout.add_widget(button_container)

        back_button = MDIconButton(
            icon='arrow-left',
            pos_hint={'x': 0, 'top': 1},
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            on_release=self.voltar,
            font_size="40sp"
        )
        layout.add_widget(back_button)

        self.add_widget(layout)

    def definir_dificuldade(self, dificuldade):
        # Chamado pelo main.py para injetar a dificuldade escolhida
        self.dificuldade = dificuldade
        print(f"[TelaFracoesInfo] Dificuldade definida: {self.dificuldade}")

    def navegar_para_destino(self, destino_tela, *args):
        # Se for para o jogo, passa a dificuldade adiante
        if destino_tela == "fracoes":
            try:
                game_screen = self.manager.get_screen("fracoes")
                if hasattr(game_screen, 'definir_dificuldade'):
                    game_screen.definir_dificuldade(self.dificuldade)
            except Exception as e:
                print(f"Erro ao configurar jogo: {e}")

        self.manager.transition = SlideTransition(direction="left", duration=0.4)
        self.manager.current = destino_tela

    def voltar(self, instance):
        self.manager.transition = SlideTransition(direction="right", duration=0.4)
        self.manager.current = "jogar"


# =============================================================================
# WIDGETS GRÁFICOS PERSONALIZADOS (EDUCATIVOS)
# =============================================================================
class InteractiveFractionDisplay(Widget):
    numerator = NumericProperty(1)
    denominator = NumericProperty(4)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(numerator=self.update_canvas, denominator=self.update_canvas, size=self.update_canvas, pos=self.update_canvas)
        self.update_canvas()

    def update_canvas(self, *args):
        if self.denominator < 2: self.denominator = 2
        if self.numerator > self.denominator: self.numerator = self.denominator
        if self.numerator < 0: self.numerator = 0
        N = int(self.numerator)
        D = int(self.denominator)
        self.canvas.clear()
        bar_margin = self.width * 0.1
        bar_height = self.height * 0.4
        bar_x = self.x + bar_margin
        bar_y = self.center_y - (bar_height / 2)
        bar_width = self.width - (2 * bar_margin)
        piece_width = bar_width / D
        with self.canvas:
            Color(0.8, 0.8, 0.8, 1)
            Rectangle(pos=(bar_x, bar_y), size=(bar_width, bar_height))
            Color(1, 0.2, 0.2, 1)
            Rectangle(pos=(bar_x, bar_y), size=(piece_width * N, bar_height))
            Color(0, 0, 0, 1)
            Line(rectangle=(bar_x, bar_y, bar_width, bar_height), width=dp(2))
            for i in range(1, D):
                x_pos = bar_x + (i * piece_width)
                Line(points=[x_pos, bar_y, x_pos, bar_y + bar_height], width=dp(1.5))

class MultiBarFractionDisplay(Widget):
    numerator = NumericProperty(1)
    denominator = NumericProperty(2)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(numerator=self.update_canvas, denominator=self.update_canvas, size=self.update_canvas, pos=self.update_canvas)
        self.update_canvas()

    def update_canvas(self, *args):
        if self.denominator < 1: self.denominator = 1
        if self.numerator < 0: self.numerator = 0
        N = int(self.numerator)
        D = int(self.denominator)
        if D == 0: return
        self.canvas.clear()
        num_bars = math.ceil(N / D) if N > 0 else 1
        total_bar_height = self.height * 0.25
        bar_margin_x = self.width * 0.05
        bar_padding_y = self.height * 0.05
        bar_width = self.width - (2 * bar_margin_x)
        piece_width = bar_width / D
        bar_x = self.x + bar_margin_x
        with self.canvas:
            for bar_index in range(num_bars):
                bar_y = self.y + self.height - total_bar_height - (bar_index * (total_bar_height + bar_padding_y))
                drawn_parts = bar_index * D
                parts_in_bar = min(N - drawn_parts, D)
                Color(0.8, 0.8, 0.8, 1)
                Rectangle(pos=(bar_x, bar_y), size=(bar_width, total_bar_height))
                if parts_in_bar > 0:
                    Color(1, 0.2, 0.2, 1)
                    Rectangle(pos=(bar_x, bar_y), size=(piece_width * parts_in_bar, total_bar_height))
                Color(0, 0, 0, 1)
                Line(rectangle=(bar_x, bar_y, bar_width, total_bar_height), width=dp(2))
                for i in range(1, D):
                    x_pos = bar_x + (i * piece_width)
                    Line(points=[x_pos, bar_y, x_pos, bar_y + total_bar_height], width=dp(1.5))

class CircularFractionDisplay(Widget):
    numerator = NumericProperty(1)
    denominator = NumericProperty(4)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(numerator=self.update_canvas, denominator=self.update_canvas, size=self.update_canvas, pos=self.update_canvas)
        self.update_canvas()

    def update_canvas(self, *args):
        N = int(self.numerator)
        D = int(self.denominator)
        if D < 2: D = 2
        if N > D: N = D
        if N < 0: N = 0
        self.canvas.clear()
        center_x, center_y = self.center_x, self.center_y
        radius = min(self.width, self.height) * 0.4
        angle_per_slice = 360 / D
        num_segments = 20
        with self.canvas:
            Color(0.8, 0.8, 0.8, 1)
            Ellipse(pos=(center_x - radius, center_y - radius), size=(radius*2, radius*2))
            if N > 0:
                Color(1, 0.2, 0.2, 1)
                total_angle = N * angle_per_slice
                for i in range(num_segments * N):
                    angle1 = (i / (num_segments * N)) * total_angle
                    angle2 = ((i + 1) / (num_segments * N)) * total_angle
                    rad1 = math.radians(angle1)
                    rad2 = math.radians(angle2)
                    p1_x = center_x + radius * math.cos(rad1)
                    p1_y = center_y + radius * math.sin(rad1)
                    p2_x = center_x + radius * math.cos(rad2)
                    p2_y = center_y + radius * math.sin(rad2)
                    Triangle(points=[center_x, center_y, p1_x, p1_y, p2_x, p2_y])
            Color(0, 0, 0, 1)
            Line(circle=(center_x, center_y, radius), width=dp(2))
            for i in range(D):
                angle_start = i * angle_per_slice
                angle_rad = math.radians(angle_start)
                Line(points=[center_x, center_y, center_x + radius * math.cos(angle_rad), center_y + radius * math.sin(angle_rad)], width=dp(1.5))

class SetFractionDisplay(Widget):
    numerator = NumericProperty(1)
    denominator = NumericProperty(4)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(numerator=self.update_canvas, denominator=self.update_canvas, size=self.update_canvas, pos=self.update_canvas)
        self.update_canvas()

    def update_canvas(self, *args):
        N = int(self.numerator)
        D = int(self.denominator)
        if D < 2: D = 2
        if N > D: N = D
        if N < 0: N = 0
        self.canvas.clear()
        max_cols = 4
        cols = min(max_cols, D)
        rows = math.ceil(D / cols)
        padding_x = self.width * 0.05
        padding_y = self.height * 0.15
        available_width = self.width - 2 * padding_x
        available_height = self.height - 2 * padding_y
        cell_width = available_width / cols
        cell_height = available_height / rows
        circle_radius = min(cell_width, cell_height) * 0.4
        ellipse_size = (circle_radius * 2, circle_radius * 2)
        with self.canvas:
            for i in range(D):
                row = i // cols
                col = i % cols
                center_x = self.x + padding_x + col * cell_width + cell_width / 2
                center_y = self.y + padding_y + (rows - 1 - row) * cell_height + cell_height / 2
                ellipse_pos = (center_x - circle_radius, center_y - circle_radius)
                if i < N:
                    Color(1, 0.2, 0.2, 1)
                else:
                    Color(0.6, 0.6, 0.6, 1)
                Ellipse(pos=ellipse_pos, size=ellipse_size)
                Color(0, 0, 0, 1)
                Line(circle=(center_x, center_y, circle_radius), width=dp(1.5))