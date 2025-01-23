import requests
import time
from scapy.all import sniff, ARP, Ether, IP, srp

# Renseignez l'URL de l'API
url = 'http://localhost:8000/api/packets/'

def mac(ipadd):
    arp_request = ARP(pdst=ipadd)
    br = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_req_br = br / arp_request
    answered, _ = srp(arp_req_br, timeout=5, 
                       verbose=False)
    if answered:
        return answered[0][1].hwsrc
    return None

def packet_callback(packet, session):
    if packet.haslayer(ARP) and packet[ARP].op == 2:
        # Comparaison des adresses MAC

        announced_mac = packet[ARP].hwsrc
        real_mac = mac(packet[ARP].psrc)

        print(announced_mac + ' ' + real_mac)

        if announced_mac != real_mac:
            data = {
                'src_ip': packet[ARP].psrc,
                'dst_ip': packet[ARP].pdst,
                'src_mac': announced_mac,
                'dst_mac': packet[ARP].hwdst,
                'timestamp': time.time()
            }
        session.post(url, json=data)

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