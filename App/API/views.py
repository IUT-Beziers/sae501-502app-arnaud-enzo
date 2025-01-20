from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from API.models import Packets, Agents

from API.serializers import GroupSerializer, UserSerializer, PacketsSerializer, AgentsSerializer
from rest_framework import status
from rest_framework.response import Response

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]

class PacketsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows packets to be viewed or edited.
    """
    queryset = Packets.objects.all().order_by('-timestamp')
    serializer_class = PacketsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def POST(self, request):
        data = request.data
        serializer = PacketsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def GET(self, request):
        data = Packets.objects.all()
        serializer = PacketsSerializer(data, many=True)
        return Response(serializer.data)

class AgentsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows agents to be viewed or edited.
    """
    queryset = Agents.objects.all().order_by('agent_ip')
    serializer_class = AgentsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def POST(self, request):
        data = request.data
        serializer = AgentsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def GET(self, request):
        data = Agents.objects.all()
        serializer = AgentsSerializer(data, many=True)
        return Response(serializer.data)