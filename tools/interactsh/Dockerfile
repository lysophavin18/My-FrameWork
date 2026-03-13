FROM golang:1.22-alpine AS build
RUN apk add --no-cache git
RUN go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-server@latest

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=build /go/bin/interactsh-server /usr/local/bin/interactsh-server
EXPOSE 8053
CMD ["sh", "-lc", "interactsh-server -http-port 8080 -dns-port 8053"]

