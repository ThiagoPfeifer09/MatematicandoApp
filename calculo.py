from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.screen import MDScreen
from kivy.uix.label import Label
from kivymd.uix.button import MDRaisedButton, MDIconButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDIcon
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle
from kivy.animation import Animation
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.properties import StringProperty
import random
import banco_dados
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
class calculoI(MDScreen):
    dificuldade = StringProperty("primario")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.timer = 0
        self.running = False
        self.modo = "normal"
        self.operacao = "Soma"
        self.rodadas = 5

        # Variáveis de Controle
        self.nivel_atual = 1
        self.nivel_max = 4
        self.nivel_selecionado = 1
        self.tudo_desbloqueado = False

        # Pontuação
        self.pontos_nivel = 0
        self.acertos_total = 0
        self.erros_total = 0

        # --- LAYOUT PRINCIPAL ---
        layout = FloatLayout()
        try:
            self.bg_image = Image(source='fundoapp.png', allow_stretch=True, keep_ratio=False)
            layout.add_widget(self.bg_image)
        except:
            pass

        # --- CABEÇALHO ---
        layout.add_widget(MDIconButton(
            icon="arrow-left",
            pos_hint={"x": 0.02, "top": 0.98},
            theme_text_color="Custom",
            text_color=(0, 0, 0, 1),
            on_release=self.ir_para_niveis
        ))

        layout.add_widget(Label(
            text="MATEMATICANDO",
            font_size="24sp",
            bold=True,
            color=(0, 0, 0, 1),
            pos_hint={"center_x": 0.5, "center_y": 0.96}
        ))

        # ==========================================================
        # --- ÁREA DE ESTATÍSTICAS (POSICIONAMENTO AJUSTADO) ---
        # ==========================================================

        def criar_linha_stat(texto, y_pos, icon_name, icon_color):
            icon = MDIcon(
                icon=icon_name,
                pos_hint={"center_x": 0.08, "center_y": y_pos},
                theme_text_color="Custom",
                text_color=icon_color,
                font_size="22sp"
            )
            lbl = Label(
                text=texto,
                font_size="15sp",
                bold=True,
                color=(0, 0, 0, 1),
                halign="left",
                valign="middle",
                pos_hint={"x": 0.12, "center_y": y_pos},
                size_hint=(0.4, None),
                height=dp(40)
            )
            lbl.bind(size=lbl.setter('text_size'))
            return icon, lbl

        # Posições Y ajustadas para não cortar
        self.icon_score, self.lbl_score_val = criar_linha_stat("Pontos: 0", 0.92, "star", (0.9, 0.7, 0, 1))
        layout.add_widget(self.icon_score); layout.add_widget(self.lbl_score_val)

        self.icon_acerto, self.lbl_acerto_val = criar_linha_stat("Acertos: 0", 0.88, "check-circle", (0, 0.6, 0, 1))
        layout.add_widget(self.icon_acerto); layout.add_widget(self.lbl_acerto_val)

        self.icon_erro, self.lbl_erro_val = criar_linha_stat("Erros: 0", 0.84, "close-circle", (0.8, 0, 0, 1))
        layout.add_widget(self.icon_erro); layout.add_widget(self.lbl_erro_val)

        # ==========================================================
        # --- ÁREA DA CONTA (MAIS PARA CIMA) ---
        # ==========================================================
        self.layout_conta = BoxLayout(
            orientation='vertical', size_hint=(None, None), width=dp(240), height=dp(240),
            # Alterado para top: 0.80
            pos_hint={"center_x": 0.5, "top": 0.9}, spacing=dp(2)
        )

        self.lbl_num1 = Label(text="", font_size="55sp", bold=True, color=(0,0,0,1), halign="right", valign="bottom", size_hint_y=0.45)
        self.lbl_num1.bind(size=self.lbl_num1.setter('text_size'))
        self.layout_conta.add_widget(self.lbl_num1)

        line_2_layout = BoxLayout(orientation='horizontal', size_hint_y=0.25)
        self.lbl_operador = Label(text="+", font_size="40sp", bold=True, color=(0,0,0,1), size_hint_x=0.3, halign="left", valign="center")
        self.lbl_operador.bind(size=self.lbl_operador.setter('text_size'))

        self.lbl_num2 = Label(text="", font_size="55sp", bold=True, color=(0,0,0,1), size_hint_x=0.7, halign="right", valign="center")
        self.lbl_num2.bind(size=self.lbl_num2.setter('text_size'))

        line_2_layout.add_widget(self.lbl_operador); line_2_layout.add_widget(self.lbl_num2)
        self.layout_conta.add_widget(line_2_layout)

        self.linha_separadora = Widget(size_hint_y=None, height=dp(4))
        with self.linha_separadora.canvas:
            Color(0, 0, 0, 1)
            self.rect_linha = Rectangle(pos=self.linha_separadora.pos, size=self.linha_separadora.size)
            self.linha_separadora.bind(pos=self.atualiza_linha, size=self.atualiza_linha)
        self.layout_conta.add_widget(self.linha_separadora)

        input_row = BoxLayout(orientation='horizontal', size_hint_y=0.30, spacing=dp(5))
        self.answer_input = MDTextField(
            hint_text="?", halign="center", font_size="35sp", multiline=False, mode="rectangle",
            line_color_normal=(0,0,0,0), line_color_focus=(0,0,0,0),
            text_color_normal=(0,0,0,1), text_color_focus=(0,0,0,1), size_hint_x=0.65
        )
        self.answer_input.bind(text=self.check_responder_button)
        input_row.add_widget(self.answer_input)

        self.responder_button = MDRaisedButton(
            text="OK", size_hint=(0.35, 0.9), font_size="18sp", pos_hint={"center_y": 0.5},
            md_bg_color=(0, 0, 0.8, 1), text_color=(1, 1, 1, 1), elevation=2, on_release=self.verifica_resposta,
        )
        self.responder_button.disabled = True
        input_row.add_widget(self.responder_button)
        self.layout_conta.add_widget(input_row)
        layout.add_widget(self.layout_conta)

        # ==========================================================
        # --- TECLADO E NÍVEIS ---
        # ==========================================================
        col_x_teclado = [0.15, 0.40, 0.65]; col_x_nivel = 0.88
        base_y_teclado = 0.15; gap_y = 0.08
        btn_num_size = (0.16, None); btn_num_height = dp(45); num_bg_color = (0.2, 0.6, 0.8, 1)
        rows_y = [base_y_teclado, base_y_teclado + gap_y, base_y_teclado + gap_y*2, base_y_teclado + gap_y*3, base_y_teclado + gap_y*4]

        layout.add_widget(Label(text="Nível", font_size="16sp", color=(0,0,0,1), bold=True, pos_hint={"center_x": col_x_nivel, "center_y": rows_y[4]}))

        self.nivel_botoes = {}
        nivel_cores = [(0, 0.6, 0, 1), (0, 0, 0.8, 1), (0.6, 0, 0.6, 1), (0.5, 0.5, 0.5, 1)]
        indices_visuais = [3, 2, 1, 0]

        for i, (level, color) in enumerate(zip(range(1, self.nivel_max + 1), nivel_cores)):
            row_idx = indices_visuais[i]
            btn = MDRaisedButton(
                text=f"{level}", size_hint=(0.12, None), height=btn_num_height,
                pos_hint={"center_x": col_x_nivel, "center_y": rows_y[row_idx]},
                text_color=(0, 0, 0, 1) if level != self.nivel_atual else (1,1,1,1),
                on_release=lambda _, lvl=level: self.inicia_nivel(lvl),
            )
            btn.original_color = color
            if level == self.nivel_atual:
                btn.disabled = False; btn.md_bg_color = btn.original_color; btn.text_color = (1, 1, 1, 1)
            else:
                btn.disabled = True; btn.md_bg_color = (0.8, 0.8, 0.8, 1); btn.text_color = (0, 0, 0, 0.5)
            self.nivel_botoes[level] = btn
            layout.add_widget(btn)

        mapa_teclado = [(1, 0, 2), (2, 1, 2), (3, 2, 2), (4, 0, 3), (5, 1, 3), (6, 2, 3), (7, 0, 4), (8, 1, 4), (9, 2, 4), (0, 1, 1)]
        for numero, col_idx, row_idx in mapa_teclado:
            layout.add_widget(MDRaisedButton(
                text=str(numero), size_hint=btn_num_size, height=btn_num_height,
                pos_hint={"center_x": col_x_teclado[col_idx], "center_y": rows_y[row_idx]},
                md_bg_color=num_bg_color, text_color=(0, 0, 0, 1), font_size="26sp",
                on_release=lambda _, nmb=numero: self.instancia_numero(nmb),
            ))

        layout.add_widget(MDRaisedButton(text="-", size_hint=btn_num_size, height=btn_num_height, pos_hint={"center_x": col_x_teclado[0], "center_y": rows_y[1]}, md_bg_color=num_bg_color, text_color=(0, 0, 0, 1), font_size="28sp", on_release=self.minus_insert))
        layout.add_widget(MDRaisedButton(text=",", size_hint=btn_num_size, height=btn_num_height, pos_hint={"center_x": col_x_teclado[2], "center_y": rows_y[1]}, md_bg_color=num_bg_color, text_color=(0, 0, 0, 1), font_size="28sp", on_release=self.point_insert))
        layout.add_widget(MDRaisedButton(text="Apagar", size_hint=(0.20, None), height=dp(35), pos_hint={"center_x": col_x_teclado[0], "center_y": rows_y[0]}, font_size="14sp", md_bg_color=(0.8, 0.4, 0.4, 1), text_color=(0, 0, 0, 1), on_release=self.apagar_numero))
        layout.add_widget(MDRaisedButton(text="Limpar", size_hint=(0.20, None), height=dp(35), pos_hint={"center_x": col_x_teclado[2], "center_y": rows_y[0]}, font_size="14sp", md_bg_color=(0.8, 0.4, 0.4, 1), text_color=(0, 0, 0, 1), on_release=self.limpar_resposta))

        self.timer_label = Label(text="00:00:00", font_size="28sp", color=(0, 0, 0, 1), pos_hint={"center_x": 0.5, "center_y": 0.08})
        layout.add_widget(self.timer_label)

        control_buttons = [("Parar", 0.30, self.pause_timer, (0.6, 0, 0.6, 1)), ("Reiniciar", 0.70, self.reiniciar_jogo_btn, (0, 0, 0.8, 1))]
        for text, pos_x, callback, color in control_buttons:
            layout.add_widget(MDRaisedButton(text=text, size_hint=(0.25, None), height=dp(35), font_size="14sp", pos_hint={"center_x": pos_x, "center_y": 0.03}, md_bg_color=color, text_color=(1, 1, 1, 1), on_release=callback))

        self.add_widget(layout)

    # --- MÉTODOS DE LÓGICA ---

    def on_pre_enter(self, *args):
        """ Executado TODA vez que a tela vai aparecer. Garante o reset. """
        self.reiniciar_jogo()

    def reiniciar_jogo(self):
        """ Reseta o jogo mantendo as configurações (dificuldade/operação). """
        self.reset_timer()
        self.pontos_nivel = 0
        self.acertos_total = 0
        self.erros_total = 0
        self.nivel_atual = 1
        self.nivel_selecionado = 1

        # Limpa campos
        self.lbl_num1.text = ""
        self.lbl_num2.text = ""
        self.lbl_operador.text = ""
        self.answer_input.text = ""
        self.responder_button.disabled = True

        self.atualiza_labels_stats()

        # Reseta botões de nível visualmente
        if hasattr(self, 'nivel_botoes'):
            for lvl, btn in self.nivel_botoes.items():
                if lvl == 1:
                    btn.disabled = False
                    btn.md_bg_color = btn.original_color
                    btn.text_color = (1, 1, 1, 1)
                else:
                    btn.disabled = True
                    btn.md_bg_color = (0.8, 0.8, 0.8, 1)
                    btn.text_color = (0, 0, 0, 0.5)

        # Inicia o nível 1 imediatamente
        self.inicia_nivel(1)

    def reiniciar_jogo_btn(self, instance):
        # Wrapper para o botão "Reiniciar" da UI
        self.reiniciar_jogo()

    def confirma_rodadas(self, rodadas_value):
        if rodadas_value > 0: self.rodadas = rodadas_value
        else: self.rodadas = 5

    def escolha_modo(self, modo):
        self.modo = modo

    def atualiza_linha(self, instance, value):
        self.rect_linha.pos = instance.pos
        self.rect_linha.size = instance.size

    def atualizar_display_conta(self, texto_num1, texto_num2, operador_simbolo, eh_tres_termos=False):
        if eh_tres_termos:
            self.lbl_num1.font_size = "35sp"
            self.lbl_num1.text = texto_num1
        else:
            self.lbl_num1.font_size = "55sp"
            self.lbl_num1.text = texto_num1

        self.lbl_num2.text = texto_num2
        self.lbl_operador.text = operador_simbolo

    def minus_insert(self, instance):
        if len(self.answer_input.text) < 5: self.answer_input.text += "-"

    def point_insert(self, instance):
        if len(self.answer_input.text) < 5: self.answer_input.text += ","

    def check_responder_button(self, *args):
        if getattr(self, 'nivel_selecionado', None) and self.answer_input.text.strip():
            self.responder_button.disabled = False
            self.responder_button.md_bg_color = (0, 0, 0.8, 1)
        else:
            self.responder_button.disabled = True
            self.responder_button.md_bg_color = (0.5, 0.5, 0.5, 1)

    def instancia_numero(self, numero):
        if len(self.answer_input.text) < 5: self.answer_input.text += str(numero)

    def apagar_numero(self, instance):
        self.answer_input.text = self.answer_input.text[:-1]

    def limpar_resposta(self, instance):
        self.answer_input.text = ""

    def define_dificul(self, dificuldade):
        self.dificuldade = dificuldade
        # Não resetamos aqui, o on_pre_enter fará isso

    def define_operacao(self, operacao):
        validas = ["soma", "subtracao", "multiplicacao", "divisao"]
        if operacao.lower() in validas: self.operacao = operacao.capitalize()

    def inicia_nivel(self, level):
        if level > self.nivel_atual: return

        self.nivel_selecionado = level
        self.pontos_nivel = 0
        self.atualiza_labels_stats()
        self.answer_input.hint_text = "..."
        Clock.schedule_once(self.comecar_nivel, 0.5)

    def comecar_nivel(self, dt):
        self.answer_input.hint_text = "?"
        self.start_timer()
        self.cria_questao()

    # --- LÓGICA DE CRIAÇÃO (COM DECIMAIS E INTEIROS) ---
    def gerar_numero(self, min_v, max_v, casas):
        """Gera int ou float dependendo das casas decimais."""
        if casas == 0:
            return random.randint(min_v, max_v)
        else:
            val = random.uniform(min_v, max_v)
            return round(val, casas)

    def cria_questao(self):
        dificuldades_especificas = ["primario", "fundamental", "medio"]
        if self.dificuldade in dificuldades_especificas: self.cria_questaopersonalizada()
        elif self.modo == "normal": self.cria_questaonormal()
        else: self.cria_questaopersonalizada()

    def cria_questaonormal(self):
        min_v, max_v = 1, 10
        num1 = random.randint(min_v, max_v)
        num2 = random.randint(min_v, max_v or 1)
        self.montar_conta(num1, num2)

    def cria_questaopersonalizada(self):
        min_v = 1
        max_v = 10
        casas_decimais = 0

        # --- LÓGICA DE DIFICULDADE E NÍVEIS ---

        if self.dificuldade == "primario":
            # PRIMÁRIO: Apenas Inteiros (0 casas), Max Progressivo
            casas_decimais = 0
            if self.nivel_atual == 1: max_v = 5
            elif self.nivel_atual == 2: max_v = 10
            elif self.nivel_atual == 3: max_v = 15
            else: max_v = 20

        elif self.dificuldade == "fundamental":
            # FUNDAMENTAL: Inteiros (1-3), Decimal 1 casa (4)
            max_v = 50
            if self.nivel_atual <= 3:
                casas_decimais = 0
            else:
                casas_decimais = 1
                max_v = 20 # Reduz teto para decimais

        elif self.dificuldade == "medio":
            # MÉDIO: Decimais mistos
            max_v = 100
            if self.nivel_atual <= 2:
                casas_decimais = 1
            else:
                casas_decimais = 2

        # --- GERAÇÃO DOS NÚMEROS ---
        n1 = self.gerar_numero(min_v, max_v, casas_decimais)
        n2 = self.gerar_numero(min_v, max_v, casas_decimais)

        # Regra para usar 3 termos (Apenas Médio Nível 3+)
        usar_3_termos = (self.dificuldade == "medio" and self.nivel_atual >= 3)
        n3 = 0

        if usar_3_termos:
            n3 = self.gerar_numero(min_v, max_v, casas_decimais)
            self.montar_conta(n1, n2, n3)
        else:
            self.montar_conta(n1, n2)

    def montar_conta(self, n1, n2, n3=None):
        simbolo = "+"
        # Normaliza o nome da operação
        op_raw = self.operacao.lower()
        if "soma" in op_raw: op = "Soma"
        elif "sub" in op_raw: op = "Subtracao"
        elif "mult" in op_raw: op = "Multiplicacao"
        elif "div" in op_raw: op = "Divisao"
        else: op = "Soma"

        # Função interna para formatar (ponto -> vírgula)
        def fmt(n):
            if isinstance(n, float):
                if n.is_integer(): return str(int(n))
                return f"{n}".replace('.', ',')
            return str(n)

        # === LÓGICA DE 3 TERMOS (MÉDIO) ===
        if n3 is not None:
            if op == "Soma":
                self.answer = round(n1 + n2 + n3, 2)
                simbolo = "+"
            elif op == "Subtracao":
                # Médio pode dar negativo
                self.answer = round(n1 - n2 - n3, 2)
                simbolo = "-"
            elif op == "Multiplicacao":
                # Reduz para não explodir
                n1, n2, n3 = [round(x/3, 1) for x in [n1, n2, n3]]
                self.answer = round(n1 * n2 * n3, 2)
                simbolo = "x"

            txt_num1 = f"{fmt(n1)}\n{fmt(n2)}"
            txt_num2 = fmt(n3)
            self.atualizar_display_conta(txt_num1, txt_num2, simbolo, eh_tres_termos=True)

        # === LÓGICA DE 2 TERMOS (PADRÃO) ===
        else:
            if op == "Soma":
                self.answer = round(n1 + n2, 2)
                simbolo = "+"

            elif op == "Subtracao":
                # PRIMÁRIO: Resultado deve ser positivo (N1 >= N2)
                if self.dificuldade == "primario":
                    if n2 > n1: n1, n2 = n2, n1

                self.answer = round(n1 - n2, 2)
                simbolo = "-"

            elif op == "Multiplicacao":
                # Ajuste para não ficar números gigantes
                if isinstance(n1, float) or isinstance(n2, float):
                    if n1 > 10: n1 = round(n1/2, 1)
                    if n2 > 10: n2 = round(n2/2, 1)

                self.answer = round(n1 * n2, 2)
                simbolo = "x"

            elif op == "Divisao":
                # LÓGICA ESPECIAL PARA DIVISÃO CONTROLADA
                # Gera Resposta e Divisor, calcula Dividendo

                divisor = random.randint(2, 10)
                resposta_desejada = 0

                if self.dificuldade == "primario":
                    # Resposta Inteira
                    resposta_desejada = random.randint(1, 10)

                elif self.dificuldade == "fundamental":
                    # Resposta com max 1 casa decimal
                    if self.nivel_atual == 4:
                        resposta_desejada = round(random.uniform(1, 10), 1)
                    else:
                        resposta_desejada = random.randint(1, 20)

                else: # Medio
                    # Resposta com max 2 casas
                    resposta_desejada = round(random.uniform(1, 20), 2)

                dividendo = round(resposta_desejada * divisor, 2)

                n1 = dividendo
                n2 = divisor
                self.answer = resposta_desejada
                simbolo = "÷"

            self.atualizar_display_conta(fmt(n1), fmt(n2), simbolo, eh_tres_termos=False)

    def verifica_resposta(self, *args):
        user_answer = self.answer_input.text.replace(',', '.')
        try:
            val = float(user_answer)
            # Margem de erro pequena para floats
            if abs(val - self.answer) < 0.01:
                self.acertos_total += 1; self.pontos_nivel += 1
            else:
                self.erros_total += 1; self.pontos_nivel = max(0, self.pontos_nivel - 1)
        except ValueError:
            self.answer_input.text = ""; return

        self.answer_input.text = ""
        self.atualiza_labels_stats()

        meta_pontos = self.rodadas if self.rodadas > 0 else 5
        if self.pontos_nivel >= meta_pontos:
            self.pause_timer()
            if self.nivel_atual < self.nivel_max:
                btn_atual = self.nivel_botoes[self.nivel_atual]
                btn_atual.disabled = True; btn_atual.md_bg_color = (0.8, 0.8, 0.8, 1); btn_atual.text_color = (0, 0, 0, 0.5)

                self.nivel_atual += 1; self.pontos_nivel = 0

                next_btn = self.nivel_botoes[self.nivel_atual]
                next_btn.disabled = False; next_btn.md_bg_color = next_btn.original_color; next_btn.text_color = (1, 1, 1, 1)

                self.disparar_comemoracao()
                self.atualiza_labels_stats()
                Clock.schedule_once(lambda dt: self.inicia_nivel(self.nivel_atual), 2)
            else:
                self.ir_para_tela_fim_de_jogo()
        else:
            self.cria_questao()

    def atualiza_labels_stats(self):
        self.lbl_score_val.text = f"Pontos Nível: {self.pontos_nivel}"
        self.lbl_acerto_val.text = f"Acertos: {self.acertos_total}"
        self.lbl_erro_val.text = f"Erros: {self.erros_total}"

    def start_timer(self, *args):
        if not self.running:
            self.running = True
            Clock.schedule_interval(self.att_timer, 1)

    def pause_timer(self, *args):
        self.running = False
        Clock.unschedule(self.att_timer)

    def reset_timer(self, *args):
        self.pause_timer()
        self.timer = 0
        self.timer_label.text = "00:00:00"

    def att_timer(self, dt):
        self.timer += 1
        m, s = divmod(self.timer, 60)
        h, m = divmod(m, 60)
        self.timer_label.text = f"{h:02}:{m:02}:{s:02}"

    def ir_para_niveis(self, instance):
        if self.manager.has_screen("escolha"): self.manager.current = "escolha"
        elif self.manager.has_screen("jogar"): self.manager.current = "jogar"
        else: print("Tela anterior não encontrada no Manager")

    def disparar_comemoracao(self):
        layout = self.children[0]
        try:
            for _ in range(25):
                b = Image(source='balao.png', size_hint=(None,None), size=(dp(random.randint(50,80)), dp(random.randint(50,80))), opacity=0.8)
                b.color = (random.random(), random.random(), random.random(), 1)
                b.x = random.uniform(0, self.width - b.width)
                b.y = -dp(100)
                layout.add_widget(b)
                anim = Animation(pos=(b.x + random.uniform(-dp(100), dp(100)), self.height + dp(50)), opacity=0, duration=random.uniform(2.5, 5.0), t='out_quad')
                anim.bind(on_complete=lambda a, w: layout.remove_widget(w))
                anim.start(b)
        except: pass

    def ir_para_tela_fim_de_jogo(self):
        if self.manager.has_screen("fim_de_jogo"):
            fim = self.manager.get_screen("fim_de_jogo")
            fim.atualizar_stats(self.timer_label.text, self.operacao, self.acertos_total + self.erros_total, self.acertos_total, self.erros_total, self.dificuldade)
            self.manager.current = "fim_de_jogo"


from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.floatlayout import FloatLayout
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.app import App
import threading
import banco_dados

# Cores Padronizadas
COR_PRIMARIA = (0.2, 0.6, 0.8, 1)
COR_VERDE_SUCESSO = (0.2, 0.7, 0.2, 1)
COR_TEXTO = (0.1, 0.1, 0.1, 1)

class TelaFimDeJogo(MDScreen):
    """
    Tela de Fim para Operações / Cálculo
    Agora padronizada com o mesmo estilo das outras.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.dados_partida = {}
        self._construir_interface()

    def _construir_interface(self):
        layout = FloatLayout()
        try:
            bg = Image(source='fundoapp.png', allow_stretch=True, keep_ratio=False)
            layout.add_widget(bg)
        except: pass

        card = MDCard(
            size_hint=(0.85, 0.7),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            elevation=8,
            radius=[25],
            orientation='vertical',
            padding=dp(20),
            spacing=dp(10),
            md_bg_color=(0.95, 0.95, 0.98, 1)
        )

        self.titulo_lbl = MDLabel(
            text="FIM DE JOGO!",
            halign="center",
            font_style="H4",
            bold=True,
            theme_text_color="Custom",
            text_color=COR_PRIMARIA,
            size_hint_y=None, height=dp(40)
        )

        self.resumo_box = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None, height=dp(100))
        self.acertos_lbl = MDLabel(text="Acertos: 0", halign="center", font_style="Subtitle1", theme_text_color="Custom", text_color=COR_TEXTO)
        self.erros_lbl = MDLabel(text="Erros: 0", halign="center", font_style="Subtitle1", theme_text_color="Custom", text_color=COR_TEXTO)
        self.tempo_lbl = MDLabel(text="Tempo: 00:00", halign="center", font_style="Subtitle1", theme_text_color="Custom", text_color=COR_TEXTO)
        self.nivel_lbl = MDLabel(text="Nível: -", halign="center", font_style="Subtitle2", theme_text_color="Hint")

        self.resumo_box.add_widget(self.acertos_lbl)
        self.resumo_box.add_widget(self.erros_lbl)
        self.resumo_box.add_widget(self.tempo_lbl)
        self.resumo_box.add_widget(self.nivel_lbl)

        self.input_nome = MDTextField(
            hint_text="Digite seu nome",
            helper_text="Para o ranking",
            icon_right="account",
            size_hint_x=0.9,
            pos_hint={'center_x': 0.5}
        )

        self.btn_salvar = MDRaisedButton(
            text="SALVAR PONTUAÇÃO",
            size_hint_x=0.9,
            pos_hint={'center_x': 0.5},
            md_bg_color=COR_VERDE_SUCESSO,
            text_color=(1,1,1,1),
            on_release=self.acao_salvar
        )

        self.status_lbl = MDLabel(
            text="", halign="center", font_style="Caption",
            theme_text_color="Hint", size_hint_y=None, height=dp(20)
        )

        btn_voltar = MDRaisedButton(
            text="MENU PRINCIPAL",
            size_hint_x=0.9,
            pos_hint={'center_x': 0.5},
            md_bg_color=COR_PRIMARIA,
            text_color=(1,1,1,1),
            on_release=self.voltar_menu
        )

        card.add_widget(self.titulo_lbl)
        card.add_widget(self.resumo_box)
        card.add_widget(self.input_nome)
        card.add_widget(self.btn_salvar)
        card.add_widget(self.status_lbl)
        card.add_widget(Widget())
        card.add_widget(btn_voltar)

        layout.add_widget(card)
        self.add_widget(layout)

    def atualizar_stats(self, tempo, operacao, rodadas, acertos, erros, nivel):
        # Adaptação dos parâmetros do jogo de cálculo
        dificuldade_formatada = "Fundamental"
        d = str(nivel).lower()
        if "prim" in d: dificuldade_formatada = "Primário"
        elif "medio" in d or "médio" in d: dificuldade_formatada = "Médio"
        elif "fund" in d: dificuldade_formatada = "Fundamental"

        self.dados_partida = {
            "acertos": acertos, "erros": erros, "tempo": tempo,
            "dificuldade": dificuldade_formatada
        }

        self.acertos_lbl.text = f"Acertos: {acertos}"
        self.erros_lbl.text = f"Erros: {erros}"
        self.tempo_lbl.text = f"Tempo: {tempo}"
        self.nivel_lbl.text = f"Nível: {dificuldade_formatada}"

        # Opcional: Você pode querer adicionar a operação no título ou na dificuldade
        # Ex: self.nivel_lbl.text = f"{dificuldade_formatada} ({operacao})"

        self.input_nome.text = ""
        self.status_lbl.text = ""
        self.btn_salvar.disabled = False
        self.btn_salvar.text = "SALVAR PONTUAÇÃO"

        if acertos >= 8:
            self.titulo_lbl.text = "PARABÉNS!"
            self.titulo_lbl.text_color = COR_VERDE_SUCESSO
        else:
            self.titulo_lbl.text = "FIM DE JOGO"
            self.titulo_lbl.text_color = COR_PRIMARIA

    def acao_salvar(self, instance):
        nome = self.input_nome.text.strip()
        if not nome:
            self.status_lbl.text = "Digite um nome!"
            self.status_lbl.theme_text_color = "Error"
            return
        self.btn_salvar.disabled = True
        self.status_lbl.text = "Enviando..."
        self.status_lbl.theme_text_color = "Hint"
        threading.Thread(target=self._salvar_thread, args=(nome,)).start()

    def _salvar_thread(self, nome):
        sucesso, msg = banco_dados.salvar_partida(
            nome=nome,
            escola="Escola Padrão",
            jogo="Operações", # Nome do jogo de cálculo
            dificuldade=self.dados_partida['dificuldade'],
            acertos=self.dados_partida['acertos'],
            erros=self.dados_partida['erros'],
            tempo=self.dados_partida['tempo']
        )
        Clock.schedule_once(lambda dt: self._pos_salvar(sucesso, msg))

    def _pos_salvar(self, sucesso, msg):
        self.status_lbl.text = msg
        if sucesso:
            self.btn_salvar.text = "SALVO!"
            self.status_lbl.theme_text_color = "Custom"
            self.status_lbl.text_color = COR_VERDE_SUCESSO
        else:
            self.btn_salvar.disabled = False
            self.status_lbl.theme_text_color = "Error"

    def voltar_menu(self, instance):
        self.manager.current = "jogar"