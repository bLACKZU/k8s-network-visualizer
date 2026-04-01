import subprocess, re, threading, queue
from prometheus_client import Counter, start_http_server

def simplify_name(pod_name):
    return pod_name.split('-')[0]

def get_cilium_endpoints(namespace):
    proc = subprocess.run(
        ["kubectl", "get", "ciliumendpoints", "-n", namespace, "-o", "wide"],
        capture_output=True, text=True
    )
    pod_map = {}
    for line in proc.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 5:
            name = parts[0]
            ip = parts[4]   # pod IP
            pod_map[ip] = simplify_name(name)
    return pod_map

def node_cilium():
    proc = subprocess.run(
        ["kubectl", "-n", "kube-system", "get", "pods", "-l", "k8s-app=cilium"],
        capture_output=True, text=True
    )
    pod_list = []
    for pod in proc.stdout.splitlines()[1:]:
        parts = pod.split()
        pod_list.append(parts[0])
    return pod_list

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

def monitor_pod(pod_name, pod_map, flow_queue):
    proc = subprocess.Popen(
        ["kubectl", "-n", "kube-system", "exec", pod_name, "--", "cilium", "monitor"],
        stdout=subprocess.PIPE, text=True
    )
    pattern = re.compile(r"(\d+\.\d+\.\d+\.\d+):(\d+) -> (\d+\.\d+\.\d+\.\d+):(\d+)")
    get_svc_map = get_svc("demo")
    for line in proc.stdout:
        match = pattern.search(line.strip())
        if match:
            src_ip, src_port, dst_ip, dst_port = match.groups()
            src = pod_map.get(src_ip, src_ip)
            dst = pod_map.get(dst_ip, dst_ip)
            
            if dst_port in get_svc_map:
                # Instead of printing, push into queue
                flow_queue.put((src, src_port, dst, dst_port, get_svc_map[dst_port]))

# Main
pod_map = get_cilium_endpoints("demo")
pod_list = node_cilium()
flow_queue = queue.Queue()


threads = []
for pod in pod_list:
    t = threading.Thread(target=monitor_pod, args=(pod, pod_map, flow_queue), daemon=True)
    t.start()
    threads.append(t)

start_http_server(8000)

flow_counter = Counter(
    'k8s_service_flows',
    'Observed service-to-service flows',
    ['src_service', 'src_namespace', 'dst_service', 'dst_namespace', 'port']
)

# Central consumer loop
while True:
    src, src_port, dst, dst_port, dst_service = flow_queue.get()
    
    src_ns = dst_ns = "demo"  
    flow_counter.labels(src_service=src, src_namespace=src_ns, dst_service=dst_service, dst_namespace=dst_ns, port=dst_port).inc()
    print(f"{src}:{src_port} -> {dst}:{dst_port} ({src_ns}/{src} -> {dst_ns}/{dst_service})")


