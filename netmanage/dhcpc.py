import subprocess
import shutil


def lease(ifacename):
    """Request DHCP lease for interface.
    Note: App should already be running as root, so no sudo needed.
    """
    # Validate interface name to prevent command injection
    if not ifacename or not ifacename.replace('-', '').replace('_', '').isalnum():
        raise ValueError(f"Invalid interface name: {ifacename}")
    
    # Find available DHCP client
    dhcp_client = None
    if shutil.which('dhcpcd'):
        dhcp_client = 'dhcpcd'
        cmd = ['dhcpcd', '-4', '-t', '30', ifacename]  # IPv4, 30s timeout
    elif shutil.which('dhclient'):
        dhcp_client = 'dhclient'
        cmd = ['dhclient', '-4', '-1', '-timeout', '30', ifacename]
    elif shutil.which('udhcpc'):
        dhcp_client = 'udhcpc'
        cmd = ['udhcpc', '-i', ifacename, '-t', '5', '-T', '6']
    else:
        raise RuntimeError("No DHCP client found (dhcpcd, dhclient, or udhcpc)")
    
    try:
        # Use array instead of shell=True to prevent injection
        process = subprocess.run(
            cmd,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            timeout=60  # Prevent hanging
        )
        output = list(filter(None, map(str.strip, process.stdout.split("\n"))))
        return output
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"DHCP request timed out for {ifacename}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"DHCP failed: {e.stderr}")
