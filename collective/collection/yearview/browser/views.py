# -*- coding: utf-8 -*-

__author__  = 'Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>'
__docformat__ = 'epytext'
__copyright__ = "2009 Twinapex Research <http://www.twinapex.com>"
__license__ = "GPL"

from DateTime import DateTime
from Acquisition import aq_inner
from zope.i18nmessageid import MessageFactory

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ZCatalog.Lazy import LazyCat

from Products.CMFCore.utils import getToolByName

messageFactory = MessageFactory('collective.collection.yearview')
_ = messageFactory

class TopicYearView(BrowserView):
    """ View for ATTopic listing which allows the user to choose to display items only from a certain year.
    
    This is resource hog as it will do two queries:
    
        - One for extract the available years from the target item brain set
        
        - One to perform the actual catalog query with the 
    
    """
    
    template = ViewPageTemplateFile('year_view.pt')    
    
    def queryCatalog(self):
        """Call Topic.queryCatalog """
        context = aq_inner(self.context)    
        return _queryCatalog(context)
        
    def getFilter(self, year):
        """         
        @param: year, as an integer
        @return: DateRange filter for the selected year
        """
                
        start_date = DateTime(str(year) + "/01/01 00:00 UTC")
        end_date = DateTime(str(year) + "/31/12 23:59 UTC")
        
        # Products/PluginIndexes/tests/test_DateIndex.py
        return {"effective" :{"query":(start_date,end_date), "range" :"min:max" } }
        
    def queryCatalogFiltered(self, extra):
        """ Call queryCatalog, but filter the results by the publishing year. """        
        context = aq_inner(self.context)    
        return self.context.queryCatalog(batch=True, **extra)
    
    def queryCatalogUnfiltered(self):
        """ Call queryCatalog, make sure there are no effective batch variables. """        
        request = {}                
        b_size = self.properties.max_items_to_query # Do not kill performance if we have buggy queries or plenty of news
        return self.context.queryCatalog(REQUEST=request, b_size = b_size)
            
    def getYears(self, items):
        """ Calculate available years.
        
        Use metadata column in the settings to extract the date information.
        
        @param items: Iteratable of catalog Brain object instances
        @return: List of integers each presenting a year which has content
        """
        
        years = []
        
        for i in items:
            
            date = i[self.properties.year_provider_metadata]
            if date:
                year = date.year()
                
                if year == 1000:
                    # 1/1/1000 is the default date in unit tests and other fake content
                    continue
                
                if not year in years:
                    years.append(year)
        
        years.sort()
        years.reverse()
        return years
    
    
    def getSelector(self):
        """ Helper function to generate timespan selection in the template.
        
        @return: list of { "label" : "", "link" : "", "active" : "", title : ""
        """
        
        if self.timespan != None:
            # Some self-check not to let bad input further
            assert type(self.timespan) == type(1)
        
        if len(self.years) < 2:
            # No different years - do not display the selector
            return []
                    
        selector = []
        
        # fall back to latest items if the timespan is not explictly set
        latest = { "label" : _("latest"), "link" : self.context.absolute_url() }
        if self.timespan == None:
            latest["active"] = True
        else:
            latest["active"] = False
        
        selector.append(latest)
        
        for year in self.years:
            data = {"label" : str(year), "link" : self.context.absolute_url() + "?timespan=" + str(year) }
                        
            if self.timespan == year:
                data["active"] = True
            else:
                data["active"] = False
                
            #print "Timespan:" + str(self.timespan) + " year:" + str(year) + " active:" + str(data["active"])
                
            selector.append(data)                
            
        return selector
        
    def update(self):
        """ Prepate data for rendering """
        self.properties = self.context.portal_properties.yearview_properties
        self.all_brains = self.queryCatalogUnfiltered()
        
        # EXtract available years from the data mass
        self.years = self.getYears(self.all_brains)
                
        # This is integer year or None for the current items
        timespan = self.request.get("timespan", None)
                                                    
        if timespan:
            self.timespan = int(timespan)
            filter = self.getFilter(self.timespan)        
            self.results = self.queryCatalogFiltered(extra=filter)
        else:
            self.timespan = None
            self.results = self.queryCatalogFiltered(extra={})
            
        self.selector = self.getSelector()            
                
    def __call__(self):
        ### We cannot directly call update() here because this class is wrapped to magical Five wrapper        
        self.update()
        return self.template()
    
