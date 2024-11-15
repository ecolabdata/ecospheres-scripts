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
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.json().get('id')

    def get_org_harvesters(self, ident):
        url = f"{self.base_url}/api/1/harvest/sources/?owner={ident}"
        r = session.get(url)
        r.raise_for_status()
        return r.json().get('data', [])

    def create_org(self, name):
        url = f"{self.base_url}/api/1/organizations/"
        headers = {'Content-Type': 'application/json', 'X-API-KEY': self.token}
        data = {
            "name": name,
            "description": "Ecospheres test org",
        }
        if not self.dry_run:
            r = session.post(url, headers=headers, data=json.dumps(data))
            r.raise_for_status()
            return r.json()
        else:
            print('Would create organization:', json.dumps(data, indent=2))
            return None


    def create_harvester(self, name, backend, target, org_id, prefix=None):
        url = f"{self.base_url}/api/1/harvest/sources/"
        headers = {'Content-Type': 'application/json', 'X-API-KEY': self.token}
        data = {
            'active': True,
            'autoarchive': True,
            'backend': backend,
            'name': name,
            'organization': {
                'id': org_id if org_id or not self.dry_run else '<not created in dry-run>'
            },
            'url': target,
            'description': "Configuré par Écosphères - https://github.com/ecolabdata/ecospheres/issues/476"
        }
        if prefix:
            data['config'] = {
                'extra_configs': [
                    {'key': 'remote_url_prefix', 'value': prefix}
                ]
            }

        if not self.dry_run:
            r = session.post(url, data=json.dumps(data), headers=headers)
            r.raise_for_status()
            return r.json()
        else:
            print(f"Would create harvester:", json.dumps(data, indent=2, ensure_ascii=False))
            return None


    def update_harvester(self, ident, name, target, prefix=None):
        url = f"{self.base_url}/api/1/harvest/source/{ident}"
        headers = {'Content-Type': 'application/json', 'X-API-KEY': self.token}
        data = {
            'name': name,
            'url': target
        }
        if prefix:
            data['config'] = {
                'extra_configs': [
                    {'key': 'remote_url_prefix', 'value': prefix}
                ]
            }

        if not self.dry_run:
            r = session.put(url, data=json.dumps(data), headers=headers)
            r.raise_for_status()
            return r.json()
        else:
            print(f"Would update harvester:", json.dumps(data, indent=2, ensure_ascii=False))
            return None


    def update_harvester_schedule(self, ident, schedule):
        url = f"{self.base_url}/api/1/harvest/source/{ident}/schedule"
        headers = {'Content-Type': 'application/json', 'X-API-KEY': self.token}
        data = schedule

        if not self.dry_run:
            r = session.post(url, data=data, headers=headers)
            r.raise_for_status()
            print(f"Updated harvester schedule for '{name}': {schedule}")
            return r.json()
        else:
            print(f"Would update harvester schedule:", data)
            return None


    def validate_harvester(self, ident):
        if not self.dry_run:
            url = f"{self.base_url}/api/1/harvest/source/{ident}"
            headers = {
                'Content-Type': 'application/json',
                'X-API-KEY': self.token,
                'X-Fields': 'validation{state}',
            }
            r = session.get(url, headers=headers)
            r.raise_for_status()
            validated = r.json().get("validation", {}).get("state") == "accepted"
            if validated:
                print("Harvester is already validated, nothing to do.")
                return True
        else:
            print("Would check harvester state, then validate if needed.")
            return None

        url = f"{self.base_url}/api/1/harvest/source/{ident}/validate"
        headers = {
            'Content-Type': 'application/json',
            'X-API-KEY': self.token,
            'X-Fields': 'validation{state}',
        }
        data = {'state': 'accepted'}
        if not self.dry_run:
            r = session.post(url, data=json.dumps(data), headers=headers)
            r.raise_for_status()
            validated = r.json().get("validation", {}).get("state") == "accepted"
            print(f"Harvester validation {'succeeded' if validated else 'failed'}")
            return validated
        else:
            print('Would validate harvester:', json.dumps(data, indent=2))
            return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('harvests', nargs='+', type=argparse.FileType('r'), metavar='config',
                        help='harvesters yaml config file(s)')
    parser.add_argument('-c', '--create-orgs', action='store_true', default=False,
                        help='create missing organizations')
    parser.add_argument('-s', '--update-schedules', action='store_true', default=False,
                        help='update existing harvesters schedules')
    parser.add_argument('-u', '--update-harvesters', action='store_true', default=False,
                        help='update existing harvesters')
    parser.add_argument('-v', '--validate-harvester', action='store_true', default=False,
                        help='validate harvester right away (triggers harvesting)')
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
        schedule = endpoint.get('schedule')
        prefix = endpoint.get('prefix')

        org_id = api.get_org_id_from_slug(org_slug)
        org_exists = org_id is not None
        if not org_exists:
            print(f"Organization '{org_slug}' for '{name}' is missing")
            if args.create_orgs:
                o = api.create_org(org_slug)
                org_id = o.get('id')
                if org_id:
                    url = f"{api_url}/fr/admin/organization/{org_id}"
                    print(f"Created organization for '{name}': {url}")
            else:
                print(f"(skipping endpoint)")
                continue

        harvesters = api.get_org_harvesters(org_id) if org_exists else []
        harvester_id = None
        harvester_exists = False
        for h in harvesters:
            if h['url'] == target:
                harvester_exists = True
                harvester_id = h.get('id')
                url = f"{api_url}/fr/admin/harvester/{harvester_id}"
                break

        if harvester_exists:
            if args.update_harvesters:
                api.update_harvester(harvester_id, name, target, prefix=prefix)
                print(f"Updated harvester for '{name}': {url}")
            else:
                print(f"Harvester for '{name}' already exists (skipping): {url}")
        else:
            h = api.create_harvester(name, backend, target, org_id, prefix=prefix)
            if h:
                harvester_id = h.get("id")
                if harvester_id:
                    url = f"{api_url}/fr/admin/harvester/{harvester_id}"
                    print(f"Created harvester for '{name}': {url}")

        if schedule and args.update_schedules:
            api.update_harvester_schedule(harvester_id, schedule)

        if args.validate_harvester:
            validated = api.validate_harvester(harvester_id)
