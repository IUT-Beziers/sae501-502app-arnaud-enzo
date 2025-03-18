from django.db import models
class APRPackets(models.Model):
    id = models.AutoField(primary_key=True)
    src_ip = models.CharField(max_length=15)
    dst_ip = models.CharField(max_length=15)
    src_mac = models.CharField(max_length=17)
    dst_mac = models.CharField(max_length=17)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.src_ip + ' -> ' + self.dst_ip

class Agents(models.Model):
    id = models.AutoField(primary_key=True)
    agent_name = models.CharField(max_length=255)
    agent_ip = models.CharField(max_length=15)
    agent_last_seen = models.DateTimeField(auto_now=True)
    data_count = models.FloatField()

    def __str__(self):
        return self.agent_id + ' -> ' + self.agent_ipy

class Attacks(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.CharField(max_length=50)
    arp_packets = models.ManyToManyField(APRPackets)
    type = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type + ' -> ' + self.timestamp

    def get_packets(self):
        return self.arp_packets.all()