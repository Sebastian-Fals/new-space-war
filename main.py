import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.core.game import Game

if __name__ == "__main__":
    game = Game()
    game.run()
