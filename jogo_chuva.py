from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton, MDFillRoundFlatButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivy.clock import Clock
from kivy.metrics import dp
from random import randint, choice

# --- CORES ---
CORAL = (1, 0.44, 0.26, 1)
LILAS = (0.65, 0.55, 0.98, 1)
VERDE_SUCESSO = (0.2, 0.8, 0.2, 1)
BRANCO = (1, 1, 1, 1)
CINZA_TXT = (0.5, 0.5, 0.5, 1)
AZUL_CLARO_FUNDO = (0.7, 0.85, 0.95, 1)
DOURADO_CRITICO = (1, 0.84, 0, 1)

class GotaMatematica(MDCard):
    def __init__(self, conta_str, resultado_correto, velocidade, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(110), dp(60))
        self.md_bg_color = (1, 1, 1, 0.95)
        self.radius = [dp(10)]
        self.elevation = 3
        
        self.conta_str = conta_str
        self.resultado = resultado_correto
        self.velocidade = velocidade
        self.destacada = False

        self.label = MDLabel(
            text=conta_str, 
            halign="center", 
            valign="center",
            bold=True, 
            theme_text_color="Custom", 
            text_color=(0.2, 0.2, 0.2, 1),
            font_style="H6"
        )
        self.add_widget(self.label)

    def destacar_dica(self):
        if not self.destacada:
            self.md_bg_color = VERDE_SUCESSO
            self.label.text_color = BRANCO
            self.destacada = True
            Clock.schedule_once(self.remover_destaque, 1.5)

    def remover_destaque(self, dt):
        if self.destacada:
            self.md_bg_color = (1, 1, 1, 0.95)
            self.label.text_color = (0.2, 0.2, 0.2, 1)
            self.destacada = False

    def transformar_em_bloco_fixo(self):
        self.md_bg_color = VERDE_SUCESSO 
        self.label.text_color = BRANCO
        self.label.text = str(self.resultado)
        self.elevation = 1

class ChuvaNumerosScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_active = False
        self.pontos = 0
        self.vidas = 3
        self.acertos = 0
        self.erros = 0
        self.alvo_atual = 0
        self.tempo_restante = 60
        self.combo = 0
        self.multiplicador = 1
        
        self.gotas = [] 
        self.pilha_blocos = [] 
        self.dificuldade = "Primario"
        
        self.evento_spawn = None
        self.evento_update = None
        self.evento_tempo = None
        self.dialog = None
        self.menu_dificuldade = None
        self.keys_pressed = set()
        
        self.speed_base = dp(2)
        self.spawn_rate = 2.5
        self.dicas_disponiveis = 3

        # === LAYOUT PRINCIPAL ===
        self.main_box = MDBoxLayout(orientation="vertical", md_bg_color=AZUL_CLARO_FUNDO)
        self.game_area = FloatLayout(size_hint_y=1)

        # -- HUD --
        btn_voltar = MDIconButton(
            icon="arrow-left", pos_hint={"x": 0.02, "top": 0.98}, 
            on_release=self.sair_jogo
        )
        self.game_area.add_widget(btn_voltar)

        self.lbl_pontos = MDLabel(
            text="Pontos: 0", halign="center", pos_hint={"center_x": 0.5, "top": 0.95}, 
            bold=True, theme_text_color="Custom", text_color=CORAL, font_style="H5"
        )
        self.game_area.add_widget(self.lbl_pontos)

        self.lbl_stats_extra = MDLabel(
            text="Tempo: 60s | Combo: 0", halign="center", pos_hint={"center_x": 0.5, "top": 0.88},
            theme_text_color="Custom", text_color=CINZA_TXT, font_style="Caption"
        )
        self.game_area.add_widget(self.lbl_stats_extra)
        
        box_vidas = MDBoxLayout(
            orientation="horizontal", adaptive_size=True, spacing=dp(5),
            pos_hint={"right": 0.95, "top": 0.95}
        )
        box_vidas.add_widget(MDIcon(icon="heart", theme_text_color="Custom", text_color=CORAL))
        self.lbl_vidas = MDLabel(text="3", bold=True, theme_text_color="Custom", text_color=CORAL, adaptive_size=True)
        box_vidas.add_widget(self.lbl_vidas)
        self.game_area.add_widget(box_vidas)

        # -- JOGADOR --
        self.jogador = MDCard(
            orientation="vertical", size_hint=(None, None), size=(dp(120), dp(90)),
            radius=[dp(15), dp(15), 0, 0], md_bg_color=LILAS, elevation=4, y=dp(90) 
        )
        self.jogador.add_widget(MDLabel(text="ALVO", halign="center", font_style="Caption", theme_text_color="Custom", text_color=(1,1,1,0.8)))
        self.lbl_alvo = MDLabel(text="?", halign="center", bold=True, theme_text_color="Custom", text_color=BRANCO, font_style="H3")
        self.jogador.add_widget(self.lbl_alvo)
        self.game_area.add_widget(self.jogador)

        self.btn_start = MDFillRoundFlatButton(
            text="JOGAR", font_size=dp(24), pos_hint={"center_x": 0.5, "center_y": 0.5},
            md_bg_color=CORAL, on_release=self.mostrar_tutorial
        )
        self.game_area.add_widget(self.btn_start)
        self.main_box.add_widget(self.game_area)

        # BARRA INFERIOR
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

    def resetar_dados(self):
        """ Limpa o jogo visualmente e logicamente """
        # Para todos os eventos ativos para evitar erros de widget sem parent
        if self.evento_update: self.evento_update.cancel()
        if self.evento_spawn: self.evento_spawn.cancel()
        if self.evento_tempo: self.evento_tempo.cancel()

        self.pontos = 0; self.vidas = 3; self.acertos = 0; self.erros = 0; 
        self.dicas_disponiveis = 3; self.tempo_restante = 60; self.combo = 0; self.multiplicador = 1
        
        self.lbl_pontos.text = "Pontos: 0"; self.lbl_vidas.text = "3"
        self.lbl_alvo.text = "?"
        self.lbl_pontos.text_color = CORAL
        self.lbl_stats_extra.text = "Tempo: 60s | Combo: 0"
        self.definir_dificuldade(self.dificuldade)
        
        # LIMPEZA VISUAL (Remove widgets da tela)
        for gota in self.gotas:
            if gota.parent: self.game_area.remove_widget(gota)
        self.gotas = []
        
        for bloco in self.pilha_blocos:
            if bloco.parent: self.game_area.remove_widget(bloco)
        self.pilha_blocos = []
        
        self.jogador.x = (Window.width / 2) - (self.jogador.width / 2)

    def atualizar_tempo(self, dt):
        if self.game_active:
            self.tempo_restante -= 1
            self.lbl_stats_extra.text = f"Tempo: {self.tempo_restante}s | Combo: {self.combo}"
            if self.tempo_restante <= 0:
                self.game_over("O tempo acabou!")

    def mostrar_tutorial(self, instance=None):
        self.definir_novo_alvo()
        if self.btn_start in self.game_area.children:
            self.game_area.remove_widget(self.btn_start)
        self.dialog = MDDialog(
            title="Novo Jogo", text=f"Alvo: [b]{self.alvo_atual}[/b].\nBoa sorte!", 
            buttons=[MDFlatButton(text="INICIAR", on_release=self.iniciar_partida_real)], 
            auto_dismiss=False
        )
        self.dialog.open()

    def iniciar_partida_real(self, instance):
        if self.dialog: self.dialog.dismiss()
        self.resetar_dados() # Limpa tudo antes de começar cronômetros
        self.game_active = True
        self.definir_novo_alvo() # Garante que o alvo da partida seja definido após o reset
        self.evento_update = Clock.schedule_interval(self.atualizar_jogo, 1.0/60.0)
        self.evento_spawn = Clock.schedule_interval(self.spawn_gota, self.spawn_rate)
        self.evento_tempo = Clock.schedule_interval(self.atualizar_tempo, 1)

    def verificar_captura(self, gota):
        if gota.resultado == self.alvo_atual:
            self.combo += 1
            self.multiplicador = 1 + (self.combo // 5)
            pontos_ganhos = 10 * self.multiplicador
            
            if randint(1, 100) <= (10 + self.combo):
                pontos_ganhos *= 2
                self.feedback_visual_critico()

            self.pontos += pontos_ganhos
            self.acertos += 1
            self.tempo_restante += 2 
            self.speed_base += dp(0.05)
            
            self.lbl_pontos.text = f"Pontos: {self.pontos} (x{self.multiplicador})"
            self.lbl_stats_extra.text = f"Tempo: {self.tempo_restante}s | Combo: {self.combo}"
            
            self.definir_novo_alvo()
            self.empilhar_bloco(gota)
            return True
        else:
            self.combo = 0
            self.multiplicador = 1
            self.erros += 1
            self.perder_vida()
            return False

    def feedback_visual_critico(self):
        self.lbl_pontos.text_color = DOURADO_CRITICO
        Clock.schedule_once(lambda dt: setattr(self.lbl_pontos, 'text_color', CORAL), 0.5)

    def spawn_gota(self, dt):
        if not self.game_active: return
        ops = ['+', '-']
        if self.dificuldade in ["Fundamental", "Medio"]: ops.append('x')
        if self.dificuldade == "Medio": ops.append('÷')
        
        if randint(1, 100) <= 40: resultado = self.alvo_atual
        else: resultado = self.alvo_atual + choice([-1, 1])
        
        op = choice(ops)
        if op == '+': b = randint(0, resultado); a = max(0, resultado - b)
        elif op == '-': b = randint(1, 10); a = resultado + b
        elif op == 'x': 
            fatores = [i for i in range(1, resultado + 1) if resultado % i == 0]
            a = choice(fatores) if fatores else 1; b = resultado // a
        else: b = randint(2, 5); a = resultado * b
            
        velocidade = self.speed_base + (self.pontos * 0.001)
        gota = GotaMatematica(f"{a} {op} {b}", resultado, velocidade)
        gota.x = randint(0, int(Window.width - gota.width))
        gota.y = Window.height
        self.game_area.add_widget(gota)
        self.gotas.append(gota)

    def atualizar_jogo(self, dt):
        if not self.game_active: return
        vel_manual = dp(15) 
        if 276 in self.keys_pressed or 97 in self.keys_pressed: self.mover_jogador(self.jogador.center_x - vel_manual)
        if 275 in self.keys_pressed or 100 in self.keys_pressed: self.mover_jogador(self.jogador.center_x + vel_manual)
        
        alvo_colisao = self.pilha_blocos[-1] if self.pilha_blocos else self.jogador
        to_remove = []
        for gota in self.gotas[:]:
            gota.y -= gota.velocidade
            if gota.collide_widget(alvo_colisao):
                if not self.verificar_captura(gota): to_remove.append(gota)
            elif gota.y < dp(0):
                to_remove.append(gota)

        for g in to_remove: 
            if g.parent: self.game_area.remove_widget(g)
            if g in self.gotas: self.gotas.remove(g)

    def empilhar_bloco(self, gota):
        if gota in self.gotas: self.gotas.remove(gota)
        topo = self.pilha_blocos[-1] if self.pilha_blocos else self.jogador
        gota.y = topo.top
        gota.x = self.jogador.center_x - (gota.width / 2)
        gota.transformar_em_bloco_fixo()
        self.pilha_blocos.append(gota)
        if gota.top >= Window.height - dp(100):
            self.game_over("Torre muito alta!")

    def game_over(self, motivo="Fim de Jogo"):
        self.game_active = False
        if self.evento_update: self.evento_update.cancel()
        if self.evento_spawn: self.evento_spawn.cancel()
        if self.evento_tempo: self.evento_tempo.cancel()
        
        self.dialog = MDDialog(
            title="GAME OVER", text=f"{motivo}\nPontos: {self.pontos}", 
            buttons=[MDFlatButton(text="SAIR", on_release=self.sair_jogo), 
                     MDFillRoundFlatButton(text="REPETIR", md_bg_color=CORAL, on_release=self.iniciar_partida_real)],
            auto_dismiss=False
        )
        self.dialog.open()

    def definir_novo_alvo(self):
        max_n = 15 if self.dificuldade == "Primario" else 30 if self.dificuldade == "Fundamental" else 50
        self.alvo_atual = randint(4, max_n)
        self.lbl_alvo.text = str(self.alvo_atual)

    def definir_dificuldade(self, dificuldade_str):
        self.dificuldade = dificuldade_str
        if dificuldade_str == "Primario": self.speed_base = dp(2); self.spawn_rate = 2.5
        elif dificuldade_str == "Fundamental": self.speed_base = dp(3.5); self.spawn_rate = 2.0
        else: self.speed_base = dp(5); self.spawn_rate = 1.5

    def abrir_menu_dificuldade(self, instance):
        if not self.menu_dificuldade:
            opcoes = [
                {"text": "Fácil", "viewclass": "OneLineListItem", "on_release": lambda: self.mudar_dificuldade("Primario")},
                {"text": "Médio", "viewclass": "OneLineListItem", "on_release": lambda: self.mudar_dificuldade("Fundamental")},
                {"text": "Difícil", "viewclass": "OneLineListItem", "on_release": lambda: self.mudar_dificuldade("Medio")},
            ]
            self.menu_dificuldade = MDDropdownMenu(caller=instance, items=opcoes, width_mult=4)
        self.menu_dificuldade.open()

    def mudar_dificuldade(self, cod):
        self.menu_dificuldade.dismiss()
        self.definir_dificuldade(cod)
        self.resetar_dados()
        self.mostrar_dialogo_simples("Dificuldade", f"Nível {cod} selecionado.")

    def mostrar_score(self, instance):
        self.mostrar_dialogo_simples("Placar", f"Pontos: {self.pontos}\nAcertos: {self.acertos}")

    def mostrar_dialogo_simples(self, tit, txt):
        self.dialog = MDDialog(title=tit, text=txt, buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())])
        self.dialog.open()

    def usar_dica(self, instance):
        if not self.game_active or self.dicas_disponiveis <= 0: return
        for g in self.gotas:
            if g.resultado == self.alvo_atual and not g.destacada:
                g.destacar_dica(); self.dicas_disponiveis -= 1; break

    def mover_jogador(self, target_x):
        new_x = target_x - (self.jogador.width / 2)
        new_x = max(0, min(new_x, Window.width - self.jogador.width))
        self.jogador.x = new_x
        for bloco in self.pilha_blocos:
            bloco.x = self.jogador.center_x - (bloco.width / 2)

    def on_enter(self):
        # GARANTE QUE AO ENTRAR NA TELA O JOGO ESTEJA LIMPO
        self.resetar_dados()
        if self.btn_start not in self.game_area.children:
            self.game_area.add_widget(self.btn_start)
            
        Window.bind(on_key_down=self._on_keyboard_down, on_key_up=self._on_keyboard_up, mouse_pos=self._on_mouse_move)
        
    def on_leave(self):
        Window.unbind(on_key_down=self._on_keyboard_down, on_key_up=self._on_keyboard_up, mouse_pos=self._on_mouse_move)
        self.game_active = False

    def _on_mouse_move(self, w, pos):
        if self.game_active and not self.dialog: self.mover_jogador(pos[0])
    def _on_keyboard_down(self, w, key, *args): self.keys_pressed.add(key)
    def _on_keyboard_up(self, w, key, *args): 
        if key in self.keys_pressed: self.keys_pressed.remove(key)
    def on_touch_down(self, touch):
        if self.game_active and not self.dialog and touch.y > dp(90): self.mover_jogador(touch.x)
        return super().on_touch_down(touch)
    def on_touch_move(self, touch):
        if self.game_active and not self.dialog and touch.y > dp(90): self.mover_jogador(touch.x)
    def perder_vida(self):
        self.vidas -= 1; self.lbl_vidas.text = str(self.vidas)
        if self.vidas <= 0: self.game_over("Fim das vidas!")
    def sair_jogo(self, *args):
        self.game_active = False
        self.resetar_dados() # Limpa a tela antes de sair
        if self.dialog: self.dialog.dismiss()
        if self.manager: self.manager.current = "inicial"