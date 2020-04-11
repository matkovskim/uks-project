FROM python:3-slim

ARG git_key 
ARG git_secret

ENV SOCIAL_AUTH_GITHUB_KEY=$git_key
ENV SOCIAL_AUTH_GITHUB_SECRET=$git_secret

ENV PYTHONUNBUFFERED 1
WORKDIR /code
ADD . /code
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
RUN ["chmod", "+x", "wait_for_postgres.sh"]
RUN ["chmod", "+x", "start.sh"]

EXPOSE 8000
STOPSIGNAL SIGINT
ENTRYPOINT ["./start.sh"]