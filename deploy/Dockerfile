FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOME=/data OMP_NUM_THREADS=1
WORKDIR /application
COPY requirements.txt requirements-rag.txt ./
RUN pip install --no-cache-dir -r requirements-rag.txt \
    && useradd --uid 10001 --create-home app \
    && mkdir /data && chown 10001:10001 /data
COPY app ./app
COPY studio_tools ./studio_tools
COPY docs/rag/corpus ./docs/rag/corpus
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-proxy-headers", "--no-access-log"]
