#!/usr/bin/env python3
import argparse
import re
import subprocess
import shlex
import sys
import signal


def parse_nmap_file(filename):
    results = {}

    # -----------------------------
    #  PORT-BASED MAPPING (STABLE)
    # -----------------------------
    port_map = {
        "ftp": ["21"],
        "wmi": ["135"],
        "smb": ["445"],
        "ldap": ["389"],
        "mssql": ["1433"],
        "nfs": ["2049"],
        "rdp": ["3389"],
        "vnc": ["5900"],
        "winrm": ["5985", "5986"],
    }

    # -----------------------------
    #  SERVICE-BASED MAPPING
    # -----------------------------
    service_map = {
        "ftp": ["ftp", "ftp-alt", "ftps"],
        "smb": ["microsoft-ds", "microsoft-ds?"],
        "ldap": ["ldap"],
        "mssql": ["ms-sql-s"],
        "nfs": ["nfs"],
        "rdp": ["ms-wbt-server"],
        "vnc": ["vnc", "rfb"],
    }

    # -----------------------------
    #  VERSION-BASED FINGERPRINTS
    # -----------------------------
    version_fingerprints = {
        "winrm": [
            r"Microsoft HTTPAPI",
            r"WinRM",
        ],
    }

    # -----------------------------
    #  PARSE FILE
    # -----------------------------
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            # PORT / SERVICE / VERSION (version optional)
            match = re.match(
                r"^(\d+)/tcp\s+open\s+(\S+)(?:\s+(.*))?$",
                line
            )
            if not match:
                continue

            port = match.group(1)
            service = match.group(2)
            rest = match.group(3) or ""

            version = rest
            
            # -----------------------------
            #  PORT-BASED DETECTION
            # -----------------------------
            for proto, ports in port_map.items():
                if port in ports:
                    results.setdefault(proto, []).append(port)

            # -----------------------------
            #  SERVICE-BASED DETECTION
            # -----------------------------
            for proto, patterns in service_map.items():
                if service in patterns:
                    results.setdefault(proto, []).append(port)

            # -----------------------------
            #  VERSION-BASED DETECTION (OPTIONAL)
            # -----------------------------
            if version:
                for proto, patterns in version_fingerprints.items():
                    for pat in patterns:
                        if re.search(pat, version, re.IGNORECASE):
                            results.setdefault(proto, []).append(port)

    # -----------------------------
    #  DEDUPLICATE PORTS
    # -----------------------------
    for proto in results:
        results[proto] = sorted(set(results[proto]), key=int)

    return results


# -----------------------------
#  EXECUTE NXC
# -----------------------------

def run_nxc(service, ip, port, user_command):
    cmd = [
        "nxc",
        service,
        ip,
        "--port", port
    ]

    if user_command:
        cmd += shlex.split(user_command)

    print(f"\n\033[1m\033[36m[EXEC]\033[0m {' '.join(cmd)}")

    try:
        # Start NXC process but IGNORE SIGINT in the child
        proc = subprocess.Popen(
            cmd,
            preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN)
        )

        try:
            proc.wait()
        except KeyboardInterrupt:
            print("-" * 60)
            print("\n\033[1m\033[33m[INFO]\033[0m Interrupt received. Killing current NXC process...")
            proc.terminate()
            proc.wait()
            print("\033[1m\033[33m[INFO]\033[0m Moving on to next port...")
            return

        print("-" * 60)

    except Exception as e:
        print(f"\033[1m\033[31m[EXCEPTION]\033[0m Failed to execute nxc: {e}")
        print("-" * 60)


# -----------------------------
#  MAIN LOGIC
# -----------------------------

def main():
    try:
        parser = argparse.ArgumentParser(description="BoberExec automation tool")

        parser.add_argument("-f", "--nmap-file", required=True, help="Nmap output file")
        parser.add_argument("-ip", "--target-ip", required=True, help="Target IP address")

        parser.add_argument(
            "-c", "--command",
            help="Command string passed directly to nxc. Example: -c \"-u 'guest' -p ''\""
        )

        args = parser.parse_args()

        # -----------------------------
        #  PARSE NMAP FILE
        # -----------------------------

        services = parse_nmap_file(args.nmap_file)

        print("\n\033[1m\033[33m[INFO]\033[0m Detected services from Nmap:")
        for proto, ports in services.items():
            print(f"  {proto}: {', '.join(ports)}")

        print("\n\033[1m\033[33m[INFO]\033[0m Using command:")
        print(f"  {args.command}")

        print("\n\033[1m\033[33m[INFO]\033[0m Starting nxc execution...\n")

        # -----------------------------
        #  EXECUTION MATRIX
        # -----------------------------

        for proto, ports in services.items():
            for port in ports:

                run_nxc(
                    service=proto,
                    ip=args.target_ip,
                    port=port,
                    user_command=args.command
                )

        print("\n\033[1m\033[33m[INFO]\033[0m All ports have been tested. Execution completed.\n")
    except KeyboardInterrupt:
        print("\n\033[1m\033[33m[INFO]\033[0m Execution interrupted by user. Exiting...\n")
        sys.exit(0)

if __name__ == "__main__":
    main()

