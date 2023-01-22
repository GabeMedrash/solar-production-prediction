FROM python:3.11

COPY requirements.txt requirements.txt
RUN python3 -m venv --upgrade-deps /opt/venv && /opt/venv/bin/python -m pip install -r requirements.txt

ENTRYPOINT ["/opt/venv/bin/python", "./.github/actions/refresh_enphase_tokens/refresh_tokens.py"]
