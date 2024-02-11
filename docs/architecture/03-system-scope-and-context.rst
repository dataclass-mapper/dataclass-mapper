System Scope and Context
------------------------

Business Context
^^^^^^^^^^^^^^^^

.. .. uml::

..    skinparam componentStyle rectangle

..    actor User

..    package "Controller" {
..       Controller] as C
..       [Controller Model] as CM
..       C --> CM : uses
..    }

..    package "Service Layer" {
..       [Service Layer] as SL
..       [Domain Model] as DM
..       SL --> DM : uses
..       }

..    User -> C : sends HTTP request
..    C -> SL : "converts models and calls"
..    CM -> DM : define mapping

.. **<Diagram or Table>**

.. **<optionally: Explanation of external domain interfaces>**

Technical Context
^^^^^^^^^^^^^^^^^

.. **<Diagram or Table>**

.. **<optionally: Explanation of technical interfaces>**

.. **<Mapping Input/Output to Channels>**

