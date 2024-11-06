import yaml

base_url = str
api_key = str
model = str
port = str


def get_config(path):
    global api_key, model, port, base_url
    with open(path) as f:
        setting = yaml.safe_load(f)
    api_key = setting['api_key']
    model = setting['model']
    port = setting['port']
    base_url = setting['base_url']
