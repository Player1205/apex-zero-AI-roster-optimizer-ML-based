import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")

PREDICTIONS_FILE = os.path.join(DATA_DIR, "players_with_predictions.csv")