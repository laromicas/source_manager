#!/usr/bin/env python3
"""
Import GitHub data.
"""
import os
import argparse
import requests
from requests.auth import HTTPBasicAuth
import config

def parse_args():
    """
    Parses the arguments passed to the script.
    """
    parser = argparse.ArgumentParser(description='Import GitHub data.')
    parser.add_argument('--type', required=True, help='Type of data to import.', choices=['apps', 'emulators', 'games', '3D'])
    parser.add_argument('--developer', required=True, help='Name of the developer.')
    parser.add_argument('--path', help='Path to the API repo.', default='users', choices=['users', 'orgs'])

    return parser.parse_args()


def main(sourcetype, developer, path):
    """ Main function. """
    url = f'https://api.github.com/{path}/{developer}/repos'

    page = 1

    more_data = True

    while more_data:
        pg = f'?page={page}'  # pylint: disable=invalid-name
        r = requests.get(f'{url}{pg}', auth=HTTPBasicAuth('laromicas', 'aipscorp'))  # pylint: disable=invalid-name

        data = r.json()
        if 'message' in data:
            print('No repositories found')
            break

        if len(data) == 0:
            break

        for source in data:
            # print(source['clone_url'])
            command = f'./sourceManager.py add --type={sourcetype} --url={source["clone_url"]}'
            print(f'Adding {source["clone_url"]} to {sourcetype}')
            # print(command)
            os.system(command)
        page += 1


if __name__ == '__main__':
    args = parse_args()
    main(args.type, args.developer, args.path)


# fsutil file SetCaseSensitiveInfo i: \Sources enable
# dir - recurse - include * .git | %{fsutil file SetCaseSensitiveInfo $_.FullName enable}
# dir - recurse - include - depth 3 * .git | %{echo $_.FullName}
# Get-childitem . -recurse - depth 3 - Directory | %{fsutil file SetCaseSensitiveInfo $_.FullName enable}
# Get-childitem . -Directory | %{git restore .}
