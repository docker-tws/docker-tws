FROM ubuntu:18.04

#libavcodec58 \
#libavformat58 \
RUN \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get -y update && \
    apt-get -y upgrade && \
    apt-get -y dist-upgrade && \
    apt-get -y install \
        ca-certificates \
        openbox \
        tightvncserver \
        unzip \
        wget \
        xterm \
        \
        python3 \
        libappindicator3-1 \
        libgbm1 \
        libxss1 \
        libxslt1.1 \
        xdg-utils \
        libasound2 \
        fonts-liberation \
        fonts-dejavu-core \
        fonts-dejavu-extra \
        libavcodec57 \
        libavformat57 \
        libnspr4 \
        libnss3 \
        zstd \
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

RUN \
    wget -O /tmp/tws.sh https://download2.interactivebrokers.com/installers/tws/latest-standalone/tws-latest-standalone-linux-x64.sh && \
        runuser -u tws -- mkdir -p /home/tws/.vnc && \
        echo x | vncpasswd -f > /home/tws/.vnc/passwd && \
        chown -R tws: /home/tws/.vnc && \
        chmod -R go= /home/tws/.vnc && \
        runuser -u tws -- tightvncserver :0 && \
        runuser -u tws -- env DISPLAY=:0 bash /tmp/tws.sh -q -dir /home/tws/Jts/current && \
        rm -rf /home/tws/.vnc && \
    rm /tmp/tws.sh && \
    \
    mv /home/tws /home/tws.pristine && \
    mkdir -v /home/tws && \
    chown -v tws: /home/tws

USER root
ADD https://github.com/krallin/tini/releases/download/v0.19.0/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

COPY configs/openbox_rc.xml /etc/xdg/openbox/rc.xml

#wget -O /tmp/ibc.zip https://github.com/IbcAlpha/IBC/releases/download/3.8.2/IBCLinux-3.8.2.zip && \
RUN \
    wget -O /tmp/ibc.zip https://github.com/docker-tws/IBC/releases/download/initial/IBCLinux-3.8.2.zip && \
        mkdir -p /opt/ibc && \
        unzip -d /opt/ibc /tmp/ibc.zip && \
        chmod +x /opt/ibc/*.sh /opt/ibc/*/*.sh && \
    rm /tmp/ibc.zip

COPY . /opt/docker-tws
EXPOSE 5900 5901 7496 7497 7462 7463
CMD ["/opt/docker-tws/start.py"]
