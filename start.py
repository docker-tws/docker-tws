#!/usr/bin/env python3

import binascii
import configparser
import glob
import os
import pwd
import shutil
import signal
import subprocess
import sys
import time


def fix_permissions_and_restart():
    subprocess.check_call(['chown', '-R', 'tws:', '/home/tws'])
    os.execlp('runuser', 'runuser', '-p', 'tws', 'bash', '-c', __file__)


def set_timezone():
    os.environ.setdefault('TZ', 'America/New_York')


def get_profile_dir():
    parser = configparser.ConfigParser()
    with open('/conf/jts.ini') as fp:
        parser.read_file(fp)

    d = dict(parser.items('Logon'))
    print(d)
    lst = d['usernametodirectory'].split(',')
    print('Found profile directory:', lst[0])
    return lst[0]


def set_vnc_password():
    default_password = binascii.hexlify(os.getrandom(16)).decode()
    os.environ.setdefault('VNC_PASSWORD', default_password)

    os.makedirs(os.path.expanduser('~/.vnc'), exist_ok=True)
    with open(os.path.expanduser('~/.vnc/passwd'), 'w') as fp:
        proc = subprocess.Popen(
            args=['vncpasswd', '-f'],
            stdout=fp,
            stdin=subprocess.PIPE,
        )
        proc.communicate(input=os.environ['VNC_PASSWORD'].encode())
        proc.wait()
        assert proc.returncode == 0

    subprocess.check_call(['chmod', '-R', 'go=', os.path.expanduser('~/.vnc')])
    print('VNC password is:', os.environ['VNC_PASSWORD'])


def copy_initial_data():
    if os.path.exists('/conf/jts.ini'):
        shutil.copy('/conf/jts.ini',
                    os.path.expanduser('~/Jts/jts.ini'))

    if os.path.exists('/conf/tws.xml'):
        profile_dir = os.path.join('~/Jts', get_profile_dir())
        os.makedirs(os.path.expanduser(profile_dir), exist_ok=True)
        shutil.copy('/conf/tws.xml',
                    os.path.expanduser(os.path.join(profile_dir, 'tws.xml')))


def write_ibc_config():
    os.makedirs(os.path.expanduser('~/ibc'), exist_ok=True)
    env = lambda k, d: (os.environ.get(k, d),)

    with open(os.path.expanduser('~/ibc/config.ini'), 'w') as fp:
        fp.write('%s\n' % (
            '\n'.join((
                'LogOutputPath=/tmp/logs-fifo',
                'FIX=%s' % env('IBC_FIX', 'no'),
                'IbLoginId=%s' % env(
                    'IBC_USERNAME',
                    '',
                ),
                'IbPassword=%s' % env(
                    'IBC_PASSWORD',
                    '',
                ),
                'FIXLoginId=%s' % env(
                    'IBC_FIX_USERNAME',
                    '',
                ),
                'FIXPassword=%s' % env(
                    'IBC_FIX_PASSWORD',
                    '',
                ),
                'TradingMode=%s' % env(
                    'IBC_TRADING_MODE',
                    'live',
                ),
                'IbDir=',
                'SendTWSLogsToConsole=%s' % env(
                    'IBC_SEND_TWS_LOGS_TO_CONSOLE',
                    'yes',
                ),
                'StoreSettingsOnServer=%s' % env(
                    'IBC_STORE_SETTINGS_ON_SERVER',
                    'no',
                ),
                'MinimizeMainWindow=%s' % env(
                    'IBC_MINIMIZE_MAIN_WINDOW',
                    'no',
                ),
                'MaximizeMainWindow=%s' % env(
                    'IBC_MAXIMIZE_MAIN_WINDOW',
                    'yes'
                ),
                'ExistingSessionDetectedAction=%s' % env(
                    'IBC_EXISTING_SESSION_DETECTED',
                    'manual',
                ),
                'AcceptIncomingConnectionAction=%s' % env(
                    'IBC_ACCEPT_INCOMING_CONNECTION',
                    'accept',
                ),
                'ShowAllTrades=%s' % env(
                    'IBC_SHOW_ALL_TRADES',
                    'no',
                ),
                'OverrideTwsApiPort=',
                'ReadOnlyLogin=%s' % env(
                    'IBC_READONLY_LOGIN',
                    'no',
                ),
                'ReadOnlyApi=%s' % env(
                    'IBC_READONLY_API',
                    '',
                ),
                'AcceptNonBrokerageAccountWarning=%s' % env(
                    'IBC_ACCEPT_NON_BROKERAGE_WARNING',
                    'yes',
                ),
                'IbAutoClosedown=%s' % env(
                    'IBC_AUTO_CLOSEDOWN',
                    'yes',
                ),
                'ClosedownAt=%s' % env(
                    'IBC_CLOSEDOWN_AT',
                    ''
                ),
                'AllowBlindTrading=%s' % env(
                    'IBC_ALLOW_BLIND_TRADING',
                    'no',
                ),
                'DismissPasswordExpiryWarning=%s' % env(
                    'IBC_DISMISS_PASSWORD_EXPIRY',
                    'no',
                ),
                'DismissNSEComplianceNotice=%s' % env(
                    'IBC_DISMISS_NSE_COMPLIANCE',
                    'yes',
                ),
                'SaveTwsSettingsAt=',
                'CommandServerPort=7462',
                'ControlFrom=%s' % env(
                    'IBC_CONTROL_FROM',
                    '172.17.0.1',
                ),
                'BindAddress=',
                'CommandPrompt=%s' % env(
                    'IBC_COMMAND_PROMPT',
                    'IBC> ',
                ),
                'SuppressInfoMessages=%s' % env(
                    'IBC_SUPPRESS_INFO_MESSAGES',
                    'yes'
                ),
                'LogComponents=%s' % env(
                    'IBC_LOG_COMPONENTS',
                    'never',
                ),
            )),
        ))


def fixup_environment():
    pwent = pwd.getpwuid(os.geteuid())
    os.environ['USER'] = pwent.pw_name
    os.environ['LOGNAME'] = pwent.pw_name
    os.environ['HOME'] = pwent.pw_dir
    os.environ['SHELL'] = pwent.pw_shell


def cleanup_x11():
    try:
        os.unlink('/tmp/.X11-unix/X0')
    except OSError:
        pass

    try:
        os.unlink('/tmp/.X0-lock')
    except OSError:
        pass


def start_vnc_server():
    vnc = subprocess.Popen([
        'Xtightvnc',
        ':0',
        '-geometry', os.environ.get('VNC_GEOMETRY', '1920x1080'),
        '-depth', os.environ.get('VNC_DEPTH', '24'),
        '-rfbwait', '120000',
        '-nevershared',
        '-rfbauth', os.path.expanduser('~/.vnc/passwd'),
        '-desktop', os.environ.get(
            'VNC_NAME',
            'tws-%s-%s' % (
                os.environ.get('IBC_TRADING_MODE', 'live'),
                os.environ.get('IBC_USERNAME', 'default')
            ),
        ),
    ])

    while not os.path.exists('/tmp/.X11-unix/X0'):
        if vnc.poll():
            print('VNC failed to start')
            return False
        time.sleep(0.05)

    return True


def update_jvm_options():
    path = '/home/tws/Jts/current/tws.vmoptions'
    agent_line = -1

    with open(path, 'r+') as fp:
        lines = fp.readlines()
        for i, line in enumerate(lines):
            if line.startswith('-Xmx'):
                lines[i] = '-Xmx%s\n' % (os.environ.get('JVM_HEAP_SIZE', '4096m'),)
            if line.startswith('-javaagent'):
                agent_line = i

        if agent_line == -1:
            lines.append(None)

        lines[agent_line] = '-javaagent:%s=%s\n' % (
            '/opt/ibc/IBC.jar',
            os.path.expanduser('~/ibc/config.ini'),
        )

        fp.seek(0)
        fp.truncate(0)
        fp.writelines(lines)


_logs_fifo = None


def start_logs_forwarder():
    global _logs_fifo

    if not os.path.exists('/tmp/logs-fifo'):
        os.mkfifo('/tmp/logs-fifo')

    proc = subprocess.Popen(['stdbuf', '-oL', 'cat', '/tmp/logs-fifo'])
    # Hold the FIFO open to prevent 'cat' from exiting during TWS auto-restart.
    # Must occur *after* cat has started to avoid deadlock.
    _logs_fifo = open('/tmp/logs-fifo', 'wb', 0)
    return proc


def start_tws():
    os.environ['DISPLAY'] = ':0'

    subprocess.check_call([
        'xsetroot',
        '-solid', os.environ.get('X11_ROOT_COLOR', '#473C8B')
    ])

    wm = subprocess.Popen(['openbox'])
    tws_path = '/home/tws/Jts/current/tws'
    return subprocess.Popen(
        args=[tws_path],
        env=dict(os.environ, **{'I_AM_TWS': '1'})
    )


def is_process_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def wait_for_completion(pid):
    while is_process_alive(pid):
        time.sleep(1.5)


def find_tws_process():
    for pid in os.listdir('/proc'):
        if not pid.isdigit():
            continue

        try:
            path = os.readlink('/proc/%s/exe' % (pid,))
        except OSError:
            continue

        if os.path.basename(path) != 'java':
            continue

        with open('/proc/%s/environ' % (pid,)) as fp:
            env = fp.read()

        if 'I_AM_TWS=1' in env:
            sys.stderr.write('docker_tws: found new TWS PID %s\n' % (pid,))
            return int(pid)

    sys.stderr.write('docker_tws: could not find new TWS PID\n')
    return None


def block_until_exit(proc):
    """
    TWS auto-restart may exit the original process, but another will spring up
    in its wake. We identify it by scanning for a /proc/*/exe whose
    basename(readlink()) is "java" and whose environ contains "I_AM_TWS"
    """
    pid = proc.pid
    while pid is not None:
        wait_for_completion(pid)
        pid = find_tws_process()


def main():
    if os.geteuid() == 0:
        fix_permissions_and_restart()

    # Allow child processes to self-reap (during auto-restart)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    fixup_environment()
    set_timezone()
    set_vnc_password()
    cleanup_x11()
    copy_initial_data()
    write_ibc_config()
    update_jvm_options()
    if not start_vnc_server():
        return

    forwarder = start_logs_forwarder()
    try:
        block_until_exit(start_tws())
    finally:
        forwarder.terminate()
        forwarder.wait()

if __name__ == '__main__':
    main()
