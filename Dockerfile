FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY kb/ kb/

ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1

CMD ["python", "-m", "steel_brain.mcp_server"]
