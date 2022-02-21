SeKube a dumb program to show kubernetes secrets
================================================

It does two(and a half) things:

 * It lists kubernetes secrets
 * It prints kubernetes secrets
 * It caches availible secrets for fast tab-completion

KubeCTL is fine and dandy but when you are doing OPS and some one asks
you “we can’t get it to work, can you confirm the content of this
secret” or “could you check the certificate in this secret and see if
you can figure out what is wrong..” you have to do this little dance
with ``kubectl [blah] -o json | jq -r .data[] |base64 -d`` and it gets
quite tedious after a while. This script aims to be stupid and simple
and just simplify those steps.

Further more trying to use kubectl for tab-completion can be quite a
chore due to the long response time. In order to aliviate this sekube
tries to keep a local cache of availible keys in order to make
tab-completion faster.
 
Usage example
-------------

entering a non-existant secret (not using tab-complete) ::

  $ sekube certi
  Error: "certi" not found in "None", did you mean:
    sec-certificate-monitor in default
    certificate-controller-token in kube-system
    sec-webscale in default
    ipfs in ipfs 


Printing the content of a secret to the screen ::

  $ sekube sec-certificate-monitor
  ============= github_token =============
  coffebeef39aa0f530e231709895700911232f0c
  ============== sentry_dsn ==============
  https://badb0xcas9ae5bd8c956a35b5c50d3e9@sentry.io/555

It supports tab-completion
~~~~~~~~~~~~~~~~~~~~~~~~~~

Add ``eval "$(_SEKUBE_COMPLETE=bash_source sekube)"`` to your .bashrc to
enable it

Why is it called sekube? and not kube-secrets or similar ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because I use ``ku-<TAB>`` as a shortcut for kubectl waay to ofte to
want to have things interfearing with that (yes I could create an alias
for ``kubectl``, but I wont)
