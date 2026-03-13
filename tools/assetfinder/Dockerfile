FROM golang:1.22-alpine AS build
RUN apk add --no-cache git
RUN go install -v github.com/tomnomnom/assetfinder@latest

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=build /go/bin/assetfinder /usr/local/bin/assetfinder
CMD ["sleep", "infinity"]

