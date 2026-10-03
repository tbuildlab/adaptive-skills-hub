# Nexus G2 Route D Reference Source Register v1

Version: `1.0.0`

Date / source retrieval: **2026-10-03**

Baseline: `8818b0b674878f016a779197a6f04cb0c5b3a39f` / `nexus-v2-g2-development`

Status: **D-REF FACTUAL / DESIGN CHECKPOINT ONLY - NOT ACCEPTED; NO HOST OR EXPERIMENT AUTHORITY**

## 1. Source and cache boundary

64 successful first-party source bodies, opened/read from public URLs or exact same-day reused cache; no binaries or code execution. Tier 1 = upstream API/manual/specification; Tier 2 = pinned project design/code/license. No community source or Tier 3 audit is used. The failed obsolete Kata architecture.md path is retained in external acquisition metadata as a 404, excluded from positive evidence; KA05 resolves the current architecture directory. Neither pinned main nor a public page is a selected supported release or current Host state.

Exact cache: `D:\chatgpt\安装skills\output\route-d-dref-2026-10-03`; *.raw.txt are source text only. No third-party source is vendored into Nexus. Same-day CG/SC/NS/QT/WD and SD06-SD08 reuse previous cache after byte verification.

## 2. Project pins

| Project / source owner | Commit | Commit date | Scope |
| --- | --- | --- | --- |
| containers/bubblewrap | `0f8073dd9b547e15e8ec9451371f9729830b083d` | 2026-09-25T18:27:32Z | Documentary source pin only; not installed release |
| containerd/containerd | `81af89b1d4b1feab373a5251254f3cc82b9b4494` | 2026-10-02T22:25:44Z | Documentary source pin only; not installed release |
| firecracker-microvm/firecracker | `f23a2136011e89e7953923d0efcf67f72d18fc87` | 2026-10-01T14:02:57Z | Documentary source pin only; not installed release |
| google/gvisor | `0b0c579a788579db106713f67e8d0cf88506bda8` | 2026-10-03T01:43:29Z | Documentary source pin only; not installed release |
| kata-containers/kata-containers | `fdff4bb12d2a0292724681e2ca8b47e3e8828100` | 2026-10-02T19:02:07Z | Documentary source pin only; not installed release |
| kubernetes/kubernetes | `99a4ea72fe6fe258d2e2875e7f83223bfbd50463` | 2026-10-02T23:37:18Z | Documentary source pin only; not installed release |
| kubernetes/website | `192e45e734c55f41d7691d965ccf567dea9cbd0e` | 2026-10-02T23:11:19Z | Documentary source pin only; not installed release |
| torvalds/linux | `ff47652a4b66c067c765a7ad464d930b5a9367cc` | 2026-10-02T21:04:11Z | Documentary source pin only; not installed release |
| google/nsjail | `4ff54a6e0d5b65a0e1633d6e2fd1425ba6c882ce` | 2026-10-02T07:37:47Z | Documentary source pin only; not installed release |
| opencontainers/runtime-spec | `6999a89a76a0329f440d5740497bedb9dd431297` | 2026-04-24T18:48:18Z | Documentary source pin only; not installed release |
| opencontainers/runc | `a945133d52eb87415b3a9004f68e11b8b6e0cc2e` | 2026-10-03T00:46:25Z | Documentary source pin only; not installed release |
| systemd/systemd | `0794ba0045d11d4227f61ebacf7d75983ba884f1` | 2026-10-02T22:09:19Z | Documentary source pin only; not installed release |

## 3. Material source register

Every row: retrieval 2026-10-03; scope/exclusions in the last column. Full byte/hash records in section 4. A document may be normative for its upstream interface, never for Nexus qualification. Source-code conclusions are implementation details for the fixed commit, not exhaustive security audit.

| ID | Project / source owner | Exact URL / title | Tier / evidence kind | Supported property and exclusions |
| --- | --- | --- | --- | --- |
| BW01 | containers/bubblewrap | [README.md](https://raw.githubusercontent.com/containers/bubblewrap/0f8073dd9b547e15e8ec9451371f9729830b083d/README.md) | 2 / DESIGN_INTENT | Construction-tool/policy responsibility/userns and hazards; historical README examples may lag code |
| BW02 | containers/bubblewrap | [bubblewrap.c](https://raw.githubusercontent.com/containers/bubblewrap/0f8073dd9b547e15e8ec9451371f9729830b083d/bubblewrap.c) | 2 / IMPLEMENTATION_DETAIL | Current source LGPL-2.0-or-later, parent death/seccomp/PID/FD path; not a complete sandbox policy |
| BW03 | containers/bubblewrap | [COPYING](https://raw.githubusercontent.com/containers/bubblewrap/0f8073dd9b547e15e8ec9451371f9729830b083d/COPYING) | 2 / LICENSE_TEXT | LGPL-2.1 license text distributed in COPYING; per-file SPDX version remains distinct |
| CD01 | containerd/containerd | [docs/runtime-v2.md](https://raw.githubusercontent.com/containerd/containerd/81af89b1d4b1feab373a5251254f3cc82b9b4494/docs/runtime-v2.md) | 2 / DESIGN_INTENT | Runtime-v2 shim/socket/event/subreaper/lifecycle contract; daemon death is not a stop guarantee |
| CD02 | containerd/containerd | [core/runtime/v2/task_manager.go](https://raw.githubusercontent.com/containerd/containerd/81af89b1d4b1feab373a5251254f3cc82b9b4494/core/runtime/v2/task_manager.go) | 2 / IMPLEMENTATION_DETAIL | Task manager reconnect/delete/cleanup implementation; no exactly-once or outer deadline evidence |
| CD03 | containerd/containerd | [LICENSE](https://raw.githubusercontent.com/containerd/containerd/81af89b1d4b1feab373a5251254f3cc82b9b4494/LICENSE) | 2 / LICENSE_TEXT | Apache-2.0 terms; snapshotter/plugin/runtime dependencies separate |
| CG01 | Linux kernel / upstream man-pages | [cgroup-v2.html](https://docs.kernel.org/admin-guide/cgroup-v2.html) | 1 / UPSTREAM_CONTRACT | cgroups v2 CPU/RAM/swap/tasks/delegation/subtree kill/populated semantics; no wall time or disk quota |
| CP01 | Linux man-pages | [Upstream Linux capability model](https://man7.org/linux/man-pages/man7/capabilities.7.html) | 1 / UPSTREAM_CONTRACT | Capabilities per-thread and namespace privilege model; CAP_SYS_ADMIN not universal least privilege |
| FC01 | firecracker-microvm/firecracker | [docs/design.md](https://raw.githubusercontent.com/firecracker-microvm/firecracker/f23a2136011e89e7953923d0efcf67f72d18fc87/docs/design.md) | 2 / DESIGN_INTENT | KVM/microVM process, API, device and isolation layering; host network filtering excluded |
| FC02 | firecracker-microvm/firecracker | [docs/jailer.md](https://raw.githubusercontent.com/firecracker-microvm/firecracker/f23a2136011e89e7953923d0efcf67f72d18fc87/docs/jailer.md) | 2 / DESIGN_INTENT | Jailer-specific UID/GID/chroot/cgroups/netns/daemon model; not a generic jailer or finite lifetime guarantee |
| FC03 | firecracker-microvm/firecracker | [docs/prod-host-setup.md](https://raw.githubusercontent.com/firecracker-microvm/firecracker/f23a2136011e89e7953923d0efcf67f72d18fc87/docs/prod-host-setup.md) | 2 / DESIGN_INTENT | Production seccomp/patching/log/serial/overwatch responsibilities; examples not tested settings |
| FC04 | firecracker-microvm/firecracker | [docs/snapshotting/snapshot-support.md](https://raw.githubusercontent.com/firecracker-microvm/firecracker/f23a2136011e89e7953923d0efcf67f72d18fc87/docs/snapshotting/snapshot-support.md) | 2 / DESIGN_INTENT | Snapshot pause/load/guest-memory persistence; no restoration of Nexus authority |
| FC05 | firecracker-microvm/firecracker | [src/jailer/src/env.rs](https://raw.githubusercontent.com/firecracker-microvm/firecracker/f23a2136011e89e7953923d0efcf67f72d18fc87/src/jailer/src/env.rs) | 2 / IMPLEMENTATION_DETAIL | Env::new/run and cgroup-parent/exec ordering implementation; current source not deployed proof |
| FC06 | firecracker-microvm/firecracker | [LICENSE](https://raw.githubusercontent.com/firecracker-microvm/firecracker/f23a2136011e89e7953923d0efcf67f72d18fc87/LICENSE) | 2 / LICENSE_TEXT | Apache-2.0 license terms; dependencies and actual redistribution still need review |
| FC07 | firecracker-microvm/firecracker | [NOTICE](https://raw.githubusercontent.com/firecracker-microvm/firecracker/f23a2136011e89e7953923d0efcf67f72d18fc87/NOTICE) | 2 / LICENSE_TEXT | Project NOTICE; preserve applicable notices rather than assume none |
| GV01 | google/gvisor | [runsc/container/container.go](https://raw.githubusercontent.com/google/gvisor/0b0c579a788579db106713f67e8d0cf88506bda8/runsc/container/container.go) | 2 / IMPLEMENTATION_DETAIL | Container New/Destroy/Signal/metadata implementation, Sentry/Gofer ownership; no hard timeout contract |
| GV02 | google/gvisor | [LICENSE](https://raw.githubusercontent.com/google/gvisor/0b0c579a788579db106713f67e8d0cf88506bda8/LICENSE) | 2 / LICENSE_TEXT | Apache-2.0 terms; no proprietary/dependency clearance inferred |
| GV03 | google/gvisor | [gVisor security introduction](https://gvisor.dev/docs/architecture_guide/intro/) | 1 / UPSTREAM_CONTRACT | Sentry and syscall mediation architecture; not hardware side-channel or Host pre-runtime protection |
| GV04 | google/gvisor | [gVisor security model](https://gvisor.dev/docs/architecture_guide/security/) | 1 / UPSTREAM_CONTRACT | Security TCB, directfs/Gofer/network and host cgroup dependencies; no Nexus grants/evidence |
| GV05 | google/gvisor | [gVisor resource model](https://gvisor.dev/docs/architecture_guide/resources/) | 1 / UPSTREAM_CONTRACT | Virtual tasks/memory/time and host resource model; host PID count not virtual task bound |
| GV06 | google/gvisor | [gVisor platform guide](https://gvisor.dev/docs/architecture_guide/platforms/) | 1 / UPSTREAM_CONTRACT | Systrap/KVM platform prerequisites; no installed-mode qualification |
| GV07 | google/gvisor | [gVisor networking](https://gvisor.dev/docs/user_guide/networking/) | 1 / UPSTREAM_CONTRACT | Network stack/host mode/disabled choices; route-specific policy remains required |
| KA02 | kata-containers/kata-containers | [docs/design/README.md](https://raw.githubusercontent.com/kata-containers/kata-containers/fdff4bb12d2a0292724681e2ca8b47e3e8828100/docs/design/README.md) | 2 / DESIGN_INTENT | Design index and actual architecture directory discovery; not a security guarantee |
| KA03 | kata-containers/kata-containers | [src/runtime/virtcontainers/sandbox.go](https://raw.githubusercontent.com/kata-containers/kata-containers/fdff4bb12d2a0292724681e2ca8b47e3e8828100/src/runtime/virtcontainers/sandbox.go) | 2 / IMPLEMENTATION_DETAIL | Sandbox state/hypervisor/agent/create/stop API implementation; no universal fault latency |
| KA04 | kata-containers/kata-containers | [LICENSE](https://raw.githubusercontent.com/kata-containers/kata-containers/fdff4bb12d2a0292724681e2ca8b47e3e8828100/LICENSE) | 2 / LICENSE_TEXT | Apache-2.0 terms; guest assets/hypervisor/dependencies are separate |
| KA05 | kata-containers/kata-containers | [docs/design/architecture/README.md](https://raw.githubusercontent.com/kata-containers/kata-containers/fdff4bb12d2a0292724681e2ca8b47e3e8828100/docs/design/architecture/README.md) | 2 / DESIGN_INTENT | Shim/VM/guest-agent and container boundary, normal shutdown; not guest-independent cessation proof |
| KA06 | kata-containers/kata-containers | [docs/design/architecture/networking.md](https://raw.githubusercontent.com/kata-containers/kata-containers/fdff4bb12d2a0292724681e2ca8b47e3e8828100/docs/design/architecture/networking.md) | 2 / DESIGN_INTENT | Host veth/TAP/TC/CNI and guest network lifecycle; no exact-host allowlist guarantee |
| KA07 | kata-containers/kata-containers | [docs/design/architecture/storage.md](https://raw.githubusercontent.com/kata-containers/kata-containers/fdff4bb12d2a0292724681e2ca8b47e3e8828100/docs/design/architecture/storage.md) | 2 / DESIGN_INTENT | Virtio-fs/host sharing and storage-limit responsibility; no storage capacity ceiling by default |
| KA08 | kata-containers/kata-containers | [docs/design/host-cgroups.md](https://raw.githubusercontent.com/kata-containers/kata-containers/fdff4bb12d2a0292724681e2ca8b47e3e8828100/docs/design/host-cgroups.md) | 2 / DESIGN_INTENT | Host cgroup topology/overhead allocation; dated design, configuration must match chosen implementation |
| KJ01 | kubernetes/kubernetes | [pkg/controller/job/job_controller.go](https://raw.githubusercontent.com/kubernetes/kubernetes/99a4ea72fe6fe258d2e2875e7f83223bfbd50463/pkg/controller/job/job_controller.go) | 2 / IMPLEMENTATION_DETAIL | Job-controller desired-state/deadline/replacement implementation; not physical node cessation |
| KJ02 | kubernetes/kubernetes | [LICENSE](https://raw.githubusercontent.com/kubernetes/kubernetes/99a4ea72fe6fe258d2e2875e7f83223bfbd50463/LICENSE) | 2 / LICENSE_TEXT | Apache-2.0 code terms; cluster ecosystem excluded |
| KW01 | kubernetes/website | [content/en/docs/concepts/workloads/controllers/job.md](https://raw.githubusercontent.com/kubernetes/website/192e45e734c55f41d7691d965ccf567dea9cbd0e/content/en/docs/concepts/workloads/controllers/job.md) | 2 / DESIGN_INTENT | Jobs deadlines/suspend reset/retry/terminal conditions/finalizers; pattern only, version-feature binding needed |
| KW02 | kubernetes/website | [content/en/docs/concepts/workloads/pods/pod-lifecycle.md](https://raw.githubusercontent.com/kubernetes/website/192e45e734c55f41d7691d965ccf567dea9cbd0e/content/en/docs/concepts/workloads/pods/pod-lifecycle.md) | 2 / DESIGN_INTENT | Pod termination/grace/node lifecycle; object deletion not physical cleanup |
| KW03 | kubernetes/website | [content/en/docs/concepts/workloads/controllers/ttlafterfinished.md](https://raw.githubusercontent.com/kubernetes/website/192e45e734c55f41d7691d965ccf567dea9cbd0e/content/en/docs/concepts/workloads/controllers/ttlafterfinished.md) | 2 / DESIGN_INTENT | TTL-after-finished object cleanup; no active-work lifetime or hard garbage-collection latency |
| KW04 | kubernetes/website | [LICENSE](https://raw.githubusercontent.com/kubernetes/website/192e45e734c55f41d7691d965ccf567dea9cbd0e/LICENSE) | 2 / LICENSE_TEXT | CC-BY-4.0 documentation terms; no wholesale copied docs |
| LK01 | torvalds/linux | [COPYING](https://raw.githubusercontent.com/torvalds/linux/ff47652a4b66c067c765a7ad464d930b5a9367cc/COPYING) | 2 / LICENSE_TEXT | Kernel license scope and syscall exception; not all components same license |
| LK02 | torvalds/linux | [LICENSES/preferred/GPL-2.0](https://raw.githubusercontent.com/torvalds/linux/ff47652a4b66c067c765a7ad464d930b5a9367cc/LICENSES/preferred/GPL-2.0) | 2 / LICENSE_TEXT | GPL-2.0 license text; kernel redistribution/source obligations scoped |
| LK03 | torvalds/linux | [Documentation/security/landlock.rst](https://raw.githubusercontent.com/torvalds/linux/ff47652a4b66c067c765a7ad464d930b5a9367cc/Documentation/security/landlock.rst) | 2 / DESIGN_INTENT | Landlock LSM design/IPC/FD semantics; not a userspace policy or resource fence |
| LL01 | Linux kernel | [Landlock userspace API](https://docs.kernel.org/userspace-api/landlock.html) | 1 / UPSTREAM_CONTRACT | Landlock userspace ABI/access model, best-effort compatibility examples; unsupported mandatory enforcement must STOP |
| NJ01 | google/nsjail | [README.md](https://raw.githubusercontent.com/google/nsjail/4ff54a6e0d5b65a0e1633d6e2fd1425ba6c882ce/README.md) | 2 / DESIGN_INTENT | Process isolation modes/configuration and prerequisites; examples not accepted Nexus policy |
| NJ02 | google/nsjail | [subproc.cc](https://raw.githubusercontent.com/google/nsjail/4ff54a6e0d5b65a0e1633d6e2fd1425ba6c882ce/subproc.cc) | 2 / IMPLEMENTATION_DETAIL | reapProc time(NULL) timeout/kill and child tracking; parent loop is not independent ultimate fence |
| NJ03 | google/nsjail | [contain.cc](https://raw.githubusercontent.com/google/nsjail/4ff54a6e0d5b65a0e1633d6e2fd1425ba6c882ce/contain.cc) | 2 / IMPLEMENTATION_DETAIL | containment, parent-death race checks, privilege/input/rlimit setup; no physical kill bound |
| NJ04 | google/nsjail | [cgroup2.cc](https://raw.githubusercontent.com/google/nsjail/4ff54a6e0d5b65a0e1633d6e2fd1425ba6c882ce/cgroup2.cc) | 2 / IMPLEMENTATION_DETAIL | cgroup2 parent setup/apply/cleanup implementation; delegation/current supported controllers unverified |
| NJ05 | google/nsjail | [config.proto](https://raw.githubusercontent.com/google/nsjail/4ff54a6e0d5b65a0e1633d6e2fd1425ba6c882ce/config.proto) | 2 / IMPLEMENTATION_DETAIL | Configuration schema exposes time/namespace/resource policy; trusted config closure required |
| NJ06 | google/nsjail | [LICENSE](https://raw.githubusercontent.com/google/nsjail/4ff54a6e0d5b65a0e1633d6e2fd1425ba6c882ce/LICENSE) | 2 / LICENSE_TEXT | Apache-2.0 terms; Kafel/other dependencies separately scoped |
| NS01 | Linux kernel / upstream man-pages | [namespaces.7.html](https://man7.org/linux/man-pages/man7/namespaces.7.html) | 1 / UPSTREAM_CONTRACT | Namespace views/membership; shared host kernel and FDs remain |
| OC01 | opencontainers/runtime-spec | [runtime.md](https://raw.githubusercontent.com/opencontainers/runtime-spec/6999a89a76a0329f440d5740497bedb9dd431297/runtime.md) | 1 / UPSTREAM_CONTRACT | Normative OCI lifecycle/state/create-start barriers/error/hook contract; not safety or timing qualification |
| OC02 | opencontainers/runtime-spec | [config-linux.md](https://raw.githubusercontent.com/opencontainers/runtime-spec/6999a89a76a0329f440d5740497bedb9dd431297/config-linux.md) | 1 / UPSTREAM_CONTRACT | Normative Linux namespace/cgroup/capability/seccomp configuration; implementation support/applied state separate |
| OC03 | opencontainers/runtime-spec | [LICENSE](https://raw.githubusercontent.com/opencontainers/runtime-spec/6999a89a76a0329f440d5740497bedb9dd431297/LICENSE) | 1 / LICENSE_TEXT | Apache-2.0 specification terms; no complete runtime selection |
| QT01 | Linux kernel / upstream man-pages | [quota.html](https://docs.kernel.org/filesystems/quota.html) | 1 / UPSTREAM_CONTRACT | Quota subsystem concepts; no selected filesystem/project-quota configuration |
| RC01 | opencontainers/runc | [README.md](https://raw.githubusercontent.com/opencontainers/runc/a945133d52eb87415b3a9004f68e11b8b6e0cc2e/README.md) | 2 / DESIGN_INTENT | OCI CLI create/start/rootless and supervisor responsibilities; example defaults not hardened policy |
| RC02 | opencontainers/runc | [libcontainer/container_linux.go](https://raw.githubusercontent.com/opencontainers/runc/a945133d52eb87415b3a9004f68e11b8b6e0cc2e/libcontainer/container_linux.go) | 2 / IMPLEMENTATION_DETAIL | Container Signal/Set/state; shared-PID/rootless missing-cgroup fallback can leak processes |
| RC03 | opencontainers/runc | [libcontainer/standard_init_linux.go](https://raw.githubusercontent.com/opencontainers/runc/a945133d52eb87415b3a9004f68e11b8b6e0cc2e/libcontainer/standard_init_linux.go) | 2 / IMPLEMENTATION_DETAIL | Standard init Linux setup/no_new_privs/seccomp/exec ordering; trusted hooks and dependencies included |
| RC04 | opencontainers/runc | [LICENSE](https://raw.githubusercontent.com/opencontainers/runc/a945133d52eb87415b3a9004f68e11b8b6e0cc2e/LICENSE) | 2 / LICENSE_TEXT | Apache-2.0 terms; libcontainer linking and dependencies need concrete distribution review |
| SC01 | Linux kernel / upstream man-pages | [seccomp_filter.html](https://docs.kernel.org/userspace-api/seccomp_filter.html) | 1 / UPSTREAM_CONTRACT | Seccomp filtering semantics and limitations; explicitly not complete sandbox |
| SD01 | systemd/systemd | [man/systemd.scope.xml](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/systemd.scope.xml) | 2 / DESIGN_INTENT | Scope externally created process group, no main process, RuntimeMaxSec; create-to-attach race not solved |
| SD02 | systemd/systemd | [man/systemd.resource-control.xml](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/systemd.resource-control.xml) | 2 / DESIGN_INTENT | Resource control/delegation/cgroup directives; requested properties not effective proof |
| SD03 | systemd/systemd | [man/org.freedesktop.systemd1.xml](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/org.freedesktop.systemd1.xml) | 2 / DESIGN_INTENT | Manager D-Bus StartTransientUnit/property/operation interface; not Nexus-authorized generic root API |
| SD04 | systemd/systemd | [LICENSE.LGPL2.1](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/LICENSE.LGPL2.1) | 2 / LICENSE_TEXT | LGPL-2.1 license text; file and other program licenses separately governed |
| SD05 | systemd/systemd | [LICENSES/README.md](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/LICENSES/README.md) | 2 / LICENSE_TEXT | Default LGPL-2.1-or-later and exceptions/NOTICE-like distribution scope; not legal approval |
| SD06 | systemd/systemd | [systemd.service.xml](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/systemd.service.xml) | 2 / DESIGN_INTENT | Service startup/active/stop, notify extension, watchdog/restart; none implies immutable universal wall bound |
| SD07 | systemd/systemd | [systemd.kill.xml](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/systemd.kill.xml) | 2 / DESIGN_INTENT | KillMode/control-group/escalation; no maximum SIGKILL completion latency |
| SD08 | systemd/systemd | [systemd.exec.xml](https://raw.githubusercontent.com/systemd/systemd/0794ba0045d11d4227f61ebacf7d75983ba884f1/man/systemd.exec.xml) | 2 / DESIGN_INTENT | Effective exec environment/root/temporary input facilities; independent runtime observations still required |
| WD01 | Linux kernel / upstream man-pages | [watchdog-api.html](https://docs.kernel.org/watchdog/watchdog-api.html) | 1 / UPSTREAM_CONTRACT | Watchdog API device/reset/feed variations; no universal poweroff or finite failure bound |

## 4. Exact retrieved-byte binding

These hashes identify public source bodies, not actual-loaded qualification code. Commit-bearing URLs bind the version above; moving pages bind only these exact dated bytes.

| ID | Bytes | SHA-256 |
| --- | --- | --- |
| BW01 | 10687 | `0C1DC12C6D94017C45E220FC0E5B679F24C0F09494BDD4BC7157D8ABCD75C001` |
| BW02 | 114758 | `3C712DE373A531EB727963883AEB3B258335156A31A9ADB7C9E5BB3E6C57DB82` |
| BW03 | 26530 | `DC626520DCD53A22F727AF3EE42C770E56C97A64FE3ADB063799D8AB032FE551` |
| CD01 | 26443 | `D29E753BE2BB3704403D73228517947C32AF575C6235E2D339DF1E5304787269` |
| CD02 | 14432 | `7046E67A782FD9B058C71A2BEE8715A92889F4A339532148E89E4D606D11F6A6` |
| CD03 | 10765 | `4BBE3B885E8CD1907AB4CF9A41E862E74E24B5422297A4F2FE524E6A30ADA2B4` |
| CG01 | 172971 | `6EFABE7ED748F1D863859A0E5C50E770E47255C9A071BF878F6460E7E01C0563` |
| CP01 | 83601 | `79CA88F6D8984CA2858860E7267D7C4660F6555151CC1F570305A9C6DFCCF714` |
| FC01 | 9988 | `58CDE9CFA1E9CF7A87B687EAD69BED5FD7542B331AC45DE18E91059D29B6ACE6` |
| FC02 | 17751 | `E71C8647C46F5FEE16A2E72B0FE68D0BE130BC84987FF0EF37C55504267927F9` |
| FC03 | 21548 | `19CF9CF9965FB4FDD36C0F55CEB7165E06EFD8601629E956827069D9F1A3DE16` |
| FC04 | 33367 | `FC716201060779E0164F7625652C026F9EDB78B44B98E2892747B550D5AA47E1` |
| FC05 | 58950 | `355A100DA24646FC5752C7B28DD761BD39963CE782C05593AA7E6A595070972E` |
| FC06 | 11358 | `CFC7749B96F63BD31C3C42B5C471BF756814053E847C10F3EB003417BC523D30` |
| FC07 | 535 | `0F443AF83CA8226C7EC44E2ADE3A09FA3EED8C9B923B6C014B6D439816B6F1C2` |
| GV01 | 90491 | `4DED3053DE06B9E2962CB7D2BF4A0C549DB66B1A46D96EAAD9EF74B1BDAA13CB` |
| GV02 | 14110 | `0FBAB5C58EFBDF6D31E8085214F2DD821659C03D73CFF3ED2B08E98826EA1CD9` |
| GV03 | 38274 | `19CB853233BB4954447CC82925B63BDBB112ABA737B84AF81D706EAE2BA9B32D` |
| GV04 | 35468 | `959292C5FEC7CF308D783AD612D1AF27FF1FAD893FBB1592DF8EB6C611DD0695` |
| GV05 | 27640 | `3A194E89B162FB1A9B7018DE1316372DFD8F06FDF5F0A11A5F448C4441EE5018` |
| GV06 | 24848 | `79F81D3E2B05E0244073CFB497DCD5F78B4B952C39587163CF5B8DF80CDEF9F9` |
| GV07 | 33223 | `240CBC305D43F174AA1B0BCA858D937B104BD9101092B3F3DD6BC26B8F6F6B43` |
| KA02 | 1098 | `5302BC0E2C615A9A331E4D585279FE20C132496AE0DC542D5FFB9E0D7C20BC43` |
| KA03 | 101931 | `594B6EF542D46C122E268FFB26D197E510C0A40A2E8484823A2CDE13FD6941C7` |
| KA04 | 11357 | `C71D239DF91726FC519C6EB72D318EC65820627232B2F796219E87DCF35D0AB4` |
| KA05 | 19776 | `5A48C237FB00F97D4A1DBD327C9FCAC4D6D350CED41C19D3C1072A105DCE657B` |
| KA06 | 3129 | `9E95822251A2F1F91168DF5799EE869599A1F1BEF07D0924B3021B2ED44B44EA` |
| KA07 | 2509 | `AEF5B2F48D01B46090C29E284063D9760B508A490AE07407127849F768DB12FE` |
| KA08 | 20405 | `F00E39435587F92AA60E21E1FC849584E98EBB028382166183EE58DC7E7E99E3` |
| KJ01 | 87908 | `6AD9DEBBED7978670AA32A8BD12DE624D628B5D25571081003EB3C3730E02887` |
| KJ02 | 11358 | `CFC7749B96F63BD31C3C42B5C471BF756814053E847C10F3EB003417BC523D30` |
| KW01 | 65389 | `D7AA50F7270853D3BB944BBF98478B6E0B25AAD33FF6A2A29F2D33B37D63A6F7` |
| KW02 | 56400 | `1D81A56B63AA75E10D3CEA41978420DA7C046027A143C56852F6698FF5E6623C` |
| KW03 | 4008 | `CE1F476BD9BC596535EFED8E57B292AE475931BAA14D2496112DEE1717B19C41` |
| KW04 | 18657 | `9BA9550AD48438D0836DDAB3DA480B3B69FFA0AAC7B7878B5A0039E7AB429411` |
| LK01 | 496 | `FB5A425BD3B3CD6071A3A9AFF9909A859E7C1158D54D32E07658398CD67EB6A0` |
| LK02 | 18600 | `8780E78A1A737E127F25A65F6D95269BFFD36158DC261114DE7859B490BFC5AA` |
| LK03 | 9301 | `3D593D0927E3A10C46E430A5FBD3212F69FB62B7A7B4581564F78E7A68BE6864` |
| LL01 | 150991 | `1C258549336D01DF7163EF551674B314C9E6B81AE4B9F26C3B4D80336AB87875` |
| NJ01 | 8237 | `D2D919E9CF5CF0267F11A124678AA0459B3A822610D2EA75AFA55B385CFFCE84` |
| NJ02 | 20751 | `B928419D45A099E464268AA833A8BC7715E149DD1C4390DF8BC4CCAA855A8882` |
| NJ03 | 13441 | `3B84D867608C6B89755B8EECDC2EBE7529DEF2D6A970C5B483716B35F072F94B` |
| NJ04 | 9197 | `84B72D89437B8285EDF4C49FB6261620987F11CEEDABAF43B13CE6143C66CC12` |
| NJ05 | 17725 | `4FB2050C88CE38BC42D999AFDD412B412C8DE236525072214595D408CE6A58DF` |
| NJ06 | 11358 | `CFC7749B96F63BD31C3C42B5C471BF756814053E847C10F3EB003417BC523D30` |
| NS01 | 25329 | `F8E08716DF1F4AFDF05B22E11B010E14F47311EB92F0A948FEDBB95099C36AA7` |
| OC01 | 10065 | `6236BFD0C5762CFCF1E86BE084C07E767CB6DFF35692959E6811CECF2D334D91` |
| OC02 | 52544 | `0B9BDAD8C8B5FF0EF3E99FF4452C874D9D78A4AF347DD145D2B6087E67CA1395` |
| OC03 | 10767 | `A964A27C435167BDD78827FF83E4BD4473ECA53D583A39598D2F445894A9225D` |
| QT01 | 13430 | `D9D456E70A7465DFCDFEA1ADDFFCCFEDBBB0124DEF8A05630432140F46EAB140` |
| RC01 | 14953 | `90C9050F1D5BFF14E28CE2BDF8CD6A6DE8EB71ABD13A732B6DDF5A90D3572D95` |
| RC02 | 37807 | `9E6F499A8B5BCD32B1C7A4089B9222C3CEE2117CB13DACF209AE486A96369104` |
| RC03 | 10531 | `3C76AC0AEFE0169A3A43C4AD0AA42511819230EF9931C9EBDC929FDA15A3AAA0` |
| RC04 | 10758 | `552A739C3B25792263F731542238B92F6F8D07E9A488EAE27E6C4690038A8243` |
| SC01 | 38437 | `419DE4141B38BCE8754DE25A28902CFB8F7BC98FC6F1C9C9640983CC5BC8065D` |
| SD01 | 6777 | `266529B134EAF133ED1DF8EFA8CE5E069FDA76EC06818142B3A3E542D7B09D3C` |
| SD02 | 110159 | `D57641DF40E45811403DE91E55059B6A8F7506C6812A85CBE9C6BA22900587D8` |
| SD03 | 603472 | `59CFEEA5144E169369EE81F2B797FE9EB63EC18CB6AA918C2E66A7D5218117CA` |
| SD04 | 26518 | `6D9BB3B7FC818A8FACC4CC296060A0883FEF8710D6498F86165335846E82EE9D` |
| SD05 | 4206 | `A817486A61DF66EF79F96032763C861ABD0EDF4199CF39A7B1515A7E29F6E6D0` |
| SD06 | 120642 | `12770F86A26DCDF32873225669F5AA9421283C303BBC72BDDB04530850F66D44` |
| SD07 | 11224 | `448322830DBBD02C64CCA99941BA92705AFE9648241FC917DB7A8D6AE7910E72` |
| SD08 | 343315 | `44B89BFFCE737AFF803966C207329E9FE2D28AD07709A4BB8E0EDF6A4EC0D844` |
| WD01 | 24828 | `0E0D19BBCE5CCCA8D22DC8CBF754CF626E9D723B144C029477235326C69882D0` |

Scenario 01-04 NOT RUN; HQ1-HQ5 NOT PASS; HQ6 NOT STARTED; Positive Host Binding ABSENT; G2 HOLD. D0-D7 NOT STARTED. Route B unresolved; OpenAI human escalation PENDING. Accepted architecture/A0-A6/P1-P12 and sealed V4 unchanged. No installation, Host/provider execution, credentials, paid activity, privileged/system changes, G2/G3/G4 implementation, acceptance, merge/push/tag/freeze.
