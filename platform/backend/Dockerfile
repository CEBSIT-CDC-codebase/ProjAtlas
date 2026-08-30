# NOTE: build context must be the monorepo root, not this directory, so that
# ../multi-agent-framework is visible during the build:
#   docker build -f platform/backend/Dockerfile -t ai-atlas-backend .

FROM pytorch/pytorch:2.5.1-cuda12.4-cudnn9-runtime

RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements files
COPY platform/backend/requirements.txt ./backend-requirements.txt
COPY multi-agent-framework/requirements.txt ./atlas-assistant-requirements.txt

RUN pip install --default-timeout=1000 --no-cache-dir \
    -r atlas-assistant-requirements.txt \
    -r backend-requirements.txt

# Copy and install multi-agent-framework (provides the atlas_assistant package)
COPY multi-agent-framework ./multi-agent-framework
RUN pip install --no-deps -e ./multi-agent-framework

# Copy backend code
COPY platform/backend .

EXPOSE 5000

CMD ["python", "run.py"]