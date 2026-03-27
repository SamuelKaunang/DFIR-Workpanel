from scapy.all import rdpcap, IP, TCP, UDP, DNS, DNSQR
from collections import Counter

def analyze_pcap(pcap_path):
    packets = rdpcap(pcap_path)
    results = {
        "total_packets": len(packets),
        "src_ips": [], "dst_ips": [],
        "dns_queries": [], "http_hosts": [],
        "tcp_ports": [], "suspicious": []
    }

    ip_counter  = Counter()
    port_counter = Counter()

    for pkt in packets:
        if IP in pkt:
            ip_counter[pkt[IP].src] += 1
            if TCP in pkt:
                port_counter[pkt[TCP].dport] += 1
        if DNS in pkt and DNSQR in pkt:
            qname = pkt[DNSQR].qname.decode("utf-8",
                        errors="replace").rstrip(".")
            results["dns_queries"].append(qname)
            # Deteksi DNS tunnel: query terlalu panjang
            if len(qname) > 50:
                results["suspicious"].append({
                    "type": "dns_tunnel_suspect",
                    "value": qname
                })

    results["top_src_ips"]  = ip_counter.most_common(10)
    results["top_dst_ports"] = port_counter.most_common(10)
    results["unique_ips"]    = len(ip_counter)
    results["unique_dns"]    = len(set(results["dns_queries"]))
    return results