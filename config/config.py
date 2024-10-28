import yaml

api_key = str
model = str


def get_config(path):
    global api_key, model
    with open(path) as f:
        setting = yaml.safe_load(f)
    api_key = setting['api_key']
    model = setting['model']

