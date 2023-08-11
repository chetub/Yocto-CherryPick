import argparse
import json
import os
import subprocess
import configparser
from pygerrit2 import GerritRestAPI, HTTPBasicAuth

config = configparser.ConfigParser()
config.read('config.ini')

username = config['gerrit']['username']
password = config['gerrit']['password'] 
gerrit_url = config['gerrit']['url'] 

auth = HTTPBasicAuth(username, password)
rest = GerritRestAPI(url=gerrit_url, auth=auth)


def find_git_repositories(workspace_path):
    git_repositories = []
    for root, dirs, files in os.walk(workspace_path):
        if '.git' in dirs:
            repo_path = os.path.join(root, '.git')
            remote_url = get_remote_url(repo_path)
            git_repositories.append((root, remote_url))
    return git_repositories

def get_remote_url(repo_path):
    git_cmd = ['git', 'config', '--get', 'remote.origin.url']
    try:
        result = subprocess.check_output(git_cmd, cwd=repo_path, stderr=subprocess.DEVNULL)
        remote_url = result.strip().decode('utf-8')
        return remote_url
    except subprocess.CalledProcessError:
        return None

def json_arg_parser():
    parser = argparse.ArgumentParser(description="Parse Arguments from JSON")
    # Add arguments to the parser
    parser.add_argument("json_file", type=str, help="Path to the JSON file containing arguments")
    # Parse the command-line argument for the JSON file path
    args = parser.parse_args()
    # Read the JSON data from the file
    with open(args.json_file, "r") as file:
        json_data = json.load(file)
    # JSON data as arguments
    return (json_data)

def workspace_repositories (ws_path):
    repositories_path = {}
    workspace_path = ws_path  # Replace this with the path to your workspace directory
    
    repositories = find_git_repositories(workspace_path)
    if repositories:
        print("Git repositories found in the workspace as below:")
        print("=" * 50)
        for repo_path, remote_url in repositories:
            print(f"Repository path: {repo_path}")
            print(f"Remote URL: {remote_url}")
            print("=" * 50)
            repo_name = remote_url.split(':29418/')[1].split('.git')[0]
            repositories_path[repo_name] = repo_path
    else:
        print("No Git repositories found in the workspace.")
    return (repositories_path)

def gerrit_nums (gerrit_data) :
    gerrit_numbers = []
    for gerrit_info in gerrit_data:
        gerrit_numbers.append(gerrit_info['_number'])
    return (gerrit_numbers)



def get_gerrits_numbers(args):
    for key in args :
        if key == "query" :
            gerirt_query = args['query']
            results = rest.get("/changes/?q=%s" %(gerirt_query))
        elif key == "topic" :
            topic_name = args['topic']
            results = rest.get("/changes/?q=topic:%s" %(topic_name))
        else:
            print ("Not Valid Input")
            exit (127)
    # Get Gerrit Numbers
    gerrit_numbers = gerrit_nums(results)
    return (gerrit_numbers)

def group_gerrits (gerrit_numbers):
    for gerrit in gerrit_numbers:
        results = rest.get("/changes/?q=change:%s &o=CURRENT_REVISION&o=CURRENT_COMMIT&o=DOWNLOAD_COMMANDS" %(gerrit))
        for data in results:
            print (data['project'])


def cherry_pick_gerrits (gerrit_numbers,ws_path):
    repo_path = workspace_repositories(ws_path)
    unsorted_gerrits = [int(number) for number in gerrit_numbers]
    sorted_gerrits = sorted (unsorted_gerrits)
    print ("Gerrits to Cherry Pick as below")
    print("=" * 50)
    print (sorted_gerrits)
    print("=" * 50)
    group_gerrits(sorted_gerrits)
    
            
