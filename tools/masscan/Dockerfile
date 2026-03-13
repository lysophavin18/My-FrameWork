FROM alpine:3.20 AS build
RUN apk add --no-cache git make gcc musl-dev
WORKDIR /src
RUN git clone --depth 1 https://github.com/robertdavidgraham/masscan.git .
RUN make

FROM alpine:3.20
RUN apk add --no-cache ca-certificates
COPY --from=build /src/bin/masscan /usr/local/bin/masscan
CMD ["sleep", "infinity"]

