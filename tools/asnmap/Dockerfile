FROM golang:1.22-alpine AS build
RUN apk add --no-cache git
RUN go install -v github.com/projectdiscovery/asnmap/cmd/asnmap@latest

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=build /go/bin/asnmap /usr/local/bin/asnmap
CMD ["sleep", "infinity"]

