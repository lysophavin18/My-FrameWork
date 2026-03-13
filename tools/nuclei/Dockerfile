FROM alpine:3.20
ARG NUCLEI_VERSION=v3.4.10
RUN apk add --no-cache ca-certificates curl tar && \
	curl -fsSL "https://github.com/projectdiscovery/nuclei/releases/download/${NUCLEI_VERSION}/nuclei_${NUCLEI_VERSION#v}_linux_amd64.zip" -o /tmp/nuclei.zip && \
	apk add --no-cache unzip && \
	unzip /tmp/nuclei.zip -d /tmp && \
	mv /tmp/nuclei /usr/local/bin/nuclei && \
	chmod +x /usr/local/bin/nuclei && \
	rm -rf /tmp/nuclei.zip /tmp/LICENSE.md /tmp/README.md
CMD ["sleep", "infinity"]

