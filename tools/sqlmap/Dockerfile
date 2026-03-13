FROM python:3.11-alpine

RUN apk add --no-cache git ca-certificates
RUN git clone --depth 1 https://github.com/sqlmapproject/sqlmap.git /opt/sqlmap

WORKDIR /opt/sqlmap

RUN python -m compileall .

CMD ["sleep", "infinity"]
