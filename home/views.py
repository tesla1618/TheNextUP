from django.shortcuts import render, redirect, HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .matchResult import findResult
from .models import *
import requests
from django.views import View
from datetime import datetime, timedelta
from datetime import date
import datetime

from calendar import monthrange
from django.utils import timezone

def monthsToint(month):
    months = {
        'January': '01',
        'February': '02',
        'March': '03',
        'April': '04',
        'May': '05',
        'June': '06',
        'July': '07',
        'August': '08',
        'September': '09',
        'October': '10',
        'November': '11',
        'December': '12'
    }

    return months[month]




def calendar():
    today = date.today()
    month = today.month
    year = today.year
    last_day_of_month = monthrange(year, month)[1]
    days = [day for day in range(1, last_day_of_month + 1)]
    monthsnum = [month for month in range(1, 13)]
    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    # years = [year for year in range(year, year+20)]
    years = [year]
    dates = []
    current_date = date(year, month, 1)
    last_day = date(year, month, 1) + timedelta(days=31)
    while current_date.month == month:
        dates.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)
        if current_date == last_day:
            break
    return days, today, dates, months,years



def getVidSuggestion(skey):
    # Set up the YouTube Data API endpoint URL
    api_url = "https://www.googleapis.com/youtube/v3/search"

    searchkey = skey

    

    # Set up the search query parameters
    params = {
        "part": "id,snippet",
        "channelId": ["UCsH9CrSfzknNKKwS6wGCeQQ","UC5SQGzkWyQSW_fe-URgq7xw","UC9xRcqG8V6yNi6Hum92EoGg"],
        "q": searchkey,
        "type": "video",
        "maxResults": 4,
        "key": "AIzaSyDdlQBcR6HSwgIB7fL9ix-JgPqr7FtWWtA",
    }

    # Send the API request and retrieve the response
    response = requests.get(api_url, params=params)

    # Parse the response JSON and print the found videos
    for item in response.json()["items"]:
        video_title = item["snippet"]["title"]
        thumbnail_url = item["snippet"]["thumbnails"]["high"]["url"]
        video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        channel_name = item["snippet"]["channelTitle"]
        # print(video_title,"\n",video_url,"\n",thumbnail_url,"\n",channel_name)


# Create your views here.


def signin(request):

    if request.method == "POST":
        if request.POST.get("formFor") == 'signingIn':
            email = request.POST.get("email")
            password = request.POST.get("password")
            user = authenticate(username = email, password = password)

            if user is not None:
                login(request,user)
                return redirect(index)
                
            else:
                messages.error(request, "Wrong Credentials!", extra_tags="signin")
                return HttpResponseRedirect(request.path_info)

    
    if request.POST.get("formFor") == 'signingUp':
        # print("error")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        user = User.objects.filter(email = email)

        if user.exists():
            messages.error(request, "User already exists! Choose a different username", extra_tags="signup")
            return HttpResponseRedirect(request.path_info)
        else:
            if password1 != password2:
                messages.warning(request, "Retyped Password did not match. Please try again", extra_tags="signup")
                return HttpResponseRedirect(request.path_info)
            else:
                user = User.objects.create(username = email, email=email)
                user.set_password(password1)
                user.save()
                user = authenticate(username = email, password = password1)
                login(request,user)
                return redirect(index)
        


    return render(request, 'components/login.html')

@login_required(login_url='/login')
def index(request):

    


    # today = datetime.today()
    today = timezone.now()
    month = today.month
    year = today.year
    last_day_of_month = monthrange(year, month)[1]
    days = [day for day in range(1, last_day_of_month + 1)]

    # days,today,dates = calendar()
    days,today,dates,months,years = calendar()

    
    calTasks = ClaendarTask.objects.all().order_by("taskDate")



    

    calT2 = ClaendarTask.objects.get(taskDate=today)
    try:
        sessions = DailySession.objects.get(sessionFor=calT2)
    except:
        sessions = None
        messages.error(request, "No session found for today!", extra_tags='session')
    # print(sessions)




    print(calT2)
    # print(calTasks)
    addtoTask = ClaendarTask()
    tasks = Task.objects.filter().all()

    if request.method == "POST":
        print("Request Method POST")
        taskfor = request.POST.get("taskfor")
        taskDate = request.POST.get("taskdate")
        taskMonth = request.POST.get("taskmonth")
        print(taskMonth)
        taskMonth = monthsToint(taskMonth)
        print(taskMonth)
        taskYear = request.POST.get("taskyear")

        taskWhen = taskYear + "-" + taskMonth + "-" + taskDate
        taskWhen = datetime.datetime.strptime(taskWhen, '%Y-%m-%d').date() 

        print("dhffhdfh",taskWhen)


        taskTo = Task.objects.filter(taskName=taskfor).first()
        taskIcon = TaskIconSetter.objects.get(taskFor=taskTo)
        taskSave = ClaendarTask(task= taskTo, taskDate=taskWhen,taskIcon=taskIcon)
        taskSave.save()
        return redirect(index)


        # return redirect(addTask(request,taskfor,taskDate))
    
    month = today.month
    months = months[month-1:]
    days = days[today.day-1:]
    month = '{:02d}'.format(month)
    year = str(today.year)
    print(month)
    print(year)
    almostDate = year+"-"+month
    print("----------")
    print(type(almostDate))
    print(date(2023,3,3))

    listOfBads = []
    dictBad = {
        "morefouls": None,
        "moreOffShots":None,
        "lessOnShots":None,
        "lessCATK":None,
        "lessPossession":None,
        "moreoffsides":None,
    }
    stats = MatchResult.objects.filter().order_by('-added')[:1]
    for stat in stats:
        frm = int((stat.fouls_rm / (stat.fouls_opp+stat.fouls_rm))*100)
        fopp = int((stat.fouls_opp / (stat.fouls_opp+stat.fouls_rm))*100)

        if frm > fopp:
            listOfBads.append(frm)
            dictBad["morefouls"] = frm
        
        offrm = int((stat.offsides_rm / (stat.offsides_opp+stat.offsides_rm))*100)
        offopp = int((stat.offsides_opp / (stat.offsides_opp+stat.offsides_rm))*100)

        if offrm > offopp:
            listOfBads.append(offrm)
            dictBad["moreoffsides"] = offrm
        
        sontrm = int((stat.shootsOnTarget_rm / (stat.shootsOnTarget_opp+stat.shootsOnTarget_rm))*100)
        sontopp = int((stat.shootsOnTarget_opp / (stat.shootsOnTarget_opp+stat.shootsOnTarget_rm))*100)

        if sontrm < sontopp:
            listOfBads.append(sontrm)
            dictBad["lessOnShots"] = sontrm
    
        soffrm = int((stat.shootsOffTarget_rm / (stat.shootsOffTarget_opp+stat.shootsOffTarget_rm))*100)
        soffopp = int((stat.shootsOffTarget_opp / (stat.shootsOffTarget_opp+stat.shootsOffTarget_rm))*100)

        if soffrm > soffopp:
            listOfBads.append(soffrm)
            dictBad["moreOffShots"] = soffrm
    

        catkrm = int((stat.counterAttack_rm / (stat.counterAttack_opp+stat.counterAttack_rm))*100)
        catkopp = int((stat.counterAttack_opp / (stat.counterAttack_opp+stat.counterAttack_rm))*100)

        if catkopp > catkrm:
            listOfBads.append(catkrm)
            dictBad["lessCATK"] = catkrm

        posrm = int((stat.possession_rm / (stat.possession_opp+stat.possession_rm))*100)
        posopp = int((stat.possession_opp / (stat.possession_opp+stat.possession_rm))*100)

        if posopp > posrm:
            listOfBads.append(posrm)
            dictBad["lessPossession"] = posrm
    
    for key in list(dictBad.keys()):
        if dictBad[key] is None:
            del dictBad[key]

    sorted_dictBad = dict(sorted(dictBad.items(), key=lambda x: x[1], reverse=True))
    queryDict = {k: v for i, (k, v) in enumerate(sorted_dictBad.items()) if i < 1}

    for key in queryDict:
        if "moreOffShots" in key:
            query = "How to shoot target"
        elif "lessOnShots" in key:
            query = "Shoot Accuracy"
        elif "lessCATK" in key:
            query = "Improve Counter Attack"
        elif "morefouls" in key:
            query = "Decrease Foul"
        elif "lessPossession" in key:
            query = "Keep Possession"
        elif "moreoffsides" in key:
            query = "Offside Improve"

    # print(queryDict)
    # getVidSuggestion(query)


    api_url = "https://www.googleapis.com/youtube/v3/search"

    searchkey = query
    apikey = APIKey.objects.last()
    apikey = str(apikey)

    # Set up the search query parameters
    params = {
        "part": "id,snippet",
        "channelId": ["UCsH9CrSfzknNKKwS6wGCeQQ","UC5SQGzkWyQSW_fe-URgq7xw","UC9xRcqG8V6yNi6Hum92EoGg"],
        "q": searchkey,
        "type": "video",
        "maxResults": 4,
        "key": apikey,
    }

    # Send the API request and retrieve the response
    response = requests.get(api_url, params=params)

    # Parse the response JSON and print the found videos


    vtitle = []
    thumb = []
    vurl = []
    chname = []
    videos = []

    svdata = SuggestedVideo()

    for item in response.json()["items"]:
        video_title = item["snippet"]["title"]
        vtitle.append(video_title)
        thumbnail_url = item["snippet"]["thumbnails"]["high"]["url"]
        thumb.append(thumbnail_url)
        # print(thumbnail_url)
        thumbnail_url = thumbnail_url.replace("hqdefault","maxresdefault")
        # print(thumbnail_url)
        video_url = f"https://www.youtube.com/watch?v={item['id']['videoId']}"
        vurl.append(video_url)
        channel_name = item["snippet"]["channelTitle"]
        chname.append(channel_name)
        video = {
            "title": video_title,
            "url": video_url,
            "thumbnail": thumbnail_url
        }
        videos.append(video)



        # videos.append([video_title, video_url, thumbnail_url])
        # print(video_title,"\n",video_url,"\n",thumbnail_url,"\n",channel_name)

    # print(videos)
    # for video in videos:
    #     print(video[0])
    #     print(video[1])
    #     print(video[2])

    context = {
        'stats':stats,
        'frm':frm,
        'fopp':fopp,
        'offrm':offrm,
        'offopp':offopp,
        'sontrm': sontrm,
        'sontopp':sontopp,
        'soffrm': soffrm,
        'soffopp':soffopp,
        'catkrm':catkrm,
        'catkopp':catkopp,
        "vtitle":vtitle,
        "thumb":thumb,
        "chname":chname,
        "videos":videos,
        "today":today,
        'dates':dates,
        'tasks':tasks,
        'calTasks': calTasks,
        'almostDate': almostDate,
        "days":days,
        'months': months,
        'years': years,
        'session':sessions,

    }
    return render(request, 'pages/index.html', context)


def signout(request):
    logout(request)
    return redirect(index)


def matchResult(request):
    stats = MatchResult.objects.filter().order_by('-added')[:1]
    context = {
        'stats':stats,
    }
    return render(request, 'components/matchResult.html', context)

def settings(request):
    days,today,dates,months,years = calendar()
    year = today.year
    years = [year for year in range(year-100, year-10)]
    settings.resultLink = []
    apidb = APIKey()
    if request.method == "POST":
        if request.POST.get("formFor") == 'addResult':
            settings.resultLink.append(request.POST.get("resultLink"))
            rLink = settings.resultLink[0]
            try:
                findResult(rLink)
                messages.success(request, "Match result successfully added to the database!", extra_tags="result")
                return redirect(settings)
            except:
                messages.error(request, "Invalid Link! please provide a valid stat link", extra_tags="result")
                return redirect(settings)
    
    if request.method == "POST":
        if request.POST.get("formFor") == 'addAPI':
            apikey = request.POST.get("apikey")
            apidb.key = apikey
            try:
                apidb.save()
                messages.success(request, "API key successfully added to the database!", extra_tags="api")
                return redirect(settings)
            except:
                messages.error(request, "Invalid API key! please provide a valid API key", extra_tags="api")
                return redirect(settings)
    
    if request.method == "POST":
        if request.POST.get("formFor") == 'addPlayer':
            try:
                name = request.POST.get("playerName")
                team = request.POST.get("playerTeam")
                position = request.POST.get("playerPosition")
                played = request.POST.get("gamesPlayed")
                goals = request.POST.get("playerGoals")
                assists = request.POST.get("playerAssists")
                placeBirth = request.POST.get("placeOfBirth")
                foot = request.POST.get("prefFoot")
                photo = request.FILES['playerPhoto']
                birthDate = request.POST.get("birthdate")
                birthMonth = request.POST.get("birthmonth")
                birthMonth = monthsToint(birthMonth)
                birthYear = request.POST.get("birthyear")
                age = today.year - int(birthYear)
                birthWhen = birthYear + "-" + birthMonth + "-" + birthDate
                print(birthWhen)
                birthWhen = datetime.datetime.strptime(birthWhen, '%Y-%m-%d').date()
                print(birthWhen)
                savePlayer = Player(name=name,team=team,position=position,gamesPlayed=played,
                    goals=goals,assists=assists,pob=placeBirth,age=age,pfp=photo,dob=birthWhen,isPreferredFootRight=foot)
                savePlayer.save()
                messages.success(request, "Player information has successfully added to the database!", extra_tags="player")
                return redirect(settings)
            except:
                messages.error(request, "Invalid Information! Or player may already exist!", extra_tags="player")
                return redirect(settings)


    
    
    
    
    
    
    
    
    
    context = {
        "days":days,
        'months': months,
        'years': years,
    }


    return render(request, "pages/settings.html", context)


class searchPage(View):

    def get(self, request, *args, **kwargs):
        q = self.request.GET.get('q')
        players = Player.objects.filter(name__icontains=q)
        allplayers = Player.objects.filter().all()
        suggested_players = Player.objects.filter().order_by('?')[:10]
        totfound = len(players)
        totfounds = len(suggested_players)
        # print(totfounds)
        context ={
            'players':players,
            'q':q,
            'totfound':totfound,
            'suggested_players':suggested_players,
            'allplayers': allplayers,
        }

        return render(request, 'pages/search.html', context)


def addTask(request,taskfor,taskDate):
    print("-------addTask-------")
    print(taskfor)
    print(taskDate)
    print("------addTask--------")

def testPage(request):
    days,today,dates,months,years = calendar()
    calTasks = ClaendarTask.objects.all().order_by("taskDate")
    print(calTasks)
    print(calTasks)
    addtoTask = ClaendarTask()
    tasks = Task.objects.filter().all()

    if request.method == "POST":
        print("Request Method POST")
        taskfor = request.POST.get("taskfor")
        taskDate = request.POST.get("taskdate")
        taskMonth = request.POST.get("taskmonth")
        print(taskMonth)
        taskMonth = monthsToint(taskMonth)
        print(taskMonth)
        taskYear = request.POST.get("taskyear")

        taskWhen = taskYear + "-" + taskMonth + "-" + taskDate
        taskWhen = datetime.datetime.strptime(taskWhen, '%Y-%m-%d').date() 

        print("dhffhdfh",taskWhen)


        taskTo = Task.objects.filter(taskName=taskfor).first()
        taskIcon = TaskIconSetter.objects.get(taskFor=taskTo)
        taskSave = ClaendarTask(task= taskTo, taskDate=taskWhen,taskIcon=taskIcon)
        taskSave.save()
        return redirect(testPage)


        # return redirect(addTask(request,taskfor,taskDate))
    
    month = today.month
    months = months[month-1:]
    days = days[today.day-1:]
    month = '{:02d}'.format(month)
    year = str(today.year)
    print(month)
    print(year)
    almostDate = year+"-"+month
    print("----------")
    print(type(almostDate))
    print(date(2023,3,3))
    # for day in days:
    #     print(type(day))


    # print(FetchTask.objects.get(taskFetch=1))

    context = {
        'days':days,
        'today':today,
        'dates':dates,
        'icon': "<i class=\"bi bi-search\"></i>",
        'tasks': tasks,
        'calTasks': calTasks,
        'almostDate': almostDate,
        'months': months,
        'years': years,
    }
    # print(today)
    # print(dates[int(today)])
    return render(request, 'pages/testingPage2.html', context)


# def calTest(request):
#     pass
    # now = datetime.now()
    # month = now.month
    # year = now.year
    # calendar = Calendar.objects.filter(month=month, year=year).first()
    # icon = TaskIconSetter()

    # if not calendar:
    #     calendar = Calendar.objects.create(month=month, year=year)
    # tasks = ClaendarTask.objects.filter(calendar=calendar)
    # # context['calendar'] = calendar
    # # context['tasks'] = tasks
    # context = {
    #     'calendar':calendar,
    #     'tasks':tasks,
    #     'icon':icon,
    # }
    # print(tasks)
    # print(calendar)
    # return render(request, 'pages/testingPage2.html',context)


def getPlayer(request,slug):
    player = Player.objects.get(slug = slug)

    access_key = 'zypfgGMeGIf8ZPudbxKoSeMEWM90m8g-K0MsZ1DCuRI'
    query = player.slug
    url = f'https://api.unsplash.com/search/photos?query={query}&client_id={access_key}'
    print(url)
    response = requests.get(url)
    data = response.json()
    images = data['results']




    context = {
        'player': player,
        'images': images,
    }
    return render(request, 'pages/playerProfile.html', context)