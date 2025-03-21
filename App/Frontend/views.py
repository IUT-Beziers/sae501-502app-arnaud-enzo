from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import requests
from django.contrib.auth.models import User
from datetime import datetime

def index(request):
    """Login page"""
    if request.user.is_authenticated:
        return redirect('home')
    else :
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                return render(request, 'dashboard/index.html', {'error': 'Invalid credentials'})

    return render(request, 'dashboard/index.html')

@login_required
def home(request):
    try:
        response_packets = requests.get('http://localhost:8000/api/packets')
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

    try:
        response_attacks = requests.get('http://localhost:8000/api/analysis')
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

    if response_packets.status_code == 200 and response_attacks.status_code == 200:
        try:
            ARPPackets = response_packets.json()
        except:
            ARPPackets = []
        try:
            Attacks = response_attacks.json()
        except:
            Attacks = []
    else:
        ARPPackets = []
        Attacks = []

    return render(request, 'dashboard/home.html', {'packets': ARPPackets, 'attacks': Attacks})

@login_required
def agent(request):
    response_agents = requests.get('http://localhost:8000/api/agents/')

    if request.method == 'POST':
        agent_name = request.POST['agent_name']
        agent_ip = "N/A"
        agent_interface = request.POST['agent_interface']
        data_count = 0
        action = "create"
        agent_data = {'agent_name': agent_name, 'agent_ip': agent_ip, 'data_count': data_count, 'action': action, 'interface': agent_interface}

        try:
            response = requests.post('http://localhost:8000/api/agents/', data=agent_data)
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

        try:
            response_agents = requests.get('http://localhost:8000/api/agents/')
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

        if response.status_code == 201:
            try:
                detail = response.json()["detail"]
                curl_command = response.json()["curl_command"]
            except:
                detail = ""
                curl_command = ""
        else:
            detail = ""
            curl_command = ""


        if response_agents.status_code == 200:
            try:
                Agents = response_agents.json()
                for agent in Agents:
                    if 'agent_last_seen' in agent:
                        agent['agent_last_seen'] = datetime.strptime(agent['agent_last_seen'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d/%m/%Y %H:%M')
            except:
                    Agents = []
        else:
            Agents = []

        return render(request, 'dashboard/agent.html', {'agents': response_agents.json(), 'detail': detail, 'curl_command': curl_command})

    if response_agents.status_code == 200:
        try:
            Agents = response_agents.json()
            for agent in Agents:
                if 'agent_last_seen' in agent:
                    agent['agent_last_seen'] = datetime.strptime(agent['agent_last_seen'], '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d/%m/%Y %H:%M')
        except:
            Agents = []
    else:
        Agents = []

    return render(request, 'dashboard/agent.html', {'agents': Agents, 'create': True})

@login_required
def settings(request):
    return render(request, 'dashboard/settings.html')

@login_required
def signout(request):
    logout(request)
    return redirect('index')