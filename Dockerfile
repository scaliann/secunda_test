FROM ubuntu:latest
LABEL authors="scaliann"

ENTRYPOINT ["top", "-b"]