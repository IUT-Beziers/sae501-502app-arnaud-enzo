from django.contrib.auth.models import Group, User
from API.models import APR_MITM, Agents
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']

class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class APR_MITMSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = APR_MITM
        fields = ['src_ip', 'dst_ip', 'src_mac', 'dst_mac', 'data', 'timestamp']

class AgentsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Agents
        fields = ['agent_ip', 'agent_port', 'data_count']