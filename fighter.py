import pygame

class Fighter():
    def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
        # Atributos do personagem
        self.player = player  # Identificação do jogador (1 ou 2)
        self.size = data[0]  # Tamanho de cada quadro de animação
        self.image_scale = data[1]  # Escala da imagem
        self.offset = data[2]  # Deslocamento da imagem
        self.flip = flip  # Se a imagem está invertida ou não
        self.animation_list = self.load_images(sprite_sheet, animation_steps)  # Lista com as imagens de animação
        self.action = 0  # Ação atual do personagem: 0:idle, 1:correr, 2:pular, 3:ataque1, 4:ataque2, 5:levou dano, 6:morte
        self.frame_index = 0  # Índice do quadro da animação atual
        self.image = self.animation_list[self.action][self.frame_index]  # Imagem atual
        self.update_time = pygame.time.get_ticks()  # Momento da última atualização da animação
        self.rect = pygame.Rect((x, y, 80, 180))  # Retângulo que define a posição e tamanho do personagem na tela
        self.vel_y = 0  # Velocidade vertical
        self.running = False  # Se o personagem está correndo ou não
        self.jump = False  # Se o personagem está pulando ou não
        self.attacking = False  # Se o personagem está atacando ou não
        self.attack_type = 0  # Tipo de ataque que está sendo executado (1 ou 2)
        self.attack_cooldown = 0  # Tempo de espera antes de poder atacar novamente
        self.attack_sound = sound  # Som de ataque
        self.hit = False  # Se o personagem levou dano ou não
        self.health = 100  # Vida do personagem
        self.alive = True  # Se o personagem está vivo ou não

      # Carrega as imagens de animação a partir da spritesheet
    def load_images(self, sprite_sheet, animation_steps):
        animation_list = []
        # Extrai as imagens de cada animação
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                # Pega um quadro da animação
                temp_img = sprite_sheet.subsurface(
                    x * self.size, y * self.size, self.size, self.size
                )
                # Redimensiona a imagem
                temp_img_list.append(
                    pygame.transform.scale(
                        temp_img,
                        (self.size * self.image_scale, self.size * self.image_scale),
                    )
                )
            animation_list.append(temp_img_list)
        return animation_list

    # Método que move o personagem
    def move(self, screen_width, screen_height, surface, target, round_over):
        SPEED = 10 # Velocidade de movimento
        GRAVITY = 2 # Força da gravidade
        dx = 0 # Deslocamento horizontal
        dy = 0 # Deslocamento vertical
        self.running = False # Personagem não está correndo
        self.attack_type = 0 # Sem ataque sendo executado

        # faz o tratamento se os joysticks estao conectados...

        # Verifica se pelo menos um joystick está conectado
        joystick_count = pygame.joystick.get_count()
        if joystick_count >= 1:
            # Obtém o joystick 1
            joystick_1 = pygame.joystick.Joystick(0)
            # Inicializa o joystick
            joystick_1.init()
            # Verifica se o joystick está conectado
            if joystick_1.get_init():
                # print("Joystick 1 conectado")
                pass
        else:
            joystick_1 = None

        if joystick_count >= 2:
            # Obtém o joystick 2
            joystick_2 = pygame.joystick.Joystick(1)
            # Inicializa o joystick
            joystick_2.init()
            # Verifica se o joystick está conectado
            if joystick_2.get_init():
                # print("Joystick 2 conectado")
                pass
        else: 
            joystick_2 = None
        
        if joystick_count < 1:
            joystick_1 = None
            joystick_2 = None
            # print("Nenhum joystick conectado")


        # Pega as teclas pressionadas
        key = pygame.key.get_pressed()

        # Só pode realizar outras ações se não estiver atacando
        if self.attacking == False and self.alive == True and round_over == False:
            # Controles do jogador 1
            if self.player == 1:
                # Movimentação com teclado
                if key[pygame.K_a]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_d]:
                    dx = SPEED
                    self.running = True

                # Movimentação com joystick 1
                if joystick_1:
                    axis = joystick_1.get_axis(0)
                    if axis < -0.5:
                        dx = -SPEED
                        self.running = True
                    if axis > 0.5:
                        dx = SPEED
                        self.running = True

                # Pulo
                if (key[pygame.K_w] and self.jump == False):
                    self.vel_y = -30
                    self.jump = True
                # Ataque
                if key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(target)
                    # Determina qual tipo de ataque foi usado
                    if key[pygame.K_r]:
                        self.attack_type = 1
                    if key[pygame.K_t]:
                        self.attack_type = 2

                # permite o funcionamento se o joytick 1 estiver ativo se nao, utiliza o teclado
                if joystick_1:
                    # Adiciona o controle via joystick
                    joystick_1 = pygame.joystick.Joystick(0)
                    joystick_1.init()
                    axis_x = joystick_1.get_axis(0)
                    axis_y = joystick_1.get_axis(1)

                    # Aplica o movimento do joystick
                    if axis_x > 0.5:
                        dx = SPEED
                        self.running = True
                    elif axis_x < -0.5:
                        dx = -SPEED
                        self.running = True
                    if axis_y < -0.5 and self.jump == False:
                        self.vel_y = -30
                        self.jump = True
                    if joystick_1.get_button(0):
                        self.attack(target)
                        self.attack_type = 1    

                    if joystick_1.get_button(2):
                        self.attack(target)
                        self.attack_type = 2    

            # Controles do jogador 2
            if self.player == 2:
                # Movimentação com teclado
                if key[pygame.K_LEFT]:
                    dx = -SPEED
                    self.running = True
                if key[pygame.K_RIGHT]:
                    dx = SPEED
                    self.running = True

                # Movimentação com joystick 2
                if joystick_2:
                    axis = joystick_2.get_axis(0)
                    if axis < -0.5:
                        dx = -SPEED
                        self.running = True
                    if axis > 0.5:
                        dx = SPEED
                        self.running = True

                # Pulo
                if key[pygame.K_UP] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True
                # Ataque
                if key[pygame.K_KP1] or key[pygame.K_KP2]:
                    self.attack(target)
                    # Determina qual tipo de ataque foi usado
                    if key[pygame.K_KP1]:
                        self.attack_type = 1
                    if key[pygame.K_KP2]:
                        self.attack_type = 2

                # permite o funcionamento se o joytick 1 estiver ativo se nao, utiliza o teclado
                if joystick_2:
                    # Adiciona o controle via joystick
                    joystick_2 = pygame.joystick.Joystick(1)
                    joystick_2.init()
                    axis_x = joystick_2.get_axis(0)
                    axis_y = joystick_2.get_axis(1)

                    # Aplica o movimento do joystick
                    if axis_x > 0.5:
                        dx = SPEED
                        self.running = True
                    elif axis_x < -0.5:
                        dx = -SPEED
                        self.running = True
                    if axis_y < -0.5 and self.jump == False:
                        self.vel_y = -30
                        self.jump = True
                    if joystick_2.get_button(0):
                        self.attack(target)
                        self.attack_type = 1  

                    if joystick_2.get_button(2):
                        self.attack(target)
                        self.attack_type = 2      

        # Aplica a gravidade
        self.vel_y += GRAVITY
        dy += self.vel_y

        # Mantém o personagem na tela
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom

        # Faz os personagens se olharem
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        # Aplica o tempo de espera para o próximo ataque
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Atualiza a posição do personagem
        self.rect.x += dx
        self.rect.y += dy

    # Método que atualiza a animação do personagem
    def update(self):
        # Verifica qual ação o personagem está realizando
        if self.health <= 0:
            self.health = 0
            self.alive = False
            self.update_action(6)  # 6: Morte
        elif self.hit == True:
            self.update_action(5)  # 5: Levando dano
        elif self.attacking == True:
            if self.attack_type == 1:
                # print("Atack 1")
                self.update_action(3)  # 3: Ataque 1
            elif self.attack_type == 2:
                self.update_action(4)  # 4: Ataque 2
        elif self.jump == True:
            self.update_action(2)  # 2: Pulo
        elif self.running == True:
            self.update_action(1)  # 1: Correndo
        else:
            self.update_action(0)  # 0: Parado

        animation_cooldown = 50 # Tempo entre cada frame da animação
        
        # Atualiza a imagem do personagem
        self.image = self.animation_list[self.action][self.frame_index]
        
        # Verifica se já passou o tempo suficiente desde a última atualização
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()

        # Verifica se a animação acabou
        if self.frame_index >= len(self.animation_list[self.action]):
            # Se o personagem morreu, a animação acaba
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

                # Verifica se um ataque foi executado
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20

                # Verifica se o personagem levou dano
                if self.action == 5:
                    self.hit = False
                    # Se o personagem estava realizando um ataque, o ataque é interrompido
                    self.attacking = False
                    self.attack_cooldown = 20

    def attack(self, target):
        # Verifica se o tempo de espera para o próximo ataque já acabou
        if self.attack_cooldown == 0:
            
            # Executa o ataque
            self.attacking = True
            self.attack_sound.play()

             # Cria um retângulo para representar o alcance do ataque
            attacking_rect = pygame.Rect(
                self.rect.centerx - (2 * self.rect.width * self.flip),
                self.rect.y,
                2 * self.rect.width,
                self.rect.height,
            )

            # Verifica se o alvo do ataque está dentro do alcance
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True

    # atualiza as acoes do personagem.
    def update_action(self, new_action):
        # Verifica se a nova ação é diferente da ação anterior
        if new_action != self.action:
            self.action = new_action

            # Atualiza as configurações da animação
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self, surface):
        # realiza o desenho do personagem na tela
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(
            img,
            (
                self.rect.x - (self.offset[0] * self.image_scale),
                self.rect.y - (self.offset[1] * self.image_scale),
            ),
        )
