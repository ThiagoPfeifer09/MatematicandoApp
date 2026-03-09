from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.uix.carousel import Carousel
from kivymd.uix.button import MDIconButton, MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import MDGridLayout
from kivy.metrics import dp
from kivy.uix.image import Image

# --- PALETA DE CORES ---
CORAL = (1, 0.44, 0.26, 1)
CORAL_BG = (1, 0.44, 0.26, 0.12)
LILAS = (0.65, 0.55, 0.98, 1)
LILAS_BG = (0.65, 0.55, 0.98, 0.12)
AZUL = (0.2, 0.6, 1, 1)
AZUL_BG = (0.2, 0.6, 1, 0.12)
AMARELO = (1, 0.75, 0, 1)
AMARELO_BG = (1, 0.75, 0, 0.12)
BRANCO = (1, 1, 1, 1)
PRETO_TITULO = (0.2, 0.2, 0.2, 1)
CINZA_TEXTO = (0.5, 0.5, 0.5, 1)

# ================================================================
# COMPONENTE: ITEM DA LISTA (BenefitRow) - ÍCONE CENTRALIZADO
# ================================================================
class BenefitRow(MDBoxLayout):
    def __init__(self, icon, title, subtitle, color, bg_color, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(60)       
        self.size_hint_x = None
        self.width = dp(310)       
        self.spacing = dp(15)      
        self.pos_hint = {"center_x": 0.5}

        # 1. Círculo do Ícone
        icon_box = MDCard(
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            radius=[dp(25)], # Raio = metade do tamanho (Círculo perfeito)
            md_bg_color=bg_color,
            elevation=0,
            pos_hint={"center_y": 0.5},
            padding=0
        )
        
        # TRUQUE DE CENTRALIZAÇÃO: FloatLayout dentro do Card
        container_icon = MDFloatLayout()
        
        icone_visual = MDIcon(
            icon=icon,
            halign="center",
            theme_text_color="Custom",
            text_color=color,
            font_size=dp(26),
            pos_hint={"center_x": 0.5, "center_y": 0.5} # Centralização Absoluta
        )
        container_icon.add_widget(icone_visual)
        icon_box.add_widget(container_icon)
        
        # 2. Textos
        text_box = MDBoxLayout(
            orientation="vertical",
            adaptive_height=True,
            spacing=dp(2),
            pos_hint={"center_y": 0.5}
        )
        
        lbl_title = MDLabel(
            text=title,
            bold=True,
            font_style="Subtitle1",
            theme_text_color="Custom",
            text_color=PRETO_TITULO,
            halign="left",
            adaptive_height=True
        )
        
        lbl_sub = MDLabel(
            text=subtitle,
            font_style="Caption",
            theme_text_color="Custom",
            text_color=CINZA_TEXTO,
            halign="left",
            adaptive_height=True
        )

        text_box.add_widget(lbl_title)
        text_box.add_widget(lbl_sub)

        self.add_widget(icon_box)
        self.add_widget(text_box)

# ================================================================
# COMPONENTE: CARD GRANDE (Para Slide 1)
# ================================================================
class BigFeatureCard(MDCard):
    def __init__(self, text="", icon="help", color=AZUL, bg_color=AZUL_BG, **kwargs):
        super().__init__(
            orientation="vertical",
            size_hint=(None, None),
            size=(dp(100), dp(110)),
            radius=[16],
            md_bg_color=bg_color,
            elevation=0,
            padding=0, # Padding zero para usar layout interno
            **kwargs
        )
        
        # Layout interno para centralizar tudo perfeitamente
        layout_interno = MDBoxLayout(
            orientation='vertical', 
            padding=dp(10), 
            spacing=dp(5),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        
        layout_interno.add_widget(MDIcon(
            icon=icon, 
            halign="center", 
            font_size="42sp", 
            theme_text_color="Custom", 
            text_color=color
        ))
        
        layout_interno.add_widget(MDLabel(
            text=text, 
            halign="center", 
            bold=True, 
            font_style="Subtitle2", 
            theme_text_color="Custom",
            text_color=PRETO_TITULO
        ))
        
        self.add_widget(layout_interno)

# ================================================================
# TELA PRINCIPAL
# ================================================================
class TelaTutorial(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()

    def setup_ui(self):
        # Fundo
        try:
            bg = Image(source='fundoapp.png', allow_stretch=True, keep_ratio=False)
            self.add_widget(bg)
        except:
            self.md_bg_color = (0.9, 0.96, 0.98, 1)

        layout = MDBoxLayout(orientation="vertical")
        
        # --- HEADER ---
        header = MDBoxLayout(size_hint_y=None, height=dp(60), padding=[dp(12), 0])
        btn_voltar = MDIconButton(
            icon="arrow-left", 
            on_release=self.voltar,
            theme_text_color="Custom",
            text_color=PRETO_TITULO,
            pos_hint={"center_y": 0.5}
        )
        lbl_header = MDLabel(
            text="Tutorial", 
            bold=True, 
            font_style="H6",
            pos_hint={"center_y": 0.5}
        )
        header.add_widget(btn_voltar)
        header.add_widget(lbl_header)
        layout.add_widget(header)

        # --- ÁREA CENTRAL ---
        center_area = MDBoxLayout(padding=[dp(20), dp(5), dp(20), dp(20)])
        
        self.card_main = MDCard(
            orientation="vertical",
            radius=[dp(20)],
            elevation=4,
            md_bg_color=BRANCO,
            padding=0
        )

        # Carrossel
        self.carrossel = Carousel(direction="right", loop=False)
        self.carrossel.add_widget(self.slide_boas_vindas())
        self.carrossel.add_widget(self.slide_jogos())
        self.carrossel.add_widget(self.slide_estudos())
        self.carrossel.add_widget(self.slide_final())
        
        self.card_main.add_widget(self.carrossel)

        # --- RODAPÉ ---
        nav_bar = MDBoxLayout(
            size_hint_y=None, height=dp(70), 
            padding=[dp(24), 0, dp(24), dp(10)], spacing=dp(10)
        )
        
        self.btn_pular = MDFlatButton(
            text="Pular", theme_text_color="Hint",
            on_release=self.voltar, size_hint_x=0.25,
            pos_hint={'center_y': 0.5}
        )
        
        self.lbl_indicador = MDLabel(
            text="1 / 4", halign="center", theme_text_color="Hint", 
            font_style="Caption", size_hint_x=0.2,
            pos_hint={'center_y': 0.5}
        )
        
        self.btn_acao = MDRaisedButton(
            text="Próximo", md_bg_color=LILAS, text_color=BRANCO,
            elevation=0, size_hint_x=0.45, pos_hint={'center_y': 0.5},
            on_release=self.avancar
        )

        nav_bar.add_widget(self.btn_pular)
        nav_bar.add_widget(self.lbl_indicador)
        nav_bar.add_widget(self.btn_acao)

        self.card_main.add_widget(nav_bar)
        center_area.add_widget(self.card_main)
        layout.add_widget(center_area)
        self.add_widget(layout)

        self.carrossel.bind(current_slide=self.update_nav)

    def voltar(self, *args):
        if self.manager: self.manager.current = "inicial"

    def avancar(self, *args):
        if self.carrossel.index < len(self.carrossel.slides) - 1:
            self.carrossel.load_next()
        else:
            self.voltar()

    def update_nav(self, instance, value):
        idx = instance.index
        total = len(instance.slides)
        self.lbl_indicador.text = f"{idx + 1} / {total}"
        
        if idx == total - 1:
            self.btn_acao.text = "COMEÇAR"
            self.btn_acao.md_bg_color = CORAL
            self.btn_pular.opacity = 0
            self.btn_pular.disabled = True
        else:
            self.btn_acao.text = "Próximo"
            self.btn_acao.md_bg_color = LILAS
            self.btn_pular.opacity = 1
            self.btn_pular.disabled = False

    # ---------------- SLIDES ----------------
    def slide_boas_vindas(self):
        slide = MDBoxLayout(orientation="vertical", padding=dp(20))
        slide.add_widget(MDLabel(size_hint_y=0.2)) 
        
        slide.add_widget(MDIcon(
            icon="school-outline", halign="center", font_size="60sp", 
            theme_text_color="Custom", text_color=PRETO_TITULO
        ))
        slide.add_widget(MDLabel(text="Bem-vindo!", halign="center", bold=True, font_style="H5", size_hint_y=None, height=dp(40)))
        
        slide.add_widget(MDLabel(
            text="O Matematicando é o seu parceiro para dominar a matemática de forma leve e divertida.",
            halign="center", theme_text_color="Secondary", size_hint_y=None, height=dp(60)
        ))

        slide.add_widget(MDLabel(size_hint_y=None, height=dp(20)))

        diagrama = MDBoxLayout(orientation="horizontal", spacing=dp(10), adaptive_size=True, pos_hint={"center_x": 0.5})
        diagrama.add_widget(BigFeatureCard("Jogos", "gamepad-variant", CORAL, CORAL_BG))
        diagrama.add_widget(MDIcon(icon="arrow-right", pos_hint={"center_y": 0.5}, theme_text_color="Hint"))
        diagrama.add_widget(BigFeatureCard("Estudos", "book-open-variant", LILAS, LILAS_BG))
        
        slide.add_widget(diagrama)
        slide.add_widget(MDLabel(size_hint_y=1))
        return slide

    def slide_jogos(self):
        slide = MDBoxLayout(orientation="vertical", padding=dp(20))
        
        top_box = MDBoxLayout(adaptive_height=True, size_hint_y=None, height=dp(40))
        top_box.add_widget(MDIcon(icon="trophy-outline", theme_text_color="Custom", text_color=CORAL, font_size="28sp"))
        slide.add_widget(top_box)
        
        slide.add_widget(MDLabel(size_hint_y=0.1))

        slide.add_widget(MDLabel(
            text="Desafie-se!", 
            halign="center", bold=True, font_style="H5", 
            theme_text_color="Custom", text_color=PRETO_TITULO,
            size_hint_y=None, height=dp(40)
        ))

        slide.add_widget(MDLabel(
            text="Escolha seu nível de escolaridade e pratique com diversos minigames.",
            halign="center", theme_text_color="Secondary", font_style="Body2",
            size_hint_y=None, height=dp(50)
        ))
        
        slide.add_widget(MDLabel(size_hint_y=None, height=dp(20)))

        list_container = MDBoxLayout(
            orientation="vertical", 
            adaptive_height=True, 
            spacing=dp(10),
            pos_hint={"center_x": 0.57}
        )

        list_container.add_widget(BenefitRow("school", "Níveis Graduais", "Fund. I, II e Médio", CORAL, CORAL_BG))
        list_container.add_widget(BenefitRow("star", "Ganhe XP", "Suba de nível ao acertar", AMARELO, AMARELO_BG))
        list_container.add_widget(BenefitRow("chart-line-variant", "Evolua", "Acompanhe seu progresso", AZUL, AZUL_BG))

        slide.add_widget(list_container)
        slide.add_widget(MDLabel(size_hint_y=1))
        return slide

    def slide_estudos(self):
        slide = MDBoxLayout(orientation="vertical", padding=dp(20))
        slide.add_widget(MDLabel(size_hint_y=0.2))

        slide.add_widget(MDIcon(icon="notebook-edit-outline", halign="center", font_size="50sp", theme_text_color="Custom", text_color=LILAS))
        slide.add_widget(MDLabel(text="Conteúdos", halign="center", bold=True, font_style="H5", size_hint_y=None, height=dp(40)))
        
        slide.add_widget(MDLabel(
            text="Revise conceitos importantes antes de jogar. Tudo organizado por temas:",
            halign="center", theme_text_color="Secondary", size_hint_y=None, height=dp(60)
        ))

        grid = MDGridLayout(cols=2, spacing=dp(15), adaptive_height=True, adaptive_width=True, pos_hint={"center_x": 0.5})
        
        materias = [("Álgebra", "variable", LILAS, LILAS_BG), ("Geometria", "shape-outline", CORAL, CORAL_BG),
                    ("Estatística", "chart-bar", AZUL, AZUL_BG), ("Frações", "chart-pie", AMARELO, AMARELO_BG)]
        
        for nome, icone, cor, bg in materias:
            # Reutilizando a lógica do BigFeatureCard simplificada para os cards menores
            card = MDCard(size_hint=(None, None), size=(dp(110), dp(70)), radius=[12], md_bg_color=bg, elevation=0, padding=0)
            layout_int = MDFloatLayout()
            layout_int.add_widget(MDIcon(icon=icone, halign="center", theme_text_color="Custom", text_color=cor, font_size="28sp", pos_hint={"center_x": 0.5, "center_y": 0.65}))
            layout_int.add_widget(MDLabel(text=nome, halign="center", font_style="Caption", bold=True, pos_hint={"center_x": 0.5, "center_y": 0.25}))
            card.add_widget(layout_int)
            grid.add_widget(card)

        slide.add_widget(grid)
        slide.add_widget(MDLabel(size_hint_y=1))
        return slide

    def slide_final(self):
        slide = MDBoxLayout(orientation="vertical", padding=dp(20))
        slide.add_widget(MDLabel(size_hint_y=1))

        rocket_bg = MDCard(size_hint=(None, None), size=(dp(110), dp(110)), radius=[55], md_bg_color=CORAL_BG, elevation=0, pos_hint={"center_x": 0.5}, padding=0)
        layout_bg = MDFloatLayout()
        layout_bg.add_widget(MDIcon(icon="rocket-launch", halign="center", font_size="55sp", theme_text_color="Custom", text_color=CORAL, pos_hint={"center_x": 0.5, "center_y": 0.5}))
        rocket_bg.add_widget(layout_bg)
        
        slide.add_widget(rocket_bg)
        slide.add_widget(MDLabel(text="Tudo Pronto!", halign="center", bold=True, font_style="H4", size_hint_y=None, height=dp(50)))
        slide.add_widget(MDLabel(
            text="Explore, estude e divirta-se!\nSua jornada matemática começa agora.",
            halign="center", theme_text_color="Secondary"
        ))

        slide.add_widget(MDLabel(size_hint_y=1))
        return slide

if __name__ == "__main__":
    TelaTutorial().run()