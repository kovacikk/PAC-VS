from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from . forms import CreateRoomForm
from . models import Server, Stats
import json


# Create your views here.
def home(request):
    error = "No Error"


    if (request.method == "GET"):
        #print("here")
        form = CreateRoomForm(request.GET)

        if (request.GET.get('pacstats')):
            return redirect('/stats')

        if form.is_valid():
            #print("here2")
            lobbyName = form.cleaned_data['lobbyName']

            if (request.GET.get('createLobby')):
                print("createLobby")
                servers = Server.objects.filter(serverName=lobbyName).first()
                print(servers)
                if (servers != None and servers.numOfPlayers != 0):
                    print("Server already Created")
                    error = "Server Already Created"
                else:
                    Server.objects.create(serverName=lobbyName, numOfPlayers=0)
                    return redirect('/game/' + lobbyName)
            elif(request.GET.get('joinLobby')):
                servers = Server.objects.filter(serverName=lobbyName).first()
                print(servers)
                if (servers == None):
                    print("Server Doesn't Exist")
                    error = "Server Doesn't Exist"
                elif(servers.numOfPlayers >= 2):
                    print("Server Already Full")
                    error = "Server Already Full"
                else:
                    print("redirect")
                    return redirect('/game/' + lobbyName)
            #else:
            print(lobbyName)

    return render(request, 'pac_vs.html', {'error_message': error})

def disconnected(request):
    return render(request, 'disconnected.html')

def stats(request):

    print(request.GET.get('break'))
    if (request.GET.get('break')):
            return redirect('/home')

    stat = Stats.objects.filter(id=1).first()
    if(stat == None):
        stat = Stats.objects.create()
        stat.save()

    pacWin = stat.pacVictories / (stat.ghostVictories + stat.pacVictories)
    pacWin = int(pacWin * 100)

    ghostWin = stat.ghostVictories / (stat.pacVictories + stat.ghostVictories)
    ghostWin = int(ghostWin * 100)
    return render(request, 'stats.html',{'stats': stat, 'pacWinRate': pacWin, 'ghostWinRate': ghostWin,})

def game(request, room_name):
    servers = Server.objects.filter(serverName=room_name).first()
    
    if (servers == None or servers.numOfPlayers >= 2):
        return redirect('/home')
    else:
        return render(request, 'game.html', {
            'room_name_json': mark_safe(json.dumps(room_name))
        })

def test(request, room_name):
    return render(request, 'test.html', {
        'room_name_json': mark_safe(json.dumps(room_name))
    })

def pac_test(request, room_name):

    servers = Server.objects.filter(serverName=room_name).first()
    #print(servers)

    #print(servers.numOfPlayers)
    if (servers == None or servers.numOfPlayers >= 2):
        return redirect('/home')
    else:
        servers.numOfPlayers += 1
        servers.save()
        return render(request, 'pac_test.html', {
            'room_name_json': mark_safe(json.dumps(room_name))
        })

def lose(request):
    return render(request, 'loser.html')

def winner(request):
    return render(request, 'winner.html')

def win(request, pellets, power, win):

    stats = Stats.objects.filter(id=1).first()

    print("pellets", pellets)
    stats.pellets += int(pellets)
    print("power", power)
    stats.PP += int(power)
    print("win", win)
    if (win == 'pacman'):
        stats.pacVictories += 1
    else:
        stats.ghostVictories += 1
    stats.save()

    return redirect('/winner')
