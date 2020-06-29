FROM ubuntu:20.04

RUN \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y dist-upgrade && \
    apt-get -y install \
        ca-certificates \
        openbox \
        openjdk-8-jre \
        openjfx \
        tightvncserver \
        unzip \
        wget \
        xterm \
        \
        fonts-liberation \
        libappindicator3-1 \
        libgbm1 \
        libxss1 \
        xdg-utils \
        \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists /usr/share/{doc,man} && \
    useradd -m -s /bin/bash tws

RUN \
    wget -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i /tmp/chrome.deb && \
    rm /tmp/chrome.deb && \
    sed -ie 's/^exec.*/\0 --no-sandbox/' /opt/google/chrome/google-chrome

USER tws
RUN \
    wget -O /tmp/tws.sh https://download2.interactivebrokers.com/installers/tws/stable-standalone/tws-stable-standalone-linux-x64.sh && \
        mkdir -p /home/tws/.vnc && \
        echo x | vncpasswd -f > /home/tws/.vnc/passwd && \
        chmod -R go= /home/tws/.vnc && \
        USER=tws tightvncserver :0 && \
        DISPLAY=:0 bash /tmp/tws.sh -q && \
        rm -rf /home/tws/.vnc && \
    rm /tmp/tws.sh

#wget -O /tmp/ibc.zip https://github.com/IbcAlpha/IBC/releases/download/3.8.2/IBCLinux-3.8.2.zip && \
USER root

RUN \
    wget -O /tmp/ibc.zip https://github.com/docker-tws/IBC/releases/download/initial/IBCLinux-3.8.2.zip && \
        mkdir -p /opt/ibc && \
        unzip -d /opt/ibc /tmp/ibc.zip && \
        chmod +x /opt/ibc/*.sh /opt/ibc/*/*.sh && \
    rm /tmp/ibc.zip

COPY . /opt/docker-tws
EXPOSE 5900 7496 7497 7462
CMD ["/opt/docker-tws/start.py"]
