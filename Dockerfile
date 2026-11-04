FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir "."

EXPOSE 8000

# Serve what the image was built for. A CMD of `--help` would be a container
# that starts, prints and exits — which looks like it works and does nothing.
#
# `sprezzature-ui-mcp` rather than `uvicorn sprezzature_ui.api:app`: it serves
# the same FastAPI app, with the MCP endpoint mounted on it, so one container
# answers both `/v1/...` and `/mcp` on port 8000. Plain `uvicorn` on `api:app`
# never imports `sprezzature_ui.mcp`, so it never mounts `/mcp`.
#
# Override with the command line:
#
#   docker run --rm -v "$PWD:/work" IMAGE make-ui i18n-audit /work/src
CMD ["sprezzature-ui-mcp", "--host", "0.0.0.0", "--port", "8000"]
