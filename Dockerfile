FROM python:3-slim

ARG git_key 
ARG git_secret

ARG email_port
ARG email_host_user
ARG email_host_password
ARG email_use_tls

ARG db_password
ARG db_user
ARG db_name
ARG db_host
ARG db_port

ARG debug
ARG secret_key
ARG allowed_hosts

ENV SOCIAL_AUTH_GITHUB_KEY=$git_key
ENV SOCIAL_AUTH_GITHUB_SECRET=$git_secret

ENV EMAIL_PORT=$email_port
ENV EMAIL_HOST_USER=$email_host_user
ENV EMAIL_HOST_PASSWORD=$email_host_password
ENV EMAIL_USE_TLS=$email_use_tls

ENV DB_PASSWORD=$db_password
ENV DB_USER=$db_user
ENV DB_NAME=$db_name
ENV DB_HOST=$db_host
ENV DB_PORT=$db_port

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