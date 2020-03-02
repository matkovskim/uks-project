FROM python:3-slim

ARG git_key 
ARG git_secret

ARG email_port
ARG email_host_user
ARG email_host_password
ARG email_use_tls

ARG debug
ARG secret_key
ARG allowed_hosts

ENV SOCIAL_AUTH_GITHUB_KEY=$git_key
ENV SOCIAL_AUTH_GITHUB_SECRET=$git_secret

ENV EMAIL_PORT=$email_port
ENV EMAIL_HOST_USER=$email_host_user
ENV EMAIL_HOST_PASSWORD=$email_host_password
ENV EMAIL_USE_TLS=$email_use_tls

ENV DEBUG=$debug
ENV SECRET_KEY=$secret_key
ENV ALLOWED_HOSTS=$allowed_hosts

ENV PYTHONUNBUFFERED 1
WORKDIR /code
ADD . /code
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN ["chmod", "+x", "wait_for_postgres.sh"]
RUN ["chmod", "+x", "start.sh"]
# Server, just for Docker image, not for compose
EXPOSE 8000
STOPSIGNAL SIGINT
ENTRYPOINT ["./start.sh"]