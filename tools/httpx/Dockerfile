FROM golang:1.22-alpine AS build
RUN apk add --no-cache git
RUN go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=build /go/bin/httpx /usr/local/bin/httpx
CMD ["sleep", "infinity"]

