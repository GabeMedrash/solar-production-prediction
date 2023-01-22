import argparse

from src.solar_production_prediction.weather_api.enphase import Enphase


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    args = parser.parse_args()

    enphase_client = Enphase()
    # tokens = enphase_client.generate_new_tokens(args.enphase_refresh_token)
    print(enphase_client.energy_produced_today())

