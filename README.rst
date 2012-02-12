Introduction
============

collective.loremipsum is a developer tool to create dummy content and
dummy members inside your Plone site. 

Plain text fields are populated with text from the `loremipsum`_ Python
library, while rich text is retrieved from `loripsum.net`_.

The user data for the dummy members were downloaded from
`fakenamegenerator.com`_.

* After it's installed (via the Plone control panel or the portal_quickinstaller tool), you'll see a new editbar tab labeled "Populate" on all folderish content types. Clicking this tab brings up a form with parameters for specifying the kinds of objects to create, how many and the lorem ipsum rich text formatting. Objects can also be created recursively.

* You can also register 500 dummy users, but for the moment only by calling the browserview: **@@create-dummy-users**

.. _loremipsum: http://code.google.com/p/lorem-ipsum-generator/
.. _loripsum.net: http//loripsum.net
.. _fakenamegenerator.com: http://www.fakenamegenerator.com

Feedback and suggestions are welcome: <jc@opkode.com>
