import pygame
from constants import KEY_BINDINGS

class InputHandler:
    def __init__(self):
        self.key_bindings = KEY_BINDINGS.copy()
        self.controller_bindings = {
            'MOVE_LEFT': [('axis', 0, -0.5)],
            'MOVE_RIGHT': [('axis', 0, 0.5)],
            'JUMP': [('button', 0)],
            'INTERACT': [('button', 1)],
            'PAUSE': [('button', 7)]
        }
        self.buffer_time = 200
        self.last_pressed = {action: 0 for action in self.key_bindings}
        self.joysticks = []
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            self.joysticks.append(joystick)

    def remap_controls(self, action, new_keys):
        if action in self.key_bindings:
            self.key_bindings[action] = new_keys

    def get_actions(self):
        current_time = pygame.time.get_ticks()
        active_actions = set()

        # Keyboard input
        pressed_keys = pygame.key.get_pressed()
        for action, keys in self.key_bindings.items():
            if any(pressed_keys[key] for key in keys):
                active_actions.add(action)
                self.last_pressed[action] = current_time

        # Controller input
        for joystick in self.joysticks:
            for action, bindings in self.controller_bindings.items():
                for binding in bindings:
                    if binding[0] == 'button' and joystick.get_button(binding[1]):
                        active_actions.add(action)
                        self.last_pressed[action] = current_time
                    elif binding[0] == 'axis':
                        value = joystick.get_axis(binding[1])
                        if (binding[2] < 0 and value <= binding[2]) or (binding[2] > 0 and value >= binding[2]):
                            active_actions.add(action)
                            self.last_pressed[action] = current_time

        # Input buffer
        for action in self.key_bindings:
            if current_time - self.last_pressed[action] <= self.buffer_time:
                active_actions.add(action)

        return active_actions

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((1, 1))
    handler = InputHandler()

    # Test default controls
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT))
    pygame.event.get()
    assert 'MOVE_LEFT' in handler.get_actions(), "Default controls failed"

    # Test remapping
    handler.remap_controls('MOVE_LEFT', [pygame.K_z])
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_z))
    pygame.event.get()
    assert 'MOVE_LEFT' in handler.get_actions(), "Remap failed"

    # Test input buffer
    pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE))
    pygame.event.post(pygame.event.Event(pygame.KEYUP, key=pygame.K_SPACE))
    pygame.event.get()
    assert 'JUMP' in handler.get_actions(), "Buffer failed immediately"
    pygame.time.wait(handler.buffer_time + 10)
    assert 'JUMP' not in handler.get_actions(), "Buffer failed after timeout"

    # Test controller input
    if handler.joysticks:
        joystick = handler.joysticks[0]
        pygame.event.post(pygame.event.Event(pygame.JOYBUTTONDOWN, button=0, instance_id=joystick.get_instance_id()))
        pygame.event.get()
        assert 'JUMP' in handler.get_actions(), "Controller button failed"

        pygame.event.post(pygame.event.Event(pygame.JOYAXISMOTION, axis=0, value=-0.6, instance_id=joystick.get_instance_id()))
        pygame.event.get()
        assert 'MOVE_LEFT' in handler.get_actions(), "Controller axis failed"

    pygame.quit()
    print("All tests passed.")