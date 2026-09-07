"""Builds the network topology diagram (graphviz) for the Riverside branch build."""
import subprocess

DOT = r"""
digraph riverside {
    rankdir=TB;
    bgcolor="transparent";
    node [fontname="Helvetica", fontsize=11, style=filled];
    edge [fontname="Helvetica", fontsize=9, color="#666666"];

    internet [label="Internet", shape=cloud, fillcolor="#e8e8e8", fontcolor="#333333"];
    fw [label="Firewall (fw-01)\nDefault-deny inter-VLAN policy", shape=box, fillcolor="#2f5233", fontcolor="white"];
    core [label="Core switch (core-sw-01)\nL3 — VLAN routing", shape=box, fillcolor="#3a3a3a", fontcolor="white"];

    subgraph cluster_office {
        label="office-sw-01";
        style=dashed; color="#999999";
        office_sw [label="Access switch", shape=box, fillcolor="#5b7fa6", fontcolor="white"];
        vlan10 [label="VLAN 10 — OFFICE\n28 devices\n10.10.10.0/24", shape=ellipse, fillcolor="#dce8f5"];
        vlan30 [label="VLAN 30 — VOIP\n14 devices\n10.10.30.0/24", shape=ellipse, fillcolor="#dce8f5"];
        vlan40 [label="VLAN 40 — GUEST\n12 devices\n10.10.40.0/24", shape=ellipse, fillcolor="#f5dcdc"];
        office_sw -> vlan10;
        office_sw -> vlan30;
        office_sw -> vlan40 [label="AP trunk"];
    }

    subgraph cluster_warehouse {
        label="warehouse-sw-01";
        style=dashed; color="#999999";
        wh_sw [label="Access switch", shape=box, fillcolor="#a6745b", fontcolor="white"];
        vlan20 [label="VLAN 20 — WAREHOUSE\n18 devices (14 legacy)\n10.10.20.0/24", shape=ellipse, fillcolor="#f5ecdc"];
        wh_sw -> vlan20;
    }

    mgmt [label="VLAN 99 — MANAGEMENT\n6 devices\n10.10.99.0/28", shape=ellipse, fillcolor="#e8dcf5"];

    internet -> fw;
    fw -> core;
    core -> office_sw [label="trunk: 10,30,40,99"];
    core -> wh_sw [label="trunk: 20,99"];
    core -> mgmt [style=dotted, label="mgmt only"];
}
"""

with open("/tmp/riverside.dot", "w") as f:
    f.write(DOT)

subprocess.run(["dot", "-Tpng", "-Gdpi=150", "/tmp/riverside.dot", "-o", "visuals/network-diagram.png"], check=True)
print("Wrote visuals/network-diagram.png")
