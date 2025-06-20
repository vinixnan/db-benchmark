import requests
from packaging.version import parse
from packaging.specifiers import SpecifierSet
from packaging.version import Version


URL_BASE = "https://pypi.org/pypi/"

KNOWN_PYTHON_VERSIONS = [
    "2.7",
    "3.4",  # mínimo suportado por virtualenv antigos
    "3.5",
    "3.6",
    "3.7",
    "3.8",
    "3.9",
    "3.10",
    "3.11",
    "3.12",
    "3.13",
]

COMPARISON_OPERATORS = ['>=', '<=', '==', '~=', '!=', '>', '<']

def is_specifier(text):
    return any(op in text for op in COMPARISON_OPERATORS)

def parse_cp_tag(tag: str) -> str:
    if tag.startswith("cp"):
        digits = tag[2:]
        if len(digits) == 2:
            major = digits[0]
            minor = digits[1]
        else:
            major = digits[0]
            minor = digits[1:]
        return f"{major}.{minor}"
    return tag


def versions(package_name):
    url = f"{URL_BASE}{package_name}/json"
    data = requests.get(url).json()
    if "releases" not in data:
        return []
    result = []
    
    for k, v in data["releases"].items():
        extracted = set([t['python_version'] for t in v])
        tup = None
        for t in extracted:
            if t != 'source':
                if is_specifier(t):
                    spec = SpecifierSet(t)
                    versions = [Version(v) for v in KNOWN_PYTHON_VERSIONS if Version(v) in spec]
                    t = max(versions)
                t = parse_cp_tag(t)
                tup = (parse(k), parse(t))
                break
        if tup is not None:        
            result.append(tup)

    return result