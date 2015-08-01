=========
devpi-rss
=========

devpi-rss is a plug-in for `devpi-server <http://doc.devpi.net>`_ which generates RSS feeds.

.. image:: screenshot.png
   :alt: Screenshot
   :target: center

Usage
=====

An RSS feed can be activated or deactivated for every single index:

.. code::

   devpi-server index someuser/someindex rss_active=True

or

.. code::

   devpi-server index someuser/someindex rss_active=False

Additional devpi-server commandline options:

.. code::

  --rss-max-items RSS_MAX_ITEMS
                        maximum number of stored feed items [50]
  --rss-truncate-desc   do not let descriptions exceed 32 lines or 1024
                        characters
  --rss-no-auto         do not automatically activate rss for new indices
