Introduction
============

collective.loremipsum is a developer tool to create dummy content to test your
website with.

It populates the content with text and html retrieved from loripsum.net

Just call /@@create-dummies in the context where you want dummy data to be
created. 

Here are all the parameters that can be passed to @@create-dummies:

* type: string
    The portal_type of the content type to create. If this is not
    specified, the types are gotten from the locallyAllowedTypes attribute, or from
    the allowed_content_types FTI attribute.

* amount: integer 
    The amount of objects to create

* ul: bool 
    Add unordered lists.

* ol: bool 
    Add numbered lists.

* dl: bool - Add description lists.

* bq: bool - Add blockquotes.

* code: bool - Add code samples.

* link: bool - Add links.

* prude: bool - Prude version.

* headers: bool - Add headers.

* allcaps: bool - Use ALL CAPS.

* decorate: bool - Add bold, italic and marked text.

* publish: bool - Should the objects be published

* recurse: bool - Should objects be created recursively?


TODO: Date fields currently don't get dummy values
