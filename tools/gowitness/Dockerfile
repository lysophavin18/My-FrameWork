FROM golang:1.22-alpine AS build
RUN apk add --no-cache git
RUN go install -v github.com/sensepost/gowitness@latest

FROM alpine:3.20
RUN apk add --no-cache ca-certificates chromium nss freetype harfbuzz ttf-freefont
COPY --from=build /go/bin/gowitness /usr/local/bin/gowitness
WORKDIR /app
CMD ["sleep", "infinity"]

