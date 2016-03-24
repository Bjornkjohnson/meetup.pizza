from django.conf import settings

class MeetupUrlBuilder():
  def __init__(self, meetup_url):
    self.meetup_url = meetup_url

  def build_api_components(self):
    url = self.build_api_url()
    params = self.build_params()
    return {'url': url, 'params': params}

  def get_unique_id(self):
    return self.meetup_url.split('/')[-2]

  def build_api_url(self):
    return "https://api.meetup.com/" + self.get_unique_id() + '/events'

  def build_params(self):
    return {"key": settings.MEETUP_KEY }