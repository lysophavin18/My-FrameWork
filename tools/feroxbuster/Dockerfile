FROM rust:1.78-alpine AS build
RUN apk add --no-cache musl-dev openssl-dev
RUN cargo install feroxbuster

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=build /root/.cargo/bin/feroxbuster /usr/local/bin/feroxbuster
CMD ["sleep", "infinity"]

