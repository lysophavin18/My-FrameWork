from __future__ import annotations

import json
import xml.etree.ElementTree as ET


def parse_nmap_xml(xml_text: str) -> dict:
    root = ET.fromstring(xml_text)
    ports = []
    for host in root.findall("host"):
        for port in host.findall("./ports/port"):
            state = port.find("./state")
            if state is None or state.get("state") != "open":
                continue
            service = port.find("./service")
            ports.append(
                {
                    "port": int(port.get("portid", "0")),
                    "proto": port.get("protocol", "tcp"),
                    "service": service.get("name") if service is not None else None,
                    "product": service.get("product") if service is not None else None,
                    "version": service.get("version") if service is not None else None,
                }
            )
    return {"open_ports": ports}


def parse_jsonl(text: str) -> list[dict]:
    out: list[dict] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out

