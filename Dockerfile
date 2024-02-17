FROM ubuntu:latest
LABEL authors="agraw"

ENTRYPOINT ["top", "-b"]