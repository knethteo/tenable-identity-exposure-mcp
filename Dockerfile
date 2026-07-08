FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml ./
COPY src/ ./src/

RUN uv pip install --system --no-cache .

ENV TIE_URL=""
ENV TIE_API_KEY=""
ENV TIE_VERIFY_SSL="true"

EXPOSE 8000

ENTRYPOINT ["tenable-tie-mcp"]
CMD ["--transport", "sse", "--port", "8000"]
