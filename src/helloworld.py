from __future__ import division
import wsgiref.handlers
import os
from datetime import datetime
from time import time, gmtime, localtime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

from Rose import Rose
import twitter_local
from account import uname, passwd

class RoseHolder(object):
    def __init__(self, name):
        self.name = name
        self.api = twitter_local.Api(username=uname,password=passwd)
        self.offset = self.api.GetUser(name).GetUtcOffset()
        self.updates = None
        self.friend_updates = None
        self.utimes = None
        self.ftimes = None
        attempts = 0
        while ((attempts < 3) and (self.updates is None)):
            try:
                self.updates = self.userTimeline(name)
            except:
                attempts += 1
                self.updates = self.userTimeline(name)
        attempts = 0
        while ((attempts < 3) and (self.friend_updates is None)):
            try:
                self.friend_updates = self.friendTimeline(name)
            except:
                attempts += 1
                self.friend_updates = self.friendTimeline(name)
                            
    def userTimeline(self, name):
        return self.api.GetUserTimeline(name, 500)
    def friendTimeline(self, name):
        return self.api.GetFriendsTimeline(name, 200)

    def getClock(self,user=True, hr=24, size=400, times=None):
        if user: stati = self.updates
        else: stati = self.friend_updates
        if times: lst = times
        else: 
            lst = self.getTimes(stati)
            if user: self.utimes = lst
            else: self.ftimes = lst
        r = Rose()
        r.list = lst
        r.size = size
        if (hr == 24): r.labels = ['Midnight','Morning','Noon','Evening']
        else: r.labels = ['12','3','6','9']
        r.range = (0.0,float(hr*10))
        r.step = 10
        r.mod = 10
        r.generate()
        return r

    def getTimes(self, updates):
        lst = []
        for status in updates:
            d = status
            t = d.GetCreatedAtInSeconds() + self.offset
            h, m, s = localtime(t)[3:6]
            print h, m, s,
            lst.append((h*10) + (m/10) + (s/100))
        return lst
    
    def userClock(self): return self.getClock()
    def friendClock(self): return self.getClock(False)
    def user12Clocks(self):
        am = [i for i in filter(lambda x: x <=120, self.utimes)]
        pm = [i-120 for i in filter(lambda x: x > 120, self.utimes)]
        amclock = self.getClock(True, 12, 200, am)
        pmclock = self.getClock(True, 12, 200, pm)
        return amclock, pmclock
    def friend12Clocks(self):
        am = [i for i in filter(lambda x: x <=120, self.ftimes)]
        pm = [i-120 for i in filter(lambda x: x > 120, self.ftimes)]
        amclock = self.getClock(True, 12, 200, am)
        pmclock = self.getClock(True, 12, 200, pm)
        return amclock, pmclock


class MainPage(webapp.RequestHandler):    
    def get(self):
        clock = RoseHolder('twitter')
        userClock = clock.userClock()
        friendClock = clock.friendClock()
        u_amclock, u_pmclock = clock.user12Clocks()
        f_amclock, f_pmclock = clock.friend12Clocks()
        
        template_values = {'rose': userClock.url,
                           'frose': friendClock.url,
                           'u_amclock': u_amclock.url,
                           'u_pmclock': u_pmclock.url,
                           'f_amclock': f_amclock.url,
                           'f_pmclock': f_pmclock.url,
                           'name': clock.name}
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

class Diagrams(webapp.RequestHandler):
    def post(self):
        name = self.request.get('name')
        self.redirect('/user/%s' % name)
#        path = os.path.join(os.path.dirname(__file__), 'user/%s' % name)
#        self.response.out.write(template.render(path, template_values))
            
#        self.redirect('/result')
class DiagramsDirect(webapp.RequestHandler):
    def get(self, name):
        clock = RoseHolder(name)
        userClock = clock.userClock()
        friendClock = clock.friendClock()
        u_amclock, u_pmclock = clock.user12Clocks()
        f_amclock, f_pmclock = clock.friend12Clocks()
        template_values = {'rose': userClock.url,
                           'frose': friendClock.url,
                           'u_amclock': u_amclock.url,
                           'u_pmclock': u_pmclock.url,
                           'f_amclock': f_amclock.url,
                           'f_pmclock': f_pmclock.url,
                           'name': clock.name}
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

            

def main():
    application = webapp.WSGIApplication([('/', MainPage),
                                        ('/submit_form', Diagrams),
                                        (r'/user/(.*)', DiagramsDirect)],#,
                                        debug=True)
                                        #('/result', Result),
                                        #('/recent', Recent)],
    wsgiref.handlers.CGIHandler().run(application)


if __name__ == "__main__":
    main()
