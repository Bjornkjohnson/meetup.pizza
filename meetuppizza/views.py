from django.shortcuts import render

from meetup.models import Meetup
from meetup.services.meetup_service import MeetupService


def index(request):
  meetups = Meetup.objects.all()
  meetup_presenters = [MeetupService(meetup).get_decorated_meetup() for meetup in meetups]

  return render(request, 'index.html', {"meetups": meetup_presenters})
