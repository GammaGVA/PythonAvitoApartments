# Файл под решение мелких вопросов.
import json

with open('data.json', 'r') as f:
    p = json.load(f)
print(len(p))
