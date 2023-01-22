FROM python:3.11

COPY requirements.txt requirements.txt

RUN python3 -m venv --upgrade-deps venv \
    && ./venv/bin/python -m pip install -r requirements.txt

COPY refresh_tokens.py refresh_tokens.py

ENTRYPOINT ["sh", "-c", "./venv/bin/python", "refresh_tokens.py"]
