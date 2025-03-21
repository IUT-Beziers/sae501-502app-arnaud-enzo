from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from API.models import APRPackets, Agents, Attacks
from API.serializers import GroupSerializer, UserSerializer, AgentsSerializer, ARPPacketsSerializer, AttacksSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_api_key.models import APIKey
from datetime import timedelta
from django.utils import timezone
import os

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
    queryset = APRPackets.objects.all().order_by('-timestamp')
    serializer_class = ARPPacketsSerializer
    permission_classes = [HasAPIKey | permissions.IsAuthenticatedOrReadOnly]

    def create(self, request):
        data = request.data

        # Handle both single packet and batch submissions
        if isinstance(data, list):
            # Batch submission
            return self._handle_batch_packets(data)
        else:
            # Single packet submission
            return self._handle_single_packet(data)

    def _handle_single_packet(self, data):
        """
        Handle submission of a single packet.
        """
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # Extract packet data
        src_mac = serializer.validated_data.get('src_mac')
        src_ip = serializer.validated_data.get('src_ip')
        dst_mac = serializer.validated_data.get('dst_mac')
        dst_ip = serializer.validated_data.get('dst_ip')
        timestamp = serializer.validated_data.get('timestamp')

        # Check for duplicates
        if not self._is_duplicate_packet(src_mac, src_ip, dst_mac, dst_ip, timestamp):
            # Update some agent data
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"detail": "Duplicate packet detected."},
                status=status.HTTP_409_CONFLICT
            )

    def _handle_batch_packets(self, data):
        """
        Handle submission of a batch of packets.
        """
        saved_packets = []
        duplicate_packets = []

        for packet_data in data:
            serializer = self.get_serializer(data=packet_data)
            if serializer.is_valid():
                src_mac = serializer.validated_data.get('src_mac')
                src_ip = serializer.validated_data.get('src_ip')
                dst_mac = serializer.validated_data.get('dst_mac')
                dst_ip = serializer.validated_data.get('dst_ip')
                timestamp = serializer.validated_data.get('timestamp')

                # Check for duplicates
                if not self._is_duplicate_packet(src_mac, src_ip, dst_mac, dst_ip, timestamp):
                    self.perform_create(serializer)
                    saved_packets.append(serializer.data)
                else:
                    duplicate_packets.append(packet_data)
            else:
                # Handle invalid packet data
                duplicate_packets.append(packet_data)

        # Return response with saved and duplicate packets
        response_data = {
            "saved_packets": saved_packets,
            "duplicate_packets": duplicate_packets
        }
        return Response(response_data, status=status.HTTP_207_MULTI_STATUS)

    def _is_duplicate_packet(self, src_mac, src_ip, dst_mac, dst_ip, timestamp):
        """
        Check if a packet with the same attributes already exists in the database.
        """
        # Allow for a small time window (e.g., 1 second) to account for minor timestamp differences
        time_window = timedelta(seconds=1)
        if timestamp is None:
            return False
        duplicate = APRPackets.objects.filter(
            src_mac=src_mac,
            src_ip=src_ip,
            dst_mac=dst_mac,
            dst_ip=dst_ip,
            timestamp__gte=timestamp - time_window,
            timestamp__lte=timestamp + time_window
        ).exists()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AnalysisViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows attacks to be viewed.
    """
    queryset = Attacks.objects.all().order_by('-timestamp')
    serializer_class = AttacksSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class AgentsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows agents to be viewed or edited.
    """
    queryset = Agents.objects.all().order_by('agent_name')
    serializer_class = AgentsSerializer
    permission_classes = [permissions.AllowAny]

    def agent_exists(self, name):
        return Agents.objects.filter(agent_name=name).exists()

    def create(self, request):
        data = request.data

        if self.agent_exists(data.get('agent_name')):
            if(data.get('action') == 'update'):
                agent = Agents.objects.get(agent_name=data.get('agent_name'))
                agent.agent_ip = data.get('agent_ip')
                agent.agent_last_seen = timezone.now()
                agent.save()
                return Response(
                    {"detail": "Agent updated successfully."},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {"detail": "Agent already exists."},
                    status=status.HTTP_409_CONFLICT
                )
        else:
            if data.get('action') == 'update':
                return Response(
                    {"detail": "Agent does not exist."},
                    status=status.HTTP_404_NOT_FOUND
                )
            else:
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)

                # Create API key for agent using rest_framework_api_key library
                api_key, key = APIKey.objects.create_key(name=data.get('agent_name'))

                # Generate curl command for agent registration using APP_FQDN environment variable
                app_fqdn = os.getenv('APP_FQDN', 'localhost')
                scipt_url = os.getenv('SCRIPT_URL', 'http://localhost:8000/static/install-agent.sh')
                curl_command = (
                    f"curl -sSL {scipt_url} | sudo bash -s -- "
                    f"--api-url \"http://{app_fqdn}/api/packets/\" "
                    f"--api-key \"{key}\" "
                    f"--interface \"{data.get('interface')}\""
                )

                return Response(
                    {"detail": "Agent registered successfully.", "curl_command": curl_command},
                    status=status.HTTP_201_CREATED
                )

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)