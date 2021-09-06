import yaml
from yaml.loader import SafeLoader

with open('chitchat.yml') as f:
    data = yaml.load(f, Loader=SafeLoader)
print(data['nlu'])