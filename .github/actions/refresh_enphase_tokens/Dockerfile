FROM python:3.11

RUN python3 -m venv --upgrade-deps venv
    && ./venv/bin/python -m pip install -r requirements.txt

ENTRYPOINT ["./venv/bin/python", ".github/actions/refresh_enphase_tokens/refresh_tokens.py"]
