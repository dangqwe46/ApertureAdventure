# Research Note: Web Networking and Backend for Aperture

| Field | Value |
|-------|-------|
| **Type** | Technical research note (input to future ADRs, not an ADR) |
| **Author** | technical-director |
| **Date** | 2026-11-03 |
| **Engine** | Godot 4.7.2, GDScript, Web export, Compatibility renderer, Jolt physics (`project.yaml`) |
| **Export assumption** | Web export with **Thread Support OFF** |
| **Inputs** | `design/gdd/game-concept.md` §Online play, §Technical considerations; `docs/engine-reference/godot/modules/networking.md`; `.claude/rules/network-code.md` |
| **Status** | Research. Nothing here is decided. Each "Decision to make" becomes an ADR via `/architecture-decision` |

> **Sourcing rule used in this note.** Every engine-version-specific claim cites a URL.
> Where a claim could not be confirmed in this research pass it is marked
> **NOT SOURCEABLE** and must be verified (usually by a 30-minute spike) before an
> ADR relies on it. Third-party sources are labelled as such.

---

## 1. Requirements recap (from the concept)

- **Real-time:** co-op crews of 2-4 players in a shared 3D expedition space; a larger shared hub later.
- **Asynchronous/global:** market and trading, top-100 leaderboards (all-time, weekly, by category, rarity), galleries, commission board, found photos, themes judged by players.
- **Server authority:** the server owns inventories, trades, prices, scores, rarity rolls, supply and claim counters. Messages are versioned and field ranges validated (`.claude/rules/network-code.md`).
- **Photo as recipe:** camera pose, settings, time of day, subject pose. The server re-scores every photo; clients cannot upload images.
- **Constraints:** browser client; no paid services beyond what the user has; free or self-hostable; solo developer.

---

## 2. Audit of the existing engine reference (`docs/engine-reference/godot/modules/networking.md`)

| Section of the reference | Applies to Aperture? | Notes |
|---|---|---|
| `ENetMultiplayerPeer` host/join code | **No, for the web client.** Usable only on the server if the server also served native clients, which it will not | Browser builds support only HTTP client, HTTPRequest, WebSocket (client) and WebRTC [S1]. Replace with `WebSocketMultiplayerPeer` on both ends |
| RPC annotations (`any_peer`, `authority`, `call_local`, `reliable`) and the server-validates-then-broadcasts pattern | **Yes** | Transport-independent. The 4.7 WebSocket tutorial states the WebSocket implementation works with the high-level multiplayer system [S2] |
| `MultiplayerSpawner` / `MultiplayerSynchronizer` | **Yes, with caveat** | They sit on the MultiplayerAPI, which works over WebSocket [S2]. An explicit 4.7 test of Synchronizer over `WebSocketMultiplayerPeer` in a single-threaded web build: **NOT SOURCEABLE**. Spike it |
| `SceneMultiplayer.auth_callback` | **Yes, important** | Use it for the version handshake and token check before a peer joins a room |
| `server_relay = false` comment "Direct peer connections" | **Misleading for us** | WebSocket is client-server; there are no direct peer connections. Setting `server_relay = false` is still right (clients should not relay to each other) but for authority reasons |
| "Use `unreliable` for position updates" | **Partly** | WebSocket runs over TCP [S3], so all traffic is ordered and reliable underneath. How `WebSocketMultiplayerPeer` treats the `unreliable` transfer mode: **NOT SOURCEABLE**. Assume it is delivered reliably and budget for head-of-line blocking |
| 4.5/4.6/4.7 change notes | Consistent with research | No 4.7 networking changes were found in release coverage [S4]; the 4.7 WebSocket docs and demos exist [S2][S5] |

**Recommendation for the reference file (not edited here):** add a "Web export" section with the `WebSocketMultiplayerPeer` equivalent, the `wss://` rule and the HTTPRequest/CORS notes below. Route this through whoever owns `docs/engine-reference/`.

---

## 3. Godot 4.7 web-export networking findings

### 3.1 What the browser build can use

- Only **HTTP client, HTTPRequest, WebSocket (client) and WebRTC** are available on the web; no low-level sockets [S1]. A browser tab can **never be a server**; there is no player-hosted room in a web build.
- `WebSocketMultiplayerPeer.create_client(url, tls_client_options)` and `create_server(port, bind_address, tls_server_options)` exist in the 4.7 class reference; `wss://` certificates are verified against the hostname [S6].
- `WebSocketPeer` is the underlying class; Godot supports WebSocket in native and web exports [S2].
- **Custom handshake headers are not supported in web exports** (browser restriction) [S7]. Auth tokens must therefore go in the URL query string or in the first message / `auth_callback` payload, not in an `Authorization` header on the socket. (Same browser rule; no 4.7-specific page found that says it changed.)
- **`wss://` is mandatory in practice.** A page served over HTTPS (itch.io, Pages hosts) cannot open `ws://` to a non-localhost host (mixed content). Use the domain name that matches the certificate, not an IP [S8][S9]. Consequence: **the server needs a domain name and a valid TLS certificate**, even for a prototype playtest.
- **HTTPRequest on web is subject to CORS.** The server must send `Access-Control-Allow-Origin` for the page's origin [S10]. Any REST backend we choose must be configured for this.

### 3.2 WebRTC

- WebRTC classes (`WebRTCPeerConnection`, `WebRTCDataChannel`, `WebRTCMultiplayerPeer`) are built into the web export, but **native platforms need the external `webrtc-native` GDExtension** [S3]. A headless Linux Godot server joining as a WebRTC peer would need that extension.
- WebRTC requires a separate **signaling server** (typically WebSocket) [S3]. A NAT-traversal relay (TURN) is normally needed for some players; free public TURN availability and reliability: **NOT SOURCEABLE** in this pass.
- The 4.7 stable WebRTC page carries a "not yet updated for 4.7" banner [S11].
- **Verdict:** WebRTC's benefit (unreliable/unordered UDP-like channels) matters for fast action games. Aperture's crews move at walking pace and take photos; TCP latency is acceptable. WebRTC adds signaling, TURN and a GDExtension on the server for little gain. **Defer.**

### 3.3 Threads OFF (no SharedArrayBuffer)

- Single-threaded web export is the default since 4.3 and avoids the cross-origin isolation headers (COOP/COEP) that threaded builds need [S12][S13]. It is less performant than the threaded build but works on more hosts, including itch.io [S13].
- **Networking impact:** `WebSocketPeer` and `HTTPRequest` are polled APIs driven from the main loop. A documented requirement for threads in either: none found. An explicit statement that they work without threads: **NOT SOURCEABLE**; the Godot WebSocket demos are the spike target [S5].
- Set `HTTPRequest.use_threads = false` on web. The Nakama Godot client disabled it for HTML5 exports [S14] (third-party evidence, consistent with no-threads).
- Non-networking side effect worth knowing: without threads, audio defaults to Sample playback with no AudioEffects/reverb/doppler and imperfect positional audio; Stream mode restores features at higher latency [S13]. Flag to audio-director.
- **Hosting benefit:** with threads off, the client is a plain static site. No header configuration is needed, so itch.io, GitHub Pages and Cloudflare Pages all work [S15] (third-party).

### 3.4 Jolt on web

Whether Jolt physics is available and behaves identically in the 4.7 web export: **NOT SOURCEABLE** in this pass. It matters for scoring parity (§5). Verify in the first web spike.

---

## 4. Server options compared

### 4.1 The scoring constraint decides most of this

Re-scoring a recipe means placing the camera and the subject in the **same scene** the client used, then evaluating framing, occlusion, light, moment and gear limits. Only Godot can load `.tscn`/`.glb` scene data, collision shapes and the time-of-day model without re-implementing them. **Scoring must run in Godot**, whatever else the backend is.

Second constraint: **headless Godot 4 cannot render.** `--headless` uses a dummy rendering server; `get_viewport().get_texture().get_image()` returns null [S16][S17]. Rendering on a server would need a normal build under a virtual display and, realistically, a GPU, which is outside the free budget.

**Therefore the scoring model must be analytic, not pixel-based:** frustum and projection math, raycasts against collision geometry for occlusion, a light value computed from the time-of-day/light-source data, and gear ceilings from data tables. This is a design constraint the scoring GDD must respect. Whether `Camera3D.unproject_position` / `is_position_in_frustum` return correct values under the dummy renderer: **NOT SOURCEABLE**. If not, compute the projection manually from the camera transform and FOV (simple math, testable in unit tests).

The dedicated-server export mode adds the `dedicated_server` feature tag, forces `--headless`, and can strip visuals [S18]. Strip Visuals is advised unless the server needs image data [S18]; whether it also removes mesh data scoring might read (subject AABBs): **NOT SOURCEABLE**. Scoring should read collision shapes and explicit bounds resources, not render meshes.

### 4.2 Comparison

| Criterion | A. Headless Godot only (+ SQLite GDExtension) | B. Headless Godot + custom backend (TypeScript/Go/Python) | C. Headless Godot + PocketBase | D. Headless Godot + Nakama | E. Headless Godot + Supabase self-hosted |
|---|---|---|---|---|---|
| Real-time crew rooms | Godot | Godot | Godot | Godot (Nakama could relay, but authority and scene data stay in Godot) | Godot |
| Accounts/auth | **Hand-written.** Password hashing, sessions, resets in GDScript. High risk | Library-backed (e.g. a mature auth library). Medium effort | **Built in**: email/password and OAuth2 [S19] (third-party) | **Built in** (device, email, social) | **Built in** (GoTrue) |
| Database for market, serials, supply | SQLite via third-party GDExtension; transactions possible | Any (SQLite/Postgres). Full control | SQLite embedded; single binary; no clustering [S19] (third-party) | PostgreSQL or CockroachDB required [S20] | PostgreSQL |
| Atomic trades/serials | You write it | You write it | Server-side hooks you write; DB transactions | Server runtime (Go/Lua/TS) with storage + wallet; built-in leaderboards | SQL functions/RLS; powerful but SQL-heavy |
| Leaderboards | You write it | You write it | You write it (simple SQL) | **Built in** | You write it (SQL views) |
| Ops footprint | 1 process | 2 processes | 2 processes, one is a single Go binary | Nakama + Postgres; README recommends separate DB node in production [S20] | ~10-15 containers; **4 GB RAM / 2 cores minimum** [S21] |
| Licence/cost | Free | Free | MIT [S19] (third-party) | Apache-2.0 [S20] (mirrors; confirm on official repo) | Open source, self-hosted free |
| Godot web client fit | Native RPC only | HTTPRequest + REST (CORS) | HTTPRequest + REST (CORS). Its realtime feed is SSE [S19]; Godot has no SSE client, so realtime would need `JavaScriptBridge` + `EventSource` (**NOT SOURCEABLE**, and not needed if crews use Godot) | Official GDScript client for Godot 4 [S14]; explicit HTML5 support for the GDScript socket: **NOT SOURCEABLE** (release notes mention HTML5 fixes) | REST via HTTPRequest; no official Godot client found |
| Solo-dev learning cost | Low tooling, high security risk | High (second language, second codebase) | **Low** (admin UI, schema in browser) | Medium-high (new server runtime, DB ops) | Medium-high (Postgres, RLS, many services) |
| Fits free hosting | Yes | Yes | **Yes, smallest** | Tight on a 1-2 GB VM | **No** on free VMs (4 GB minimum) |
| Main risk | Rolling your own auth/crypto | Two codebases for one person | Pre-1.0 project with breaking changes between versions (general knowledge, verify current version); SQLite single-node | Operational weight; two DBs to reason about if Godot also stores state | Resource weight |

Notes:
- A Nakama-only design (no Godot server) is not viable because scoring needs Godot scenes (§4.1).
- Option A's "no second service" simplicity is real, but auth is the one thing a solo developer should not hand-write.

---

## 5. Recommended architecture

### 5.1 Primary recommendation: Godot room/scoring server + PocketBase meta service

```
 Browser (Godot 4.7 web, single-threaded, static host e.g. itch.io)
   |  HTTPS REST (HTTPRequest)            |  WSS (WebSocketMultiplayerPeer)
   v                                      v
 [Reverse proxy: Caddy, TLS for one domain, path routing]
   |                                      |
   v                                      v
 PocketBase "Meta"                      Godot headless "Room servers" (same project,
  - accounts, auth tokens                 dedicated_server export, Linux)
  - inventory, market, trades           - crew rooms 2-4 players, one room per process
  - serial numbers, supply counters     - authoritative movement, spirits, claims
  - galleries, leaderboards (SQL)       - SCORING: re-runs every recipe analytically
  - commission board, found photos      - rarity roll (server RNG)
   ^                                      |
   +---- privileged service API ----------+
         (room server writes scored photos, claims, rolls; clients cannot)
```

How it works:
1. Player logs in through PocketBase REST and gets a token.
2. Client asks Meta for a room; Meta returns `wss://domain/room/<n>` and a short-lived room ticket.
3. Client connects; `SceneMultiplayer.auth_callback` checks the **build version** and the ticket (ticket in the auth payload, since web sockets cannot send custom headers [S7]).
4. In the room, the client sends a shutter RPC with a recipe. The room server validates field ranges, re-scores, rolls rarity, and writes the result to Meta through a service-only endpoint. The client displays the server's score, not its own.
5. Market, galleries and leaderboards are plain REST against Meta; no room server needed, so asynchronous features work when nobody is in a crew.
6. **A scoring-only mode of the same server binary** (no room, just "score this recipe") handles photos taken outside a crew and re-checks during disputes.

Why this fits:
- Only one language (GDScript) for game logic and scoring; PocketBase hooks are small and confined to transactions (trades, serial issue, supply decrement).
- Smallest footprint: two light processes and a proxy fit on one small free VM.
- Client remains a static site (threads off), so it can be hosted for free anywhere.
- Each piece is replaceable: Meta's REST contract can later be re-implemented in Nakama or a custom service without touching the client's room code.

### 5.2 Alternative: Godot room/scoring server + Nakama

Choose this if the user prefers a game-specific backend with built-in leaderboards, wallets, matchmaking and friends, and accepts running PostgreSQL. Godot still does rooms and scoring; Nakama replaces PocketBase. Costs: heavier ops, a server runtime to learn (Go, Lua or TypeScript), and tighter fit on free VMs.

### 5.3 Rejected for v1

- **WebRTC transport:** see §3.2.
- **Supabase self-hosted:** 4 GB minimum RAM [S21] is beyond free VMs once Godot is running too.
- **Godot-only with hand-written auth:** security risk out of proportion to the time saved.
- **Pixel-based scoring:** headless cannot render [S16][S17].

### 5.4 Performance and bandwidth budgets (initial, to validate)

| Item | Initial budget | Basis |
|---|---|---|
| Crew sync rate | 10-15 Hz transforms, interpolated client-side | Walking-pace game over TCP |
| Per-player downstream in room | < 10 KB/s | 3 other players + spirits; to measure |
| Recipe payload | < 512 bytes | Pose, settings, time, subject id/pose, version |
| Server scoring time | < 20 ms per recipe | Raycasts + math; measure on target VM |
| Room server RAM | **NOT SOURCEABLE**; measure a stripped dedicated-server build | Determines rooms per free VM |

---

## 6. Hosting for a prototype (free first)

| Option | What you get | Limits and catches | Fit |
|---|---|---|---|
| **itch.io** (client) | Free HTTPS static hosting of the web build; optional SharedArrayBuffer toggle not needed with threads off [S15][S22] (third-party) | Page is HTTPS, so the server must be `wss://` with a real certificate [S9] | **Client: recommended** |
| GitHub Pages / Cloudflare Pages (client) | Free static hosting | Fine for a no-threads build; header control matters only for threaded builds [S15] (third-party) | Client alternative |
| **Home PC + Cloudflare Tunnel** (server) | Free; WSS works through tunnels per community guides; TLS terminates at Cloudflare [S23] (third-party) | Free-plan connection limits not officially documented in this pass (**NOT SOURCEABLE**); a named tunnel needs a domain on Cloudflare; uptime = your PC | **Dev and playtests: recommended** |
| **Oracle Cloud Always Free, Ampere A1** (server) | Always-on ARM VM | Reportedly **halved in 2026 to 2 OCPU / 12 GB** total, with conflicting effective dates (June or August 2026) [S24][S25] (third-party; confirm on Oracle docs). Over-limit instances reportedly disabled and deleted after 30 days [S26] (third-party). ARM needs a Linux arm64 Godot export template: availability for 4.7.2 **NOT SOURCEABLE** in this pass | **First always-on host: recommended, with verification** |
| Google Cloud e2-micro (server) | One always-free micro VM in us-west1/us-central1/us-east1, 30 GB standard disk [S27] (third-party) | **1 GB/month egress** to North America [S27]; a billing account reportedly required [S28] (third-party). Too little egress beyond a tiny test | Backup option |
| Render free web service | No card required [S29] | Free services spin down after ~15 min idle [S29] (third-party), dropping WebSocket sessions | Not suitable for rooms |
| Fly.io / Railway | Easy deploys | Trial-only for new accounts; ongoing use is paid (~$2/month small machine on Fly) [S30][S29] | Violates the no-paid constraint |

**Domain and TLS:** a domain is effectively required for `wss://` [S9]. Options to evaluate: a domain already owned by the user on Cloudflare (tunnel), or a free dynamic-DNS subdomain with Caddy's automatic Let's Encrypt certificates (**NOT SOURCEABLE** in this pass; verify the chosen provider's terms).

**Honest budget note:** zero-cost always-on hosting is fragile (see Oracle's 2026 reduction). If the game reaches an open beta, a small VPS in the low single-digit dollars per month is the realistic next step. That is a user decision, not a technical one.

---

## 7. Decisions that should become ADRs (titles only)

1. ADR: Network transport for web clients (WebSocket now, WebRTC deferred)
2. ADR: Server topology: headless Godot room/scoring servers plus a separate meta service
3. ADR: Meta backend selection (PocketBase vs Nakama vs custom)
4. ADR: Authentication, room tickets and token flow between client, meta service and room servers
5. ADR: Photo recipe schema and versioning
6. ADR: Analytic server-side scoring in headless Godot (no pixel rendering)
7. ADR: Client/server build lockstep and shared-code layout (one project, two export presets)
8. ADR: Room lifecycle and process model (process per room, allocation, shutdown)
9. ADR: Economy transaction integrity (inventory, trades, serial numbers, supply counters)
10. ADR: Server RNG authority and rarity-roll audit log
11. ADR: Network message protocol, validation and rate limiting
12. ADR: Web export configuration (single-threaded, HTTPRequest threading off, audio mode)
13. ADR: Hosting, reverse proxy and TLS termination
14. ADR: Leaderboard computation, windows and storage
15. ADR: Persistence backup, restore and schema migration

---

## 8. Biggest risks

| # | Risk | Why it matters | Mitigation |
|---|---|---|---|
| 1 | **Scoring parity between client preview and server** | Headless cannot render [S16], so scoring must be analytic; WASM client vs native Linux (possibly ARM) server can produce different float results; Jolt on web unverified (§3.4); scene data drifting between builds changes scores | Server score is the only truth; client shows "pending" then the server result. Quantize recipe fields. Score from collision shapes and explicit data, not render meshes. Golden-recipe regression tests run on both the web build and the server build in CI. Build-version check in `auth_callback` |
| 2 | **Free hosting is fragile** | Oracle halved its free ARM tier in 2026 [S24]; Render sleeps [S29]; GCP egress is 1 GB/month [S27]; a domain and certificate are needed for `wss://` [S9] | Keep the server stateless apart from Meta's database; script the deploy (one command, any Linux VM); nightly DB backup off-host; plan for a paid VPS as a user decision before beta |
| 3 | **Economy integrity across two services, for one developer** | Duplication, double-spend and serial collisions happen when the room server and meta DB disagree or a request is retried | All economy writes live in Meta inside single DB transactions; room servers call idempotent endpoints with request IDs; no economy state held in Godot memory; trade and serial tests written first. PocketBase version pinned (pre-1.0 churn) |

Other risks to log: TCP head-of-line stalls on poor connections (acceptable at walking pace; measure); a browser tab cannot host, so every crew session costs server resources (one process per room; measure RAM); the `unreliable` mode behaviour over WebSocket is unconfirmed (§2).

---

## 9. First spike (validates the NOT SOURCEABLE items)

One throwaway prototype in `prototypes/`, about two days:
1. Single-threaded web export connects over `wss://` (through Caddy or a tunnel) to a headless Godot 4.7.2 dedicated-server build; two browser tabs see each other via `MultiplayerSynchronizer`.
2. `auth_callback` rejects a mismatched build version.
3. Server scores a hard-coded recipe with raycasts and frustum math under `--headless`; the same function in the web build returns the same score within tolerance. Check Jolt on web here.
4. Measure server RAM per room process and bytes/second per client.
5. Web client calls a PocketBase REST endpoint (CORS configured) with `HTTPRequest.use_threads = false`.

---

## Sources

- [S1] Exporting for the Web (stable): https://docs.godotengine.org/en/stable//tutorials/export/exporting_for_web.html
- [S2] Using WebSockets (4.7): https://docs.godotengine.org/en/4.7/tutorials/networking/websocket.html
- [S3] WebRTC (stable): https://docs.godotengine.org/en/stable/tutorials/networking/webrtc.html
- [S4] Godot 4.7 release coverage (Phoronix via linux.org): https://www.linux.org/threads/phoronix-godot-4-7-released-with-hdr-output-support.67946/latest ; 4.7 migration guide: https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html
- [S5] WebSocket multiplayer demo (Godot Foundation, Asset Store): https://store.godotengine.org/asset/godot-foundation/websocket-multiplayer-demo/
- [S6] WebSocketMultiplayerPeer class reference (4.7): https://docs.godotengine.org/en/4.7/classes/class_websocketmultiplayerpeer.html
- [S7] WebSocketPeer class reference (4.2, `handshake_headers` not supported on web): https://docs.godotengine.org/en/4.2/classes/class_websocketpeer.html
- [S8] Godot forum, wss on HTTPS pages: https://forum.godotengine.org/t/problems-with-websockets-and-html5-export/12451
- [S9] Godot docs commit on wss:// caveats (FQDN must match certificate): https://git.objectionable.solutions/Sara/behaviour-tree-test/commit/a56e37545bec0390784cab2efccbaa985a685eae ; Godot WebSocket SSL article: https://godotengine.org/article/websocket-ssl-testing-html5-export/
- [S10] HTTPRequest CORS note (docs commit) and forum report: https://git.objectionable.solutions/Sara/behaviour-tree-test/commit/90db42d9dbc645db01912f1c99bd1aeeb3adbd9b ; https://forum.godotengine.org/t/http-requests-always-fail-in-html5/3412
- [S11] WebRTC (latest, version banner): https://docs.godotengine.org/en/latest/tutorials/networking/webrtc.html
- [S12] Exporting for the Web (4.7): https://docs.godotengine.org/en/4.7/tutorials/export/exporting_for_web.html
- [S13] Exporting for the Web (stable, translated mirrors: single-threaded default, audio modes): https://docs.godotengine.org/es/stable/tutorials/export/exporting_for_web.html ; https://docs.godotengine.org/ja/stable/tutorials/export/exporting_for_web.html
- [S14] nakama-godot repository and releases: https://github.com/heroiclabs/nakama-godot ; https://github.com/heroiclabs/nakama-godot/releases
- [S15] Summer Engine, Godot web export guide 2026 (third-party): https://www.summerengine.com/blog/godot-web-export-guide
- [S16] RenderingServer class reference (headless returns dummy values): https://docs.godotengine.org/en/4.2/classes/class_renderingserver.html
- [S17] Godot Q&A, Godot 4 `--headless` cannot render: https://ask.godotengine.org/150510/godot-headless-not-same-godot-window-cant-render-the-backend
- [S18] Exporting for dedicated servers (stable): https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_dedicated_servers.html
- [S19] PocketBase overviews (third-party): https://selfhostyourself.com/services/pocketbase ; https://railway.com/deploy/pocketbase-firebas-1
- [S20] Nakama README/package mirrors and forum: https://beta.pkg.go.dev/github.com/heroiclabs/nakama/v2 ; https://forum.heroiclabs.com/t/questions-about-the-capabilities-of-nakama-open-source/1783
- [S21] Supabase self-hosting with Docker: https://supabase.com/docs/guides/self-hosting/docker
- [S22] itch.io Godot 4 web export walkthrough (2023, third-party): https://foosel.net/til/2023-05-14-how-to-export-a-godot-4-game-to-run-on-the-web-on-itchio/
- [S23] Cloudflare Tunnel WebSocket guides (third-party): https://developersharif.medium.com/reverb-zero-trust-secure-laravel-websockets-with-cloudflare-tunnel-ed70d9964f7c ; https://iq.thc.org/tunnel-via-cloudflare-to-any-tcp-service
- [S24] InfoQ, Oracle free tier limits (July 2026): https://infoq.com/news/2026/07/oracle-cloud-free-tier-limits/ ; https://terminalbytes.com/oracle-cloud-free-tier-changes-2026
- [S25] Oracle community post on A1 allocation change: https://community.oracle.com/customerconnect/discussion/972539/cannot-change-ampere-a1-compute-resource-allocation
- [S26] Over-limit deletion note (third-party, Japanese): https://www.issoh.co.jp/tech/details/17531/
- [S27] GCP free tier summaries (third-party): https://agentdeals.dev/vendor/google-compute-engine ; https://agentdeals.dev/gcp-free-tier-2026
- [S28] GCP billing account note (third-party, Korean): https://tilnote.io/pages/6a5d6bccb6df574798034d9a
- [S29] Free tier comparisons (Render article is a competitor source): https://render.com/articles/platforms-with-a-real-free-tier-for-developers-in-2026 ; https://flaviocopes.com/hosting-free-tiers/
- [S30] Fly.io alternatives (trial terms, third-party): https://developer.puter.com/blog/fly-io-alternatives/
