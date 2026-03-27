import random
from kivy.app import App
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivy.uix.modalview import ModalView
from kivy.metrics import dp

# Cores
COR_FUNDO = (0.95, 0.95, 0.95, 1)
COR_LOUSA = (0.1, 0.2, 0.15, 1) # Verde escuro de quadro negro
COR_GIZ = (0.9, 0.9, 0.9, 1)
COR_PRIMARIA = (0.2, 0.4, 0.8, 1)
COR_ERRO = (0.8, 0.2, 0.2, 1)
COR_ACERTO = (0.2, 0.7, 0.3, 1)

# ============================================================================
# WIDGET: LOUSA DIGITAL PARA RASCUNHO
# ============================================================================
class LousaDigital(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.linhas = []
        with self.canvas.before:
            Color(*COR_LOUSA)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.atualizar_bg, size=self.atualizar_bg)

    def atualizar_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            with self.canvas:
                Color(*COR_GIZ)
                linha = Line(points=(touch.x, touch.y), width=dp(1.5))
                self.linhas.append(linha)
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.collide_point(*touch.pos):
            if self.linhas:
                self.linhas[-1].points += [touch.x, touch.y]
            return True
        return super().on_touch_move(touch)

    def limpar(self):
        self.canvas.clear()
        with self.canvas.before:
            Color(*COR_LOUSA)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.linhas = []


# ============================================================================
# TELA PRINCIPAL: TUTOR DE ÁLGEBRA
# ============================================================================
class TutorEquacaoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.a = 0
        self.b = 0
        self.c = 0
        self.x_correto = 0
        self._setup_ui()
        self.gerar_equacao()

    def _setup_ui(self):
        layout = MDBoxLayout(orientation='vertical', padding=dp(15), spacing=dp(15), md_bg_color=COR_FUNDO)

        # Cabeçalho da Equação
        card_eq = MDCard(orientation='vertical', size_hint_y=None, height=dp(100), radius=[15], padding=dp(10), md_bg_color=(1,1,1,1), elevation=2)
        card_eq.add_widget(MDLabel(text="RESOLVA A EQUAÇÃO NO QUADRO:", halign="center", font_style="Caption", theme_text_color="Hint"))

        self.lbl_equacao = MDLabel(text="3x + 5 = 20", halign="center", font_style="H4", bold=True, theme_text_color="Custom", text_color=COR_PRIMARIA)
        card_eq.add_widget(self.lbl_equacao)
        layout.add_widget(card_eq)

        # Lousa de Rascunho
        self.lousa = LousaDigital(size_hint_y=1)

        card_lousa = MDCard(orientation='vertical', radius=[10], elevation=4)
        card_lousa.add_widget(self.lousa)

        btn_limpar = MDFlatButton(text="APAGAR RASCUNHO", theme_text_color="Custom", text_color=(0.7,0.7,0.7,1), on_release=lambda x: self.lousa.limpar())
        card_lousa.add_widget(btn_limpar)

        layout.add_widget(card_lousa)

        # Entrada de Resposta
        box_resposta = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(60), spacing=dp(10))

        self.input_resposta = MDTextField(hint_text="Digite o valor final de X", input_filter="float", mode="fill")
        box_resposta.add_widget(self.input_resposta)

        btn_verificar = MDRaisedButton(text="VERIFICAR", size_hint_y=1, md_bg_color=COR_PRIMARIA, on_release=self.verificar_resposta)
        box_resposta.add_widget(btn_verificar)

        layout.add_widget(box_resposta)
        self.add_widget(layout)

    def gerar_equacao(self):
        self.lousa.limpar()
        self.input_resposta.text = ""

        # Gera uma equação ax + b = c que resulte num número inteiro para facilitar
        self.a = random.randint(2, 6)
        self.x_correto = random.randint(2, 9)
        self.b = random.randint(1, 15) * random.choice([1, -1]) # Pode ser positivo ou negativo

        self.c = (self.a * self.x_correto) + self.b

        sinal_b = f"+ {self.b}" if self.b > 0 else f"- {abs(self.b)}"
        self.lbl_equacao.text = f"{self.a}x {sinal_b} = {self.c}"

    def verificar_resposta(self, instance):
        if not self.input_resposta.text:
            return

        try:
            x_aluno = float(self.input_resposta.text.replace(",", "."))
        except ValueError:
            return

        if x_aluno == self.x_correto:
            self.mostrar_feedback(True, "Cálculo Perfeito!", "Você isolou o X corretamente.")
        else:
            # ENGENHARIA REVERSA DO ERRO (Error Pattern Analysis)
            motivo_erro = self.analisar_erro(x_aluno)
            self.mostrar_feedback(False, "Há um erro lógico!", motivo_erro)

    def analisar_erro(self, x_aluno):
        # 1. Erro de Sinal na Transição do 'b'
        # Em vez de passar subtraindo, passou somando (ou vice-versa)
        erro_sinal_b = (self.c + self.b) / self.a

        # 2. Esqueceu de passar o 'a' dividindo (Parou na metade)
        erro_nao_dividiu = self.c - self.b

        # 3. Errou o sinal do 'b' E não dividiu
        erro_sinal_e_nao_dividiu = self.c + self.b

        # 4. Inverteu a divisão (dividiu 'a' pelo resultado em vez do resultado por 'a')
        if (self.c - self.b) != 0:
            erro_divisao_invertida = self.a / (self.c - self.b)
        else:
            erro_divisao_invertida = None

        # Verificação do padrão
        if x_aluno == erro_sinal_b:
            if self.b > 0:
                return "Você errou no primeiro passo! O número estava somando e você o passou para o outro lado somando de novo. Lembre-se de INVERTER o sinal."
            else:
                return "Você errou no primeiro passo! O número estava subtraindo e você o passou para o outro lado subtraindo. Lembre-se de INVERTER o sinal para mais."

        elif x_aluno == erro_nao_dividiu:
            return f"Você passou o {abs(self.b)} para o outro lado corretamente, mas parou aí! Você esqueceu de passar o {self.a} dividindo o resultado."

        elif x_aluno == erro_sinal_e_nao_dividiu:
            return "Cuidado! Você cometeu dois erros: não inverteu o sinal ao passar o número pro outro lado, e também esqueceu de dividir pelo número colado no X."

        elif x_aluno == erro_divisao_invertida:
            return "Na hora de dividir, você colocou os números na ordem errada! O número que está acompanhando o X é o que vai para baixo (denominador)."

        else:
            return "Parece ter havido um erro de aritmética básica (soma, subtração ou divisão errada no rascunho). Revise as suas contas na lousa!"

    def mostrar_feedback(self, acertou, titulo, mensagem):
        cor = COR_ACERTO if acertou else COR_ERRO
        icone = "school" if acertou else "alert-circle-outline"

        content = MDBoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        content.add_widget(MDIcon(icon=icone, halign="center", font_size="64sp", theme_text_color="Custom", text_color=cor))
        content.add_widget(MDLabel(text=titulo, halign="center", bold=True, font_style="H5", theme_text_color="Custom", text_color=cor))
        content.add_widget(MDLabel(text=mensagem, halign="center", theme_text_color="Secondary"))

        if acertou:
            btn_txt = "PRÓXIMA EQUAÇÃO"
            acao = self.proxima_fase
        else:
            btn_txt = "TENTAR CORRIGIR"
            acao = self.fechar_modal

        btn = MDRaisedButton(text=btn_txt, pos_hint={'center_x': 0.5}, md_bg_color=cor, on_release=acao)
        content.add_widget(btn)

        self.modal = ModalView(size_hint=(0.85, 0.45), auto_dismiss=False, background_color=(0,0,0,0.6))
        card = MDCard(radius=[20], md_bg_color=(1,1,1,1))
        card.add_widget(content)
        self.modal.add_widget(card)
        self.modal.open()

    def fechar_modal(self, instance):
        self.modal.dismiss()

    def proxima_fase(self, instance):
        self.modal.dismiss()
        self.gerar_equacao()

# Inicializador do App para testar separadamente
class AppTutor(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        sm = ScreenManager()
        sm.add_widget(TutorEquacaoScreen(name="tutor"))
        return sm

if __name__ == '__main__':
    AppTutor().run()