from kivy.core.text import LabelBase
import os
import json  # <--- IMPORTANTE PARA SALVAR SESSÃO
from kivy.uix.boxlayout import BoxLayout
from random import choice
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.button import MDIconButton, MDRectangleFlatButton, MDRaisedButton, MDRectangleFlatIconButton, MDFlatButton, MDFillRoundFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.slider import MDSlider
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.card import MDCard
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.dialog import MDDialog
from kivy.uix.modalview import ModalView
from kivy.animation import Animation
from kivymd.uix.textfield import MDTextField
from kivymd.uix.relativelayout import MDRelativeLayout

# --- IMPORT DO BANCO DE DADOS ---
import banco_dados

# Configuração de Fonte e Caminhos
font_path = os.path.join(os.path.dirname(__file__), "Fontes", "Duo-Dunkel.ttf")
LabelBase.register(name="BungeeShade", fn_regular=font_path)

# Cores Globais
CORAL = (1, 0.44, 0.26, 1)
LILAS = (0.65, 0.55, 0.98, 1)
PRETO = (0, 0, 0, 1)
PRETO_70 = (0, 0, 0, 0.7)
BRANCO = (1, 1, 1, 1)

class ImageButton(ButtonBehavior, Image):
    pass

# --- CLASSES AUXILIARES PARA OS DIALOGS DE RECUPERAÇÃO ---
class ContentRecuperacao(MDBoxLayout):
    pass

class ContentNovaSenha(MDBoxLayout):
    pass

# -------------------------------------------------
# TELA DE LOGIN
# -------------------------------------------------
class TelaLogin(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # Fundo
        layout.add_widget(Image(source="fundoapp.png", allow_stretch=True, keep_ratio=False, size_hint=(1, 1)))
        self.adicionar_decoracao_fundo(layout)

        # Card Central
        card = MDCard(
            orientation="vertical",
            size_hint=(0.85, None),
            height=dp(600), # Aumentado para caber o novo botão offline
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=[dp(25), dp(30), dp(25), dp(30)],
            spacing=dp(15),
            radius=[dp(25)],
            elevation=6,
            md_bg_color=(1, 1, 1, 0.98)
        )

        # Cabeçalho
        box_logo = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(5), pos_hint={"center_x": 0.5})

        box_logo.add_widget(MDLabel(
            text="Acesse sua conta",
            halign="center", theme_text_color="Custom", text_color=LILAS,
            font_style="H5", bold=True, adaptive_height=True
        ))
        box_logo.add_widget(MDLabel(
            text="Entre com seu usuário único",
            halign="center", theme_text_color="Hint", font_style="Caption", adaptive_height=True
        ))
        card.add_widget(box_logo)

        # Campos
        card.add_widget(MDBoxLayout(size_hint_y=None, height=dp(10)))

        self.user_input = MDTextField(
            hint_text="Nome de Usuário",
            mode="rectangle",
            icon_right="account",
            line_color_focus=LILAS,
            text_color_focus=PRETO,
            multiline=False,
            write_tab=False
        )
        self.user_input.bind(on_text_validate=self.focar_senha)
        card.add_widget(self.user_input)

        # Senha
        box_senha = MDRelativeLayout(size_hint_y=None, height=dp(66))

        self.senha_input = MDTextField(
            hint_text="Senha",
            mode="rectangle",
            password=True,
            line_color_focus=LILAS,
            text_color_focus=PRETO,
            pos_hint={"center_y": 0.5},
            multiline=False,
            write_tab=False
        )
        self.senha_input.bind(on_text_validate=self.fazer_login)

        box_senha.add_widget(self.senha_input)

        self.btn_olho = MDIconButton(
            icon="eye-off", theme_text_color="Hint",
            pos_hint={"right": 0.98, "center_y": 0.55},
            on_release=self.toggle_senha
        )
        box_senha.add_widget(self.btn_olho)
        card.add_widget(box_senha)

        # --- LINHA DE OPÇÕES (Lembrar de mim + Esqueci Senha) ---
        box_opcoes = MDBoxLayout(orientation="horizontal", adaptive_height=True, size_hint_x=1, padding=[0, dp(5), 0, dp(5)])

        # Lembrar de mim
        box_lembrar = MDBoxLayout(orientation="horizontal", spacing=dp(5), adaptive_width=True)
        self.switch_lembrar = MDSwitch(active=False, widget_style="ios", pos_hint={'center_y': .5})

        lbl_lembrar = MDLabel(text="Lembrar", theme_text_color="Hint", font_style="Caption", pos_hint={'center_y': .5}, adaptive_width=True)

        box_lembrar.add_widget(self.switch_lembrar)
        box_lembrar.add_widget(lbl_lembrar)

        box_opcoes.add_widget(box_lembrar)

        # Espaçador
        box_opcoes.add_widget(MDBoxLayout())

        # Esqueci Senha
        btn_esqueci = MDFlatButton(
            text="Esqueci senha", theme_text_color="Custom", text_color=CORAL, font_size=dp(11)
        )
        btn_esqueci.bind(on_release=self.abrir_recuperar_senha)
        box_opcoes.add_widget(btn_esqueci)

        card.add_widget(box_opcoes)

        # Botão Entrar
        btn_entrar = MDFillRoundFlatButton(
            text="ENTRAR", font_size=dp(18), theme_text_color="Custom", text_color=BRANCO,
            md_bg_color=LILAS, size_hint_x=1, size_hint_y=None, height=dp(50)
        )
        btn_entrar.bind(on_release=self.fazer_login)
        card.add_widget(btn_entrar)

        # Botão Criar Conta
        btn_criar = MDFlatButton(
            text="Não tem um usuário? Crie agora", theme_text_color="Custom", text_color=PRETO_70,
            pos_hint={"center_x": 0.5}, font_size=dp(12)
        )
        btn_criar.bind(on_release=self.ir_para_cadastro)
        card.add_widget(btn_criar)

        # --- BOTÃO ENTRAR SEM LOGIN (OFFLINE) ---
        btn_offline = MDFlatButton(
            text="Entrar sem login (Modo Offline)", theme_text_color="Custom", text_color=CORAL,
            pos_hint={"center_x": 0.5}, font_size=dp(12)
        )
        btn_offline.bind(on_release=self.entrar_offline)
        card.add_widget(btn_offline)

        # Redes Sociais
        box_ou = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(30), pos_hint={"center_x": 0.5})
        box_ou.add_widget(MDBoxLayout(md_bg_color=(0.9, 0.9, 0.9, 1), size_hint_y=None, height=dp(1), pos_hint={"center_y": 0.5}))
        box_ou.add_widget(MDLabel(text="Sincronizar com", halign="center", theme_text_color="Hint", font_style="Caption", size_hint_x=None, width=dp(100)))
        box_ou.add_widget(MDBoxLayout(md_bg_color=(0.9, 0.9, 0.9, 1), size_hint_y=None, height=dp(1), pos_hint={"center_y": 0.5}))
        card.add_widget(box_ou)

        box_social = MDBoxLayout(orientation="horizontal", spacing=dp(20), adaptive_size=True, pos_hint={"center_x": 0.5})
        btn_google = MDIconButton(icon="google", theme_text_color="Custom", text_color=(0.85, 0.2, 0.2, 1), icon_size=dp(30), md_bg_color=(0.95, 0.95, 0.95, 1))
        btn_facebook = MDIconButton(icon="facebook", theme_text_color="Custom", text_color=(0.1, 0.35, 0.7, 1), icon_size=dp(30), md_bg_color=(0.95, 0.95, 0.95, 1))
        box_social.add_widget(btn_google)
        box_social.add_widget(btn_facebook)
        card.add_widget(box_social)

        layout.add_widget(card)
        self.add_widget(layout)

    def adicionar_decoracao_fundo(self, layout):
        icones = ["pi", "function", "calculator", "sigma", "chart-bar"]
        positions = [{"x": 0.05, "y": 0.9}, {"x": 0.85, "y": 0.1}, {"x": 0.1, "y": 0.2}, {"x": 0.85, "y": 0.8}, {"x": 0.5, "y": 0.92}]
        for pos in positions:
            layout.add_widget(MDIconButton(icon=choice(icones), theme_text_color="Custom", text_color=(0, 0, 0, 0.08), pos_hint=pos, icon_size=dp(60), disabled=True))

    def toggle_senha(self, instance):
        self.senha_input.password = not self.senha_input.password
        instance.icon = "eye" if not self.senha_input.password else "eye-off"

    def focar_senha(self, instance):
        self.senha_input.focus = True

    def fazer_login(self, instance):
        self.user_input.error = False
        nome = self.user_input.text.strip()
        senha = self.senha_input.text.strip()

        if nome == "" or senha == "":
            self.user_input.helper_text = "Preencha usuário e senha"
            self.user_input.helper_text_mode = "on_error"
            self.user_input.error = True
            return

        print(f"Tentando logar: {nome}...")
        sucesso, mensagem, dados = banco_dados.verificar_login(nome, senha)

        if sucesso:
            # --- SALVANDO O USUÁRIO NO APP ---
            app = MDApp.get_running_app()
            app.user_id = dados['id']      # Salva ID
            app.user_nome = dados['nome']  # Salva Nome
            app.user_email = dados.get('email')

            # --- LÓGICA DO "LEMBRAR DE MIM" ---
            if self.switch_lembrar.active:
                print("Salvando sessão no disco...")
                app.salvar_sessao(dados['id'])
            else:
                print("Não salvar sessão. Limpando dados antigos se houver.")
                app.limpar_sessao()

            print(f"Login Aprovado! Usuário ID: {app.user_id} ({app.user_nome})")

            self.senha_input.text = ""
            self.user_input.text = ""
            self.manager.current = "inicial"
        else:
            self.user_input.helper_text = mensagem
            self.user_input.helper_text_mode = "on_error"
            self.user_input.error = True

    def entrar_offline(self, instance):
        """Função para bypassar o banco de dados e entrar como convidado."""
        app = MDApp.get_running_app()
        app.user_id = 0 # 0 significa usuário não logado/offline
        app.user_nome = "Convidado"
        app.user_email = "offline@local"

        # Se escolheu entrar offline, garantimos que não tem sessão antiga salva
        app.limpar_sessao()

        print("Entrando no modo Convidado (Offline)")
        self.senha_input.text = ""
        self.user_input.text = ""
        self.manager.current = "inicial"

    def ir_para_cadastro(self, instance):
        self.manager.current = "cadastro"

    # --- LÓGICA DE RECUPERAÇÃO DE SENHA ---
    def abrir_recuperar_senha(self, instance):
        self.content_rec = MDBoxLayout(orientation="vertical", spacing="12dp", size_hint_y=None, height="120dp")

        self.input_rec_user = MDTextField(
            hint_text="Nome de Usuário",
            multiline=False,
            write_tab=False
        )
        self.input_rec_user.bind(on_text_validate=self.focar_rec_email)

        self.input_rec_email = MDTextField(
            hint_text="E-mail cadastrado",
            multiline=False,
            write_tab=False
        )
        self.input_rec_email.bind(on_text_validate=self.verificar_dados_recuperacao)

        self.content_rec.add_widget(self.input_rec_user)
        self.content_rec.add_widget(self.input_rec_email)

        self.dialog_rec = MDDialog(
            title="Recuperar Senha", text="Confirme seus dados:", type="custom", content_cls=self.content_rec,
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=lambda x: self.dialog_rec.dismiss()),
                MDFlatButton(text="VERIFICAR", text_color=LILAS, on_release=self.verificar_dados_recuperacao)
            ],
        )
        self.dialog_rec.open()

    def focar_rec_email(self, instance):
        self.input_rec_email.focus = True

    def verificar_dados_recuperacao(self, instance):
        nome = self.input_rec_user.text.strip()
        email = self.input_rec_email.text.strip()
        if not nome or not email:
            self.input_rec_user.error = True
            return

        print(f"Verificando: {nome} | {email}")
        sucesso, resultado = banco_dados.verificar_dados_recuperacao(nome, email)

        if sucesso:
            user_id = resultado
            self.dialog_rec.dismiss()
            self.abrir_dialog_nova_senha(user_id)
        else:
            self.input_rec_email.helper_text = "Dados incorretos"
            self.input_rec_email.helper_text_mode = "on_error"
            self.input_rec_email.error = True

    def abrir_dialog_nova_senha(self, user_id):
        self.content_nova = MDBoxLayout(orientation="vertical", spacing="12dp", size_hint_y=None, height="60dp")

        self.input_nova_senha = MDTextField(
            hint_text="Nova Senha",
            password=True,
            multiline=False,
            write_tab=False
        )
        self.input_nova_senha.bind(on_text_validate=lambda x: self.salvar_nova_senha(user_id))

        self.content_nova.add_widget(self.input_nova_senha)

        self.dialog_nova = MDDialog(
            title="Redefinir Senha", type="custom", content_cls=self.content_nova,
            buttons=[MDFlatButton(text="SALVAR", text_color=LILAS, on_release=lambda x: self.salvar_nova_senha(user_id))]
        )
        self.dialog_nova.open()

    def salvar_nova_senha(self, user_id):
        nova_senha = self.input_nova_senha.text.strip()
        if len(nova_senha) < 6:
            self.input_nova_senha.helper_text = "Mínimo 6 caracteres"
            self.input_nova_senha.error = True
            return

        sucesso, msg = banco_dados.atualizar_senha(user_id, nova_senha)
        self.dialog_nova.dismiss()

        if sucesso:
            MDDialog(title="Sucesso", text="Senha atualizada! Faça login agora.", buttons=[MDFlatButton(text="OK", on_release=lambda x: x.parent.parent.parent.dismiss())]).open()
        else:
            MDDialog(title="Erro", text=msg, buttons=[MDFlatButton(text="OK", on_release=lambda x: x.parent.parent.parent.dismiss())]).open()

# -------------------------------------------------
# TELA DE CADASTRO
# -------------------------------------------------
class TelaCadastro(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        layout.add_widget(Image(source="fundoapp.png", allow_stretch=True, keep_ratio=False, size_hint=(1, 1)))
        self.adicionar_decoracao_fundo(layout)

        card = MDCard(
            orientation="vertical",
            size_hint=(0.85, None),
            height=dp(620),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=[dp(25), dp(20), dp(25), dp(20)],
            spacing=dp(12),
            radius=[dp(25)],
            elevation=6,
            md_bg_color=(1, 1, 1, 0.98)
        )

        box_header = MDBoxLayout(orientation="vertical", adaptive_height=True, spacing=dp(5), pos_hint={"center_x": 0.5})
        box_header.add_widget(MDLabel(
            text="Crie sua conta",
            halign="center", theme_text_color="Custom", text_color=CORAL,
            font_style="H5", bold=True, adaptive_height=True
        ))
        box_header.add_widget(MDLabel(
            text="Comece sua jornada matemática",
            halign="center", theme_text_color="Hint", font_style="Caption", adaptive_height=True
        ))
        card.add_widget(box_header)

        self.user_input = MDTextField(
            hint_text="Escolha um Usuário", mode="rectangle", icon_right="account-plus",
            line_color_focus=CORAL, text_color_focus=PRETO,
            multiline=False, write_tab=False
        )
        card.add_widget(self.user_input)

        self.email_input = MDTextField(
            hint_text="Seu melhor E-mail", mode="rectangle", icon_right="email",
            line_color_focus=CORAL, text_color_focus=PRETO,
            multiline=False, write_tab=False
        )
        card.add_widget(self.email_input)

        box_senha = MDRelativeLayout(size_hint_y=None, height=dp(66))
        self.senha_input = MDTextField(
            hint_text="Crie uma Senha", mode="rectangle", password=True,
            line_color_focus=CORAL, text_color_focus=PRETO, pos_hint={"center_y": 0.5},
            multiline=False, write_tab=False
        )
        box_senha.add_widget(self.senha_input)
        self.btn_olho_1 = MDIconButton(
            icon="eye-off", theme_text_color="Hint", pos_hint={"right": 0.98, "center_y": 0.55},
            on_release=lambda x: self.toggle_senha(self.senha_input, x)
        )
        box_senha.add_widget(self.btn_olho_1)
        card.add_widget(box_senha)

        box_confirma = MDRelativeLayout(size_hint_y=None, height=dp(66))
        self.confirma_input = MDTextField(
            hint_text="Confirme a Senha", mode="rectangle", password=True,
            line_color_focus=CORAL, text_color_focus=PRETO, pos_hint={"center_y": 0.5},
            multiline=False, write_tab=False
        )
        box_confirma.add_widget(self.confirma_input)
        self.btn_olho_2 = MDIconButton(
            icon="eye-off", theme_text_color="Hint", pos_hint={"right": 0.98, "center_y": 0.55},
            on_release=lambda x: self.toggle_senha(self.confirma_input, x)
        )
        box_confirma.add_widget(self.btn_olho_2)
        card.add_widget(box_confirma)

        card.add_widget(MDBoxLayout(size_hint_y=None, height=dp(10)))

        btn_cadastrar = MDFillRoundFlatButton(
            text="CADASTRAR", font_size=dp(18), theme_text_color="Custom", text_color=BRANCO,
            md_bg_color=CORAL, size_hint_x=1, size_hint_y=None, height=dp(50)
        )
        btn_cadastrar.bind(on_release=self.realizar_cadastro)
        card.add_widget(btn_cadastrar)

        btn_voltar = MDFlatButton(
            text="Já tenho conta? Fazer Login", theme_text_color="Custom", text_color=PRETO_70,
            pos_hint={"center_x": 0.5}, font_size=dp(12)
        )
        btn_voltar.bind(on_release=self.voltar_login)
        card.add_widget(btn_voltar)

        layout.add_widget(card)
        self.add_widget(layout)

    def adicionar_decoracao_fundo(self, layout):
        icones = ["pi", "function", "calculator", "sigma", "chart-bar"]
        positions = [{"x": 0.05, "y": 0.9}, {"x": 0.85, "y": 0.1}, {"x": 0.1, "y": 0.2}, {"x": 0.85, "y": 0.8}]
        for pos in positions:
            layout.add_widget(MDIconButton(icon=choice(icones), theme_text_color="Custom", text_color=(0, 0, 0, 0.08), pos_hint=pos, icon_size=dp(60), disabled=True))

    def toggle_senha(self, field, button):
        field.password = not field.password
        button.icon = "eye" if not field.password else "eye-off"

    def realizar_cadastro(self, instance):
        self.user_input.error = False
        self.confirma_input.error = False
        self.senha_input.error = False

        usuario = self.user_input.text.strip()
        email = self.email_input.text.strip()
        senha = self.senha_input.text.strip()
        confirma = self.confirma_input.text.strip()

        if usuario == "" or email == "":
            self.user_input.helper_text = "Preencha todos os campos"
            self.user_input.helper_text_mode = "on_error"
            self.user_input.error = True
            return

        if senha != confirma:
            self.confirma_input.helper_text = "As senhas não coincidem"
            self.confirma_input.helper_text_mode = "on_error"
            self.confirma_input.error = True
            return

        if len(senha) < 6:
            self.senha_input.helper_text = "Mínimo 6 caracteres"
            self.senha_input.helper_text_mode = "on_error"
            self.senha_input.error = True
            return

        print(f"Tentando cadastrar: {usuario}")
        sucesso, mensagem = banco_dados.criar_conta(usuario, senha, email)

        if sucesso:
            # --- LIMPEZA DOS CAMPOS ---
            self.user_input.text = ""
            self.email_input.text = ""
            self.senha_input.text = ""
            self.confirma_input.text = ""

            self.dialog_sucesso = MDDialog(
                title="Sucesso!",
                text="Conta criada com sucesso! Agora faça login.",
                buttons=[MDFlatButton(text="OK", theme_text_color="Custom", text_color=CORAL, on_release=lambda x: self.fechar_dialog_e_ir_login())]
            )
            self.dialog_sucesso.open()
        else:
            self.user_input.helper_text = mensagem
            self.user_input.helper_text_mode = "on_error"
            self.user_input.error = True

    def fechar_dialog_e_ir_login(self):
        self.dialog_sucesso.dismiss()
        self.manager.current = "login"

    def voltar_login(self, instance):
        self.manager.current = "login"


# -------------------------------------------------
# TELA INICIAL (ATUALIZADA COM LOJA E RANKING)
# -------------------------------------------------
class TelaInicial(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        self.setup_background(layout)
        self.adicionar_decoracao_fundo(layout)

        # Logo Principal
        logo = Image(source="matemas.webp", size_hint=(0.70, None), height=dp(160), allow_stretch=True, keep_ratio=True, pos_hint={"center_x": 0.5, "top": 0.98})
        layout.add_widget(logo)

        # --- BOTÕES DO MENU (REORGANIZADOS PARA 5 BOTÕES) ---

        # 1. JOGAR
        botao_jogar = ImageButton(source="jogar.webp", size_hint=(None, None), size=(400, 160), pos_hint={"center_x": 0.5, "center_y": 0.75})
        botao_jogar.bind(on_release=lambda *a: self.seleciona_n())
        layout.add_widget(botao_jogar)

        # 2. ESTUDAR
        botao_conteudos = ImageButton(source="conteudos.webp", size_hint=(None, None), size=(400, 160), pos_hint={"center_x": 0.5, "center_y": 0.60})
        botao_conteudos.bind(on_release=lambda *a: self.acao_conteudos())
        layout.add_widget(botao_conteudos)

        # 3. TUTORIAL
        botao_tutorial = ImageButton(source="tutorial.webp", size_hint=(None, None), size=(400, 160), pos_hint={"center_x": 0.5, "center_y": 0.45})
        botao_tutorial.bind(on_release=lambda *a: self.acao_tutorial())
        layout.add_widget(botao_tutorial)

        # 4. RANKING
        botao_ranking = ImageButton(source="ranking.webp", size_hint=(None, None), size=(400, 160), pos_hint={"center_x": 0.5, "center_y": 0.30})
        botao_ranking.bind(on_release=lambda *a: self.acao_ranking())
        layout.add_widget(botao_ranking)

        # 5. LOJA (NOVO)
        botao_loja = ImageButton(source="loja.webp", size_hint=(None, None), size=(400, 160), pos_hint={"center_x": 0.5, "center_y": 0.15})
        botao_loja.bind(on_release=lambda *a: self.acao_loja())
        layout.add_widget(botao_loja)

        # --- Ícones do Topo ---
        # Logout
        login_button = MDIconButton(icon="logout", icon_size=dp(32), theme_text_color="Custom", text_color=(0, 0, 0, 1), pos_hint={"x": 0.02, "top": 0.98})
        login_button.bind(on_release=lambda x: self.fazer_logout())
        layout.add_widget(login_button)

        # Configurações
        settings_button = MDIconButton(icon="cog", icon_size=dp(32), theme_text_color="Custom", text_color=(0, 0, 0, 1), pos_hint={"right": 0.98, "top": 0.98})
        settings_button.bind(on_release=lambda *a: self.abrir_tela_config())
        layout.add_widget(settings_button)
        self.add_widget(layout)

    def setup_background(self, layout):
        layout.add_widget(Image(source="fundoapp.png", allow_stretch=True, keep_ratio=False, size_hint=(1, 1)))

    def adicionar_decoracao_fundo(self, layout):
        icones = ["calculator-variant", "shape-outline", "chart-pie", "ruler", "function-variant", "pi", "sigma"]
        positions = [{"x": 0.05, "y": 0.85}, {"x": 0.85, "y": 0.9}, {"x": 0.1, "y": 0.6}, {"x": 0.85, "y": 0.6}, {"x": 0.05, "y": 0.15}, {"x": 0.9, "y": 0.2}]
        for pos in positions:
            layout.add_widget(MDIconButton(icon=choice(icones), theme_text_color="Custom", text_color=(0, 0, 0, 0.08), pos_hint=pos, icon_size=dp(45), disabled=True))

    def seleciona_n(self):
        if self.manager: self.manager.current = "jogar"

    def acao_conteudos(self):
        if self.manager: self.manager.current = "conteudos"

    def acao_tutorial(self):
        if self.manager: self.manager.current = "tutorial"

    def acao_ranking(self):
        if self.manager: self.manager.current = "ranking"

    def acao_loja(self):
        if self.manager: self.manager.current = "loja"

    def abrir_tela_config(self):
        PainelConfiguracoes().open()

    def fazer_logout(self):
        # Chama o logout no APP (limpa sessão e vai pra login)
        app = MDApp.get_running_app()
        app.limpar_sessao()
        if self.manager: self.manager.current = "login"

# -------------------------------------------------
# TELA DE CONTEÚDOS
# -------------------------------------------------
class TelaConteudos(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        layout.add_widget(Image(source="fundoapp.png", allow_stretch=True, keep_ratio=False, size_hint=(1, 1)))
        self.adicionar_decoracao_fundo(layout)
        container_botoes = BoxLayout(orientation="vertical", spacing=dp(15), padding=[0, dp(20), 0, dp(20)], size_hint=(0.55, 0.75), pos_hint={"center_x": 0.5, "center_y": 0.5})
        topicos = [("Estudos/novo_Operacoes.webp", "tela"), ("Estudos/novo_Algebra.webp", "algebra_tela"), ("Estudos/novo_Geometria.webp", "geometria_tela"), ("Estudos/novo_Grandezas.webp", "grandezas_tela"), ("Estudos/novo_Estatistica.webp", "estatistica_tela")]
        for img, tela in topicos:
            btn_img = ImageButton(source=img, size_hint=(1, 1), allow_stretch=True, keep_ratio=True)
            btn_img.bind(on_release=lambda *a, t=tela: self.ir_para(t))
            container_botoes.add_widget(btn_img)
        layout.add_widget(container_botoes)
        back_button = MDIconButton(icon="arrow-left", pos_hint={"x": 0, "top": 1}, theme_text_color="Custom", text_color=(0, 0, 0, 1))
        back_button.bind(on_release=lambda *a: self.voltar())
        layout.add_widget(back_button)
        self.add_widget(layout)

    def adicionar_decoracao_fundo(self, layout):
        icones = ["book-open-page-variant", "lightbulb-outline", "school", "pencil", "notebook", "calculator", "brain"]
        positions = [{"x": 0.05, "y": 0.9}, {"x": 0.85, "y": 0.88}, {"x": 0.02, "y": 0.5}, {"x": 0.9, "y": 0.55}, {"x": 0.05, "y": 0.1}, {"x": 0.85, "y": 0.15}]
        for pos in positions:
            layout.add_widget(MDIconButton(icon=choice(icones), theme_text_color="Custom", text_color=(0, 0, 0, 0.08), pos_hint=pos, icon_size=dp(45), disabled=True))

    def ir_para(self, tela_destino):
        if tela_destino in self.manager.screen_names: self.manager.current = tela_destino
        else: print(f"⚠️ Tela '{tela_destino}' não existe!")

    def voltar(self): self.manager.current = "inicial"

# -------------------------------------------------
# TELA DE CONFIGURAÇÕES
# -------------------------------------------------
class PainelConfiguracoes(ModalView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0.4)
        self.auto_dismiss = False
        self.size_hint = (1, 1)
        self.painel_width = 0.85
        self.painel = MDBoxLayout(orientation='vertical', padding=[0, 0, 0, 0], spacing=0, size_hint=(self.painel_width, 1), md_bg_color=(0.96, 0.96, 0.98, 1))
        self.add_widget(self.painel)

        header_box = MDBoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(60), padding=[dp(15), 0, dp(15), 0], md_bg_color=(1, 1, 1, 1))
        header_box.add_widget(MDLabel(text="Configurações", font_style="H6", theme_text_color="Custom", text_color=PRETO, bold=True, valign="center"))
        header_box.add_widget(MDIconButton(icon="close", icon_size=dp(24), theme_text_color="Custom", text_color=PRETO_70, on_release=lambda *a: self.fechar(), pos_hint={'center_y': 0.5}))
        self.painel.add_widget(header_box)

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        conteudo = MDBoxLayout(orientation="vertical", spacing=dp(20), size_hint_y=None, adaptive_height=True, padding=[dp(20), dp(20), dp(20), dp(40)])

        card_perfil = MDCard(orientation="vertical", size_hint_y=None, height=dp(190), padding=dp(20), spacing=dp(10), radius=[dp(20)], elevation=1, md_bg_color=(1, 1, 1, 1))
        linha_topo = MDBoxLayout(orientation="horizontal", spacing=dp(15), size_hint_y=None, height=dp(60))
        linha_topo.add_widget(Image(source="matemas.webp", size_hint=(None, None), size=(dp(55), dp(55)), allow_stretch=True))
        box_nome = MDBoxLayout(orientation="vertical", pos_hint={'center_y': 0.5}, spacing=dp(2))
        linha_nome_edit = MDBoxLayout(orientation="horizontal", spacing=dp(5), adaptive_height=True)

        # O nome no painel de configurações poderia ser puxado do usuário atual
        app = MDApp.get_running_app()
        nome_jogador = app.user_nome if hasattr(app, 'user_nome') and app.user_nome else "Convidado"

        linha_nome_edit.add_widget(MDLabel(text=f"Jogador: {nome_jogador}", font_style="H6", theme_text_color="Custom", text_color=PRETO, bold=True, adaptive_size=True))
        linha_nome_edit.add_widget(MDIcon(icon="pencil-outline", font_size=dp(16), theme_text_color="Hint", pos_hint={'center_y': 0.6}))
        box_nome.add_widget(linha_nome_edit)
        box_nome.add_widget(MDLabel(text="Iniciante (Nível 1)", theme_text_color="Custom", text_color=LILAS, font_style="Caption", bold=True))
        linha_topo.add_widget(box_nome)
        card_perfil.add_widget(linha_topo)

        box_xp = MDBoxLayout(orientation="vertical", spacing=dp(5), size_hint_y=None, height=dp(35))
        linha_txt_xp = MDBoxLayout(orientation="horizontal")
        linha_txt_xp.add_widget(MDLabel(text="XP", bold=True, theme_text_color="Secondary", font_style="Overline"))
        linha_txt_xp.add_widget(MDLabel(text="120 / 500", halign="right", theme_text_color="Primary", bold=True, font_style="Caption"))
        box_xp.add_widget(linha_txt_xp)
        box_xp.add_widget(MDProgressBar(value=24, color=LILAS, size_hint_y=None, height=dp(10)))
        card_perfil.add_widget(box_xp)

        linha_stats = MDBoxLayout(orientation="horizontal", spacing=dp(10), size_hint_y=None, height=dp(40))
        def criar_stat(icone, valor, cor_icone):
            box = MDCard(orientation="horizontal", padding=[dp(8), dp(4)], spacing=dp(5), radius=[dp(8)], md_bg_color=(0.95, 0.95, 0.95, 1), elevation=0, size_hint=(1, 1))
            box.add_widget(MDIcon(icon=icone, theme_text_color="Custom", text_color=cor_icone, font_size=dp(18), pos_hint={'center_y': 0.5}))
            box.add_widget(MDLabel(text=valor, theme_text_color="Primary", font_style="Caption", bold=True, pos_hint={'center_y': 0.5}, halign="center"))
            return box
        linha_stats.add_widget(criar_stat("fire", "3", CORAL))
        linha_stats.add_widget(criar_stat("trophy", "12", (1, 0.8, 0, 1)))
        linha_stats.add_widget(criar_stat("bitcoin", "850", LILAS))
        card_perfil.add_widget(linha_stats)
        conteudo.add_widget(card_perfil)

        card_prefs = MDCard(orientation="vertical", size_hint_y=None, adaptive_height=True, padding=[dp(20), dp(20), dp(20), dp(10)], radius=[dp(20)], elevation=1, md_bg_color=(1, 1, 1, 1))
        card_prefs.add_widget(MDLabel(text="Preferências", theme_text_color="Custom", text_color=LILAS, font_style="Subtitle2", bold=True, adaptive_height=True))
        card_prefs.add_widget(MDBoxLayout(size_hint_y=None, height=dp(15)))
        box_tema = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50))
        box_tema.add_widget(MDIcon(icon="theme-light-dark", pos_hint={"center_y": 0.5}, theme_text_color="Secondary"))
        box_tema.add_widget(MDBoxLayout(size_hint_x=None, width=dp(15)))
        box_tema.add_widget(MDLabel(text="Modo Escuro", pos_hint={"center_y": 0.5}, theme_text_color="Primary", bold=False))
        self.switch_tema = MDSwitch(pos_hint={"center_y": 0.5}, widget_style="ios", active=(MDApp.get_running_app().theme_cls.theme_style == "Dark"))
        self.switch_tema.bind(active=self.atualizar_tema)
        box_tema.add_widget(self.switch_tema)
        card_prefs.add_widget(box_tema)

        box_som = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50))
        box_som.add_widget(MDIcon(icon="volume-high", pos_hint={"center_y": 0.5}, theme_text_color="Secondary"))
        box_som.add_widget(MDBoxLayout(size_hint_x=None, width=dp(15)))
        box_som.add_widget(MDLabel(text="Efeitos Sonoros", pos_hint={"center_y": 0.5}, theme_text_color="Primary"))
        self.switch_som = MDSwitch(pos_hint={"center_y": 0.5}, widget_style="ios", active=True)
        self.switch_som.bind(active=self.atualizar_som)
        box_som.add_widget(self.switch_som)
        card_prefs.add_widget(box_som)

        card_prefs.add_widget(MDBoxLayout(size_hint_y=None, height=dp(20)))
        self.label_volume = MDLabel(text="Volume: 75%", theme_text_color="Secondary", font_style="Caption", halign="left")
        card_prefs.add_widget(self.label_volume)
        self.slider_volume = MDSlider(min=0, max=100, value=75, hint=False, size_hint_y=None, height=dp(20), color=LILAS)
        self.slider_volume.bind(value=self.atualizar_volume)
        card_prefs.add_widget(self.slider_volume)
        card_prefs.add_widget(MDBoxLayout(size_hint_y=None, height=dp(10)))
        conteudo.add_widget(card_prefs)

        card_suporte = MDCard(orientation="vertical", size_hint_y=None, adaptive_height=True, padding=dp(20), spacing=dp(10), radius=[dp(20)], elevation=1, md_bg_color=(1, 1, 1, 1))
        card_suporte.add_widget(MDLabel(text="Ajuda & Suporte", theme_text_color="Custom", text_color=LILAS, font_style="Subtitle2", bold=True, adaptive_height=True))
        btn_report = MDRectangleFlatIconButton(icon="bug-outline", text="Reportar um problema", theme_text_color="Custom", text_color=PRETO_70, line_color=(0,0,0,0), icon_color=CORAL, size_hint_x=1, pos_hint={"center_x": 0.5})
        btn_dev = MDRectangleFlatIconButton(icon="code-tags", text="Desenvolvedores", theme_text_color="Custom", text_color=PRETO_70, line_color=(0,0,0,0), icon_color=LILAS, size_hint_x=1, pos_hint={"center_x": 0.5})
        card_suporte.add_widget(btn_report)
        card_suporte.add_widget(MDBoxLayout(size_hint_y=None, height=dp(1), md_bg_color=(0.9, 0.9, 0.9, 1)))
        card_suporte.add_widget(btn_dev)
        conteudo.add_widget(card_suporte)

        conteudo.add_widget(MDLabel(text="Versão 1.0.0 Alpha", halign="center", theme_text_color="Hint", font_style="Caption"))
        scroll.add_widget(conteudo)
        self.painel.add_widget(scroll)

    def atualizar_volume(self, instance, value): self.label_volume.text = f"Volume: {int(value)}%"
    def atualizar_tema(self, instance, value): MDApp.get_running_app().mudar_tema_global(value)
    def atualizar_som(self, instance, value):
        app = MDApp.get_running_app()
        if hasattr(app, 'som_ligado'): app.som_ligado = value

    def open(self, *args):
        super().open()
        self.painel.x = self.width
        Animation(x=self.width * (1 - self.painel_width), d=0.3, t='out_quart').start(self.painel)

    def fechar(self, *args):
        anim = Animation(x=self.width, d=0.2, t='in_quart')
        anim.bind(on_complete=lambda *a: ModalView.dismiss(self))
        anim.start(self.painel)

    def on_touch_down(self, touch):
        if not self.painel.collide_point(*touch.pos):
            self.fechar()
            return True
        return super().on_touch_down(touch)

# IMPORTS GAMES E TELAS AUXILIARES
# IMPORTS GAMES E TELAS AUXILIARES
# -----------------------------------------------------------
# Bloco 1: Telas essenciais de navegação (Tutorial, MeiaTela, Ranking, Loja)
try:
    from jogar import TelaJogar, TelaEscolhaNivel
    from tutorial import TelaTutorial
    from ranking import TelaRanking
    from loja import TelaLoja
    from meia_tela import TelaRepresentacoes, MeiaTela, OperacoesDefinicoesTela
    from meia_algebra import AlgebraTela, AlgebraRepresentacoes, AlgebraDefinicoesTela
    from meia_grandezas import GrandezasTela, GrandezasRepresentacoes, GrandezasDefinicoesTela
    from meia_geometria import GeometriaRepresentacoes, GeometriaDefinicoesTela, GeometriaTela
    from meia_estatistica import EstatisticaTela, EstatisticaRepresentacoes, EstatisticaDefinicoesTela
except ImportError as e:
    print(f"[ERRO CRITICO] Falha ao importar telas base: {e}")
    # Definindo classes dummy para não quebrar o build
    class TelaTutorial(Screen): pass
    class TelaRanking(Screen): pass
    class TelaLoja(Screen): pass

# Bloco 2: Jogos padrão
try:
    from jogar import JogosPrimario, JogosFundamental, JogosMedio
    from velha_matematica import JogoDaVelhaScreen
    from cross_nova import CruzadinhaScreen
    from calculo import calculoI, TelaFimDeJogo
    from algebra import AlgebraGameScreen, TelaFimAlgebra
    from fracoes import FracoesGameScreen, TelaFimFracoes
    from sudoku_logic import TelaSudoku, TelaDefinicaoSudoku
    from fracoes1 import TelaFracoesInfo, TelaFracoesRepresentacoes, TelaFracoesExplicacoes, TelaFracoesPropriedades
    from jogo_geometria import GeometriaGameScreen
    from jogo_estatistica import EstatisticaGameScreen,TelaFimEstatistica
except ImportError as e:
    print(f"[AVISO] Alguns jogos padrão não foram encontrados: {e}")

# Bloco 3: Jogos Novos / Instáveis (Chuva de Números)
try:
    from jogo_chuva import ChuvaNumerosScreen
except ImportError:
    print("[AVISO] Jogo 'Chuva de Números' não encontrado. Criando tela temporária.")
    # CRIANDO UMA TELA TEMPORÁRIA PARA EVITAR CRASH
    class ChuvaNumerosScreen(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(20))
            layout.add_widget(MDLabel(text="Jogo 'Chuva de Números'\nEm desenvolvimento ou arquivo não encontrado.", halign="center", theme_text_color="Error"))
            btn = MDRaisedButton(text="Voltar", pos_hint={"center_x": 0.5})
            btn.bind(on_release=lambda x: setattr(self.manager, "current", "inicial"))
            layout.add_widget(btn)
            self.add_widget(layout)

# Bloco 4: Jogo Novo / Boliche (O CAUSADOR DO ERRO)
try:
    from boliche_matematico import BolicheMatematicoScreen
except ImportError:
    print("[AVISO] Jogo 'Boliche' não encontrado. Criando tela temporária.")
    # CRIANDO UMA TELA TEMPORÁRIA PARA EVITAR CRASH
    class BolicheMatematicoScreen(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(20))
            layout.add_widget(MDLabel(text="Jogo 'Boliche Matemático'\nEm desenvolvimento ou arquivo não encontrado.", halign="center", theme_text_color="Error"))
            btn = MDRaisedButton(text="Voltar", pos_hint={"center_x": 0.5})
            btn.bind(on_release=lambda x: setattr(self.manager, "current", "inicial"))
            layout.add_widget(btn)
            self.add_widget(layout)

# Bloco 5: Jogo Novo / Pac-Man Matemático
try:
    from pacman import PacManMatematicoScreen
except ImportError:
    print("[AVISO] Jogo 'Pac-Man' não encontrado. Criando tela temporária.")
    # CRIANDO UMA TELA TEMPORÁRIA PARA EVITAR CRASH
    class PacManMatematicoScreen(Screen):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            layout = MDBoxLayout(orientation="vertical", padding=dp(20), spacing=dp(20))
            layout.add_widget(MDLabel(text="Jogo 'Pac-Man Matemático'\nEm desenvolvimento ou arquivo não encontrado.", halign="center", theme_text_color="Error"))
            btn = MDRaisedButton(text="Voltar", pos_hint={"center_x": 0.5})
            btn.bind(on_release=lambda x: setattr(self.manager, "current", "inicial"))
            layout.add_widget(btn)
            self.add_widget(layout)

# ---------- App Principal ----------
class TesteApp(MDApp):
    def build(self):
        # --- VARIÁVEIS GLOBAIS DO USUÁRIO ---
        self.user_id = None
        self.user_nome = None
        self.user_email = None

        sm = ScreenManager()

        # 1. Login e Cadastro
        sm.add_widget(TelaLogin(name="login"))
        sm.add_widget(TelaCadastro(name="cadastro"))

        # 2. Telas principais
        sm.add_widget(TelaInicial(name="inicial"))
        sm.add_widget(TelaConteudos(name="conteudos"))
        sm.add_widget(TelaTutorial(name="tutorial"))
        sm.add_widget(TelaJogar(name="jogar"))

        # --- ROTAS NOVAS (RANKING E LOJA) ---
        sm.add_widget(TelaRanking(name="ranking"))
        sm.add_widget(TelaLoja(name="loja"))

        # --- JOGO CHUVA ---
        sm.add_widget(ChuvaNumerosScreen(name="chuva_numeros"))

        # 3. Niveis
        sm.add_widget(TelaEscolhaNivel(name="primario", dificuldade="primario", titulo="Fundamental I", tela_voltar="jogar"))
        sm.add_widget(TelaEscolhaNivel(name="fundamental", dificuldade="fundamental", titulo="Fundamental II", tela_voltar="jogar"))
        sm.add_widget(TelaEscolhaNivel(name="medio", dificuldade="medio", titulo="Ensino Médio", tela_voltar="jogar"))

        # 4. Jogos
        sm.add_widget(calculoI(name="game1", dificuldade="primario"))
        sm.add_widget(calculoI(name="game2", dificuldade="fundamental"))
        sm.add_widget(calculoI(name="game3", dificuldade="medio"))
        sm.add_widget(CruzadinhaScreen(name="cross_p", dificuldade="fundI"))
        sm.add_widget(CruzadinhaScreen(name="cross_f", dificuldade="fundII"))
        sm.add_widget(CruzadinhaScreen(name="cross", dificuldade="medio"))
        sm.add_widget(AlgebraGameScreen(name="algebra"))
        sm.add_widget(TelaFimAlgebra(name="fim_algebra"))
        sm.add_widget(FracoesGameScreen(name="fracoes"))
        sm.add_widget(TelaSudoku(name="sudoku"))
        sm.add_widget(TelaDefinicaoSudoku(name="definicao_sudoku"))
        sm.add_widget(GeometriaGameScreen(name="jogo_geometria"))
        sm.add_widget(EstatisticaGameScreen(name="jogo_estatistica"))
        sm.add_widget(JogoDaVelhaScreen(name="velha"))
        sm.add_widget(BolicheMatematicoScreen(name="boliche_matematico"))
        sm.add_widget(PacManMatematicoScreen(name="pacman_matematico")) # <--- ADICIONADO O PAC-MAN AQUI
        # 5. Telas de Info/Estudo
        sm.add_widget(TelaFracoesInfo(name="fracoes_info"))
        sm.add_widget(TelaFracoesPropriedades(name="fracoes_propriedades"))
        sm.add_widget(TelaFracoesRepresentacoes(name="fracoes_representacoes"))
        sm.add_widget(TelaFracoesExplicacoes(name="fracoes_explicacoes"))
        sm.add_widget(TelaFimDeJogo(name="fim_de_jogo"))
        sm.add_widget(TelaFimEstatistica(name="fim_estatistica"))

        sm.add_widget(OperacoesDefinicoesTela(name="definicoes"))
        sm.add_widget(TelaRepresentacoes(name="representacoes"))
        sm.add_widget(MeiaTela(name="tela"))
        sm.add_widget(GrandezasRepresentacoes(name="grandezas_representacoes"))
        sm.add_widget(GrandezasTela(name="grandezas_tela"))
        sm.add_widget(GrandezasDefinicoesTela(name="grandezas_definicoes"))
        sm.add_widget(GeometriaTela(name="geometria_tela"))
        sm.add_widget(GeometriaDefinicoesTela(name="geometria_definicoes"))
        sm.add_widget(GeometriaRepresentacoes(name="geometria_representacoes"))
        sm.add_widget(AlgebraTela(name="algebra_tela"))
        sm.add_widget(AlgebraRepresentacoes(name="algebra_representacoes"))
        sm.add_widget(AlgebraDefinicoesTela(name="algebra_definicoes"))
        sm.add_widget(EstatisticaTela(name="estatistica_tela"))
        sm.add_widget(EstatisticaRepresentacoes(name="estatistica_representacoes"))
        sm.add_widget(EstatisticaDefinicoesTela(name="estatistica_definicoes"))

        return sm

    def on_start(self):
        """Verifica se existe sessão salva ao iniciar o app"""
        if self.carregar_sessao_local():
            print("[INIT] Sessão encontrada. Indo para Inicio.")
            # Acesso à ScreenManager via self.root (pois build retorna sm)
            self.root.current = "inicial"
        else:
            print("[INIT] Sem sessão. Indo para Login.")
            self.root.current = "login"

    # --- GERENCIAMENTO DE SESSÃO ---
    def salvar_sessao(self, user_id):
        try:
            with open("session.json", "w") as f:
                json.dump({"user_id": user_id}, f)
        except Exception as e:
            print(f"Erro ao salvar sessão: {e}")

    def carregar_sessao_local(self):
        if not os.path.exists("session.json"):
            return False
        try:
            with open("session.json", "r") as f:
                data = json.load(f)
                user_id = data.get("user_id")
                if user_id:
                    # Busca dados no banco usando o ID salvo
                    sucesso, msg, dados = banco_dados.obter_usuario_por_id(user_id)
                    if sucesso:
                        self.user_id = dados['id']
                        self.user_nome = dados['nome']
                        self.user_email = dados.get('email')
                        return True
        except Exception as e:
            print(f"Erro ao ler sessão: {e}")
            self.limpar_sessao()
        return False

    def limpar_sessao(self):
        if os.path.exists("session.json"):
            os.remove("session.json")
        self.user_id = None
        self.user_nome = None

    def mudar_tema_global(self, is_dark):
        self.theme_cls.theme_style = "Dark" if is_dark else "Light"

if __name__ == "__main__":
    TesteApp().run()