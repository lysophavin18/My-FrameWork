FROM golang:1.22-alpine AS build
RUN apk add --no-cache git
RUN go install -v github.com/projectdiscovery/katana/cmd/katana@latest

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=build /go/bin/katana /usr/local/bin/katana
CMD ["sleep", "infinity"]

