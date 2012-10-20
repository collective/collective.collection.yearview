# -*- coding: utf-8 -*-

__author__ = 'Mikko Ohtamaa <mikko.ohtamaa@twinapex.com>'
__docformat__ = 'epytext'
__copyright__ = "2009 Twinapex Research <http://www.twinapex.com>"
__license__ = "GPL"

from DateTime import DateTime
from Acquisition import aq_inner
from zope.i18nmessageid import MessageFactory
from Products.Five.browser import BrowserView
from plone.app.querystring.querybuilder import QueryBuilder
from copy import deepcopy
from plone.memoize.view import memoize

messageFactory = MessageFactory('collective.collection.yearview')
_ = messageFactory


class TopicYearView(BrowserView):
    """ View for ATTopic listing which allows the user to choose to display
    items only from a certain year.

    This is resource hog as it will do two queries:

        - One for extract the available years from the target item brain set

        - One to perform the actual catalog query with the

    """
    @property
    def properties(self):
        return self.context.portal_properties.yearview_properties

    @memoize
    def results(self):
        """ Call queryCatalog, but filter the results by the publishing year.
        """
        context = aq_inner(self.context)
        rawquery = deepcopy(context.getQuery(raw=True))
        year = self.request.get("timespan", None)

        if year:
            row = {}
            row['i'] = self.properties.year_provider_metadata
            row['o'] = "plone.app.querystring.operation.date.between"
            start_date = DateTime(str(year) + "/01/01 00:00 UTC")
            end_date = DateTime(str(year) + "/31/12 23:59 UTC")
            row['v'] = (start_date, end_date)
            rawquery.append(row)

        querybuilder = QueryBuilder(context, self.request)

        sort_on = context.getSort_on()
        sort_order = 'reverse' if context.getSort_reversed() else 'ascending'
        limit = context.getLimit()
        return querybuilder(query=rawquery,
                            batch=False,
                            brains=True,
                            sort_on=sort_on,
                            sort_order=sort_order,
                            limit=limit)

    def resultsUnfiltered(self):
        """ Call queryCatalog, make sure there are no effective batch variables
        """
        # Do not kill performance if we have buggy queries or plenty of news
        b_size = self.properties.max_items_to_query
        return self.context.results(b_size=b_size, brains=True)

    @memoize
    def getYears(self):
        """ Calculate available years.

        Use metadata column in the settings to extract the date information.

        @return: List of integers each presenting a year which has content
        """
        years = []
        for item in self.resultsUnfiltered():
            date = item[self.properties.year_provider_metadata]
            if not date:
                continue
            year = date.year()
            if year == 1000:
                # 1/1/1000 is the default date in unit tests and other fake
                # content
                continue
            if not year in years:
                years.append(year)
        return sorted(years, reverse=True)

    def selector(self, view_url):
        """ Helper function to generate timespan selection in the template.

        @return: list of { "label" : "", "link" : "", "active" : ""
        """
        timespan = self.request.get("timespan", None)
        if timespan != None:
            timespan = int(timespan)

        if len(self.getYears()) < 2:
            # No different years - do not display the selector
            return []

        selector = []

        # fall back to latest items if the timespan is not explictly set
        latest = {"label": _("latest"), "link": view_url}
        latest["active"] = timespan == None

        selector.append(latest)

        for year in self.getYears():
            data = {"label": str(year),
                    "link": "%s?timespan=%s" % (view_url, str(year))
                   }
            data["active"] = timespan == year
            selector.append(data)

        return selector
