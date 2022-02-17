SeKube a dumb program to show kubernetes secrets
================================================

It does two things: \* It lists kubernetes secrets \* It prints
kubernetes secrets

KubeCTL is fine and dandy but when you are doing OPS and some one asks
you “we can’t get it to work, can you confirm the content of this
secret” or “could you check the certificate in this secret and see if
you can figure out what is wrong..” you have to do this little dance
with ``kubectl [blah] -o json | jq -r .data[] |base64 -d`` and it gets
quite tedious after a while. This script aims to be stupid and simple
and just simplify those steps.

It supports tab-completion
~~~~~~~~~~~~~~~~~~~~~~~~~~

Add ``eval "$(_SEKUBE_COMPLETE=bash_source sekube)"`` to your .bashrc to
enable it

Why is it called sekube? and not kube-secrets or similar ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because I use ``ku-<TAB>`` as a shortcut for kubectl waay to ofte to
want to have things interfearing with that (yes I could create an alias
for ``kubectl``, but I wont)
