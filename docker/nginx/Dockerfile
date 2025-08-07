FROM nginx:alpine

# Install openssl for certificate generation
RUN apk add --no-cache openssl

# Copy the certificate generation script
COPY ./generate-certs.sh /usr/local/bin/generate-certs.sh
RUN chmod +x /usr/local/bin/generate-certs.sh

# Use our script as the entrypoint
ENTRYPOINT ["/usr/local/bin/generate-certs.sh"]
