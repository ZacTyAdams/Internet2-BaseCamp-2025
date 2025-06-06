FROM --platform=linux/amd64 python:slim-bookworm

# Install required Python packages
RUN python3 -m pip install langchain langchain-ollama duckduckgo-search langchain-community langchain-experimental --break-system-packages

# Install bash
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

COPY app/agent_app.py /agent_app.py
COPY app/application.log /var/log/application.log

# Create entrypoint script
RUN echo '#!/bin/bash\npython3 /agent_app.py\nexec /bin/bash' > /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Run the entrypoint script
CMD ["/entrypoint.sh"]