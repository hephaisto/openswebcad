FROM alpine:latest AS pythoninstall
RUN apk add python3 py3-pip
RUN python3 -m venv /root/venv
COPY *.whl /root/packages/
RUN /root/venv/bin/python3 -m pip install /root/packages/*.whl

FROM alpine:latest
RUN apk add openscad xvfb mesa mesa-dri-gallium mesa-gl mesa-utils python3
COPY --from=pythoninstall /root/venv /root/venv

LABEL org.opencontainers.image.source="https://github.com/hephaisto/openswebcad"

RUN mkdir /root/workdir
WORKDIR /root/workdir
ENTRYPOINT ["/root/venv/bin/python3", "-m", "openswebcad.run_gui", "-x"]
CMD ["-v", "/root/models/"]
