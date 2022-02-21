#!/usr/bin/python

import base64
import sys
import json

import editdistance
import click

from multiprocessing import Queue
import os
import time
import pathlib

CACHE_PATH=pathlib.Path.home()/".sekube_cache/"
CACHE_FILE_NAME = "sekube_cache"
CACHE_MAX_AGE=60

def load_kube():
   import kubernetes
   import traceback
   kubernetes.config.load_kube_config()
   return  kubernetes.client.CoreV1Api()

def cache_worker(cache_file,q):
   import fasteners
   import sys
   
   lock = fasteners.InterProcessLock(cache_file.absolute().parent/ (cache_file.name+".LOCK"))
   tempfile = cache_file.absolute().parent/ (cache_file.name+".TEMP")

   if lock.acquire(blocking=False):
      try:
         all_secrets = [(i.metadata.name, i.metadata.namespace ) for i in load_kube().list_secret_for_all_namespaces().items]
         json.dump(all_secrets,tempfile.open("w"))
         tempfile.replace(cache_file.absolute())
         q.put(all_secrets)
      except Exception as e:
         import traceback
         print("🛑Warning, sekube background worker experienced an error:🛑", file=sys.stderr)
         print(traceback.format_exc(), file=sys.stderr)
         q.put({})
         sys.exit(1)
      finally:
         lock.release()
   sys.exit(0)


def async_kube_cache():
   CACHE_PATH.mkdir(parents=True, exist_ok=True)
   cache_file = CACHE_PATH/ CACHE_FILE_NAME
   queue = Queue()
   if os.fork() == 0:
      cache_worker(cache_file, queue)
   if  cache_file.exists() and cache_file.stat().st_mtime + CACHE_MAX_AGE > time.time():
      #print(f"FAST PATH",file=sys.stderr)
      return json.load(cache_file.open("r"))
   else:
      #print("SLOW PATH",file=sys.stderr)
      return queue.get(timeout=10)


def print_secret(secret, write_to_files):
   if secret.data:
       for k,v in secret.data.items():
         if write_to_files is True:
            with open(k,"w") as f:
               print(f"Writing to: {k}", file=sys.stderr)
               f.write(v)
         else:
            print(f" {k} ".center(40,"="))
            print(base64.b64decode(v).decode())
   else:
      print(f" Empty Secret ".center(40,"="))

def get_suggestions(name, namespace=None):
   all_secrets = async_kube_cache()
   #yes this if-statement can be a one-liner inside the list comprehensiopndsfer but i find this more readable
   if namespace is None:
      secrets = all_secrets
   else:
      secrets = [i for i in all_secrets if i[1] == namespace]

   all_results=( (editdistance.eval(name,i[0]), i) for i in secrets )
   sorted_results = sorted([i for i in all_results] , key=lambda x :x[0])

   n=0
   in_matches=[]
   rest=[]
   for i in sorted_results:
      s, d = i
      if name in d[0] and n > 2:
         in_matches.append(i)
         n+=1
      else:
         rest.append(i)
   return in_matches + rest

def name_completion(ctx, args, incomplete):
   start_time=time.time()
   namespace = ctx.params["namespace"] or "default"
   r= [(i[0], f"in namespace {i[1]}")  for _,i in get_suggestions(incomplete) if i[1] == namespace ]
   return r

def namespace_completion(ctx, args, incomplete):
   v1_client = load_kube()
   all_namespaces = v1_client.list_namespace()
   return [i.metadata.name for i in all_namespaces.items]

@click.command()
@click.option('--namespace', type=click.STRING, default=None, autocompletion=namespace_completion)
@click.option('--write-to-files', is_flag=True, help="If set each key in the secret will be written to it's own file instead of being printed.")
@click.argument('name', nargs=1, type=click.STRING, autocompletion=name_completion)
def cli(name, namespace, write_to_files=False):
   s=time.time()
   results = get_suggestions(name, namespace)
   v1_client = load_kube()
   from kubernetes.client.exceptions import ApiException
   try:
      secret = v1_client.read_namespaced_secret(name, namespace if namespace is not None else "default")
      print_secret(secret, write_to_files)
      print(time.time()-s)

   except ApiException:
       suggestions = '\n'.join("  "+i[0] +" in "+i[1] for s,i in (results)[:4])
       print(f"""Error: "{name}" not found in "{namespace}", did you mean:
{ suggestions } """,
   file=sys.stderr)
   sys.exit(1)

if __name__ == '__main__':
   cli()
