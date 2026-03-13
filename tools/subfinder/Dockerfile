FROM golang:1.22-alpine AS build
RUN apk add --no-cache git
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=build /go/bin/subfinder /usr/local/bin/subfinder
CMD ["sleep", "infinity"]

