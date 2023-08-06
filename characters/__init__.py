import yaml

with open("characters.yaml", "r") as stream:
    characters = yaml.safe_load(stream)
