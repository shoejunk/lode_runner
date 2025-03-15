import pygame
from pygame import mixer
from constants import GameState

class AudioManager:
    def __init__(self, sfx_paths, music_paths):
        pygame.mixer.init()
        self.sfx_paths = sfx_paths
        self.music_paths = music_paths
        self.sounds = {}
        for name, path in sfx_paths.items():
            self.sounds[name] = pygame.mixer.Sound(path)
        self.sfx_channels = [pygame.mixer.Channel(i) for i in range(8)]
        self.channel_priorities = {}
        self.current_state = None
        self.current_intensity = None
        self.sfx_volume = 1.0
        self.music_volume = 1.0

    def play_sfx(self, name, volume=1.0, loops=0, priority=0):
        if name not in self.sounds:
            return False
        sound = self.sounds[name]
        chosen_channel = None
        lowest_priority = float('inf')
        for channel in self.sfx_channels:
            if not channel.get_busy():
                chosen_channel = channel
                break
            current_prio = self.channel_priorities.get(channel, -1)
            if current_prio < lowest_priority:
                lowest_priority = current_prio
                chosen_channel = channel
        if chosen_channel is None:
            return False
        if chosen_channel.get_busy():
            current_prio = self.channel_priorities.get(channel, -1)
            if priority <= current_prio:
                return False
            chosen_channel.stop()
        final_volume = volume * self.sfx_volume
        chosen_channel.play(sound, loops=loops)
        chosen_channel.set_volume(final_volume)
        self.channel_priorities[chosen_channel] = priority
        return True

    def set_music(self, state, intensity='base'):
        if state not in self.music_paths:
            return
        track_info = self.music_paths[state]
        if isinstance(track_info, dict):
            if intensity not in track_info:
                return
            track_path = track_info[intensity]
        else:
            track_path = track_info
        if state == self.current_state and (not isinstance(track_info, dict) or intensity == self.current_intensity):
            return
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.music.load(track_path)
        pygame.mixer.music.play(-1, fade_ms=1000)
        pygame.mixer.music.set_volume(self.music_volume)
        self.current_state = state
        if isinstance(track_info, dict):
            self.current_intensity = intensity

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)

def main():
    import pygame
    pygame.init()

    sfx_paths = {
        'jump': 'assets/sfx/jump.wav',
        'hit': 'assets/sfx/hit.wav'
    }
    music_paths = {
        GameState.MAIN_MENU: 'assets/music/menu.ogg',
        GameState.RUNNING: {
            'low': 'assets/music/game_low.ogg',
            'high': 'assets/music/game_high.ogg'
        }
    }

    audio = AudioManager(sfx_paths, music_paths)

    assert audio.play_sfx('jump') == True
    assert audio.play_sfx('hit', priority=1) == True

    for _ in range(8):
        audio.play_sfx('jump', priority=0)
    assert audio.play_sfx('hit', priority=1) == True

    audio.set_music(GameState.MAIN_MENU)
    audio.set_music(GameState.RUNNING, intensity='low')
    audio.set_music(GameState.RUNNING, intensity='high')

    audio.set_sfx_volume(0.5)
    audio.set_music_volume(0.7)

    print("All tests passed.")

if __name__ == "__main__":
    main()