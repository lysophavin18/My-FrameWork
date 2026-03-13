FROM golang:1.22-alpine AS build
RUN apk add --no-cache git
WORKDIR /src
RUN git clone --depth 1 https://github.com/owasp-amass/amass.git .
RUN go build -o /out/amass ./cmd/amass

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=build /out/amass /usr/local/bin/amass
CMD ["sleep", "infinity"]

