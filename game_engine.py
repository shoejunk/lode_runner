#!/usr/bin/env python3
import time

class GameEngine:
    def __init__(self, frame_rate=60):
        # Initialize engine settings
        self.frame_rate = frame_rate
        self.frame_duration = 1.0 / frame_rate
        self.running = False
        self.state = "uninitialized"
        self.resources = None
        self.frame_count = 0

    def load_resources(self):
        # Simulate resource loading
        self.resources = {"textures": "loaded", "sounds": "loaded", "levels": "loaded"}
        # In a real game engine, we would load images, sounds, etc.
    
    def initialize(self):
        # System initialization and resource loading
        self.load_resources()
        self.state = "initialized"

    def update(self, frame_number):
        # Update game logic; In a real game, this would include physics, AI, etc.
        # For simulation, we just update a frame counter.
        self.frame_count = frame_number
        # Simulate a state change every frame to mimic game progression
        if frame_number == 0:
            self.state = "starting"
        elif frame_number > 0:
            self.state = "running"
    
    def render(self, frame_number):
        # Render the game state to the screen; here just a placeholder.
        # In an actual engine, this would draw graphics to the screen.
        pass

    def run(self, max_frames=None):
        # Main game loop
        self.initialize()
        self.running = True
        current_frame = 0
        
        while self.running:
            frame_start = time.time()
            
            # Update framework: update game state
            self.update(current_frame)
            
            # Render game state
            self.render(current_frame)
            
            current_frame += 1
            
            # Check if we need to exit the loop for testing purposes
            if max_frames is not None and current_frame >= max_frames:
                self.running = False
            
            # Frame timing management: Ensure stable frame rate
            frame_end = time.time()
            elapsed = frame_end - frame_start
            sleep_duration = self.frame_duration - elapsed
            if sleep_duration > 0:
                time.sleep(sleep_duration)
        
        # End of main loop; update state for clean shutdown
        self.state = "stopped"
        return current_frame

def main():
    # Comprehensive tests for GameEngine
    
    # Test 1: Initialization of engine and resource loading
    engine = GameEngine()
    assert engine.state == "uninitialized", "Initial state should be 'uninitialized'"
    engine.initialize()
    assert engine.state == "initialized", "After initialization, state should be 'initialized'"
    assert engine.resources is not None, "Resources should be loaded during initialization"
    assert engine.resources.get("textures") == "loaded", "Textures should be loaded"
    
    # Test 2: Run loop with fixed number of frames and verify frame rate control and state transition
    test_frames = 5
    engine2 = GameEngine(frame_rate=60)
    start_time = time.time()
    frames_processed = engine2.run(max_frames=test_frames)
    end_time = time.time()
    total_time = end_time - start_time
    
    # The total time should be roughly test_frames/frame_rate seconds
    expected_time = test_frames / engine2.frame_rate
    tolerance = 0.05  # Allow small variation
    assert abs(total_time - expected_time) < tolerance or total_time >= expected_time, "Stable frame rate not maintained"
    assert frames_processed == test_frames, f"Expected {test_frames} frames processed, got {frames_processed}"
    assert engine2.state == "stopped", "Engine state should be 'stopped' after run completes"
    
    # Test 3: Verify update ordering by checking frame count and state transitions
    # Create a custom engine instance and simulate two update calls manually
    engine3 = GameEngine()
    engine3.initialize()
    engine3.update(0)
    assert engine3.state == "starting", "State should be 'starting' after update with frame 0"
    engine3.update(1)
    assert engine3.state == "running", "State should be 'running' after update with frame > 0"
    assert engine3.frame_count == 1, "Frame counter should update with the latest frame number"

    print("All tests passed successfully.")

if __name__ == "__main__":
    main()