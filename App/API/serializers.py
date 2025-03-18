from django.contrib.auth.models import Group, User
from API.models import APRPackets, Agents, Attacks
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class ARPPacketsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = APRPackets
        fields = ['src_ip', 'dst_ip', 'src_mac', 'dst_mac', 'timestamp']

class AttacksSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Attacks
        fields = ['source', 'arp_packets', 'type', 'timestamp']

class AgentsSerializer(serializers.HyperlinkedModelSerializer):
    action = serializers.CharField(read_only=True)
    class Meta:
        model = Agents
        fields = ['agent_name', 'agent_ip', 'agent_last_seen', 'data_count', 'action']