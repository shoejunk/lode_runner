import os
import pickle
from constants import GameState

class GameStateManager:
    def __init__(self):
        self.save_file = "save.dat"
        self.current_state = GameState.MAIN_MENU
        self.current_level = 1
        self.score = 0
        self.lives = 3
        self.collected_treasures = []
        if os.path.exists(self.save_file):
            self.load()
    
    def transition_to(self, state):
        self.current_state = state
    
    def increment_level(self):
        self.current_level += 1
    
    def update_score(self, delta):
        self.score += delta
    
    def update_lives(self, delta):
        self.lives += delta
    
    def add_treasure(self, treasure_id):
        if treasure_id not in self.collected_treasures:
            self.collected_treasures.append(treasure_id)
    
    def save(self):
        data = {
            'current_level': self.current_level,
            'score': self.score,
            'lives': self.lives,
            'collected_treasures': self.collected_treasures
        }
        with open(self.save_file, 'wb') as f:
            pickle.dump(data, f)
    
    def load(self):
        if os.path.exists(self.save_file):
            with open(self.save_file, 'rb') as f:
                data = pickle.load(f)
                self.current_level = data.get('current_level', 1)
                self.score = data.get('score', 0)
                self.lives = data.get('lives', 3)
                self.collected_treasures = data.get('collected_treasures', [])

def main():
    # Test initialization
    manager = GameStateManager()
    assert manager.current_state == GameState.MAIN_MENU
    assert manager.current_level == 1
    assert manager.score == 0
    assert manager.lives == 3
    assert manager.collected_treasures == []
    
    # Test state transitions
    manager.transition_to(GameState.RUNNING)
    assert manager.current_state == GameState.RUNNING
    manager.transition_to(GameState.PAUSED)
    assert manager.current_state == GameState.PAUSED
    
    # Test score updates
    manager.update_score(100)
    assert manager.score == 100
    manager.update_score(-20)
    assert manager.score == 80
    
    # Test lives updates
    manager.update_lives(-1)
    assert manager.lives == 2
    
    # Test level progression
    manager.increment_level()
    assert manager.current_level == 2
    
    # Test treasure collection
    manager.add_treasure("gem_red")
    assert "gem_red" in manager.collected_treasures
    manager.add_treasure("gem_red")
    assert len(manager.collected_treasures) == 1
    
    # Test save/load functionality
    manager.save()
    new_manager = GameStateManager()
    assert new_manager.current_level == 2
    assert new_manager.score == 80
    assert new_manager.lives == 2
    assert "gem_red" in new_manager.collected_treasures
    
    # Cleanup
    if os.path.exists("save.dat"):
        os.remove("save.dat")
    
    print("All tests passed!")

if __name__ == "__main__":
    main()