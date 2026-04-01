import subprocess

# def node_cilium():
#     proc = subprocess.run(
#         ["kubectl", "-n", "kube-system", "get", "pods", "-l", "k8s-app=cilium"],
#         capture_output=True, text=True
#     )
#     pod_list = []
#     for pod in proc.stdout.splitlines()[2:]:
#         parts = pod.split()
#         print(parts[0])
#         print("x")
        
    

# node_cilium()

def get_svc(namespace):
    proc = subprocess.run(
        ["kubectl", "get", "svc", "-n", namespace],
        capture_output=True, text=True
    )
    svc_map = {}
    for svc in proc.stdout.splitlines()[1:]:
        svc_name = svc.split()[0]
        svc_port_protocol = svc.split()[4]
        svc_port = svc_port_protocol.split('/')[0]
        if "front" not in svc_name:
            svc_map[svc_port] = svc_name
    return svc_map

svc_map = get_svc("demo")
print(svc_map)
        