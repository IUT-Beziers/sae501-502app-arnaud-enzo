import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import logging
import requests
from scapy.all import sniff, ARP, get_if_list
import ipaddress
from datetime import datetime
from collections import deque
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import argparse

# Configuration
DEFAULT_API_URL = ""
DEFAULT_API_KEY = ""
PACKET_BUFFER_SIZE = 100

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Packet buffer
packet_buffer = deque(maxlen=PACKET_BUFFER_SIZE)

class ARPMonitorService(win32serviceutil.ServiceFramework):
    """
    Set up the Windows service for the ARP monitoring agent.
    """
    _svc_name_ = "ARPMonitoringAgent"
    _svc_display_name_ = "ARP Monitoring Agent"
    _svc_description_ = "Monitors ARP packets and sends them to an API."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_alive = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def is_private_ip(self, ip):
        """
        Check if an IP address is private.
        """
        return ipaddress.ip_address(ip).is_private

    def create_session(self, api_key):
        """
        Create a new requests session with retries.
        """
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({'Authorization': f'Api-Key {api_key}'})
        return session

    def packet_callback(self, packet, session, api_url):
        """
        Callback function for sniffing packets, captures ARP packets and sends them to the API.
        """
        try:
            if packet.haslayer(ARP):
                src_ip = packet[ARP].psrc
                dst_ip = packet[ARP].pdst
                if self.is_private_ip(src_ip) and self.is_private_ip(dst_ip):
                    data = {
                        'src_ip': src_ip,
                        'dst_ip': dst_ip,
                        'src_mac': packet[ARP].hwsrc,
                        'dst_mac': packet[ARP].hwdst,
                        'timestamp': datetime.now().isoformat()
                    }
                    packet_buffer.append(data)
                    logger.info(f"Captured packet: {data}")

                    if len(packet_buffer) >= PACKET_BUFFER_SIZE:
                        packets_formated = []
                        for packet in packet_buffer:
                            packets_formated.append(f"src_ip: {packet['src_ip']}, dst_ip: {packet['dst_ip']}, src_mac: {packet['src_mac']}, dst_mac: {packet['dst_mac']}, timestamp: {packet['timestamp']}")
                        logger.info(f"Sending {len(packet_buffer)} packets to the API: {packets_formated}")
                        response = session.post(api_url, json=list(packet_buffer))
                        response.raise_for_status()
                        packet_buffer.clear()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending packet to API: {e}")

    def select_interface(self):
        """
        Select a network interface for packet sniffing if not provided as an argument.
        """
        interfaces = get_if_list()
        logger.info("Available interfaces:")
        for i, iface in enumerate(interfaces):
            logger.info(f"{i + 1}. {iface}")
        choice = int(input("Select the interface number: ")) - 1
        return interfaces[choice]

    def main(self):
        """
        Main function for the ARP monitoring agent.
        """
        parser = argparse.ArgumentParser(description="ARP Monitoring Agent")
        parser.add_argument('--api-url', type=str, default=DEFAULT_API_URL, help="API endpoint URL")
        parser.add_argument('--api-key', type=str, default=DEFAULT_API_KEY, help="API key for authentication")
        parser.add_argument('--interface', type=str, help="Network interface to monitor")
        args = parser.parse_args()

        if not args.interface:
            args.interface = self.select_interface()

        session = self.create_session(args.api_key)
        while self.is_alive:
            sniff(prn=lambda packet: self.packet_callback(packet, session, args.api_url), iface=args.interface, store=0, count=100, timeout=10)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(ARPMonitorService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(ARPMonitorService)