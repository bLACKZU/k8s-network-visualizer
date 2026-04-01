import subprocess, re

def simplify_name(pod_name):
    # Take everything before the first dash
    return pod_name.split('-')[0]

def get_cilium_endpoints(namespace):
    proc = subprocess.run(
        ["kubectl", "get", "ciliumendpoints", "-n", namespace],
        capture_output=True, text=True
    )
    identity_map = {}
    for line in proc.stdout.splitlines()[1:]:
        parts = line.split()
        name = parts[0]
        security_id = parts[1]
        identity_map[security_id] = simplify_name(name)
    return identity_map
    
    
map = get_cilium_endpoints("demo")
print(map)
    