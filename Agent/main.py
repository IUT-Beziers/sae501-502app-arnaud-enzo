import requests
import time
from scapy.all import sniff, ARP

# Renseignez l'URL de l'API
url = 'http://localhost:8000/api/packets/'

def packet_callback(packet, session):
    if packet.haslayer(ARP):
        print(packet[ARP].psrc + ' -> ' + packet[ARP].pdst)
        print(packet[ARP].hwsrc + ' -> ' + packet[ARP].hwdst)
        data = {
            'src_ip': packet[ARP].psrc,
            'dst_ip': packet[ARP].pdst,
            'src_mac': packet[ARP].hwsrc,
            'dst_mac': packet[ARP].hwdst,
            'data': packet.summary(),
            'timestamp': time.time()
        }
        session.post(url, json=data)
        print("Headers: ", session.headers)

def main():
    session = requests.Session()
    # Authentification vers l'API avec session
    login_page = session.get('http://localhost:8000/api-auth/login/')
    csrf_token = login_page.cookies['csrftoken']
    api_key = 'QzCMaDju.d1tuKzqkl9zrCjUfn1TR6WHTEawFVRVz'
    session.headers.update({'Authorization': 'Api-Key QzCMaDju.d1tuKzqkl9zrCjUfn1TR6WHTEawFVRVz'})
    session.post('http://localhost:8000/api-auth/login/', data={'csrfmiddlewaretoken': csrf_token})

    sniff(prn=lambda packet: packet_callback(packet, session), iface='en7', store=0)

if __name__ == '__main__':
    main()