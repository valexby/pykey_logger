import json

__config_path__ = '/home/valex/workspace/IiPU/pykey_logger/config'

def load_config():
    f = open(__config_path__, 'r')
    raw = f.read()
    f.close()
    return json.loads(raw)
