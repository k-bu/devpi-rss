=========
devpi-rss
=========

devpi-rss is a plug-in for `devpi-server <http://doc.devpi.net>`_ which generates RSS feeds.

.. image:: screenshot.png
   :alt: Screenshot
   :target: center

Requirements
------------

.. code::

   devpi-server >= 2.2.2
   devpi-web >= 2.4.0

Installation
------------

.. code::

   pip install devpi-rss

When the devpi-server gets started without a custom theme (without passing the ``--theme``
parameter), then no further configuration is required, since devpi-rss overwrites the
``templates/macro.pt`` of the default theme in order to make the RSS button visible. If you use a
custom theme, then you have to manually apply the content of ``devpi-rss/templates/macro.pt`` into
your theme.

Usage
-----

By default every single index generates its own RSS feed, but an RSS feed can be activated or
deactivated by modifying the regarding index property:

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
