import re

with open("src/tools/verify_images.py", "r") as f:
    content = f.read()

content = content.replace(
"""        try:
            addr_info = socket.getaddrinfo(clean_hostname, None, socket.AF_UNSPEC)
            for info in addr_info:
                ip_str = info[4][0]
                ip = ipaddress.ip_address(ip_str)
                if ip.is_private or ip.is_loopback or ip.is_link_local:
                    return False
        except socket.gaierror:
            return False""",
"""        try:
            addr_info = socket.getaddrinfo(clean_hostname, None, socket.AF_UNSPEC)
            for info in addr_info:
                ip_str = info[4][0]
                # Strip zone index (e.g. %eth0) if present in IPv6 addresses
                ip_str = ip_str.split("%")[0]
                ip = ipaddress.ip_address(ip_str)
                if ip.is_private or ip.is_loopback or ip.is_link_local:
                    return False
        except socket.gaierror:
            return False""")

with open("src/tools/verify_images.py", "w") as f:
    f.write(content)
