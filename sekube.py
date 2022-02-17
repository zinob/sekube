#!/usr/bin/python

import base64
import sys
import json

from kubernetes import client, config
import editdistance
import click


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

def get_suggestions(client,name, namespace=None):
    all_secrets = client.list_secret_for_all_namespaces().items
    #yes this if-statement can be a one-liner inside the lit comprehensiopndsfer but i find this more readable
    if namespace is None:
        secrets = all_secrets
    else:
        secrets = [i for i in all_secrets if i.metadata.namespace == namespace]

    all_results=( (editdistance.eval(name,i.metadata.name), i.metadata) for i in secrets )
    sorted_results = sorted([i for i in all_results] , key=lambda x :x[0])

    n=0
    in_matches=[]
    for i,meta in enumerate(sorted_results):
        if name in meta[1].name:
            in_matches.append(meta)
            sorted_results.remove(meta)
            n+=1
            if n > 2:
                break
    return in_matches + sorted_results

def name_completion(ctx, args, incomplete):
    v1_client = load_kube()
    namespace = ctx.params["namespace"] or "default"
    return [(i.name, f"in namespace {i.namespace}")  for _,i in get_suggestions(v1_client, incomplete) if i.namespace == namespace ]

def namespace_completion(ctx, args, incomplete):
    v1_client = load_kube()
    all_namespaces = v1_client.list_namespace()
    return [i.metadata.name for i in all_namespaces.items]

def load_kube():
    config.load_kube_config()
    return  client.CoreV1Api()

@click.command()
@click.option('--namespace', type=click.STRING, default=None, autocompletion=namespace_completion)
@click.option('--write-to-files', is_flag=True, help="If set each key in the secret will be written to it's own file instead of being printed.")
@click.argument('name', nargs=1, type=click.STRING, autocompletion=name_completion)
def cli(name, namespace, write_to_files=False):
    v1_client = load_kube()
    try: 
        secret = v1_client.read_namespaced_secret(name, namespace if namespace is not None else "default")
        print_secret(secret, write_to_files)

    except client.exceptions.ApiException:
        results = get_suggestions(v1_client, name, namespace)
        suggestions = '\n'.join("  "+i.name +" in "+i.namespace for s,i in (results)[:4])
        print(f"""Error: "{name}" not found in "{namespace}", did you mean:
{ suggestions } """,
    file=sys.stderr)
    sys.exit(1)

if __name__ == '__main__':
    cli()
