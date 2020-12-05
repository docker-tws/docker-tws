# `docker-tws`

Docker image for <a href="https://www.interactivebrokers.com/">Interactive
Brokers</a> TWS hosted by <a href="https://github.com/IbcAlpha/IBC">IBC</a>
running under <a href="https://www.tightvnc.com/">TightVNC</a>.

* User configuration is cleanly separated, allowing one computer to serve many
  accounts, store configuration in <a
  href="https://kubernetes.io/">Kubernetes</a> secrets, and for
  one-size-fits-all images to exist on <a
  href="https://hub.docker.com/repository/docker/dockertws/dockertws">Docker
  Hub</a>.

* In line with Kubernetes best practice, IBC and TWS logs are redirected to
  container stdout.

* Docker Hub images are completely transparent, except for upload credentials. CI
  configuration is checked in, and the build log for each cryptographic image
  digest can be audited via <a
  href="https://github.com/docker-tws/docker-tws/actions">GitHub Actions</a>.

* TWS auto-restart is supported. If TWS exits, the container will search for a
  replacement Java process and continue running when one is found.

* [krallin/tini](https://github.com/krallin/tini) is used to avoid stray TWS
  zombie processes accumulating over auto-restarts.

* Running multiple TWS containers within one Kubernetes pod is supported, to
  allow real time market data to be shared between live and paper trading
  accounts.


## Usage

```
docker run \
    --rm -it \
    -e VNC_PASSWORD=123 \
    -p 127.0.0.1:5900:5900 \
    -p 127.0.0.1:7496:7496 \
    dockertws/dockertws:ci
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

### Extracting `jts.ini` and `tws.xml`

For each account you intend to use the image with, login to TWS from a desktop
computer, or simply start the container and login through it. Repeat for each
desired account. Now grab `jts.ini` from your installation, which will contain
a list of encoded account usernames `docker-tws` needs to know where to copy
`tws.xml` to.

Simply grab `tws.xml` after you have finished customizing it. If you created
the files inside a Docker image, use something like `docker cp` to extract
them.


## Exposed Ports

<table>

<tr>
<th>Port
<th>Description

<tr>
<td><code>5900</code> / <code>5901</code>
<td>VNC display (modify using <code>VNC_DISPLAY</code> option)

<tr>
<td><code>7462</code> / <code>7463</code>
<td>IBC telnet server

<tr>
<td><code>7496</code>
<td>TWS API live trading account

<tr>
<td><code>7497</code>
<td>TWS API paper trading account (modify using <code>TWS_API_PORT</code>)

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
<td><code>/conf/tws.xml</code> or <code>tws.xml.gz</code> or <code>tws.xml.zst</code>
<td>File to install as <code>~tws/Jts/[profile]/tws.xml</code>. If provided,
    <code>jts.ini</code> must also be provided, as it is needed to detect the
    profile name.<br>
    <br>
    To fit the XML in a Kubernetes secret it is likely necessary to compress
    it. The image supports <code>zstd</code> specifically for this task, which
    outperforms gzip by a factor of 2, which in some cases may be required.
    Recommended command line: <code>zstd -19 tws.xml</code>

<tr>
<td><code>/home/tws</code>
<td>Home directory that can be mapped to a shared volume such as a Kubernetes
    <code>emptyDir</code>. On initial startup, the directory is locked and a
    pristine TWS is copied into it, if it was previously empty. See
    <strong>Simultaneous Live/Paper Containers</strong> for details.

<tr>
<td><code>/home/tws/Jts</code>
<td>Per-container application directory that can be mapped to a private volume
    such as a Kubernetes <code>emptyDir</code>. On initial startup, the
    directory is populated with a pristine copy of TWS, if it was previously
    empty. pristine TWS is copied into it, if it was previously empty. See
    <strong>Simultaneous Live/Paper Containers</strong> for details.
    <p>&nbsp;
    <p>
    Avoid storing this volume persistently, as the TWS program code is copied
    into it, complicating the task of upgrading TWS version in use.

</table>


## Simultaneous Live/Paper Containers

Your live account and the paper account associated with it may be used
simultaneously, with both receiving real-time market data, so long as both are
used on the same computer. TWS uses a fingerprinting mechanism to verify this,
which breaks if the accounts run in different pods, possibly due to changes in
container IP or MAC addresses.

However, by hosting both instances as containers within the same Kubernetes
pod, with a shared volume mapped over `/home/tws`, and a per-container private
`emptyDir` volume mapped over `/home/tws/Jts`, the check succeeds and it
becomes possible to host this configuration with unattended logins, VNC and
restarts for both accounts.

The `emptyDir` mapping over `/home/tws/Jts` is necessary since it seems
impossible to change the location of `/home/tws/Jts/jts.ini`, causing a race at
startup as the copies of IBC running in each pod update this file to configure
their associated trading mode.


#### Example

An example "combined live/paper" Kubernetes configuration as described below is
supplied in [example/tws-combined.yml](example/tws-combined.yml).


#### Paper Account Setup

Ensure your paper trading account is configured to share real-time market data.

1. From the Interactive Brokers web app, click the burger menu in the top left
2. Choose "Settings" from near the bottom
3. Choose "Account Settings" from the sub-menu
4. Click the gear icon next to "Paper Trading Account" in the right-hand column
   about one third of the way down
5. Enable the option to share real-time market data
6. Wait a few hours for the configuration change to take effect


#### Container / Volume / Environment Variable Setup

When `docker-tws` starts, if `/home/tws` or `/home/tws/Jts` are empty, they are
initialized from a pristine TWS installation stored in the image. The volumes required are:

* `/home/tws`: an `emptyDir` shared volume mounted in both containers. This
  volume will contain at least a magic `.hwid` file that appears to be part of
  the fingerprinting process.

* `/home/tws/Jts`: an `emptyDir` volume that is private to each container,
  needed to avoid a startup race condition.

* `VNC_DISPLAY` should be set to `1` for the paper trading container, so that
  both VNC servers can share the pod IP address.

* `TWS_API_PORT` should be set to `7497` for the paper trading container, so
  that both API servers can share the pod IP address.


## Environment Variables

See <a href="https://github.com/IbcAlpha/IBC/blob/master/userguide.md#configuring-ibc">the IBC documentation</a> for a description of IBC settings.

<table>

<tr>
<th>Key
<th>Default
<th>Description

<tr>
<td>JVM_HEAP_SIZE
<td>4096m
<td>Value of `-Xmx` JVM flag in `tws.vmoptions`

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
<td>IBC_SEND_TWS_LOGS_TO_CONSOLE
<td>yes
<td>If `true`, TWS diagnostic logs will also be sent to the container's stdout

<tr>
<td>IBC_STORE_SETTINGS_ON_SERVER
<td>no
<td>

<tr>
<td>IBC_MINIMIZE_MAIN_WINDOW
<td>no
<td>

<tr>
<td>IBC_MAXIMIZE_MAIN_WINDOW
<td>yes
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
<td>TWS_API_PORT
<td>
<td>If set, the provided <code>tws.xml</code> is rewritten during container
    startup, to replace its API port with the specified value. This allows you
    to manage a single <code>tws.xml</code>, with the only conflicting setting
    preventing it running multiple times within a single Kubernetes pod handled
    automatically.

<tr>
<td>TZ
<td>America/New_York
<td>Container <a
    href="https://en.wikipedia.org/wiki/List_of_tz_database_time_zones">timezone</a>,
    used by TWS to render timestamps

<tr>
<td>VNC_DISPLAY
<td><em>0</em>
<td>VNC X11 display. This is exposed to allow running multiple TWS instances
    within one Kubernetes pod, where the network interface is shared.

<tr>
<td>VNC_PASSWORD
<td><em>(random)</em>
<td>VNC server password. If unspecified, a random password is
    logged to stdout

<tr>
<td>VNC_NAME
<td>tws-<em>tradingmode</em>-<em>username</em>
<td>VNC desktop name

<tr>
<td>VNC_DEPTH
<td>24
<td>VNC desktop color depth

<tr>
<td>VNC_GEOMETRY
<td>1920x1080
<td>VNC desktop resolution

<tr>
<td>X11_ROOT_COLOR
<td>#36648B
<td><kbd>xsetroot</kbd> background color

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
<td><code>openbox</code>
<td>The window manager

<tr>
<td><code>xterm</code>
<td>Terminal emulator

<tr>
<td><code>google-chrome-stable</code>
<td>Allows account management, audit trail, 3D volatility surface to be opened

<tr>
<td><code>unzip</code>
<td>Used to extract IBC

<tr>
<td><code>openjfx</code>
<td>Needed at least for online help, "No toolkit found" exception in logs otherwise

<tr>
<td><code>openjdk-8-jre</code>
<td>Possibly optional, or required otherwise data feeds fail to connect

<tr>
<td>libnss3
<td>Required for Google Chrome

<tr>
<td>libnspr4
<td>Required for Google Chrome

<tr>
<td>fonts-liberation
<td>Required for Google Chrome

<tr>
<td>fonts-dejavu-core
<td>Required for TWS

<tr>
<td>fonts-dejavu-extra
<td>Required for TWS

<tr>
<td>libasound2
<td>Required for sound playback

<tr>
<td>libavcodec58
<td>Required for sound playback

<tr>
<td>libavformat58
<td>Required for sound playback

<tr>
<td>libappindicator3-1
<td>Required for Google Chrome

<tr>
<td>libgbm1
<td>Required for Google Chrome

<tr>
<td>libxslt1.1
<td>Required for JavaFX WebKit (iBot, various other TWS embedded web views)

<tr>
<td>libxss1
<td>Required for Google Chrome

<tr>
<td>xdg-utils
<td>Required for Google Chrome

<tr>
<td>zstd
<td>Settings file decompression

</table>
