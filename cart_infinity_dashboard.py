#!/usr/bin/env python3
import os, time, subprocess, shutil
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
START = time.time()

NET_SUPPORTED = True
NET0 = (0, 0)

def sh(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        return r.stdout.strip()
    except Exception:
        return ""

def is_repo(p: Path) -> bool:
    return bool(sh(["git","-C",str(p),"rev-parse","--is-inside-work-tree"])) and bool(sh(["git","-C",str(p),"rev-parse","HEAD"]))

def repos():
    out = []
    for p in HOME.iterdir():
        if not p.is_dir(): continue
        n = p.name
        if n.startswith("infinity") or n == "mongoose.os":
            if is_repo(p):
                out.append(p)
    return sorted(out, key=lambda x: x.name.lower())

def cpu_percent():
    try:
        def read():
            with open("/proc/stat","r") as f:
                parts = f.readline().split()
            vals = list(map(int, parts[1:8]))
            idle = vals[3] + vals[4]
            total = sum(vals)
            return idle, total
        i1,t1 = read()
        time.sleep(0.15)
        i2,t2 = read()
        return max(0.0, min(100.0, 100.0*(1 - (i2-i1)/(t2-t1))))
    except:
        return 0.0

def mem_percent():
    try:
        m={}
        with open("/proc/meminfo","r") as f:
            for line in f:
                k,v,*_ = line.split()
                m[k.strip(":")] = int(v)
        used = m["MemTotal"] - m.get("MemAvailable",0)
        return 100.0 * used / m["MemTotal"]
    except:
        return 0.0

def disk_percent():
    du = shutil.disk_usage(str(HOME))
    return 100.0 * du.used / du.total

def net_bytes():
    global NET_SUPPORTED
    try:
        rx=tx=0
        with open("/proc/net/dev","r") as f:
            for ln in f.readlines()[2:]:
                if ":" not in ln: continue
                cols = ln.split(":")[1].split()
                rx += int(cols[0])
                tx += int(cols[8])
        return rx, tx
    except:
        NET_SUPPORTED = False
        return (0, 0)

def bar(pct, w=22):
    f = int((pct/100)*w)
    return "[" + "█"*f + " "*(w-f) + f"] {pct:5.1f}%"

def repo_commits(rs):
    c=0
    for r in rs:
        try: c+=int(sh(["git","-C",str(r),"rev-list","--count","HEAD"]))
        except: pass
    return c

def repos_moved(rs, mins=10):
    now=time.time()
    k=0
    for r in rs:
        try:
            t=int(sh(["git","-C",str(r),"log","-1","--format=%ct"]))
            if now-t <= mins*60: k+=1
        except: pass
    return k

def clear(): os.system("clear")

def main():
    global NET0
    NET0 = net_bytes()
    while True:
        rs = repos()
        cpu=cpu_percent()
        mem=mem_percent()
        dsk=disk_percent()

        rx,tx = net_bytes()
        drx,dtx = max(0,rx-NET0[0]), max(0,tx-NET0[1])

        clear()
        now=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        up=int(time.time()-START)

        print(f"∞ INFINITY TERMUX DASHBOARD | {now} | uptime {up}s")
        print("="*60)
        print(f"1) CPU   {bar(cpu)}")
        print(f"2) RAM   {bar(mem)}")
        print(f"3) DISK  {bar(dsk)}")

        if NET_SUPPORTED:
            print(f"4) NET   RX {drx:,} bytes | TX {dtx:,} bytes")
        else:
            print("4) NET   unavailable (android sandbox)")

        print("-"*60)
        print(f"5) REPOS discovered: {len(rs)}")
        print(f"6) REPOS moved (10 min): {repos_moved(rs)}")
        print(f"7) TOTAL commits: {repo_commits(rs):,}")
        print(f"8) TOKENS detected: (ledger scan deferred)")

        print("-"*60)
        for r in rs[:6]:
            msg=sh(["git","-C",str(r),"log","-1","--format=%s"])
            print(f"• {r.name[:38]:38} {msg[:30]}")
        print("\nCTRL+C to stop")
        time.sleep(1)

if __name__=="__main__":
    main()
