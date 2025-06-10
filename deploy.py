#!/usr/bin/python3

import datetime
import time
import os
import sys
import openstack
import subprocess
from openstack import connection


def run_command(command):
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode().strip(), result.stderr.decode().strip()
def connect_to_openstack():
    return openstack.connect(
        auth_url=os.getenv('OS_AUTH_URL'),
        project_name=os.getenv('OS_PROJECT_NAME'),
        username=os.getenv('OS_USERNAME'),
        password=os.getenv('OS_PASSWORD'),
        user_domain_name=os.getenv('OS_USER_DOMAIN_NAME'),
        project_domain_name=os.getenv('OS_PROJECT_DOMAIN_NAME')
    )

def extract_public_key(private_key_path):
    public_key_path = private_key_path + '.pub'
    #print(f"{public_key_path}")
    if not os.path.exists(public_key_path):
        command = f"ssh-keygen -y -f {private_key_path} > {public_key_path}"
        subprocess.run(command, shell=True, check=True)
    with open(public_key_path, 'r') as file:
        public_key = file.read().strip()
        #print(f"{public_key}")
    return public_key

def create_keypair(conn, keypair_name, private_key_path):
    keypair = conn.compute.find_keypair(keypair_name)
    current_date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"{current_date_time} Checking for keypair {keypair_name}.")
    if not keypair:
        public_key = extract_public_key(private_key_path)
        keypair = conn.compute.create_keypair(name=keypair_name, public_key=public_key)
        print(f"{current_date_time} Created keypair {keypair_name}.")
        # Verify that the keypair was uploaded correctly
        uploaded_keypair = conn.compute.find_keypair(keypair_name)
        if uploaded_keypair and uploaded_keypair.public_key == public_key:
            print(f"{current_date_time} Verified keypair {keypair_name} was uploaded successfully.")
        else:
            print(f"{current_date_time} Failed to verify keypair {keypair_name}.")
    else:
        print(f"{current_date_time} Keypair {keypair_name} already exists.")
    return keypair.id

