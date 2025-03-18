from django.core.management.base import BaseCommand, CommandError
from scapy.all import srp, Ether, ARP, sr1, IP, ICMP
from API.models import APRPackets, Attacks
from datetime import timedelta
from django.utils import timezone
from collections import defaultdict

class Command(BaseCommand):
    help = "Process packets to detect ARP spam and ARP spoofing. (Run every 10 minutes with a cron job)"

    def handle(self, *args, **options):
        process_packets()
        cleanup_old_packets()
        print("Processed packets and cleaned up old data")

def process_packets():
    """
    Process ARP packets to detect ARP spam and ARP spoofing.
    """
    packets = APRPackets.objects.filter(timestamp__gt=timezone.now() - timedelta(minutes=10))
    print("Processing packets")

    statsForEachMac = defaultdict(lambda: [0, []])  # Count and list of packet IDs
    ipToMac = defaultdict(set)  # IP to MAC mapping

    for packet in packets:
        statsForEachMac[packet.src_mac][0] += 1
        statsForEachMac[packet.src_mac][1].append(packet.id)
        ipToMac[packet.src_ip].add(packet.src_mac)

    # Detect ARP Flooding
    for mac, stats in statsForEachMac.items():
        if stats[0] > 100:  # Threshold for ARP flood
            attack = Attacks(type='ARP Flood', source=mac, timestamp=timezone.now())
            attack.save()
            for packet_id in stats[1]:
                packet = APRPackets.objects.get(id=packet_id)
                attack.arp_packets.add(packet)
            attack.save()

    # Detect ARP Spoofing
    for ip, macs in ipToMac.items():
        if len(macs) > 1:  # More than one MAC address for the same IP
            # Get the real MAC address for the IP
            real_mac = getRealMac(ip)
            if real_mac:
                # Check if any MAC address in the set is not the real MAC
                spoofed_macs = {mac for mac in macs if mac != real_mac}
                if spoofed_macs:
                    # Get the real IPv4 address for the MAC
                    real_ip = getRealIPv4(real_mac)
                    attack = Attacks(
                        type='ARP Spoofing',
                        source=ip,
                        details=f"Real MAC: {real_mac}, Real IP: {real_ip}, Spoofed MACs: {', '.join(spoofed_macs)}",
                        timestamp=timezone.now()
                    )
                    attack.save()
                    for mac in spoofed_macs:
                        packets = APRPackets.objects.filter(src_ip=ip, src_mac=mac)
                        for packet in packets:
                            attack.arp_packets.add(packet)
                    attack.save()

def getRealMac(ip):
    """
    Send an ARP request to find the real MAC address for a given IP.
    """
    try:
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=2, verbose=0)
        for _, r in ans:
            return r[Ether].src
    except Exception as e:
        print(f"Error getting real MAC for IP {ip}: {e}")
    return None

def getRealIPv4(mac):
    """
    Send an ICMP (ping) request to find the real IPv4 address for a given MAC.
    """
    try:
        # Create an ICMP echo request packet
        packet = Ether(dst=mac)/IP(dst="255.255.255.255")/ICMP()
        response = sr1(packet, timeout=2, verbose=0)
        if response and response.haslayer(IP):
            return response[IP].src
    except Exception as e:
        print(f"Error getting real IPv4 for MAC {mac}: {e}")
    return None

def cleanup_old_packets():
    """
    Remove all packets older than 1 week that are not related to an attack.
    """
    one_week_ago = timezone.now() - timedelta(weeks=1)
    old_packets = APRPackets.objects.filter(timestamp__lt=one_week_ago)

    # Find packets associated with attacks
    attack_packets = set()
    for attack in Attacks.objects.all():
        attack_packets.update(attack.arp_packets.values_list('id', flat=True))

    # Delete packets older than 1 week that are not in any attack
    packets_to_delete = old_packets.exclude(id__in=attack_packets)
    count = packets_to_delete.count()
    packets_to_delete.delete()

    print(f"Deleted {count} old packets not related to any attack.")