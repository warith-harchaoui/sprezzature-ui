FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir ".[i18n,api,mcp]"

EXPOSE 8000

# Serve what the image was built for. A CMD of `--help` would be a container
# that starts, prints and exits — which looks like it works and does nothing.
# Override with either command line:
#
#   docker run --rm -v "$PWD:/work" IMAGE make-ui i18n-audit /work/src
CMD ["uvicorn", "sprezzature_ui.api:app", "--host", "0.0.0.0", "--port", "8000"]
