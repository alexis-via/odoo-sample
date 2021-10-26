NEW FORMAT :
DESCRIPTION.rst
INSTALL.rst
CONFIGURE.rst
USAGE.rst
HISTORY.rst
ROADMAP.rst
CONTRIBUTORS.rst
CREDITS.rst

To regenerate README.rst:


.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===========
Module name
===========

This module was written to extend the functionality of ... to support ... and allow you to ...

*emphasis*
**strong emphasis**
http://docutils.sourceforge.net/docs/user/rst/quickref.html

=====
Title
=====
Subtitle
--------

- Bullets are "-", "*" or "+".
  Continuing text must be aligned
  after the bullet and whitespace.

Liste ordonnée:

1. premier item
2. 2e item
#. idem suivant

Note that a blank line is required before the first item and after the
last, but is optional between items.

Field list :
:Authors:
    Tony J. (Tibs) Ibbs,
    David Goodger

:Version: 1.0 of 2001/08/08
:Dedication: To my father.

External hyperlinks, like `Python <http://www.python.org/>`_.

Pour un bloc de code (attention à la ligne vide entre .. code:: et le début du code)

.. code::

  if toto == titi:
      print "TOTO"

Include image:
.. figure:: static/description/ex_report_template.png
   :scale: 80 %
   :alt: Sample report template

Installation
============

To install this module, you need to:

* do this ...

Configuration
=============

To configure this module, you need to:

* go to ...

This module doesn't require any configuration.

Usage
=====

To use this module, you need to:

* go to ...

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/{repo_id}/{branch}

.. repo_id is available in https://github.com/OCA/maintainer-tools/tools/repos_with_ids.txt
.. branch is "8.0" for example


Known issues / Roadmap
======================

* ...

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/{project_repo}/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Alexis de Lattre <alexis.delattre@akretion.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
