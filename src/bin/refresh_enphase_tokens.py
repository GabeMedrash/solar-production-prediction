from src.env import Env
from src.external_data import Enphase

if __name__ == "__main__":
    env = Env()
    enphase_client = Enphase(env=env)
    tokens = enphase_client.generate_new_tokens()
    env.enphase_secret_tokens = tokens
