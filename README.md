
# BoberExec  
Automated Nmap → NetExec (NXC) service execution tool

BoberExec is a lightweight automation wrapper designed to parse Nmap output files, detect exposed services, and automatically run the appropriate **NetExec (NXC)** modules against each discovered port.  
It provides clean execution flow, graceful interruption handling, and direct passthrough of NXC output without modification.

---

## ✨ Features

- Parses Nmap `-oN` output and detects:
  - SMB
  - RDP
  - WinRM
  - LDAP
  - MSSQL
  - FTP
  - NFS
  - VNC
  - WMI
- Automatically runs the correct NXC module for each service
- Passes custom user commands directly to NXC (e.g. `-u user -p pass`)
- Clean, colorized execution logs
- **Graceful Ctrl+C handling**
  - Ctrl+C during an NXC run → kills only the current NXC process and continues
  - Ctrl+C when no NXC is running → clean exit without traceback
- Final summary message when all ports have been tested

---

## 📦 Installation (pipx)

You can install BoberExec directly from GitHub using:

```bash
pipx install git+https://github.com/KZ5017/BoberExec.git
```

After installation, the tool becomes available as:

```bash
bober-exec
```

---

## 🚀 Usage

### Basic example

```bash
bober-exec -f nmap_output.txt -ip 10.10.10.10
```

### With custom NXC command

```bash
bober-exec -f nmap_output.txt -ip 192.168.1.50 -c "-u 'admin' -p 'Pass123'"
```

### Using username/password lists

```bash
bober-exec -f nmap_output.txt -ip 10.129.14.245 -c "-u users.txt -p passwords.txt"
```

---

## 📘 Arguments

| Argument | Description |
|---------|-------------|
| `-f, --nmap-file` | Nmap output file (`-oN` format recommended) |
| `-ip, --target-ip` | Target IP address |
| `-c, --command` | Custom command string passed directly to NXC |

---

## 🧠 How it works

1. Reads the Nmap file line‑by‑line  
2. Detects open TCP ports and maps them to known services  
3. For each service/port pair:
   - Builds the appropriate NXC command
   - Executes it using `subprocess.Popen`
   - Handles Ctrl+C gracefully
4. After all ports are processed, prints a completion message

---

## 🛑 Graceful Interrupt Handling

- **Ctrl+C during NXC execution**  
  → Only the current NXC process is terminated  
  → Script continues to the next port

- **Ctrl+C when idle (between ports)**  
  → Script exits cleanly with a friendly message

No Python tracebacks, no messy output.

---

## ✔ Example Output

```
[INFO] Detected services from Nmap:
  smb: 445
  rdp: 3389
  winrm: 5985

[EXEC] nxc smb 10.10.10.10 --port 445 -u admin -p Pass123
... (NXC output) ...

[EXEC] nxc rdp 10.10.10.10 --port 3389 -u admin -p Pass123
... (NXC output) ...

[INFO] All ports have been tested. Execution completed.
```

---

## 📄 License

MIT License  
Feel free to modify, extend, or integrate into your own workflow.
