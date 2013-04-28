Introduction
============

collective.loremipsum is a developer tool to create dummy content and
dummy members inside your Plone site. 

Plain text fields are populated with text from the `loremipsum`_ Python
library, while rich text is retrieved from `loripsum.net`_.

The user data for the dummy members were downloaded from
`fakenamegenerator.com`_.

Fake images' content can be generated using one of these services:

	* `fakeimg.pl`_
	* `placehold.it`_
	* `placekitten.com`_
	* `lorempixel.com`_

You can add more image getters by registering named utilities for `IFakeImageGetter`.


* After it's installed (via the Plone control panel or the portal_quickinstaller tool), you'll see a new editbar tab labeled "Populate" on all folderish content types. Clicking this tab brings up a form with parameters for specifying the kinds of objects to create, how many and the lorem ipsum rich text formatting. Objects can also be created recursively. Note that you must have `collective.loremipsum: Can Populate` permission to see and access the tab (assigned to Manager and Site Administrator by default).

* You can also register 500 dummy users, but for the moment only by calling the browserview: **@@create-dummy-users**

Feedback and suggestions are welcome: <jc@opkode.com>

.. _loremipsum: http://code.google.com/p/lorem-ipsum-generator/
.. _loripsum.net: http//loripsum.net
.. _fakenamegenerator.com: http://www.fakenamegenerator.com

.. _fakeimg.pl: http://fakeimg.pl 
.. _placehold.it: http://placehold.it
.. _placekitten.com: http://placekitten.com
.. _lorempixel.com: http://lorempixel.com
