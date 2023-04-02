"""
Help tool to find a kubernetes pod with specific name then login
This required current user environment already setup google-cloud-sdk with kubectl component
"""
import os
import sys
import argparse

if getattr(sys, 'frozen', False):
    # frozen
    from sys import exit

parser = argparse.ArgumentParser()

parser.add_argument("--pod", "-p", help="Kubernetes pod name")
parser.add_argument("--container", "-c", help="Kubernetes container name")
parser.add_argument("--shell", "-s", help="Pod shell, default: /bin/bash", default="/bin/bash")

args = parser.parse_args()

if __name__ == '__main__':
    if not args.pod:
        print("Please input pod name with --pod/-p")
        exit()
    pods_list = os.popen("kubectl get pods").read()
    pod_name = None
    for line in pods_list.splitlines():
        if args.pod in line and "Running" in line:
            pod_name = line.split(' ')[0]
            print(f"Found pod name: {pod_name}")
            break
        
    if pod_name:
        container_name = args.pod
        if args.container:
            container_name = args.container
        print(f"Using container name: {container_name}")
        os.system(f"start cmd /k kubectl logs -f {pod_name} -c {container_name}")
    else:
        print(f"Cannot find pod with name: {pod_name}")
