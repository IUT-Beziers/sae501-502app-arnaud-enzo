from django.db import models

# Model for TCP packets
class Packets(models.Model):
    id = models.AutoField(primary_key=True)
    src_ip = models.CharField(max_length=15)
    dst_ip = models.CharField(max_length=15)
    src_mac = models.CharField(max_length=17)
    dst_mac = models.CharField(max_length=17)
    src_port = models.IntegerField()
    dst_port = models.IntegerField()
    data = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.src_ip + ' -> ' + self.dst_ip

class Agents(models.Model):
    id = models.AutoField(primary_key=True)
    agent_ip = models.CharField(max_length=15)
    agent_port = models.IntegerField()
    data_count = models.FloatField()

    def __str__(self):
        return self.agent_id + ' -> ' + self.agent_ip