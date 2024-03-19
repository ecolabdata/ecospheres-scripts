import argparse
import json
import requests
import yaml

session = requests.Session()

class ApiHelper:

    def __init__(self, base_url, token, dry_run=False):
        self.base_url = base_url
        self.token = token
        self.dry_run = dry_run

    def get_org_id_from_slug(self, slug):
        url = f"{self.base_url}/api/1/organizations/{slug}/"
        headers = {'X-Fields': 'id'}
        r = session.get(url, headers=headers)
        r.raise_for_status()
        return r.json().get('id')

    def get_org_harvesters(self, ident):
        url = f"{self.base_url}/api/1/harvest/sources/?owner={ident}"
        r = session.get(url)
        r.raise_for_status()
        return r.json().get('data', [])

    def create_harvester(self, name, backend, target, org_id):
        url = f"{self.base_url}/api/1/harvest/sources/"
        headers = {'Content-Type': 'application/json', 'X-API-KEY': self.token}
        data = {
            'active': True,
            'autoarchive': True,
            'backend': backend,
            'name': name,
            'organization': {
                'id': org_id
            },
            'url': target
        }
        if not self.dry_run:
            r = session.post(url, data=json.dumps(data), headers=headers)
            r.raise_for_status()
            return r.json()
        else:
            print('Would create harvester:', json.dumps(data, indent=2))
            return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('harvests', nargs='+', type=argparse.FileType('r'), metavar='config',
                        help='harvesters yaml config file(s)')
    parser.add_argument('-n', '--dry-run', action='store_true', default=False,
                        help='perform a trial run without creating harvesters')
    args = parser.parse_args()

    conf = {}
    for c in args.harvests:
        conf.update(yaml.safe_load(c))

    api_url = conf['api']['url']
    token = conf['api']['token']
    api = ApiHelper(api_url, token, dry_run=args.dry_run)

    backend = conf['harvests']['backend']

    if args.dry_run:
        print("*** DRY RUN ***")

    for endpoint in conf['harvests']['endpoints']:
        name = endpoint['name']
        target = endpoint['url']
        org_slug = endpoint['org']

        org_id = api.get_org_id_from_slug(org_slug)
        existing = api.get_org_harvesters(org_id)

        found = False
        for e in existing:
            if e['url'] == target:
                u = f"{api_url}/fr/admin/harvester/{e['id']}"
                print(f"Harvester for '{name}' already exists: {u}")
                found = True
                break
        if found:
            continue

        r = api.create_harvester(name, backend, target, org_id)
        if r:
            u = f"{api_url}/fr/admin/harvester/{r['id']}"
            print(f"Created harvester for '{name}': {u}")
