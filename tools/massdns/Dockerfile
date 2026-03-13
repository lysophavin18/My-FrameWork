FROM alpine:3.20 AS build
RUN apk add --no-cache git make gcc musl-dev
WORKDIR /src
RUN git clone --depth 1 https://github.com/blechschmidt/massdns.git .
RUN make

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=build /src/bin/massdns /usr/local/bin/massdns
CMD ["sleep", "infinity"]

