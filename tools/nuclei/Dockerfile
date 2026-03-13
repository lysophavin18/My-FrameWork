FROM golang:1.22-alpine AS build
RUN apk add --no-cache git
RUN go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=build /go/bin/nuclei /usr/local/bin/nuclei
CMD ["sleep", "infinity"]

