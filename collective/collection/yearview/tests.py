import unittest


from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc
from DateTime import DateTime

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

ptc.setupPloneSite(products=['collective.collection.yearview'])

import collective.collection.yearview

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.collection.yearview)
            fiveconfigure.debug_mode = False
            
            ztc.installPackage('collective.collection.yearview')    

        @classmethod
        def tearDown(cls):
            pass
        
        
class TestView(TestCase):
    """ Unit tests for TopicYearView browser view class """
    
    def createContent(self):
        """ Create sample content tree """
        self.loginAsPortalOwner()
        self.portal.invokeFactory("Topic", "topic")
        
        topic = self.portal.topic
    
        topic.addCriterion('portal_type', 'ATPortalTypeCriterion' )
        
        crit = topic.getCriterion("portal_type_ATPortalTypeCriterion")
        #self.dummy.Schema()['field'].set(self.dummy, 'portal_type')
        crit.setValue(('Document')) # This collection looks up Document content types

        self.content_counter = 0

    def createDocument(self, year=None):
        """
        
        @param year: Set content publishing date to arbitary value containing this year
        """
        
        self.content_counter += 1        
        id = "page" + str(self.content_counter) + "_" + str(year)      
        self.portal.invokeFactory("Document", id)
    
        doc = self.portal[id]
        
        if year:
            date = DateTime(str(year) + "/01/01 UTC")                     
            doc.setEffectiveDate(date)        
            doc.reindexObject()
            
    def test_has_config(self):
        """ Check that properties have been set up """
        self.assertTrue("yearview_properties" in self.portal.portal_properties.objectIds(), "Got properties:" + str(self.portal.portal_properties.objectIds()))
        self.assertEqual(self.portal.portal_properties.yearview_properties.latest_filter_items, 10)
        
    def test_self_check(self):
        """ Check that our ATTopic set up works """
        
        self.createContent()
        result = self.portal.topic.queryCatalog()        
        self.assertEqual(len(result), 1) # Front page
        
        self.createDocument() # create document without publishing date                
        result = self.portal.topic.queryCatalog()        
        self.assertEqual(len(result), 2) # One document, one result
        
    def test_zero_docs(self):
        self.createContent()
        view = self.portal.topic.unrestrictedTraverse("@@timeline-view")
        view.update()
        self.assertEqual(view.years, []) # We have no content yet so no year range
                
    def test_one_doc_no_publish_date(self):
        self.createContent()
        self.createDocument() # create document without publishing date                
        
        view = self.portal.topic.unrestrictedTraverse("@@timeline-view")
        view.update()
        self.assertEqual(view.years, []) # We have no content yet so no year range

    def test_one_doc_publish_date(self):
        self.createContent()
        self.createDocument(year=2008) # Create one item with year
        
        view = self.portal.topic.unrestrictedTraverse("@@timeline-view")
        view.update()                
        self.assertEqual(view.years, [2008])
        
    def test_two_docs_same_year(self):
        self.createContent()
        self.createDocument(year=2008) # Create one item with year
        self.createDocument(year=2008) # Create one item with year

        view = self.portal.topic.unrestrictedTraverse("@@timeline-view")
        view.update()                
        self.assertEqual(view.years, [2008])
        
    
    def test_two_docs_diffrent_year(self): 
        self.createContent()
        self.createDocument(year=2008) # Create one item with year
        self.createDocument(year=2009) # Create one item with year

        view = self.portal.topic.unrestrictedTraverse("@@timeline-view")
        view.update()                
        self.assertEqual(view.years, [2009, 2008])
        
        
    def test_filter(self):

        self.createContent()
        self.createDocument(year=2008) # Create one item with year
        self.createDocument(year=2009) # Create one item with year
        
        # No timespan selected yet
        view = self.portal.topic.unrestrictedTraverse("@@timeline-view")
        view.update()                
        self.assertEqual(view.timespan, None)
        
        # Select 2008
        self.portal.REQUEST["timespan"] = "2008"
        view = self.portal.topic.unrestrictedTraverse("@@timeline-view")
        view.update()                
        self.assertEqual(view.years, [2009, 2008])
        self.assertEqual(view.timespan, 2008)
        
        self.assertEqual(len(view.results), 1) # Only year 2008

        # Select 2009
        self.portal.REQUEST["timespan"] = "2009"
        view = self.portal.topic.unrestrictedTraverse("@@timeline-view")
        view.update()                
        self.assertEqual(view.years, [2009, 2008])    
        self.assertEqual(view.timespan, 2009)
        
        self.assertEqual(len(view.results), 1) # Only year 2009

        # Select non-existing
        self.portal.REQUEST["timespan"] = "2010"
        view = self.portal.topic.unrestrictedTraverse("@@timeline-view")
        view.update()                
        self.assertEqual(view.years, [2009, 2008])    

        self.assertEqual(len(view.results), 0) # No hits
        
    def test_batching(self):
        """ Check that batching functions are still intact after the modifications """
        self.createContent()
        
        for i in range(0, 20):
            self.createDocument(year=2008) # Create one item with year
        
        for i in range(0, 20):
            self.createDocument(year=2009) # Create one item with year

        # The first page
        self.portal.REQUEST["b_start"] = 0
        self.portal.REQUEST["b_size"] = 20
        view = self.portal.topic.unrestrictedTraverse("@@timeline-view")
        view.update()                
        self.assertEqual(len(view.results), 20)
        for i in view.results: 
            #print i.getURL()
            if not "front-page" in i.getURL():                
                self.assertTrue("2008" in i.getURL(), "Got url:" + str(i.getURL()))        
                
        self.assertEqual(view.years, [2009, 2008])    

        # The second page
        self.portal.REQUEST["b_start"] = 21 # = front-page + 20 * year 2008
        self.portal.REQUEST["b_size"] = 20
        view = self.portal.topic.unrestrictedTraverse("@@timeline-view")
        view.update()                        
        self.assertEqual(len(view.results), 20)        
        for i in view.results: 
            #print i.getURL()
            if not "front-page" in i.getURL():                            
                self.assertTrue("2009" in i.getURL(), "Gor URL:" + str(i.getURL()))    
            
        self.assertEqual(view.years, [2009, 2008])    
        
    
def test_suite():
    suite = unittest.TestSuite([
        ])
    suite.addTest(unittest.makeSuite(TestView))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
