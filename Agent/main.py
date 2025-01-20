import requests
import time
from scapy.all import sniff, ARP

# Renseignez l'URL de l'API
url = 'http://localhost:8000/api/arp'

packets = sniff(timeout=10, filter='arp', store=True)
if packets:
    payload = [str(pkt) for pkt in packets]
    #requests.post(url, json={"packets": payload})
    print(f"Sent {len(packets)} packets.")