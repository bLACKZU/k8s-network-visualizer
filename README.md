The setup leveraged Cilium CNI, which uses eBPF agents to monitor pod‑to‑pod traffic. My goal was straightforward: capture and filter traffic hitting my backend application, and surface those flows in a dashboard. Here’s how I approached it:
- Log ingestion – Used Python’s subprocess library to stream logs from cilium monitor across nodes.
- Parallel processing – Implemented multithreading to capture logs concurrently from two worker nodes.
- Pattern extraction – Applied regex parsing to isolate source and destination IPs from raw flow logs.
- Identity mapping – Built a mapping of Cilium security IDs to Kubernetes deployments for contextual clarity.
- Flow filtering – Focused specifically on destination ports tied to my backend service.
- Metric export – Exposed the processed flows as Prometheus counters with rich labels (src_service, dst_service, port).
- Visualization – Connected Prometheus to Grafana and built dashboards (Time series, Table panels) to observe live traffic hitting the backend.
The end result was a network flow visualizer that captures and displays every hit to an application in real time. While the setup is admittedly “toyish,” it demonstrates the full pipeline: eBPF → log parsing → metric export → Prometheus → Grafana visualization.
