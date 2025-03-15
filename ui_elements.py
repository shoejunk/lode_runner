import pygame
from constants import WHITE, BLACK, SCREEN_WIDTH, SCREEN_HEIGHT, GameState
from game_state import GameStateManager

class HUD:
    def __init__(self, screen, gsm):
        self.screen = screen
        self.gsm = gsm
        self.font = pygame.font.Font(None, 36)
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.update_positions()

    def update_screen(self, new_screen):
        self.screen = new_screen

    def update_screen_size(self, width, height):
        self.screen_width = width
        self.screen_height = height
        self.update_positions()

    def update_positions(self):
        self.score_pos = (10, 10)
        self.lives_pos = (self.screen_width - 100, 10)

    def draw(self):
        score_text = self.font.render(f"Score: {self.gsm.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.gsm.lives}", True, WHITE)
        self.screen.blit(score_text, self.score_pos)
        self.screen.blit(lives_text, self.lives_pos)

class MenuSystem:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.buttons = []
        self.update_positions()

    def update_screen(self, new_screen):
        self.screen = new_screen

    def update_screen_size(self, width, height):
        self.screen_width = width
        self.screen_height = height
        self.update_positions()

    def update_positions(self):
        self.buttons = []
        button_width = 200
        button_height = 50
        start_x = (self.screen_width - button_width) // 2
        start_y = (self.screen_height - button_height * 3) // 2
        self.buttons.append(pygame.Rect(start_x, start_y, button_width, button_height))
        self.buttons.append(pygame.Rect(start_x, start_y + 70, button_width, button_height))
        self.buttons.append(pygame.Rect(start_x, start_y + 140, button_width, button_height))

    def draw(self):
        self.screen.fill(BLACK)
        for i, button in enumerate(self.buttons):
            pygame.draw.rect(self.screen, WHITE, button)
            text = self.font.render(f"Button {i+1}", True, BLACK)
            text_rect = text.get_rect(center=button.center)
            self.screen.blit(text, text_rect)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("UI Elements Test")
    clock = pygame.time.Clock()
    gsm = GameStateManager()
    hud = HUD(screen, gsm)
    menu_system = MenuSystem(screen)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                hud.update_screen(screen)
                hud.update_screen_size(event.w, event.h)
                menu_system.update_screen(screen)
                menu_system.update_screen_size(event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if menu_system.buttons[0].collidepoint(event.pos):
                    gsm.transition_to(GameState.RUNNING)
                elif menu_system.buttons[1].collidepoint(event.pos):
                    gsm.transition_to(GameState.PAUSED)
                elif menu_system.buttons[2].collidepoint(event.pos):
                    running = False

        screen.fill(BLACK)
        if gsm.current_state == GameState.MAIN_MENU:
            menu_system.draw()
        elif gsm.current_state == GameState.RUNNING:
            hud.draw()
        pygame.display.flip()
        clock.tick(60)

    # Run tests before quitting pygame
    gsm.update_score(500)
    expected_score_text = f"Score: {gsm.score}"
    assert expected_score_text == "Score: 500", f"HUD score mismatch: {expected_score_text}"

    menu_system.update_screen_size(800, 600)
    assert menu_system.buttons[0].center == (400, 250), "Menu button position incorrect after resize"

    hud.update_screen_size(800, 600)
    assert hud.lives_pos == (700, 10), "HUD lives position incorrect after resize"

    print("All tests passed!")
    pygame.quit()

if __name__ == "__main__":
    main()