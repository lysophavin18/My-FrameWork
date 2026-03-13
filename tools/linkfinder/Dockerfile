FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir jsbeautifier==1.14.9 requests==2.32.3
RUN git clone --depth 1 https://github.com/GerbenJavado/LinkFinder.git /opt/linkfinder
WORKDIR /opt/linkfinder
RUN pip install --no-cache-dir -r requirements.txt
CMD ["sleep", "infinity"]

