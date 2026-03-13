FROM alpine:3.20

RUN apk add --no-cache perl git ca-certificates \
  && git clone --depth 1 https://github.com/sullo/nikto.git /opt/nikto

ENV PATH="/opt/nikto/program:${PATH}"
WORKDIR /opt/nikto/program

CMD ["sleep", "infinity"]

