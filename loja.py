from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFillRoundFlatButton, MDIconButton, MDRectangleFlatIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.app import MDApp
from kivy.metrics import dp
from random import choice

# Cores do Tema (Para manter consistência)
CORAL = (1, 0.44, 0.26, 1)
LILAS = (0.65, 0.55, 0.98, 1)
VERDE_XP = (0.2, 0.8, 0.2, 1)

class TelaLoja(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        
        # 1. Fundo
        layout.add_widget(Image(source="fundoapp.png", allow_stretch=True, keep_ratio=False, size_hint=(1, 1)))
        self.adicionar_decoracao_fundo(layout)

        # 2. Layout Principal (Vertical)
        main_box = MDBoxLayout(orientation="vertical", spacing=dp(10), padding=[dp(0), dp(0), dp(0), dp(0)])
        
        # --- CABEÇALHO DA LOJA ---
        header = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(80), padding=[dp(20), dp(10), dp(20), dp(0)])
        
        # Botão Voltar (Esquerda)
        btn_voltar = MDIconButton(icon="arrow-left", theme_text_color="Custom", text_color=(0,0,0,1), icon_size=dp(32))
        btn_voltar.bind(on_release=self.voltar)
        
        # Título (Centro)
        titulo = MDLabel(
            text="LOJA", 
            halign="center", 
            font_name="BungeeShade", # Usando a fonte do seu jogo
            font_size=dp(36),
            theme_text_color="Custom", 
            text_color=CORAL,
            pos_hint={"center_y": 0.5}
        )

        # Mostrador de XP (Direita) - Simulação de Carteira
        box_xp = MDCard(
            size_hint=(None, None), 
            size=(dp(100), dp(40)), 
            radius=[dp(20)], 
            md_bg_color=(1, 1, 1, 0.9),
            elevation=2,
            pos_hint={"center_y": 0.5},
            padding=[dp(10), dp(5)]
        )
        box_xp.add_widget(MDIconButton(icon="star", icon_size=dp(20), theme_text_color="Custom", text_color=VERDE_XP, pos_hint={"center_y": 0.5}))
        self.label_xp = MDLabel(text="1250", halign="center", bold=True, theme_text_color="Custom", text_color=(0.3, 0.3, 0.3, 1), pos_hint={"center_y": 0.5})
        box_xp.add_widget(self.label_xp)

        header.add_widget(btn_voltar)
        header.add_widget(titulo)
        header.add_widget(box_xp)
        
        main_box.add_widget(header)

        # --- LISTA DE PRODUTOS ---
        scroll = MDScrollView(size_hint=(1, 1))
        # Ajustei o padding para os cards não ficarem colados na borda
        grid = MDGridLayout(cols=2, spacing=dp(15), padding=[dp(20), dp(10), dp(20), dp(20)], adaptive_height=True, size_hint_y=None)
        
        # Lista de produtos (Nome, Preço, Ícone, Cor do Ícone)
        produtos = [
            ("Avatar Ninja", 500, "ninja", LILAS),
            ("Tema Escuro", 200, "theme-light-dark", (0.2, 0.2, 0.2, 1)),
            ("Dica Extra", 100, "lightbulb-on", (1, 0.8, 0, 1)),
            ("Vida Extra", 300, "heart", (0.9, 0.2, 0.2, 1)),
            ("Calculadora", 1000, "calculator", CORAL),
            ("Sem Ads", 2000, "block-helper", (0.5, 0.5, 0.5, 1))
        ]

        for nome, preco, icone, cor in produtos:
            card = self.criar_item_loja(nome, preco, icone, cor)
            grid.add_widget(card)

        scroll.add_widget(grid)
        main_box.add_widget(scroll)

        layout.add_widget(main_box)
        self.add_widget(layout)

    def criar_item_loja(self, nome, preco, icone, cor_icone):
        # Card Base
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(200),
            padding=dp(15),
            radius=[dp(20)],
            elevation=4,
            md_bg_color=(1, 1, 1, 0.95),
            ripple_behavior=True
        )
        
        # Ícone Grande no Topo
        card.add_widget(MDIconButton(
            icon=icone, 
            icon_size=dp(60), 
            pos_hint={"center_x": 0.5}, 
            theme_text_color="Custom", 
            text_color=cor_icone,
            disabled=True # Desabilita clique no icone para não bugar o ripple do card
        ))
        
        # Nome do Item
        card.add_widget(MDLabel(
            text=nome, 
            halign="center", 
            bold=True, 
            font_style="Subtitle1",
            theme_text_color="Primary"
        ))

        # Espaço flexível
        card.add_widget(MDBoxLayout(size_hint_y=None, height=dp(10)))
        
        # Preço com ícone de estrela pequeno
        box_preco = MDBoxLayout(orientation="horizontal", adaptive_height=True, spacing=dp(5), pos_hint={"center_x": 0.5})
        box_preco.add_widget(MDLabel(text="", size_hint_x=1)) # Espaçador Esq
        box_preco.add_widget(MDIconButton(icon="star", icon_size=dp(16), theme_text_color="Custom", text_color=VERDE_XP, disabled=True))
        box_preco.add_widget(MDLabel(text=f"{preco} XP", bold=True, theme_text_color="Secondary", font_style="Caption", adaptive_width=True))
        box_preco.add_widget(MDLabel(text="", size_hint_x=1)) # Espaçador Dir
        card.add_widget(box_preco)

        # Botão Comprar Estilizado
        btn = MDFillRoundFlatButton(
            text="COMPRAR", 
            font_size=dp(14),
            size_hint_x=1, 
            md_bg_color=CORAL,
            text_color=(1,1,1,1)
        )
        # Passamos os dados para a função de compra
        btn.bind(on_release=lambda x: self.tentar_comprar(nome, preco))
        
        card.add_widget(MDBoxLayout(size_hint_y=None, height=dp(10)))
        card.add_widget(btn)
        
        return card

    def adicionar_decoracao_fundo(self, layout):
        # Decoração sutil no fundo
        icones = ["cart-outline", "gift-outline", "shopping-outline", "tag-outline"]
        positions = [{"x": 0.05, "y": 0.9}, {"x": 0.9, "y": 0.1}, {"x": 0.1, "y": 0.2}, {"x": 0.85, "y": 0.85}]
        for i, pos in enumerate(positions):
            layout.add_widget(MDIconButton(
                icon=icones[i % len(icones)], 
                theme_text_color="Custom", 
                text_color=(0, 0, 0, 0.05), 
                pos_hint=pos, 
                icon_size=dp(100), 
                disabled=True
            ))

    def tentar_comprar(self, item, preco):
        # Lógica simples de compra (Mockup)
        # Aqui você pegaria o XP real do banco de dados ou do App
        xp_atual = int(self.label_xp.text)
        
        if xp_atual >= preco:
            self.mostrar_dialogo("Sucesso!", f"Você comprou {item}!", confirm=True, novo_saldo=xp_atual-preco)
        else:
            self.mostrar_dialogo("Ops!", f"Você precisa de mais {preco - xp_atual} XP para comprar isso.", confirm=False)

    def mostrar_dialogo(self, titulo, texto, confirm, novo_saldo=None):
        botoes = [MDFlatButton(text="OK", theme_text_color="Custom", text_color=LILAS, on_release=lambda x: self.fechar_dialogo(novo_saldo))]
        self.dialog = MDDialog(
            title=titulo,
            text=texto,
            buttons=botoes
        )
        self.dialog.open()

    def fechar_dialogo(self, novo_saldo):
        self.dialog.dismiss()
        if novo_saldo is not None:
            self.label_xp.text = str(novo_saldo)
            # Aqui você salvaria o novo saldo no banco de dados

    def voltar(self, instance):
        self.manager.current = "inicial"