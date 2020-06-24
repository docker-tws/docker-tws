FROM ubuntu:20.04

RUN \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y dist-upgrade && \
    apt-get -y install \
        ca-certificates \
        firefox \
        fluxbox \
        openjdk-8-jre \
        openjfx \
        tightvncserver \
        unzip \
        wget \
        xterm \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists /usr/share/{doc,man} && \
    useradd -m -s /bin/bash tws

USER tws
RUN \
    wget -O /tmp/tws.sh https://download2.interactivebrokers.com/installers/tws/stable-standalone/tws-stable-standalone-linux-x64.sh && \
        mkdir -p /home/tws/.vnc && \
        echo x | vncpasswd -f > /home/tws/.vnc/passwd && \
        chmod -R go= /home/tws/.vnc && \
        USER=tws tightvncserver :0 && \
        DISPLAY=:0 bash /tmp/tws.sh -q && \
    rm /tmp/tws.sh

#wget -O /tmp/ibc.zip https://github.com/IbcAlpha/IBC/releases/download/3.8.2/IBCLinux-3.8.2.zip && \
USER root
RUN \
    wget -O /tmp/ibc.zip https://github.com/docker-tws/IBC/files/4828321/IBCLinux-3.8.2.zip && \
        mkdir -p /opt/ibc && \
        unzip -d /opt/ibc /tmp/ibc.zip && \
        chmod +x /opt/ibc/*.sh /opt/ibc/*/*.sh && \
    rm /tmp/ibc.zip

COPY . /opt/docker-tws
EXPOSE 5900 7496 7497 7462
CMD /opt/docker-tws/start.py
