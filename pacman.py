from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFillRoundFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.graphics import Color, Rectangle, Ellipse, PushMatrix, PopMatrix, Rotate
from kivy.core.text import Label as CoreLabel
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.properties import StringProperty
from random import randint
import copy
import random

# Matriz do Labirinto (15x15)
# NOTA: Removidos os '3' fixos. Agora todo o mapa é só parede (1) e caminho (0 ou 2).
MAPA_ORIGINAL = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,1,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,0,1,0,1,1,0,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,1,1,1,0,1,1,2,1,1,0,1,1,1,1],
    [1,0,0,0,0,0,0,2,0,0,0,0,0,0,1],
    [1,0,1,1,0,1,1,2,1,1,0,1,1,0,1],
    [1,0,1,1,0,1,2,2,2,1,0,1,1,0,1],
    [1,0,1,1,0,1,1,1,1,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,0,1,1,1,1,1,0,1,1,1,1],
    [1,0,0,0,0,1,0,0,0,1,0,0,0,0,1],
    [1,0,1,1,0,1,0,1,0,1,0,1,1,0,1],
    [1,0,0,0,0,0,0,1,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]

class PacManMatematicoScreen(Screen):
    dificuldade = StringProperty("Primario")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        self.add_widget(self.layout)
        
        self.pontos = 0
        self.vidas = 3
        self.tempo = 60
        self.mapa_atual = []
        self.jogo_pausado = False
        
        # Animação e Posição do Pac-Man
        self.boca_aberta = True
        self.direcao_pacman = 'dir'
        self.pos_inicial_pacman = (7, 11)
        self.grid_x = self.pos_inicial_pacman[0]
        self.grid_y = self.pos_inicial_pacman[1]
        
        self.fantasmas = []
        
        # Matemática
        self.fator1 = 0
        self.fator2 = 0
        self.resposta_correta = 0
        self.opcoes_numeros = []
        self.posicoes_respostas = {} # DICIONÁRIO NOVO: Salva onde cada resposta caiu (x, y)
        
        self.tile_size = 0
        self.offset_x, self.offset_y = 0, 0
        self.relogio_tempo = None
        self.relogio_fantasmas = None
        self.relogio_animacao = None

    def on_enter(self):
        self.layout.clear_widgets()
        self.pontos = 0
        self.vidas = 3
        self.tempo = 60
        self.jogo_pausado = False
        
        self.setup_ui()
        self.iniciar_jogo_completo()
        
        Clock.schedule_once(self.desenhar_tudo, 0.1)
        self.relogio_tempo = Clock.schedule_interval(self.atualizar_tempo, 1.0)
        self.relogio_fantasmas = Clock.schedule_interval(self.mover_inimigos, 0.5) 
        self.relogio_animacao = Clock.schedule_interval(self.animar_boca, 0.15) 
        
        Window.bind(on_key_down=self._on_teclado)

    def on_leave(self):
        if self.relogio_tempo: self.relogio_tempo.cancel()
        if self.relogio_fantasmas: self.relogio_fantasmas.cancel()
        if self.relogio_animacao: self.relogio_animacao.cancel()
        Window.unbind(on_key_down=self._on_teclado)

    def _on_teclado(self, window, key, scancode, codepoint, modifier):
        if self.jogo_pausado or self.vidas <= 0 or self.tempo <= 0:
            return True
            
        if key == 273 or codepoint == 'w':    
            self.mover("cima")
        elif key == 274 or codepoint == 's':  
            self.mover("baixo")
        elif key == 276 or codepoint == 'a':  
            self.mover("esq")
        elif key == 275 or codepoint == 'd':  
            self.mover("dir")
            
        return True 

    def definir_dificuldade(self, diff):
        self.dificuldade = diff

    def animar_boca(self, dt):
        if not self.jogo_pausado:
            self.boca_aberta = not self.boca_aberta
            self.desenhar_tudo(0)

    def iniciar_jogo_completo(self):
        self.mapa_atual = copy.deepcopy(MAPA_ORIGINAL)
        self.grid_x, self.grid_y = self.pos_inicial_pacman
        self.direcao_pacman = 'dir'
        
        self.fantasmas = [
            {"x": 6, "y": 7, "cor": (1, 0, 0, 1)},    
            {"x": 8, "y": 7, "cor": (1, 0.5, 0, 1)}   
        ]
        self.gerar_nova_conta()

    # ==========================================
    # NOVO SISTEMA DE POSICIONAMENTO ALEATÓRIO
    # ==========================================
    def gerar_nova_conta(self):
        # 1. Limpa as bolas azuis antigas do mapa (transforma de volta em chão vazio '2')
        for r in range(len(self.mapa_atual)):
            for c in range(len(self.mapa_atual[0])):
                if self.mapa_atual[r][c] == 3:
                    self.mapa_atual[r][c] = 2

        # 2. Gera a matemática
        self.fator1, self.fator2 = randint(2, 9), randint(2, 9)
        self.resposta_correta = self.fator1 * self.fator2
        
        respostas = [self.resposta_correta]
        while len(respostas) < 4:
            erro = self.resposta_correta + randint(-12, 12)
            if erro not in respostas and erro > 0:
                respostas.append(erro)
        
        random.shuffle(respostas)
        self.opcoes_numeros = respostas
        
        # 3. Encontra todos os corredores que estão vazios ou com bolinhas
        locais_validos = []
        for r in range(len(self.mapa_atual)):
            for c in range(len(self.mapa_atual[0])):
                if self.mapa_atual[r][c] in [0, 2]:
                    # Evita colocar a resposta exatamente em cima do Pac-Man
                    if (c, r) != (self.grid_x, self.grid_y):
                        locais_validos.append((r, c))

        # 4. Sorteia 4 posições aleatórias para as novas respostas
        random.shuffle(locais_validos)
        locais_escolhidos = locais_validos[:4]

        self.posicoes_respostas = {}
        for i in range(4):
            linha_sorteada, coluna_sorteada = locais_escolhidos[i]
            self.mapa_atual[linha_sorteada][coluna_sorteada] = 3 # Coloca o círculo azul no mapa
            # Salva no dicionário: qual número está em qual posição x,y
            self.posicoes_respostas[(coluna_sorteada, linha_sorteada)] = respostas[i]
        
        if hasattr(self, 'lbl_equacao'):
            self.lbl_equacao.text = f"Calcule: {self.fator1} x {self.fator2}"

    def setup_ui(self):
        with self.layout.canvas.before:
            Color(0.05, 0.05, 0.05, 1)
            self.bg = Rectangle(size=(3000, 3000), pos=(0,0))
            
        hud_layout = MDBoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(50), pos_hint={"top": 1}, padding=[dp(5), 0, dp(15), 0], spacing=dp(5))
        
        btn_voltar = MDIconButton(icon="arrow-left", theme_text_color="Custom", text_color=(1, 1, 1, 1), on_release=self.voltar, pos_hint={"center_y": 0.5})
        self.lbl_vidas = MDLabel(text=f"Vidas: {self.vidas}", theme_text_color="Error", bold=True, halign="left")
        self.lbl_tempo = MDLabel(text=f"Tempo: {self.tempo}s", theme_text_color="Custom", text_color=(1,1,0,1), bold=True, halign="center")
        self.lbl_pontos = MDLabel(text=f"Pts: {self.pontos}", theme_text_color="Custom", text_color=(0.2, 0.8, 1, 1), bold=True, halign="right")
        
        hud_layout.add_widget(btn_voltar)
        hud_layout.add_widget(self.lbl_vidas)
        hud_layout.add_widget(self.lbl_tempo)
        hud_layout.add_widget(self.lbl_pontos)
        self.layout.add_widget(hud_layout)
            
        self.canvas_labirinto = FloatLayout()
        self.layout.add_widget(self.canvas_labirinto)

        self.lbl_equacao = MDLabel(text="", halign="center", theme_text_color="Custom", text_color=(1, 1, 1, 1), font_style="H4", pos_hint={"center_x": 0.5, "center_y": 0.20}, bold=True, size_hint_y=None, height=dp(40))
        self.layout.add_widget(self.lbl_equacao)

        self.lbl_feedback = MDLabel(text="", halign="center", theme_text_color="Custom", text_color=(0, 1, 0, 1), font_style="H4", pos_hint={"center_x": 0.5, "center_y": 0.60}, bold=True)
        self.layout.add_widget(self.lbl_feedback)

        self.btn_restart = MDFillRoundFlatButton(text="JOGAR NOVAMENTE", font_size=dp(18), pos_hint={"center_x": 0.5, "center_y": 0.45}, md_bg_color=(0, 0.8, 0.2, 1), text_color=(1, 1, 1, 1), opacity=0, disabled=True, on_release=self.reiniciar_jogo)
        self.layout.add_widget(self.btn_restart)

        self.layout.add_widget(MDIconButton(icon="arrow-up-bold-circle", icon_size=dp(50), theme_text_color="Custom", text_color=(0.3, 0.3, 0.3, 1), pos_hint={"center_x": 0.5, "y": 0.09}, on_release=lambda x: self.mover("cima")))
        self.layout.add_widget(MDIconButton(icon="arrow-down-bold-circle", icon_size=dp(50), theme_text_color="Custom", text_color=(0.3, 0.3, 0.3, 1), pos_hint={"center_x": 0.5, "y": 0.01}, on_release=lambda x: self.mover("baixo")))
        self.layout.add_widget(MDIconButton(icon="arrow-left-bold-circle", icon_size=dp(50), theme_text_color="Custom", text_color=(0.3, 0.3, 0.3, 1), pos_hint={"center_x": 0.35, "y": 0.05}, on_release=lambda x: self.mover("esq")))
        self.layout.add_widget(MDIconButton(icon="arrow-right-bold-circle", icon_size=dp(50), theme_text_color="Custom", text_color=(0.3, 0.3, 0.3, 1), pos_hint={"center_x": 0.65, "y": 0.05}, on_release=lambda x: self.mover("dir")))

    def atualizar_tempo(self, dt):
        if self.jogo_pausado: return
        if self.tempo > 0:
            self.tempo -= 1
            self.lbl_tempo.text = f"Tempo: {self.tempo}s"
        else:
            self.mostrar_game_over()

    def mover_inimigos(self, dt):
        if self.jogo_pausado: return
        direcoes = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for f in self.fantasmas:
            random.shuffle(direcoes)
            for dx, dy in direcoes:
                nx, ny = f["x"] + dx, f["y"] + dy
                if 0 <= ny < len(self.mapa_atual) and 0 <= nx < len(self.mapa_atual[0]):
                    if self.mapa_atual[ny][nx] != 1:
                        f["x"] = nx
                        f["y"] = ny
                        break
                        
        self.verificar_colisao_fantasmas()
        self.desenhar_tudo(0)

    def verificar_colisao_fantasmas(self):
        for f in self.fantasmas:
            if f["x"] == self.grid_x and f["y"] == self.grid_y:
                self.mostrar_feedback_rapido("O FANTASMA TE PEGOU!", (1, 0.5, 0, 1))
                self.perder_vida()
                break

    def perder_vida(self):
        self.vidas -= 1
        self.lbl_vidas.text = f"Vidas: {self.vidas}"
        if self.vidas > 0:
            self.grid_x, self.grid_y = self.pos_inicial_pacman
        else:
            self.mostrar_game_over()

    def mostrar_game_over(self):
        self.relogio_tempo.cancel()
        self.relogio_fantasmas.cancel()
        self.jogo_pausado = True
        
        self.lbl_equacao.text = ""
        self.lbl_feedback.text = "FIM DE JOGO!"
        self.lbl_feedback.text_color = (1, 0, 0, 1)
        
        self.btn_restart.opacity = 1
        self.btn_restart.disabled = False

    def reiniciar_jogo(self, instance):
        self.btn_restart.opacity = 0
        self.btn_restart.disabled = True
        self.lbl_feedback.text = ""
        
        self.pontos = 0
        self.vidas = 3
        self.tempo = 60
        self.lbl_vidas.text = f"Vidas: {self.vidas}"
        self.lbl_tempo.text = f"Tempo: {self.tempo}s"
        self.lbl_pontos.text = f"Pts: {self.pontos}"
        
        self.jogo_pausado = False
        self.iniciar_jogo_completo()
        
        if self.relogio_tempo: self.relogio_tempo.cancel()
        if self.relogio_fantasmas: self.relogio_fantasmas.cancel()
        self.relogio_tempo = Clock.schedule_interval(self.atualizar_tempo, 1.0)
        self.relogio_fantasmas = Clock.schedule_interval(self.mover_inimigos, 0.5) 
        self.desenhar_tudo(0)

    def mover(self, direcao):
        if self.vidas <= 0 or self.tempo <= 0 or self.jogo_pausado: return

        self.direcao_pacman = direcao

        nova_linha, nova_coluna = self.grid_y, self.grid_x

        if direcao == "cima": nova_linha -= 1
        elif direcao == "baixo": nova_linha += 1
        elif direcao == "esq": nova_coluna -= 1
        elif direcao == "dir": nova_coluna += 1

        if 0 <= nova_linha < len(self.mapa_atual) and 0 <= nova_coluna < len(self.mapa_atual[0]):
            valor_bloco = self.mapa_atual[nova_linha][nova_coluna]
            
            if valor_bloco != 1: 
                self.grid_x = nova_coluna
                self.grid_y = nova_linha
                
                if valor_bloco == 0:
                    self.mapa_atual[self.grid_y][self.grid_x] = 2
                    self.pontos += 1
                    self.lbl_pontos.text = f"Pts: {self.pontos}"
                    
                elif valor_bloco == 3:
                    self.verificar_resposta_matematica(nova_coluna, nova_linha)

                self.verificar_colisao_fantasmas()
                self.desenhar_tudo(0)

    # ==========================================
    # VERIFICAÇÃO COM O DICIONÁRIO NOVO
    # ==========================================
    def verificar_resposta_matematica(self, x, y):
        # Acha qual resposta foi sorteada exatamente para a coordenada (x, y) que o Pac-Man pisou
        resposta_escolhida = self.posicoes_respostas.get((x, y))
        
        if resposta_escolhida == self.resposta_correta:
            self.mostrar_feedback_rapido("ACERTOU!\n+50 PONTOS", (0, 1, 0, 1))
            self.pontos += 50
            self.lbl_pontos.text = f"Pts: {self.pontos}"
            Clock.schedule_once(lambda dt: self.gerar_nova_conta(), 1.5)
        else:
            msg_erro = f"ERROU!\n{self.fator1} x {self.fator2} = {self.resposta_correta}"
            self.mostrar_feedback_rapido(msg_erro, (1, 0, 0, 1))
            self.perder_vida()

    def mostrar_feedback_rapido(self, texto, cor):
        self.jogo_pausado = True 
        self.lbl_feedback.text = texto
        self.lbl_feedback.text_color = cor
        Clock.schedule_once(self.limpar_feedback_rapido, 1.5)

    def limpar_feedback_rapido(self, dt):
        if self.vidas > 0 and self.tempo > 0:
            self.lbl_feedback.text = ""
            self.jogo_pausado = False
            self.desenhar_tudo(0)

    def desenhar_tudo(self, dt):
        largura_tela = self.width
        altura_disponivel = self.height * 0.68 
        
        self.tile_size = min((largura_tela * 0.95) / len(self.mapa_atual[0]), altura_disponivel / len(self.mapa_atual))
        self.offset_x = (largura_tela - (self.tile_size * len(self.mapa_atual[0]))) / 2
        self.offset_y = self.height * 0.27 

        self.canvas_labirinto.canvas.clear()
        
        with self.canvas_labirinto.canvas:
            for linha in range(len(self.mapa_atual)):
                for coluna in range(len(self.mapa_atual[linha])):
                    valor = self.mapa_atual[linha][coluna]
                    pos_x = self.offset_x + (coluna * self.tile_size)
                    pos_y = self.offset_y + ((len(self.mapa_atual) - 1 - linha) * self.tile_size)

                    if valor == 1:
                        Color(0, 0.8, 0.2, 1) 
                        Rectangle(pos=(pos_x + 1, pos_y + 1), size=(self.tile_size - 2, self.tile_size - 2))
                        Color(0, 0, 0, 1) 
                        Rectangle(pos=(pos_x + 3, pos_y + 3), size=(self.tile_size - 6, self.tile_size - 6))
                        
                    elif valor == 0:
                        Color(1, 1, 0.6, 1) 
                        raio = self.tile_size * 0.15
                        centro_x = pos_x + (self.tile_size / 2)
                        centro_y = pos_y + (self.tile_size / 2)
                        Ellipse(pos=(centro_x - raio, centro_y - raio), size=(raio*2, raio*2))
                        
                    elif valor == 3:
                        Color(0, 0, 0.8, 1) 
                        raio = self.tile_size * 0.45
                        centro_x = pos_x + (self.tile_size / 2)
                        centro_y = pos_y + (self.tile_size / 2)
                        Ellipse(pos=(centro_x - raio, centro_y - raio), size=(raio*2, raio*2))
                        
                        # Resgata o texto certo direto do dicionário usando a coordenada atual!
                        texto_num = str(self.posicoes_respostas.get((coluna, linha), ""))
                        
                        l = CoreLabel(text=texto_num, font_size=self.tile_size * 0.5, color=(1, 1, 1, 1), bold=True)
                        l.refresh()
                        textura = l.texture
                        Color(1, 1, 1, 1) 
                        Rectangle(pos=(centro_x - (textura.width / 2), centro_y - (textura.height / 2)), size=textura.size, texture=textura)

            for f in self.fantasmas:
                Color(*f["cor"])
                px = self.offset_x + (f["x"] * self.tile_size)
                py = self.offset_y + ((len(self.mapa_atual) - 1 - f["y"]) * self.tile_size)
                pad = self.tile_size * 0.1
                tamanho = self.tile_size - pad*2
                
                Ellipse(pos=(px + pad, py + pad), size=(tamanho, tamanho))
                Rectangle(pos=(px + pad, py + pad), size=(tamanho, tamanho/2.0))
                
                Color(0.05, 0.05, 0.05, 1)
                raio_onda = tamanho / 6.0
                Ellipse(pos=(px + pad, py + pad - raio_onda), size=(raio_onda*2, raio_onda*2))
                Ellipse(pos=(px + pad + tamanho/2.0 - raio_onda, py + pad - raio_onda), size=(raio_onda*2, raio_onda*2))
                Ellipse(pos=(px + pad + tamanho - raio_onda*2, py + pad - raio_onda), size=(raio_onda*2, raio_onda*2))

                Color(1, 1, 1, 1) 
                raio_olho = tamanho * 0.25
                Ellipse(pos=(px + pad + tamanho*0.15, py + pad + tamanho*0.55), size=(raio_olho, raio_olho))
                Ellipse(pos=(px + pad + tamanho*0.6, py + pad + tamanho*0.55), size=(raio_olho, raio_olho))
                Color(0, 0, 1, 1) 
                raio_pupila = tamanho * 0.1
                Ellipse(pos=(px + pad + tamanho*0.25, py + pad + tamanho*0.6), size=(raio_pupila, raio_pupila))
                Ellipse(pos=(px + pad + tamanho*0.7, py + pad + tamanho*0.6), size=(raio_pupila, raio_pupila))

            Color(1, 1, 0, 1) 
            px = self.offset_x + (self.grid_x * self.tile_size)
            py = self.offset_y + ((len(self.mapa_atual) - 1 - self.grid_y) * self.tile_size)
            pad = self.tile_size * 0.1
            tamanho = self.tile_size - pad*2
            centro_x = px + pad + (tamanho/2)
            centro_y = py + pad + (tamanho/2)

            angulo_rotacao = 0
            if self.direcao_pacman == 'dir': angulo_rotacao = -90
            elif self.direcao_pacman == 'esq': angulo_rotacao = 90
            elif self.direcao_pacman == 'baixo': angulo_rotacao = 180
            elif self.direcao_pacman == 'cima': angulo_rotacao = 0
            
            abertura = 45 if self.boca_aberta else 5

            PushMatrix()
            Rotate(angle=angulo_rotacao, origin=(centro_x, centro_y)) 
            
            Ellipse(pos=(px + pad, py + pad), size=(tamanho, tamanho), angle_start=abertura, angle_end=360-abertura)
            
            PopMatrix() 

    def voltar(self, *args):
        self.manager.current = "jogar"