#!/usr/bin/env python3
import sys
import os
import json
import multiprocessing
import concurrent.futures
from tabulate import tabulate
# import git
import config
data = {}

GIT_EXE = 'git.exe'
GIT_EXE = '/usr/bin/git'


# class Database(object):
#     def __init__(self, file):
#         self.file = file
#         self.data = loaddata(file)
#         self.index = {}
#         for key, value in self.data.items():
#             self.index[value['name']] = key
# def get(self, name):
#     if name in self.index:
#         return self.data[self.index[name]]
#     else:
#         return None
# def set(self, name, value):
#     if name in self.index:
#         self.data[self.index[name]] = value
#     else:
#         self.data[name] = value
#         self.index[name] = name
# def save(self):
#     with open(self.file, 'w', encoding='utf-8') as json_file:
#         json.dump(self.data, json_file, indent=4)
# def getindex(self):
#     return self.index
# def getdata(self):
#     return self.data
# def getfile(self):
#     return self.file
# def getkeys(self):
#     return self.data.keys()
# def getvalues(self):
#     return self.data.values()


def loaddata(file, tryagain=True):
    """ Loads data from list.json file """
    try:
        with open(file, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        return data
    except:
        os.system('cp '+file+'.bak '+file)
        if tryagain:
            return loaddata(file, False)
        else:
            raise


# class MyProgressPrinter(git.RemoteProgress):
#     def update(self, op_code, cur_count, max_count=None, message=''):
#         # print(op_code, cur_count, max_count, cur_count / (max_count or 100.0), message or "NO MESSAGE", end="")
#         print(f'\r{(cur_count * 100 / (max_count or 100.0)):.2f}%\r', end='\r', flush=True)


def getdirs(path):
    initial = path.split('/')
    basepath = '/'.join(initial[:-2])
    devpath = '/'.join(initial[:-1])
    return basepath, devpath


def createdirs():
    urls = getindex('urls')
    for url in urls.values():
        basepath, devpath = getdirs(url['path'])
        if not os.path.exists(basepath):
            os.mkdir(basepath)
        if not os.path.exists(devpath):
            os.mkdir(devpath)


def clone(url):
    urls = getindex('urls')
    if url in urls:
        fullpath = urls[url]['path']
        createdirs()
        if not os.path.exists(fullpath):
            if urls[url]['source_url_type'] == 'git':
                git_clone(url, fullpath)
            if urls[url]['source_url_type'] == 'svn':
                svn_clone(url, fullpath)
            if urls[url]['source_url_type'] == 'direct':
                direct_clone(url, fullpath)


def fetch(url):
    urls = getindex('urls')
    if url in urls:
        fullpath = urls[url]['path']
        createdirs()
        if os.path.exists(fullpath):
            if urls[url]['source_url_type'] == 'git':
                git_fetch(url, fullpath)
            if urls[url]['source_url_type'] == 'svn':
                svn_fetch(url, fullpath)
            if urls[url]['source_url_type'] == 'direct':
                direct_fetch(url, fullpath)


def direct_clone(url, fullpath):
    urls = getindex('urls')
    if url in urls:
        org_url = url
        fullpath = urls[org_url]['path']
        os.mkdir(fullpath)
        for key, value in urls[org_url].items():
            if isinstance(value, str):
                url = url.replace('{' + key + '}', value)
        command = f'cd {fullpath}; wget {url};'
        print(f'Cloning {url} to {fullpath}')
        os.system(command)
        if 'source_rename_to' in urls[org_url]:
            rename_to = urls[org_url]['source_rename_to']
            for key, value in urls[org_url].items():
                if isinstance(value, str):
                    rename_to = rename_to.replace('{' + key + '}', value)
            filearray = url.split('/')
            filename = filearray[len(filearray) - 1]
            if filename != rename_to:
                command = f'cd {fullpath}; mv {filename} {rename_to};'
                os.system(command)


def direct_fetch(url, fullpath):
    urls = getindex('urls')
    if url in urls:
        org_url = url
        fullpath = urls[org_url]['path']
        rename_to = urls[org_url]['source_rename_to'] if (
            'source_rename_to' in urls[org_url]) else ''
        for key, value in urls[org_url].items():
            if isinstance(value, str):
                url = url.replace('{' + key + '}', value)
                rename_to = rename_to.replace('{' + key + '}', value)
        if 'source_rename_to' in urls[org_url]:
            filename = rename_to
        else:
            filearray = url.split('/')
            filename = filearray[len(filearray) - 1]
        if os.path.exists(fullpath + '/' + filename):
            print(
                f"{filename} is already updated, go to {urls[org_url]['developer_url']} to check for updates")
        else:
            command = f'cd {fullpath}; wget {url};'
            print(f'Updating {url} to {fullpath}')
            os.system(command)
            if 'source_rename_to' in urls[org_url]:
                filearray = url.split('/')
                filename = filearray[len(filearray) - 1]
                if filename != rename_to:
                    command = f'cd {fullpath}; mv {filename} {rename_to};'
                    os.system(command)


def svn_clone(url, fullpath):
    print(f'Cloning {url} to {fullpath}')
    command = f'git svn clone {url} {fullpath};'
    os.system(command)


def svn_fetch(url, fullpath):
    print(f'Fetching {url} in {fullpath}')
    command = f'git svn clone {url} {fullpath};'
    command = f'cd {fullpath}; git svn fetch; git svn rebase;'
    os.system(command)


def git_clone(url, fullpath):
    try:
        print(f'Cloning {url} to {fullpath}')
        # repo = git.Repo.clone_from(url, fullpath, progress=MyProgressPrinter())
        repo = git.Repo.clone_from(url, fullpath)
        # repo = git.Repo(fullpath)
        for remote in repo.remotes:
            remote.fetch('--tags')
            # remote.fetch('--all')
        branch = repo.active_branch.name
        edit = f'branch={branch}'
        editsource(url, [edit])
    except:
        print(f'Error cloning {url} to {fullpath}, Trying again...')
        basepath, devpath = getdirs(fullpath)
        command = f'cd {devpath}; {GIT_EXE} clone {url};'
        os.system(command)
        git_fetch(url)


def git_fetch(url, fullpath):
    print(f'Fetching {url} in {fullpath}')
    if os.path.exists(fullpath):
        command = f'cd {fullpath}; {GIT_EXE} fetch --tags >/dev/null 2>&1;'
        os.system(command)
        command = f'cd {fullpath}; {GIT_EXE} fetch --all >/dev/null 2>&1; '
        os.system(command)
        command = f'cd {fullpath}; echo pulling {fullpath} && {GIT_EXE} pull --all;'
        os.system(command)
    # repo = git.Repo(fullpath)
    # branch = repo.active_branch.name
    # edit = f'branch={%s}'
    # editsource(url, [edit])


def getCurrentBranch(url):
    urls = getindex('urls')
    if url in urls:
        fullpath = urls[url]['path']
        branch = pygit2.Repository(fullpath).head.shorthand
    return branch


def savefile(file="list.json", savebak=True):
    makeurlsindex()
    with open(file, "w", encoding='utf-8') as data_file:
        json.dump(data, data_file, indent=4, sort_keys=True)
    newdata = loaddata(file, False)
    if savebak and newdata:
        savefile(file+'.bak', False)


def detectrepotype(url):
    if url[:3] == 'git':
        return 'git'
    if url[-4:] == '.git':
        return 'git'
    if url[-5:] == 'trunk':
        return 'svn'


def extractthings(url, repotype=None, edits=[]):
    # pylint: disable=invalid-name
    if not repotype:
        repotype = detectrepotype(url)
    urlsplit = url.split('/')
    if repotype == 'git':
        if len(urlsplit) == 6:
            (c1, c2, c3, developer, source, source2) = url.split('/')
            developerurl = '/'.join([c1, c2, c3, developer])
            source = source + '/' + source2
        if len(urlsplit) == 5:
            (c1, c2, c3, developer, source) = url.split('/')
            developerurl = '/'.join([c1, c2, c3, developer])
        if len(urlsplit) == 4:
            (c1, c2, developer, source) = url.split('/')
            developerurl = '/'.join([c1, c2, developer])
        source = source.replace('.git', '')
        for edit in edits:
            key, value = edit.split('=')
            if key == 'developer':
                developer = value
            if key == 'source':
                source = value
            if key == 'developerurl':
                developerurl = value
    if repotype == 'svn':
        for i in range(len(urlsplit)):
            if urlsplit[i] == 'p':
                developer = urlsplit[i+1]
            if urlsplit[i] == 'code':
                if urlsplit[i+1] != 'trunk':
                    source = urlsplit[i+1]
                else:
                    source = developer
        developerurl = url
    if repotype == 'direct':
        developer = None
        source = None
        developerurl = None
        for edit in edits:
            key, value = edit.split('=')
            if key == 'developer':
                developer = value
            if key == 'source':
                source = value
            if key == 'developerurl':
                developerurl = value
    try:
        output = [developer, source, developerurl]
    except:
        print(f'Error extracting {url}')
    return output


def getthings(url):
    urls = getindex('urls')
    repo = urls.get(url)
    developer = repo.get('developer', None)
    source = repo.get('source', None)
    developerurl = repo.get('developerurl', None)
    try:
        output = [developer, source, developerurl]
    except:
        print(f'Error extracting {url}')
    return output


def addsource(sourcetype, url, repotype=None, edits=[]):
    if not repotype:
        repotype = detectrepotype(url)
    developer, source, developerurl = extractthings(url, repotype, edits)

    def createDeveloper(sourcetype, developer, url):
        sourcetype[developer] = {
            'name': developer,
            'url': url,
            'sources': {}
        }

    def createSource(sources, developer, source, url, sourcetype, repotype, edits):
        sources[source] = {
            'name': source,
            'url': url,
            'path': '/'.join([sourcetype, developer, source]),
            'type': repotype
        }
        for edit in edits:
            key, value = edit.split('=')
            if key not in ['developer', 'source', 'developerurl']:
                sources[source][key] = value

    # #Future
    # if not sourcetype in data:
    #     data[sourcetype] = {}

    if not sourcetype in data:
        data[sourcetype] = {}
    if not developer in data[sourcetype]:
        print(f'Adding Developer {developer} in {sourcetype}')
        createDeveloper(data[sourcetype], developer, developerurl)

    if not source in data[sourcetype][developer]['sources']:
        print(f'Adding Repository {source} in {developer} ({sourcetype})')
        createSource(data[sourcetype][developer]['sources'],
                     developer, source, url, sourcetype, repotype, edits)


def deletesource(sourcetype, developer, source=None):
    if source and developer in data[sourcetype]:
        if source in data[sourcetype][developer]['sources']:
            print(
                f'Deleting Repository {source} from {developer} ({sourcetype})')
            del(data[sourcetype][developer]['sources'][source])

    if developer in data[sourcetype] and len(data[sourcetype][developer]['sources']) == 0:
        print(f'Deleting Developer {developer} from {sourcetype}')
        if developer in data[sourcetype]:
            del(data[sourcetype][developer])


def movesource(sourcetype, url):
    developer, source, developerurl = extractthings(url)
    urls = getindex('urls')
    if url in urls and urls[url]['app_type'] != sourcetype:
        basepath, devpath = getdirs(urls[url]['path'])
        if os.path.exists(devpath):
            newpath = devpath.replace(basepath, sourcetype)
            print(f'Moving {devpath} to {newpath}')
            command = f'mv {devpath} {newpath}'
            os.system(command)
        deletesource(urls[url]['app_type'], developer, source)
        addsource(sourcetype, url)


def getindex(indextype, *filters):
    index = data['indexes'].get(indextype, {})
    for filtr in filters:
        key, value = filtr.split('=')
        index = dict(
            filter(lambda elem: elem[1][key].lower() == value.lower(), index.items()))
    return index


def normalize(source, developer, app_type='emulators'):
    normalized = {
        'source_url_type': source['type'],
        'name': source['name'],
        'source_url': source['url'],
        'developer': developer['name'],
        'developer_url': developer['url'],
        'app_type': app_type,
    }
    more_keys = ['path', 'binary', 'binaries', 'version',
                 'branch', 'source_rename_to', 'binaries_rename_to']
    for key in more_keys:
        if key in source:
            normalized[key] = source[key]

    return normalized


def makeurlsindex():
    urls = {}
    for apptype in ['3D', 'apps', 'games', 'emulators']:
        if apptype not in data:
            data[apptype] = {}
        for developer in data[apptype].values():
            for source in developer['sources'].values():
                if source['url'] not in urls:
                    urls[source['url']] = normalize(source, developer, apptype)
                else:
                    urls[source['url'] +
                         '-copy'] = normalize(source, developer, apptype)
    data['indexes'] = {}
    data['indexes']['urls'] = urls


def editsource(url, edits):
    urls = getindex('urls')
    if url in urls:
        apptype = urls[url]['app_type']
        developer = urls[url]['developer']
        source = urls[url]['name']
        if developer in data[apptype] and source in data[apptype][developer]['sources']:
            for edit in edits:
                key, value = edit.split('=')
                oldval = data[apptype][developer]['sources'][source].get(key)
                if oldval != value:
                    print(
                        f'Changing value of {key} ({url}) from {oldval} to {value}')
                    data[apptype][developer]['sources'][source][key] = value
    savefile()


def main():
    # TODO: Pending arguments to migrate from old format to new format
    global data
    try:
        data = loaddata('list.json')
    except:
        print('Error loading data, data corrupted or missing')
        exit(1)

    command = sys.argv[1]

    if command == 'importlist':
        sourcetype = sys.argv[2]
        file = sys.argv[3] if sys.argv[3:] else 'list.txt'
        with open(file, 'r', encoding='utf-8') as data_file:
            urls = data_file.readlines()
            for url in urls:
                addsource(sourcetype, url.strip())
        savefile()

    if command == 'massedit':
        edits = sys.argv[2:]
        urls = getindex('urls')
        for url in urls:
            editsource(url, edits)


def mainload():
    global data
    file = 'list.json'
    if not os.path.exists(file) and file.endswith('.json') and 'init' not in sys.argv:
        print(f'File not found: {file} in {os.getcwd()}')
        print('Please run ./sourceManager.py init')
        exit(1)
    if 'init' not in sys.argv:
        try:
            data = loaddata(file)
        except:
            print('Error loading data, data corrupted, all lost')
            exit()


def command_reindex(args):  # pylint: disable=unused-argument
    savefile()
    print('Reindexed')


def command_details(args):
    filters = args.filters
    urls = getindex('urls', *filters)
    print(tabulate(urls.values(), headers='keys', tablefmt='psql'))


def command_fetch(args):
    filters = args.filters
    urls = getindex('urls', *filters)
    cores = multiprocessing.cpu_count()
    workers = args.workers or (int)(cores / 2)
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        for url in urls:
            executor.submit(fetch, url)


def command_clone(args):
    filters = args.filters
    urls = getindex('urls', *filters)
    for url in urls:
        clone(url)


def command_list(args):
    filters = args.filters
    urls = getindex('urls', *filters)
    for url in urls.values():
        print(url['name'])


def command_createdirs(args):  # pylint: disable=unused-argument
    with open('list.json', 'r', encoding='utf-8') as data_file:
        data = json.load(data_file)


def command_delete(args):
    sourcetype = args.sourcetype
    developer = args.developer
    source = args.source
    deletesource(sourcetype, developer, source)
    if source and '*' == source[-1:]:
        urls = getindex('urls')
        src = source[:-1]
        for url in urls.values():
            if url['name'].startswith(src):
                deletesource(sourcetype, developer, url['name'])
    savefile()


def command_add(args):
    sourcetype = args.sourcetype
    url = args.url
    repotype = args.repotype
    edits = args.filters
    addsource(sourcetype, url, repotype, edits)
    savefile()


def command_edit(args):
    url = args.url
    edits = args.filters
    editsource(url, edits)
    savefile()

# def command_massedit(args):
#     edits = args.filters
#     urls = getindex('urls')
#     for url in urls:
#         editsource(url, edits)
#     savefile()


def command_move(args):
    folder = args.to
    url = args.url
    movesource(folder, url)
    savefile()


def command_init(args):  # pylint: disable=unused-argument
    with open('list.json', 'w', encoding='utf-8') as data_file:
        data_file.write('{"indexes":{}}')


def parse_args():
    from argparse import ArgumentParser
    parser = ArgumentParser(description='update Translated English datfiles')

    subparser = parser.add_subparsers(help='sub-command help')

    parser_add = subparser.add_parser('init', help='Add repositories')
    parser_add.set_defaults(func=command_init)

    parser_add = subparser.add_parser('add', help='Add repositories')
    parser_add.set_defaults(func=command_add)

    parser_move = subparser.add_parser('move', help='Move repositories')
    parser_move.set_defaults(func=command_move)

    parser_delete = subparser.add_parser('delete', help='Delete repositories')
    parser_delete.set_defaults(func=command_delete)

    parser_edit = subparser.add_parser('edit', help='Edit repositories')
    parser_edit.set_defaults(func=command_edit)

    parser_details = subparser.add_parser(
        'details', help='List details of repositories')
    parser_details.set_defaults(func=command_details)

    parser_list = subparser.add_parser('list', help='List repositories')
    parser_list.set_defaults(func=command_list)

    parser_createdirs = subparser.add_parser(
        'createdirs', help='Create directories')
    parser_createdirs.set_defaults(func=command_createdirs)

    parser_reindex = subparser.add_parser(
        'reindex', help='Reindex list of repositories')
    parser_reindex.set_defaults(func=command_reindex)

    parser_fetch = subparser.add_parser('fetch', help='Git Fetch repositories')
    parser_fetch.set_defaults(func=command_fetch)

    parser_clone = subparser.add_parser('clone', help='Clone new repositories')
    parser_clone.set_defaults(func=command_clone)

    for parser_func in [parser_fetch]:
        parser_func.add_argument(
            '-w', '--workers', help='Number of workers to use (default to half core count)', type=int)

    for parser_func in [parser_add]:
        parser_func.add_argument(
            '-t', '--type', required=True, dest='sourcetype', help='Source type')
        parser_func.add_argument('-u', '--url', required=True, help='Url')
        parser_func.add_argument('-r', '--repotype', help='Repository type')

    for parser_func in [parser_delete]:
        parser_func.add_argument(
            '-t', '--type', required=True, dest='sourcetype', help='Source type')
        parser_func.add_argument(
            '-d', '--developer', required=True, help='Developer')
        parser_func.add_argument('-s', '--source', help='Source')

    for parser_func in [parser_move, parser_edit]:
        parser_func.add_argument('-u', '--url', required=True, help='Url')

    for parser_func in [parser_move]:
        parser_func.add_argument('-t', '--to', required=True, help='To')

    for parser_func in [parser_details, parser_fetch, parser_clone, parser_list, parser_add, parser_edit]:
        parser_func.add_argument('filters', nargs='*', help='Filters')

    args = parser.parse_args()
    # print(args)
    if getattr(args, 'func', None) is None:
        parser.print_help()
        return
    args.func(args)
    # return args


if __name__ == "__main__":
    # main()
    mainload()
    parse_args()
