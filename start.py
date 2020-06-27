#!/usr/bin/env python3

import binascii
import configparser
import glob
import os
import pwd
import shutil
import subprocess


def fix_permissions_and_restart():
    subprocess.check_call(['chown', '-R', 'tws:', '/home/tws'])
    os.execlp('runuser', 'runuser', '-p', 'tws', 'bash', '-c', __file__)


def get_profile_dir():
    parser = configparser.ConfigParser()
    with open('/conf/jts.ini') as fp:
        parser.read_file(fp)

    d = {
        k: int(v)
        for k, v in parser.items('settings')
    }

    name = max(d, key=d.get)
    print('Found profile directory:', name)
    return name


def get_tws_version():
    paths = glob.glob(os.path.expanduser('~/Jts/???'))
    version = os.path.basename(paths[0])
    print('Found TWS version:', version)
    return version


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
                'MinimizeMainWindow=no',
                'ExistingSessionDetectedAction=%s' % env(
                    'IBC_EXISTING_SESSION_DETECTED',
                    'manual',
                ),
                'AcceptIncomingConectionAction=%s' % env(
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


def start_tws():
    subprocess.check_call([
        'tightvncserver',
        '-name', os.environ.get(
            'VNC_NAME',
            'tws-' + os.environ.get('IBC_USERNAME', 'default'),
        ),
        '-depth', os.environ.get('VNC_DEPTH', '24'),
        '-geometry', os.environ.get('VNC_GEOMETRY', '1920x1080'),
        ':0'
    ])

    os.environ['DISPLAY'] = ':0'
    subprocess.check_call([
        '/opt/ibc/scripts/ibcstart.sh',
        get_tws_version()
    ])


def main():
    if os.geteuid() == 0:
        fix_permissions_and_restart()

    fixup_environment()
    set_vnc_password()
    cleanup_x11()
    copy_initial_data()
    write_ibc_config()
    start_tws()


if __name__ == '__main__':
    main()
