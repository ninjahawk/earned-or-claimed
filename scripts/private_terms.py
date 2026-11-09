"""Private term lists and local paths used by the scrub/export scripts.

The real values (names of people, excluded private workflows, local paths) are
deliberately NOT published. They live in private/terms.json, which is not in
this repository. The scripts need the private orchestrator database anyway,
so they are published for reading, not for re-running.
"""
import json, os, re
_P = os.path.join(os.path.dirname(__file__), '..', 'private', 'terms.json')
_T = json.load(open(_P)) if os.path.exists(_P) else {}
EXCLUDED_WORKFLOWS = set(_T.get('excluded_workflows', []))
PRIVATE_TOPICS = _T.get('private_topics', 'REDACTED_TOPIC')      # regex alternation
PERSON_NAMES = _T.get('person_names', 'REDACTED_NAME')           # regex alternation
OWNER_USER = _T.get('owner_user', 'USER')                         # local account name
ORCH_ROOT = _T.get('orch_root', '/path/to/orchestrator')          # orchestrator root on the VM
PC_HOME = _T.get('pc_home', 'C:/Users/USER')                      # PC home folder
PC_MOUNT = _T.get('pc_mount', '/path/to/pc_mount')
ORCH_NAME = _T.get('orch_name', 'ORCHNAME')
