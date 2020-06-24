# `docker-tws`

Docker image for <a href="https://www.interactivebrokers.com/">Interactive
Brokers</a> TWS hosted by <a href="https://github.com/IbcAlpha/IBC">IBC</a>
running under <a href="https://www.tightvnc.com/">TightVNC</a>.

* User configuration is cleanly separated, allowing one computer to serve many
  accounts, store configuration in <a
  href="https://kubernetes.io/">Kubernetes</a> secrets, and for
  one-size-fits-all images to exist on <a href="https://hub.docker.com/">Docker
  Hub</a>.

* In line with Kubernetes best practice, IBC and TWS logs are redirected to
  container stdout.

* Docker Hub images are completely transparent, except for upload credentials. CI
  configuration is checked in, and the build log for each cryptographic image
  digest can be audited via <a href="https://travis-ci.org/">Travis CI</a>.


## Usage

```
docker run \
    -e VNC_PASSWORD=123 \
    -P localhost:5900:5900 \
    -P localhost:7496:7496 \
    docker-tws/tws:latest
```

Optionally supply credentials using:

```
    -e IBC_USERNAME=myuser123
    -e IBC_PASSWORD=OpenSesame
```

Optionally supply `jts.ini` and `tws.xml` from an existing TWS installation
using:

```
    -v /path/to/jts.ini:/conf/jts.ini:ro
    -v /path/to/tws.xml:/conf/tws.xml:ro
```

## Exposed Ports

<table>

<tr>
<th>Port
<th>Description

<tr>
<td><code>5900</code>
<td>VNC display

<tr>
<td><code>7462</code>
<td>IBC telnet server

<tr>
<td><code>7496</code>
<td>TWS API live trading account

<tr>
<td><code>7497</code>
<td>TWS API paper trading account

</table>


## Volumes

All paths are optional.

<table>

<tr>
<th>Path
<th>Description

<tr>
<td><code>/conf</code>
<td>Read-only directory of configuration files to install. Usable as a Docker
    or Kubernetes volume

<tr>
<td><code>/conf/jts.ini</code>
<td>File to install as <code>~tws/Jts/jts.ini</code>

<tr>
<td><code>/conf/tws.xml</code>
<td>File to install as <code>~tws/Jts/[profile]/tws.xml</code>. If provided,
    <code>jts.ini</code> must also be provided, as it is needed to detect the
    profile name

</table>


## Environment Variables

See <a href="https://github.com/IbcAlpha/IBC/blob/master/userguide.md#configuring-ibc">the IBC documentation</a> for a description of IBC settings.

<table>

<tr>
<th>Key
<th>Default
<th>Description

<tr>
<td>IBC_USERNAME
<td>
<td>

<tr>
<td>IBC_PASSWORD
<td>
<td>

<tr>
<td>IBC_FIX
<td>no
<td>

<tr>
<td>IBC_FIX_USERNAME
<td>
<td>

<tr>
<td>IBC_FIX_PASSWORD
<td>
<td>

<tr>
<td>IBC_TRADING_MODE
<td>live
<td>

<tr>
<td>IBC_STORE_SETTINGS_ON_SERVER
<td>no
<td>

<tr>
<td>IBC_EXISTING_SESSION_DETECTED
<td>manual
<td>

<tr>
<td>IBC_ACCEPT_INCOMING_CONNECTION
<td>accept
<td>

<tr>
<td>IBC_SHOW_ALL_TRADES
<td>no
<td>

<tr>
<td>IBC_READONLY_LOGIN
<td>no
<td>

<tr>
<td>IBC_READONLY_API
<td>
<td>

<tr>
<td>IBC_ACCEPT_NON_BROKERAGE_WARNING
<td>yes
<td>

<tr>
<td>IBC_AUTO_CLOSEDOWN
<td>yes
<td>

<tr>
<td>IBC_CLOSEDOWN_AT
<td>
<td>

<tr>
<td>IBC_ALLOW_BLIND_TRADING
<td>no
<td>

<tr>
<td>IBC_DISMISS_PASSWORD_EXPIRY
<td>no
<td>

<tr>
<td>IBC_DISMISS_NSE_COMPLIANCE
<td>yes
<td>

<tr>
<td>IBC_SAVE_TWS_SETTINGS_AT
<td>
<td>

<tr>
<td>IBC_CONTROL_FROM
<td>172.17.0.1
<td>

<tr>
<td>IBC_COMMAND_PROMPT
<td>IBC&gt;
<td>

<tr>
<td>IBC_SUPPRESS_INFO_MESSAGES
<td>yes
<td>

<tr>
<td>IBC_LOG_COMPONENTS
<td>never
<td>

<tr>
<td>VNC_PASSWORD
<td><em>(random)</em>
<td>VNC server password. If unspecified, a random password is
    logged to stdout

<tr>
<td>VNC_NAME
<td>tws-docker
<td>VNC desktop name

<tr>
<td>VNC_DEPTH
<td>24
<td>VNC desktop color depth

<tr>
<td>VNC_GEOMETRY
<td>1920x1080
<td>VNC desktop resolution

</table>


## Base System

Ubuntu 20.04

<table>

<tr>
<th>Package
<th>Description

<tr>
<td><code>wget</code>
<td>Used to fetch TWS installer

<tr>
<td><code>ca-certificates</code>
<td>Inherited from original docker-tws reop

<tr>
<td><code>tightvncserver</code>
<td>The VNC server

<tr>
<td><code>fluxbox</code>
<td>The window manager

<tr>
<td><code>xterm</code>
<td>Terminal emulator

<tr>
<td><code>firefox</code>
<td>Allows account management pages to be opened

<tr>
<td><code>unzip</code>
<td>Used to extract IBC

<tr>
<td><code>openjfx</code>
<td>Needed at least for online help, "No toolkit found" exception in logs otherwise

<tr>
<td><code>openjdk-8-jre</code>
<td>Possibly optional, or required otherwise data feeds fail to connect

</table>
