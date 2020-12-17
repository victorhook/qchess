import re
import os

from engine import Engine


SAVED_GAMES_ROOT = '/home/victor/coding/projects/qchess/qchess_web/resources/saved_games'
SAVED_GAMES_NAME = 'game_'

os.environ['SAVED_GAMES_ROOT'] = SAVED_GAMES_ROOT
os.environ['SAVED_GAMES_NAME'] = SAVED_GAMES_NAME


MAX_GAMES = 10e6


class EngineLoader:

    @staticmethod
    def new_game():
        game_id = EngineLoader.make_id()
        filepath = EngineLoader.get_filepath(game_id)
        engine = Engine(game_id=game_id, save_to=filepath, autosave=True)
        engine.save()
        return engine

    @staticmethod
    def load_engine(game_id):
        filepath = EngineLoader.get_filepath(game_id)
        engine = Engine.load(filepath=filepath)
        return engine

    @staticmethod
    def make_id():
        games = os.listdir(SAVED_GAMES_ROOT)
        games = list(map(lambda game: game.replace(SAVED_GAMES_NAME, ''),
                         games))
        games = list(filter(lambda game_id: re.match('[0-9]+', game_id),
                            games))
        games = list(map(lambda game_id: int(game_id), games))
        game_id = 1
        while game_id in games and game_id < MAX_GAMES:
            game_id += 1
        return game_id

    @staticmethod
    def get_filepath(id):
        return os.path.join(SAVED_GAMES_ROOT, SAVED_GAMES_NAME + str(id))



if __name__ == "__main__":
    print(EngineLoader.make_id())
