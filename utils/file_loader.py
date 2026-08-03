import json
import csv


def load_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        return list(reader)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
