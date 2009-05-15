A collections view which display visitor clickable year selector on the collection view page. 
This allows easily read through news/events of the certain year without any extra logic
to create item archives.

New display type 'Timespan view' appears in Collection's 'Display' menu. When chosen, Topic content will 
display "latest, 2009, 2008... 2007" style year selector. Otherwise the view resembles the summary view.

Features and quality
--------------------

* Selector is only displayed if there actually exist content from different years

* By default results are grouped by publishing year (effective date), but you can choose arbitary portal_catalog metadata column

* I18N supports: English and Finnish localization provided

* Unit tests

Notes
-----

If you have many news/events you might want to use Large Plone Folder instead of a normal Folder due to scalability reasons.

The product does not contain default CSS styles - you must style it yourself. The page template has necessary classes set for rich formatting.

Settings can be found from portal_properties / yearview_properties. Please read propertiestool.xml for descriptions.

Author
------

Mikko Ohtamaa

`Twinapex Research <http://www.twinapex.com>`_, Oulu, Finland - High quality Python hackers for hire

This product is *bruteware*. Please go to `mybrute.com <http://moo33.mybrute.com>`_ and start your
career as a gladitor. (This computer game takes just 3 minutes from your everyday work time
and is überfun).
