# CVAT + UFW Firewall Troubleshooting

A personal reference for diagnosing and fixing Docker/UFW networking conflicts that
break CVAT auto-annotation with Nuclio serverless functions.

> **Environment:** Ubuntu 24, Docker, CVAT develop branch, CUDA 12.6.3, 4 GB VRAM

---

## Table of Contents

1. [How It All Fits Together](#1-how-it-all-fits-together)
2. [Why UFW Breaks Docker](#2-why-ufw-breaks-docker)
3. [Fix 1 - UFW Forward Policy](#3-fix-1--ufw-forward-policy)
4. [Fix 2 - Docker Bridge Forwarding Rules](#4-fix-2--docker-bridge-forwarding-rules)
5. [Fix 3 - Allow Docker Subnets Through UFW INPUT](#5-fix-3--allow-docker-subnets-through-ufw-input)
6. [Issue - Nuclio Port Desync After Docker Restart](#6-issue--nuclio-port-desync-after-docker-restart)
7. [Issue - Nuclio Function Returns 500](#7-issue--nuclio-function-returns-500)
8. [Issue - SAM ViT-H Crash Loop (Not Enough VRAM)](#8-issue--sam-vit-h-crash-loop-not-enough-vram)
9. [Diagnostic Commands Reference](#9-diagnostic-commands-reference)
10. [Post-Reboot Recovery Checklist](#10-post-reboot-recovery-checklist)

---

## 1. How It All Fits Together

CVAT runs as a Docker Compose stack. The `cvat_server` container handles annotation
logic and calls Nuclio serverless functions (e.g. YOLOv7, RetinaNet, SAM) to run
inference. Each Nuclio function is its own Docker container, exposed on a high-numbered
host port (32768, 32769, etc.).

```
Browser → Traefik (:8080) → cvat_server → host.docker.internal:<port>
                                                      ↓
                                           Nuclio function containers
                                           (each on its own host port)
```

`cvat_server` reaches Nuclio by calling `host.docker.internal:<port>` - the traffic
exits the container, crosses the host network stack, and re-enters via the mapped port.
**UFW intercepts this path at two points** and was silently dropping packets.

### The debugging journey

| Step | Error seen | What it meant |
|------|-----------|---------------|
| 1 | `Network error. The CVAT server is not reachable.` | Misleading - CVAT was fine, firewall was blocking. |
| 2 | `sudo ufw disable` → annotation works | UFW confirmed as sole cause. |
| 3 | Set `DEFAULT_FORWARD_POLICY=ACCEPT`, still broken | UFW injects its own DROP rules that override this. |
| 4 | `500 Server Error: Internal Server Error` | Network partially working, function reachable but crashing. |
| 5 | `Connection aborted. RemoteDisconnected` | Connection established but then killed mid-way. |
| 6 | All three fixes applied + Docker restarted in correct order | Everything works with UFW still active. |
| 7 | `Connection Refused` on specific ports | New issue: Nuclio port desync after Docker restart. |
| 8 | SAM container in crash loop | 4 GB VRAM not enough for ViT-H - redeployed on CPU. |

---

## 2. Why UFW Breaks Docker

UFW manages Linux's `iptables` chains. Docker also writes its own iptables rules, but
UFW's chains are evaluated **first** - so UFW gets to drop packets before Docker's
`DOCKER` and `DOCKER-USER` rules ever run.

```
Packet arrives
    │
    ▼
ufw-before-input / ufw-before-forward   ← UFW evaluates here first
    │  (DROP if no matching ACCEPT rule)
    ▼
DOCKER-USER / DOCKER chains             ← Docker's rules, never reached if UFW dropped it
```

### Problem 1 - FORWARD chain (container-to-container traffic)

When `cvat_server` talks to other containers on the same bridge network, packets are
**forwarded** between virtual interfaces. UFW's default FORWARD policy is `DROP`, and
even changing it to `ACCEPT` in `/etc/default/ufw` doesn't help - UFW inserts a
`ufw-before-forward` chain that drops packets before the policy is evaluated.

```
cvat_server (172.18.0.x) → br-<id> → FORWARD chain → UFW DROP ✗
```

### Problem 2 - INPUT chain (host.docker.internal traffic)

When `cvat_server` calls `host.docker.internal:32770`, traffic leaves the container,
hits the host's INPUT chain, and UFW drops it because it originates from a Docker
subnet (172.18.x.x) with no matching allow rule.

```
cvat_server → host.docker.internal:32770 → INPUT chain → UFW DROP ✗
```

### Why restart order matters

Docker re-injects its iptables rules at **startup**. If you reload UFW after Docker is
already running, UFW flushes the chains and wipes Docker's rules. Always reload in this
order:

```bash
sudo ufw reload
sudo systemctl restart docker
```

---

## 3. Fix 1 - UFW Forward Policy

Open the UFW defaults file:

```bash
sudo nano /etc/default/ufw
```

Change the forward policy from `DROP` to `ACCEPT`:

```diff
-DEFAULT_FORWARD_POLICY="DROP"
+DEFAULT_FORWARD_POLICY="ACCEPT"
```

Reload:

```bash
sudo ufw reload
```

> ⚠️ **This alone is not enough.** UFW's `ufw-before-forward` chain overrides this
> setting with its own DROP rules. Fixes 2 and 3 are also required.

---

## 4. Fix 2 - Docker Bridge Forwarding Rules

### Step 1 - Find the bridge interface name

```bash
# List all bridge interfaces
ip link show | grep br-

# Find the subnet (and confirm the hex ID) of the cvat_cvat network
docker network inspect cvat_cvat --format '{{range .IPAM.Config}}{{.Subnet}}{{end}}'
```

The bridge name follows the pattern `br-<network-id>`, e.g. `br-84c0afa3c714`.

### Step 2 - Add runtime UFW rules

```bash
# Replace br-84c0afa3c714 with your actual bridge name
sudo ufw allow in on br-84c0afa3c714
sudo ufw allow out on br-84c0afa3c714
sudo ufw allow in on docker0
sudo ufw allow out on docker0
```

### Step 3 - Make the rules persist across reboots

The UFW runtime rules above are stored in UFW's own database and survive `ufw reload`
on their own. For an additional iptables-level fallback, `docker0` was also added
to `/etc/ufw/before.rules`:

```bash
sudo nano /etc/ufw/before.rules
```

Find the existing `ufw-before-forward conntrack` block and add these two lines
immediately after it:

```iptables
# Allow Docker bridge forwarding
-A ufw-before-forward -i docker0 -j ACCEPT
-A ufw-before-forward -o docker0 -j ACCEPT
```

### Step 4 - Reload UFW and restart Docker (in this order)

```bash
sudo ufw reload
sudo systemctl restart docker

# Bring CVAT back up
cd ~/cvat
docker compose -f docker-compose.yml \
  -f components/serverless/docker-compose.serverless.yml up -d
```

---

## 5. Fix 3 - Allow Docker Subnets Through UFW INPUT

Even with Fix 2 in place, `host.docker.internal` calls still go through the host INPUT
chain. Allow the Docker subnets explicitly:

### Step 1 - Get subnet addresses

```bash
docker network inspect cvat_cvat --format '{{range .IPAM.Config}}{{.Subnet}}{{end}}'
docker network inspect bridge   --format '{{range .IPAM.Config}}{{.Subnet}}{{end}}'
```

### Step 2 - Allow them in UFW

```bash
# Use your actual subnets from Step 1
sudo ufw allow from 172.18.0.0/16 to any
sudo ufw allow from 172.17.0.0/16 to any
sudo ufw reload
```

---

## 6. Issue - Nuclio Port Desync After Docker Restart

### What happens

When Docker restarts, it reassigns host ports to containers. Nuclio's internal registry
still remembers the old ports. CVAT ends up calling ports that don't exist → `Connection
Refused`, even though the firewall is fine.

### How to detect

Run both commands and compare their output:

```bash
# Ports Docker actually assigned
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep nuclio

# Ports Nuclio thinks it assigned
nuctl get functions --namespace nuclio
```

A desync looks like this:

| Function | Nuclio registry port | Docker actual port |
|---|---|---|
| yolov7 | 32770 | *(none - container has no port!)* |
| transt | 32772 | 32768 |
| retinanet | 32773 | 32769 |
| faster-rcnn | 32774 | 32770 |

### Fix - delete and redeploy all functions

```bash
cd ~/cvat

# Delete everything desynced
nuctl delete function onnx-wongkinyiu-yolov7                        --namespace nuclio
nuctl delete function pth-dschoerk-transt                           --namespace nuclio
nuctl delete function pth-facebookresearch-detectron2-retinanet-r101 --namespace nuclio
nuctl delete function tf-faster-rcnn-inception-v2-coco              --namespace nuclio

sleep 5

# Redeploy
./serverless/deploy_gpu.sh serverless/onnx/WongKinYiu/yolov7/nuclio
./serverless/deploy_gpu.sh serverless/pytorch/facebookresearch/detectron2/retinanet_r101
./serverless/deploy_gpu.sh serverless/tensorflow/faster_rcnn_inception_v2_coco
./serverless/deploy_gpu.sh serverless/pytorch/dschoerk/transt/nuclio
```

> ⚠️ **This happens every time Docker restarts.** Always check port sync before
> chasing firewall or network issues.

---

## 7. Issue - Nuclio Function Returns 500

```
500 Server Error: Internal Server Error for url: http://host.docker.internal:32770/
```

The network is fine - the function container itself is crashing or misconfigured.

### Diagnose

```bash
# Check the function's own logs
docker logs nuclio-nuclio-onnx-wongkinyiu-yolov7 --tail=50

# Send a test request directly (bypass CVAT)
curl -X POST http://localhost:32770 \
  -H "Content-Type: application/json" \
  -d "{\"image\": \"$(base64 -w0 /path/to/test.jpg)\"}"
```

### Common causes

| Cause | How to check |
|---|---|
| Missing model weights | `docker exec nuclio-nuclio-onnx-wongkinyiu-yolov7 ls -lh /opt/nuclio/` |
| Out of RAM | `free -h` and `docker stats --no-stream \| grep nuclio` |
| Wrong runtime | Check the function YAML for `nvidia.com/gpu` - must match your hardware |

---

## 8. Issue - SAM ViT-H Crash Loop (Not Enough VRAM)

SAM ViT-H needs 8–16 GB VRAM to load. On a 4 GB card it enters a crash loop
immediately on startup. The fix is to deploy it on CPU instead.

```bash
# Remove the broken GPU deployment
nuctl delete function pth-facebookresearch-sam-vit-h --namespace nuclio

# Redeploy on CPU
cd ~/cvat
./serverless/deploy_cpu.sh serverless/pytorch/facebookresearch/sam/nuclio
```

> ⚠️ **SAM on CPU is slow** - expect 10–30 seconds per image. If the ViT-B variant
> is available for your CVAT version, prefer it: roughly 4× faster with a small
> accuracy trade-off.

---

## 9. Diagnostic Commands Reference

### Docker

```bash
# All containers with status and ports
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Stream container logs
docker logs <container> -f

# Last N lines of logs
docker logs <container> --tail=50

# Open a shell inside a container
docker exec -it <container> bash

# Resource usage snapshot
docker stats --no-stream

# List networks
docker network ls

# Inspect a network (shows subnet and connected containers)
docker network inspect cvat_cvat

# Manually connect a container to a network
docker network connect cvat_cvat <container>
```

### Nuclio

```bash
# List all functions with state and ports
nuctl get functions --namespace nuclio

# Delete a function
nuctl delete function <name> --namespace nuclio

# Deploy on GPU
./serverless/deploy_gpu.sh serverless/<path>/nuclio

# Deploy on CPU
./serverless/deploy_cpu.sh serverless/<path>/nuclio

# Force CPU deployment via nuctl directly
nuctl deploy --path serverless/<path>/nuclio \
  --namespace nuclio \
  --platform local \
  --project-name cvat \
  --resource-limit nvidia.com/gpu=0
```

### UFW

```bash
# Current rules (verbose shows policies and interfaces)
sudo ufw status verbose
sudo ufw status numbered

# Allow a subnet
sudo ufw allow from 172.18.0.0/16 to any

# Allow an interface
sudo ufw allow in  on docker0
sudo ufw allow out on docker0

# Apply changes
sudo ufw reload

# Test without firewall (re-enable after)
sudo ufw disable
sudo ufw enable

# Watch drops in real time
sudo dmesg -w | grep -i "UFW BLOCK"
```

### CVAT

```bash
# Start with serverless support
cd ~/cvat
docker compose -f docker-compose.yml \
  -f components/serverless/docker-compose.serverless.yml up -d

# Stop everything
docker compose -f docker-compose.yml \
  -f components/serverless/docker-compose.serverless.yml down
```

### Network verification

```bash
# Test cvat_server → nuclio connectivity
docker exec cvat_server curl -s http://nuclio/api/functions

# List bridge interfaces
ip link show | grep br-

# Get a network's subnet
docker network inspect cvat_cvat \
  --format '{{range .IPAM.Config}}{{.Subnet}}{{end}}'

# GPU info
nvidia-smi

# CUDA version inside a container
docker exec <container> nvcc --version
```

---

## 10. Post-Reboot Recovery Checklist

Work through these steps in order after every reboot where auto-annotation stops
working.

```bash
# 1. Are all containers up?
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "cvat|nuclio"

# 2. Are ports in sync?
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep nuclio
nuctl get functions --namespace nuclio
#   ↳ If they don't match → redeploy functions (Section 6)

# 3. Is UFW blocking anything?
sudo dmesg | grep "UFW BLOCK" | tail -20
#   ↳ If yes → reapply subnet allow rules from Section 5

# 4. Can cvat_server reach nuclio?
docker exec cvat_server curl -s http://nuclio/api/functions | head -5
#   ↳ Should return JSON. Connection error means Fix 2 needs reapplying.

# 5. Still broken? Confirm UFW is the culprit.
sudo ufw disable
#   Try annotation - if it works, UFW is still the issue.
#   Reapply all fixes, then: sudo ufw enable
```

---

*Last updated: June 2026 · Ubuntu 24 · Docker · CVAT develop branch · CUDA 12.6.3*
