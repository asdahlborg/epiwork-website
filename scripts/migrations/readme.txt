to migrate the old joomla users to the new django application I wrote
a simple ruby script, you can find it in the attachment.
The important thing to note is that the hash used to store the
passwords in joomla is recognized by django, which automatically
converts it to its hash+salt schema upon the first login, so we don't
need to worry about it.
We decided to not migrate all the accounts tied to a household but
only the account of its head, so if you want to change this behavior
and migrate all the accounts you should comment out the relevant part
in the code.

To migrate the accounts and the survey users of the old django
application to the new one I wrote another simple ruby script, it's
the second one in the attachment.
