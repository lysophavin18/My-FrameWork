FROM golang:1.22-alpine AS build
RUN apk add --no-cache git
RUN go install -v github.com/d3mondev/puredns/v2@latest

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=build /go/bin/puredns /usr/local/bin/puredns
CMD ["sleep", "infinity"]

