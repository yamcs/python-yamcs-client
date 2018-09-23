Authentication
==============

User Accounts
-------------

Yamcs Server can be configured for different authentication setups.

The common use case is to entrust Yamcs with validating user credentials
(either by locally verifying passwords, or by delegating to an upstream
server such as an LDAP tree).

To authenticate in such a scenario simply do:

.. literalinclude:: ../../examples/authenticate.py
    :pyobject: authenticate_with_username_password
    :start-after: """
    :lines: 1-2
    :dedent: 4

In the background this will convert your username/password credentials
to an access token with limited lifetime, and a long-lived refresh token
for generating new access tokens.

Further HTTP requests do not use your username/password but instead use
the access token.

.. warning::

    When the access token has expired, this API client does not currently
    use the refresh token to generate a new access token. Such support
    will be added in future work.


Service Accounts
----------------

Service accounts are useful in server-to-server scenarios. Support for service
accounts will be available in future releases.


Types
-----

.. automodule:: yamcs.core.auth
    :members:
    :undoc-members:
    :show-inheritance:
