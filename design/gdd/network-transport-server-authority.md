# Network Transport & Server Authority

> **Status**: Designed 2026-11-03 (pending `/design-review` in a fresh session)
> **Author**: network-programmer (agent draft for user review); inputs from technical-director research note
> **Last Updated**: 2026-11-03
> **Last Verified**: 2026-11-03
> **Creative Director Review (CD-GDD-ALIGN)**: REVISED 2026-11-03 — CONCERNS fixed: unsent shot never shown as taken; same-crew joint claims within tolerance; Pillar 3 line in Player Fantasy; tone words marked provisional; stale draft wording removed; Darkroom ≥ 600 ms develop time made a dependency. NOT ASSESSED: MDA aesthetics target (none stated); tone fit (tone unconfirmed).
> **Implements Pillar**: Pillar 2 "Every photo matters" (a score, a tier and an owned item are real because only the server makes them); supports Pillar 1 "Seeing is the skill" (the moment the player saw is the moment that is judged, despite latency) and the anti-pillar "not pay-to-win" (no client can grant itself results)

## Summary

Network Transport & Server Authority is the contract between the browser client and Aperture's servers: how a client connects (WebSocket over `wss://` for live sessions, HTTPS for the meta service), how every message is versioned and validated (type, range, size, rate), how connections survive drops, and which side owns which value. The server owns inventories, prices, scores, rarity rolls, supply and claim counters; the client only proposes inputs (where it stood, where it pointed the camera, which settings it chose, which moment it saw) and displays what the server decides. Every economy and scoring system relies on this contract.

> **Quick reference** — Layer: `Foundation` · Priority: `MVP` · Key deps: `Rarity Tier Ladder` (identity table and `ladder_version` in the handshake); engine networking (WebSocket, HTTPRequest) · Engine: `docs/engine-reference/godot/modules/networking.md` is ENet-centric and ENet does not work in web exports; web specifics come from `docs/architecture/research-web-networking.md`. Engine claims not sourced in the repo are marked **UNVERIFIED**.

## Overview

Aperture runs as a single-threaded Godot 4.7.2 web export in a browser tab. A browser tab cannot host a server and cannot open raw sockets; it can use HTTP requests, WebSocket (client) and WebRTC (research §3.1). This system defines two channels:

- **Session channel** — a persistent `wss://` connection to an authoritative **session server** (headless Godot, same project as the client). It carries the live world: movement, subject and spirit state, shutter requests and their scored results. In MVP a solo player gets a session of capacity 1; in Alpha, Expedition Rooms reuse the same channel for crews of 2 to 4.
- **Meta channel** — stateless HTTPS requests to the **meta service** (accounts, inventory, wallet, market, gallery, leaderboards). It works when no session is open, so asynchronous features never need a live room.

The system is a rulebook more than a feature. It specifies: the connection lifecycle and handshake (including the Rarity Tier Ladder's `ladder_version` check); the message envelope and validation pipeline; rate limits and a violation score that feeds anti-cheat; heartbeats, timeouts and reconnection with backoff; idempotent requests so a retry never duplicates money, items or rarity rolls; the authority split for every gameplay value; snapshot replication, interpolation and lag compensation for the moment of capture; and the bandwidth and latency budgets these imply. Implementation choices (meta backend product, serialization format, process model, hosting) are described as required behaviour and marked **→ becomes an ADR**.

No project latency target exists in `project.yaml`. This draft designs to the studio default: **the game must feel responsive at up to 150 ms round-trip time (RTT)**. See Decisions to confirm D12.

## Player Fantasy

Players never see this system directly, and when it works they never think about it. What they feel is **trust**:

- **"My score is real."** The number on a photo is the same number everyone else sees, computed the same way. Nobody on the leaderboard edited their own result. When a player beats someone's best shot, the win means something (Pillar 2).
- **"The moment I caught is the moment that counted."** A player on a 150 ms connection who presses the shutter as the spirit turns its head gets the photo of the spirit turning its head, not the frame a quarter-second later (Pillar 1). Lag must never be the reason a decisive moment was missed.
- **"My things are safe."** A camera bought, a photo sold, a trade agreed: these happen once, exactly once, even if the tab crashed mid-click. A dropped connection never eats money or duplicates a lens for someone else.
- **"The market is fair."** Scarce gear is scarce because the server counts it, not because someone found a duplication trick. Prices and supply caps mean what they say.
- **"A hiccup is a hiccup, not a disaster."** When Wi-Fi drops, the game says so calmly, keeps the viewfinder usable, reconnects on its own and puts the player back where they were.

The emotional target is the quiet confidence of a well-run gallery: the walls are straight, the labels are true, and nobody worries about the locks.

For Pillar 3 (*play together*), the same guarantee is shared: when my crewmate sees the spirit, I see it at the same moment, and when we both catch it, we both get the credit.

## Detailed Design

### Core Rules

**A. Channels and topology**

1. **Two channels.** The session channel is a WebSocket connection over TLS (`wss://`). The meta channel is HTTPS request/response. A plain `ws://` or `http://` endpoint is never used outside local development, because an HTTPS page cannot open insecure connections to a non-localhost host (research §3.1, sources S8, S9). The session server's URL is a domain name matching its certificate, not an IP address.
2. **No peer-to-peer.** Clients never talk to each other. All client traffic goes to a server; the server relays nothing a client sent without validating it first. (Godot setting: `SceneMultiplayer.server_relay = false`, for authority reasons, research §2.) WebRTC is deferred (research §3.2) **→ becomes an ADR (research §7.1)**.
3. **Session servers are authoritative simulations.** A session server runs the world simulation for its session (world time, subjects and spirits, player positions) and performs scoring and rarity rolls. The meta service performs all economy writes inside database transactions. Which backend product implements the meta service, and whether one server process hosts one or many sessions, **→ become ADRs (research §7.2, §7.3, §7.8)**.
4. **Privileged service path.** Only session servers may write scored photos, rarity rolls and claims to the meta service, through a service-only path with a server credential. That credential never ships in the client build. A client token presented to a service-only path is rejected with `ERR_AUTH_INVALID` and counted as a violation. Added 2026-11-05: Inventory field-swap writes and field-lease calls also use the service path (Inventory & Loadout Rules 21, 24).
5. **No offline play of authoritative actions.** Without a live session channel there is no shutter, no claim and no rarity roll. The meta channel alone allows browsing, selling and buying (each still server-validated).

**B. Authority split** — who owns each value

6. **The client never reports its own results.** No client message is ever trusted for a score, a score part, a tier, a price, a balance, an item grant, a serial, a supply count, a claim outcome or a roll. If such a field appears in a client message it is ignored, never read, and the mismatch is logged (per Rarity Tier Ladder Edge Cases, "valid but inflated tier").

| Value | Authoritative owner | What the client may send | What the client may do locally |
|---|---|---|---|
| Score and score parts | Session server (Photo Scoring) | nothing | show "developing", then the server result |
| Image tier, capture limits, rarity roll | Session server (Capture Tier Resolution, server RNG) | nothing | show the server result |
| Inventory, loadout, equipped gear | Meta service (Inventory & Loadout) | equip/unequip requests | show the last server state |
| Wallet balance, prices, sales | Meta service (Currency & Wallet, Photo Pricing) | buy/sell requests with a request ID | show "pending" until confirmed; never optimistic |
| Supply counters, serials, first-claim records | Meta service, written by session server or meta transactions | nothing | display only |
| World time, weather, light | Session server clock (World Time, Weather & Light) | nothing | predict from the server clock offset |
| Subject and spirit state (position, pose, phase) | Session server (Subject & Spirit Behaviour) | nothing | interpolate server snapshots |
| Own player position | Client-predicted, server-validated (Rule 22) | position updates with sequence numbers | move immediately; reconcile on correction |
| Camera pose at shutter | Client-proposed, server-validated (Rule 25) | camera position and orientation | everything in the viewfinder |
| Camera settings (focal length, aperture, shutter, ISO, focus) | Client-chosen, server-validated against the equipped gear | the chosen values | everything in the viewfinder |
| Moment of capture (which instant was seen) | Client-claimed, server-clamped (Rule 24) | the session tick it was viewing | — |
| Photo recipe | Session server assembles it | the client-proposed fields above | — |

7. **Recipe assembly.** A photo recipe is built **on the server**. The client proposes only camera pose, camera settings and the viewed tick. The server fills in, from its own state: player ID, gear IDs (from the server loadout), world time and weather at the clamped capture tick, subject IDs and poses (from its history buffer at that tick), `recipe_version`, and a server timestamp. The Photo Recipe & Re-render GDD owns the schema; this system owns this split.
8. **Recomputation of tiers.** Every gameplay-relevant tier (image tier, capture limits) is recomputed by the server from its own data and the recipe, never taken from the client (Rarity Tier Ladder Core Rule 10).

**C. Message envelope and versioning**

9. **Every message is versioned.** Each session-channel message carries an envelope: `pv` (protocol version, integer), `type` (message type ID from a closed list), `seq` (per-direction sequence number, unsigned 32-bit, starting at 1 and increasing by exactly 1), and `body`. State-changing requests also carry `rid` (a client-generated request ID, 128 random bits). Meta-channel requests carry `pv` and, when state-changing, `rid` in the request. The serialization format (Godot RPC arguments, JSON, or a packed binary layout) **→ becomes an ADR (research §7.11)**.
10. **Closed message list.** Each message type has a fixed direction (client→server or server→client), a size cap, a rate class and a field schema. The initial list:

| Type | Direction | Rate class | Purpose |
|---|---|---|---|
| `HELLO` | C→S | control | Handshake: versions, ticket, optional resume token |
| `HELLO_ACK` / `REJECT` | S→C | — | Handshake result; session config; ladder table when versions differ |
| `PING` / `PONG` | both | control | Heartbeat and RTT measurement |
| `MOVE` | C→S | movement | Own position and facing, with `seq` |
| `CORRECTION` | S→C | — | Authoritative position plus last accepted `seq` |
| `SNAPSHOT` | S→C | — | Transforms and states of players and subjects at a tick |
| `EVENT` | S→C | — | Reliable world events (subject spawn/despawn, phase change, claim made) |
| `SHUTTER` | C→S | shutter | Camera pose, settings, viewed tick, `rid` |
| `SHUTTER_RESULT` | S→C | — | Server-assembled recipe summary, score, tier, `rid`; or a reason it was refused |
| `INTERACT` | C→S | interact | Other in-world requests (place a found photo, assist), `rid` |
| `RESULT_QUERY` | C→S | control | After a reconnect: "what happened to request `rid`?" |
| `ERROR` | S→C | — | Error code, offending `seq`/`rid`, optional field name |
| `NOTICE` | S→C | — | Server notices: shutting down in N s, service degraded, throttled |
| `BYE` | both | — | Intentional close with a reason |

11. **Protocol compatibility window.** The server accepts a client whose `pv` lies in `[PROTOCOL_MIN_SUPPORTED, PROTOCOL_CURRENT]`. MVP recommendation: both equal (exact match), because client and server ship from one project in lockstep (research §7.7). A client outside the window is rejected with `ERR_VERSION_MISMATCH` and told to reload (UI Requirements).
12. **Content lockstep.** `HELLO` carries `content_version`, a hash of the scene and data content that scoring reads. A mismatch is a hard reject with `ERR_VERSION_MISMATCH`, because a client looking at different content than the server scores would be judged unfairly (research §8 risk 1).
13. **Ladder version (honours Rarity Tier Ladder Core Rule 10 and its Edge Cases).** `HELLO` carries the client's `ladder_version`. The server compares it with its authoritative identity table:
    - Equal: proceed.
    - Different: **the server's table wins**. The server still accepts the connection (this check is soft, unlike Rules 11 and 12), includes its identity table and `ladder_version` in `HELLO_ACK`, and flags `update_available`. The client shows the update prompt, and until it reloads, any tier ID it cannot parse is displayed as the neutral "?" badge with no colour, no blades and no comparison. Gameplay is unaffected because the server recomputes every gameplay tier (Rule 8).
14. **Unknown fields and types.** In a known message type, a field not in the schema is ignored and logged once per session (forward compatibility). An unknown message `type` is rejected with `ERR_MALFORMED` and adds a violation (Formulas F2).

**D. Validation pipeline** — applied in this order to every inbound message, on both channels; the first failure stops processing

15. **Size.** The frame's byte length is checked against the hard cap and the per-type cap (F3). Over the hard cap: the connection is closed with `ERR_OVERSIZE` without parsing. Over the type cap: rejected with `ERR_OVERSIZE`.
16. **Rate.** The message's rate class bucket is charged (F1). An empty bucket drops the message with `ERR_RATE_LIMITED`.
17. **State.** The message must be allowed in the peer's current state (States and Transitions). For example `SHUTTER` before `HELLO_ACK` is rejected with `ERR_NOT_ALLOWED`.
18. **Envelope.** `pv` matches the negotiated version; `seq` equals last `seq` + 1 (a gap or repeat is `ERR_MALFORMED`; over TCP neither happens legitimately).
19. **Schema and types.** Each field has the declared type. Numbers must be finite (NaN and infinity rejected). Strings must be valid UTF-8 and within their length cap. Arrays and dictionaries must be within their count cap and nesting depth ≤ 4. Object decoding is disabled (Godot setting believed to be `SceneMultiplayer.allow_object_decoding = false`; **UNVERIFIED** in 4.7).
20. **Range and identity.** Every numeric field is within its declared range (ranges for camera settings come from the equipped gear in Gear Catalog; world bounds from the scene). **Every tier ID from the network is re-parsed with the ladder's `parse`; `ERR_UNKNOWN` (or `ERR_UNSET` where a tier is required) rejects the message with that code and the field name, and each such rejection adds the invalid-tier violation weight (F2).** No unknown ID is ever coerced to a tier.
21. **Idempotency.** For messages with `rid`, a `rid` already processed for this account returns the stored result without re-executing (F9). The same `rid` with a different body is `ERR_IDEMPOTENCY_CONFLICT`.

Only after all seven checks does the owning gameplay system see the message. A rejected message changes no game state.

**E. Movement, moment and camera validation**

22. **Movement is client-predicted, server-validated.** The client moves its own photographer immediately and sends `MOVE` at `MOVE_SEND_HZ`. The server accepts a new position only if the distance from the last accepted position fits the movement allowance (F10), the segment does not pass through blocking collision (one shape cast per accepted `MOVE`), and the position lies inside the zone's walkable bounds. A failed check sends `CORRECTION` (last accepted position and `seq`); the client resets to it and **re-applies its unacknowledged inputs** after that `seq` (F11). Speeds and collision shapes are owned by Player Movement & Exploration. Fully server-simulated movement is the alternative (Decisions to confirm D2).
23. **Snapshots.** The server sends `SNAPSHOT` at `SNAPSHOT_HZ` with the transforms and states of every relevant entity (all entities in a session of ≤ 4 players; a relevancy radius applies only to a future shared hub). The client renders remote entities at a fixed interpolation delay behind the newest snapshot (F7). Because WebSocket runs over TCP, nothing is dropped in transit; the server therefore **coalesces**: if a client's outbound queue still holds an unsent snapshot, the new snapshot replaces it rather than queueing behind it. How `WebSocketMultiplayerPeer` treats the `unreliable` transfer mode is **NOT SOURCEABLE** (research §2); this rule assumes everything is reliable and ordered.
24. **Lag-compensated moment.** `SHUTTER` carries `view_tick`, the session tick (with fraction) the client was rendering for subjects at the instant of the press. The server checks it against its own estimate (F8): inside tolerance, the claim is used; outside tolerance, the server clamps to its estimate and logs. The capture is then evaluated against the subject and world state **at that tick**, read from a history buffer (F9b). Rewind never exceeds `MAX_REWIND_MS`. The player's own camera pose is taken at the moment of the press (it is local and already in the message).
25. **Camera pose plausibility.** The camera position in `SHUTTER` must be within `CAMERA_REACH_M` of the server's accepted player position at the capture tick, and the camera settings must lie within the ranges of the equipped body and lens as the **server** knows them (focal length within the lens range, aperture no wider than the lens maximum, ISO and shutter within the body range). A failure rejects the shot with `ERR_OUT_OF_RANGE`; the shot is not consumed and nothing is rolled. Decided 2026-11-05: the reach check compares the camera position against the player position **plus the eye offset for the current stance**, so a standing eye 1.60 m above the foot passes. Automatic settings are server-derived (Camera Model Rule 31) and the settings check is Camera Model's `validate_settings`.
26. **Shutter rate follows the gear.** The shutter bucket's refill rate is derived from the equipped body's burst rate (F1b), so a camera with a fast burst can shoot faster, and no client can exceed the gear it actually owns. Shot count and battery are owned by Camera Model; this rule only limits message rate.

**F. Reliability and economy integrity**

27. **Idempotent state changes.** Every state-changing request (shutter, interact, buy, sell, equip, trade confirm) carries a `rid`. The server records the outcome under (`account_id`, `rid`) for `IDEMPOTENCY_WINDOW_S`. A retry returns the recorded outcome. Rarity rolls are recorded with their `rid` **before** the result is sent, so a disconnect, reload or retry can never reroll.
28. **A started request finishes.** Once a `SHUTTER` passes validation, the server completes scoring, rolling and persistence even if the client disconnects. The client learns the outcome on resume via `RESULT_QUERY`. Closing the tab after seeing a bad result changes nothing.
29. **Persistence before ownership.** A photo, item or balance change exists only after the meta service commits it. The session server sends `SHUTTER_RESULT` with `saved: true` after commit. If the commit is delayed, the result is sent with `saved: false`, and the server retries the write from an outbox (same `rid`, so the meta service de-duplicates). The client shows "saving" until `saved: true` arrives (UI Requirements). Decided 2026-11-04: a `saved: false` message is an acknowledgement only. It carries **no score, tier or roll outcome**; the client shows "developing", and the result is revealed only with `saved: true` after commit. Added 2026-11-05: `SHUTTER_RESULT` carries `frames_left`, and a refused shot may carry the reason `no_frames`. Money responses carry `balance_after` and `entry_id`. The error list adds `ERR_WALLET_FULL`, and an invalid item reference adds a `W_INVALID_ITEM` violation weight.
30. **Economy is never optimistic.** The client never shows a new balance, item or sale until the server confirms it. It shows a pending state within 100 ms of the click instead (Game Feel).
31. **Server randomness only.** Rarity rolls and any other gameplay randomness come from the server's random source. The client never receives a seed or a pre-roll. RNG source and audit log **→ become an ADR (research §7.10)**.

**G. Authentication and tickets**

32. **Login on the meta channel.** The player signs in through the meta service and receives a session token. Token lifetime and refresh are owned by Accounts & Server Persistence.
33. **Session ticket.** To open a session, the client asks the meta service, which returns a session URL and a **single-use ticket** valid for `TICKET_TTL_S`. The ticket goes in the `HELLO` body, not in a WebSocket header, because custom handshake headers are not supported in web exports (research §3.1, S7). It must not appear in the URL query string either, because URLs end up in proxy logs. (Godot hook: `SceneMultiplayer.auth_callback`, which the repo reference documents; research §2.)
34. **Resume token.** `HELLO_ACK` includes a resume token bound to the account and session, valid for `RECONNECT_GRACE_S`. A `HELLO` with a valid resume token reclaims the reserved seat and the player's state without a new ticket.
35. **One live session per account.** A second successful `HELLO` for an account that already has a live session closes the older connection with `ERR_SIGNED_IN_ELSEWHERE` (newest wins; Decisions to confirm D7). In-flight requests of the older connection still complete (Rule 28).

**H. Anomaly handling and logging**

36. **Violation score.** Every rejected message adds a weight to the peer's violation score, which decays over time (F2). Crossing `THROTTLE_THRESHOLD` halves all the peer's bucket rates for `THROTTLE_DURATION_S` and sends `NOTICE throttled`. Crossing `KICK_THRESHOLD` closes the connection with `ERR_KICKED`. `KICKS_TO_FLAG` kicks within 24 hours flag the account for Moderation & Reporting. Thresholds are high enough that a normal client, including one on a bad connection, never reaches them (Edge Cases).
37. **Rate-limited logs.** Anomaly logging is itself rate-limited per peer and per anomaly kind (F1 with log parameters). Suppressed entries are summarised as a count once per `LOG_SUMMARY_INTERVAL_S`. Every log line carries session ID, account ID, peer state, message type, `seq`/`rid` and error code; never a ticket, token or password.
38. **Server notices.** Before a planned shutdown or deploy, the server sends `NOTICE shutting_down` with seconds remaining, stops accepting new `SHUTTER` and `INTERACT` requests `SHUTDOWN_DRAIN_S` before the end, and completes in-flight requests.

### States and Transitions

**Client connection states (session channel)**

| State | Meaning | Entered when | Leaves to | Shutter allowed? |
|---|---|---|---|---|
| `Offline` | No session; meta channel may still work | Start, `BYE`, after `Failed` acknowledged | `Ticketing` | No |
| `Ticketing` | Asking the meta service for URL and ticket | Player starts or resumes play | `Connecting`; `Failed` on meta error | No |
| `Connecting` | WebSocket and TLS opening | Ticket received, or a reconnect attempt starts | `Handshaking`; `Reconnecting` on failure | No |
| `Handshaking` | `HELLO` sent, awaiting `HELLO_ACK` | Socket open | `Synced`; `Rejected` on `REJECT`; `Reconnecting` on timeout (`HANDSHAKE_TIMEOUT_S`) | No |
| `Synced` | First snapshot received; normal play | `HELLO_ACK` then first `SNAPSHOT` | `Stalled`; `Closing`; `Rejected` (kick, signed in elsewhere) | Yes |
| `Stalled` | Socket open but nothing received for `STALL_TIMEOUT_S` | Silence | `Synced` when traffic resumes; `Reconnecting` after `DROP_TIMEOUT_S` | No (viewfinder stays live) |
| `Reconnecting` | Waiting out backoff, then retrying (F5) | Socket closed unexpectedly, handshake timeout, drop timeout | `Connecting` (resume token if within grace, else new ticket via `Ticketing`); `Failed` after `RECONNECT_MAX_ATTEMPTS` | No |
| `Rejected` | Server refused or removed the client | `REJECT` / `ERROR` with a terminal code | `Offline` after the player acts (reload, sign in, dismiss) | No |
| `Failed` | Automatic reconnection gave up | Attempts exhausted | `Ticketing` when the player presses Retry | No |
| `Closing` | Intentional leave | Player quits, server `BYE` | `Offline` | No |

Terminal codes (no automatic retry): `ERR_VERSION_MISMATCH`, `ERR_AUTH_INVALID`, `ERR_KICKED`, `ERR_SIGNED_IN_ELSEWHERE`, `ERR_BANNED`. Retryable codes: `ERR_SERVER_BUSY`, `ERR_SERVICE_DEGRADED`, `ERR_SHUTTING_DOWN`, `ERR_SESSION_FULL` (retry via a new ticket), `ERR_AUTH_EXPIRED` (refresh token, then retry).

**Server-side peer states**

| State | Meaning | Entered when | Leaves to |
|---|---|---|---|
| `Pending` | Socket open, no valid `HELLO` yet; accepts only `HELLO` | Connection accepted | `Active` on a valid `HELLO`; closed after `HANDSHAKE_TIMEOUT_S` or on any other message |
| `Active` | Authenticated player in the session | `HELLO` passed all checks | `Throttled`; `Grace` on disconnect; closed on kick or `BYE` |
| `Throttled` | `Active` with halved rates | Violation score ≥ `THROTTLE_THRESHOLD` | `Active` after `THROTTLE_DURATION_S` with the score below threshold; closed at `KICK_THRESHOLD` |
| `Grace` | Disconnected; seat and state reserved; in-flight requests still finishing | Socket closed or `DROP_TIMEOUT_S` silence | `Active` on a valid resume; `Released` after `RECONNECT_GRACE_S` |
| `Released` | Seat freed; player entity removed from the session | Grace expired, `BYE`, kick | — |

**Session lifecycle** (detail owned by Expedition Rooms for crews): `Starting` → `Open` (accepts joins up to capacity) → `Draining` (shutdown notice; no new shutter/interact) → `Closed`. A solo MVP session closes when its only player is `Released`.

### Interactions with Other Systems

| System | This system provides | This system receives | Contract notes |
|---|---|---|---|
| **Rarity Tier Ladder** | Version-mismatch handling and the update prompt | Identity table and `ladder_version` | `ladder_version` is carried in `HELLO` and checked (Rule 13; server table wins, soft accept, "?" badge until reload). Every tier ID from the network is re-parsed; unknown IDs are rejected with `ERR_UNKNOWN` and never coerced (Rule 20). Repeated invalid IDs count toward the violation score and rate-limit path (F2, weight `W_INVALID_TIER`). All gameplay tiers are recomputed by the server (Rule 8). The display table is never sent by the server. |
| **Accounts & Server Persistence** | Ticket/resume semantics; service-only write path; idempotency requirement | Session tokens, ticket issue and verification, account IDs, persistence commits | Token lifetime and storage are owned there. Meta service rejects client tokens on service paths. |
| **Photo Recipe & Re-render** | Recipe assembly split (Rule 7); size cap for `SHUTTER` | Recipe schema and `recipe_version` | The server fills every authoritative field; the client proposes only pose, settings and `view_tick`. |
| **Photo Scoring** | Validated, assembled recipes; scoring queue with a time budget | Score and parts | Scoring runs only on the server. Its time per recipe feeds F12 (queue budget). |
| **Capture Tier Resolution** | Server RNG; `rid`-keyed roll record (Rule 27) | Final image tier | A roll is recorded before it is sent and never repeated for the same `rid`. |
| **World Time, Weather & Light** | Authoritative server clock and tick; clock offset for clients (F6) | World state at a tick | The capture uses world state at the clamped capture tick. |
| **Subject & Spirit Behaviour** | Snapshot and event replication; history buffer for rewind (F9b) | Subject states per tick | Subjects are simulated on the server only. |
| **Player Movement & Exploration** | Allowance validation, correction and reconciliation (Rule 22, F10, F11) | Max speeds, collision shapes, walkable bounds | Movement constants live there; tolerances live here. |
| **Camera Model: Viewfinder & Exposure** | Settings validation against server-known gear (Rule 25) | Which settings are sent at shutter | The viewfinder never waits on the network. |
| **Gear Catalog & Specs** | — | Setting ranges per body and lens; burst rate per body (F1b) | Ranges are data; this system enforces them. |
| **Inventory & Loadout** | Idempotent equip requests | Server loadout at capture time | The loadout in the recipe comes from the server, never the client. |
| **Currency & Wallet, Photo Pricing & NPC Clients, Gear Shop** | Idempotent, non-optimistic request rules (Rules 27, 30) | Transaction outcomes | All economy writes are meta-service transactions. |
| **Gallery** | `saved` flag semantics (Rule 29) | Photo records | A photo exists only after commit. |
| **Expedition Rooms** (Alpha) | Session channel, seats, grace, session states | Room capacity, room lifecycle, matchmaking | Process model **→ ADR (research §7.8)**. |
| **Supply Caps & Gear Serials** (Alpha) | Authority rule: counters and serials are server-only, atomic, idempotent | — | No client message can carry a count or serial that is trusted. |
| **First-Claim & Image Serials** (Alpha) | Claim ordering by lag-compensated capture tick (F8), ties by server receive order | Claim scope and rewards | Ordering rule is Decisions to confirm D11. |
| **Found Photos** (VS) | `INTERACT` validation (position, rate, size) | Placement rules | Placement position is validated like a camera pose. |
| **Leaderboards, Gallery browsing** | Meta-channel rate limits | Read endpoints | Read-only; never via the session channel. |
| **Player-to-Player Trading & Market** (Alpha) | Idempotency and two-sided confirmation transport | Trade rules | Both confirmations are separate `rid`s; the trade commits atomically in the meta service. |
| **Moderation & Reporting** (Alpha) | Account flags from repeated kicks (Rule 36) | Ban list (`ERR_BANNED`) | Flags are evidence for review, not automatic bans. |
| **Economy Telemetry** (Alpha) | Anomaly counts, rate-limit hits | — | Aggregates only. |
| **Viewfinder HUD, Darkroom & Gallery UI, Shop UI, Settings** | Connection state, latency tier, pending/saving states | — | See UI Requirements. |

## Formulas

All constants named here are tuning knobs (see Tuning Knobs) held in a network configuration resource, not in code. Its path and format **→ become part of the ADR on message protocol (research §7.11)**.

### F1. Token bucket rate limit

The token_bucket formula is defined as:

`tokens_now = min(BURST_c, tokens_prev + RATE_c × (t_now − t_prev))`; the message is accepted if `tokens_now ≥ COST_m`, then `tokens_after = tokens_now − COST_m`; otherwise it is rejected and `tokens_after = tokens_now`.

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| c | enum | {control, movement, shutter, interact, meta_read, meta_write, connect_ip, log} | message type table (Rule 10) | Rate class of the message |
| RATE_c | float (tokens/s) | 0.1–60 | config | Refill rate for class c (shutter: F1b) |
| BURST_c | float (tokens) | 1–60 | config | Bucket capacity; the largest instantaneous burst |
| COST_m | float (tokens) | 1–5 | config (default 1) | Tokens a message costs; heavier requests may cost more |
| tokens_prev | float | 0–BURST_c | calculated (per peer, per class) | Bucket level after the previous check; starts full |
| t_now, t_prev | float (s) | ≥ 0 | server monotonic clock | Time of this and the previous check |
| throttle_mult | float | {1.0, 0.5} | calculated (Rule 36) | Multiplies RATE_c while `Throttled` |

**Output Range:** accepted or rejected; `tokens_after` in `[0, BURST_c]`. Never negative.

**Default classes (per connection unless noted):**
| Class | RATE_c | BURST_c | Basis |
|---|---|---|---|
| control (PING, RESULT_QUERY) | 4 /s | 8 | Heartbeat at 0.5 Hz plus resume queries |
| movement (MOVE) | 20 /s | 30 | `MOVE_SEND_HZ` 15 plus 33 % slack for frame jitter |
| shutter (SHUTTER) | F1b | `SHUTTER_BURST` 5 | Follows the gear |
| interact (INTERACT) | 2 /s | 6 | Infrequent world actions |
| meta_read (per account) | 5 /s | 15 | Gallery and leaderboard browsing pages |
| meta_write (per account) | 1 /s | 5 | Buy, sell, equip, trade confirm |
| connect_ip (per source address) | 10 /min | 10 | New sessions and logins; see Edge Cases for proxies |
| log (per peer, per anomaly kind) | 0.5 /s | 5 | Rule 37 |

**Example:** movement bucket, BURST 30, RATE 20/s. A TCP stall delivers 30 queued `MOVE`s at once: all 30 are accepted (bucket 30 → 0). A 31st arriving 10 ms later finds `tokens_now = min(30, 0 + 20 × 0.01) = 0.2 < 1` and is rejected with `ERR_RATE_LIMITED` (+1 violation). 50 ms later the bucket holds 1.2 and accepts again.

### F1b. Shutter refill rate from gear

The shutter_rate formula is defined as:

`RATE_shutter = min(SHUTTER_RATE_CAP, max(SHUTTER_RATE_FLOOR, burst_fps × SHUTTER_SLACK))`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| burst_fps | float (frames/s) | 0.5–20 | Gear Catalog (equipped body, as the server knows it) | The body's continuous shooting rate |
| SHUTTER_SLACK | float | 1.0–1.5 | config (default 1.25) | Headroom for timing jitter |
| SHUTTER_RATE_FLOOR | float (/s) | 0.5–3 | config (default 1) | Minimum so single-shot bodies are not starved |
| SHUTTER_RATE_CAP | float (/s) | 2–15 | config (default 10) | Hard server ceiling regardless of gear (scoring cost, F12) |

**Output Range:** `SHUTTER_RATE_FLOOR` to `SHUTTER_RATE_CAP` per second.
**Example:** a phone with `burst_fps = 3` → `min(10, max(1, 3.75)) = 3.75/s`. A sports body with `burst_fps = 12` → `min(10, 15) = 10/s`.

### F2. Violation score

The violation_score formula is defined as:

`V_now = V_prev × 2^(−(t_now − t_prev) / V_HALF_LIFE_S) + W_k`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| V_prev | float | ≥ 0 | calculated (per peer; per account across reconnects within grace) | Score after the previous violation |
| t_now − t_prev | float (s) | ≥ 0 | server monotonic clock | Time since the previous violation |
| V_HALF_LIFE_S | float (s) | 10–600 | config (default 60) | Time for the score to halve |
| W_k | float | 0–30 | config, by kind k | Weight of this violation kind |

**Default weights:**
| Kind k | W_k | Rationale |
|---|---|---|
| `ERR_RATE_LIMITED` (per dropped message) | 1 | Can happen to honest clients after a stall |
| Movement allowance exceeded (`CORRECTION` sent) | 2 | Honest clients rarely trigger it; F10 already has slack |
| `view_tick` outside tolerance (clamped, not rejected) | 0.5 | Clock noise is plausible |
| `ERR_OUT_OF_RANGE` | 3 | Honest clients validate locally first |
| `ERR_UNKNOWN` / `ERR_UNSET` on a tier field (`W_INVALID_TIER`) | 3 | Honest clients only send IDs the server gave them (Rarity Tier Ladder Edge Cases) |
| `ERR_MALFORMED`, `ERR_NOT_ALLOWED`, unknown type | 5 | Never produced by a correct client |
| `ERR_IDEMPOTENCY_CONFLICT` | 5 | Same `rid`, different body: replay tampering |
| `ERR_OVERSIZE` (under the hard cap) | 10 | Deliberate payload stuffing |
| Client token on a service-only path | 30 | Immediate kick |

**Output Range:** `V ≥ 0`; actions at `THROTTLE_THRESHOLD` (default 10) and `KICK_THRESHOLD` (default 30).
**Example:** a tampered client sends "sss" as a gallery filter tier 10 times, 1 s apart. Each adds 3 and decay per second is ×0.9885. After the 4th: ≈ 11.8 → `Throttled`. After the 10th: ≈ 28.5. An 11th 1 s later: 28.5 × 0.9885 + 3 ≈ 31.2 → kicked with `ERR_KICKED`. An honest client that hits the rate limit 5 times during a stall scores 5 and decays below 1 within about 4 minutes.

### F3. Message size check

The size_check formula is defined as:

`accept_size = (frame_bytes ≤ HARD_FRAME_CAP) AND (frame_bytes ≤ CAP_type)`; if `frame_bytes > HARD_FRAME_CAP` the connection closes.

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| frame_bytes | int (bytes) | ≥ 0 | measured (WebSocket payload length, before parsing) | Size of one inbound message |
| HARD_FRAME_CAP | int (bytes) | 1024–16384 | config (default 4096) | Absolute limit; also sets the transport's inbound buffer where the engine allows it (believed `WebSocketMultiplayerPeer.inbound_buffer_size`; **UNVERIFIED** in 4.7) |
| CAP_type | int (bytes) | 16–HARD_FRAME_CAP | config, by type | Per-type limit |

**Default per-type caps (client→server):** `HELLO` 1024 · `PING` 32 · `MOVE` 64 · `SHUTTER` 512 (research §5.4 recipe budget; the client-proposed part is smaller) · `INTERACT` 256 · `RESULT_QUERY` 64 · `BYE` 64. **Server→client budgets** (server self-check, logged if exceeded): `SNAPSHOT` 1200 · `HELLO_ACK` 2048 (includes the ladder identity table when versions differ) · `SHUTTER_RESULT` 1024 · `EVENT` 512.

**Output Range:** accept, reject (`ERR_OVERSIZE`), or close.
**Example:** a 700-byte `SHUTTER` → 700 ≤ 4096 but 700 > 512 → rejected with `ERR_OVERSIZE`, +10 violation, no scoring. A 20 000-byte frame → closed before parsing.

### F4. Heartbeat and timeouts

The liveness formula is defined as:

`silence = t_now − t_last_inbound`; state = `Synced` if `silence < STALL_TIMEOUT_S`; `Stalled` if `STALL_TIMEOUT_S ≤ silence < DROP_TIMEOUT_S`; disconnected (client `Reconnecting`, server `Grace`) if `silence ≥ DROP_TIMEOUT_S`.

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| t_last_inbound | float (s) | ≥ 0 | measured | Last time any message arrived from the other side |
| PING_INTERVAL_S | float (s) | 1–5 | config (default 2) | Each side sends `PING` if it has sent nothing for this long |
| STALL_TIMEOUT_S | float (s) | 2 × PING_INTERVAL_S – 10 | config (default 6) | Silence before the "connection unstable" state |
| DROP_TIMEOUT_S | float (s) | STALL_TIMEOUT_S + 3 – 30 | config (default 15) | Silence before treating the connection as lost |
| HANDSHAKE_TIMEOUT_S | float (s) | 2–15 | config (default 5) | Time from socket open to `HELLO` (server) or to `HELLO_ACK` (client) |

**Output Range:** one of three states. Constraint: `PING_INTERVAL_S × 2 < STALL_TIMEOUT_S < DROP_TIMEOUT_S`, so one lost interval never trips a stall.
**Example:** last inbound at t = 100.0 s. At 104 s: Synced. At 106.5 s: Stalled ("Connection unstable", shutter paused). At 115.0 s: client enters `Reconnecting`, server moves the peer to `Grace`.

### F5. Reconnect backoff

The reconnect_delay formula is defined as:

`delay(n) = min(BACKOFF_CAP_S, BACKOFF_BASE_S × 2^(n − 1)) × (1 + BACKOFF_JITTER × u)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| n | int | 1–RECONNECT_MAX_ATTEMPTS | calculated | Attempt number since the connection was lost |
| BACKOFF_BASE_S | float (s) | 0.25–3 | config (default 1) | First delay |
| BACKOFF_CAP_S | float (s) | 5–120 | config (default 30) | Longest delay |
| BACKOFF_JITTER | float | 0–0.5 | config (default 0.25) | Spread so many clients do not retry in lockstep after a server restart |
| u | float | −1 to +1 | random, uniform, client-side | Jitter sample (client-side randomness is fine here; it decides nothing in the game) |
| RECONNECT_MAX_ATTEMPTS | int | 3–20 | config (default 8) | Attempts before `Failed` |

**Output Range:** `BACKOFF_BASE_S × (1 − BACKOFF_JITTER)` to `BACKOFF_CAP_S × (1 + BACKOFF_JITTER)`; defaults 0.75 s to 37.5 s.
**Example (u = 0):** delays 1, 2, 4, 8, 16, 30, 30, 30 s → about 121 s in total. Attempts 1–5 start within the 60 s `RECONNECT_GRACE_S` and resume with the resume token; attempts 6–8 fall outside it and rejoin with a new ticket (Edge Cases).

### F6. RTT and clock estimate

The rtt_estimate formula is defined as:

`rtt_est = (1 − RTT_ALPHA) × rtt_est + RTT_ALPHA × sample`; `rtt_var = (1 − RTT_BETA) × rtt_var + RTT_BETA × |sample − rtt_est|`; `clock_offset = t_server_in_pong − (t_send + sample / 2)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| sample | float (ms) | 0–10000 | measured (PING sent → PONG received) | One RTT measurement |
| RTT_ALPHA | float | 0.05–0.5 | config (default 0.125) | Smoothing for the mean (classic TCP value) |
| RTT_BETA | float | 0.1–0.5 | config (default 0.25) | Smoothing for the variation |
| rtt_est | float (ms) | 0–10000 | calculated; first value = first sample | Smoothed RTT; drives F7, F8 and the latency indicator |
| rtt_var | float (ms) | 0–5000 | calculated; first value = sample / 2 | Smoothed variation (jitter) |
| t_send | float (ms) | ≥ 0 | client clock | When the PING left the client |
| t_server_in_pong | float (ms) | ≥ 0 | server clock (in PONG) | Server time when it answered |

**Output Range:** `rtt_est` and `rtt_var` ≥ 0; `clock_offset` any sign. The server keeps its own `rtt_est` per peer from its PINGs; that server-side value, not the client's, is used in F8.
**Example:** `rtt_est = 140`, `rtt_var = 20`, new sample 180 → `rtt_est = 0.875 × 140 + 0.125 × 180 = 145`; `rtt_var = 0.75 × 20 + 0.25 × |180 − 145| = 23.75`.

### F7. Interpolation delay

The interp_delay formula is defined as:

`interp_delay_ms = (1000 / SNAPSHOT_HZ) × INTERP_BUFFER_SNAPSHOTS + min(JITTER_MARGIN_CAP_MS, 2 × rtt_var)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| SNAPSHOT_HZ | float (Hz) | 5–20 | config (default 10) | Server snapshot rate (research §5.4: 10–15 Hz) |
| INTERP_BUFFER_SNAPSHOTS | float | 1.5–3 | config (default 2) | How many snapshot intervals the client stays behind |
| rtt_var | float (ms) | 0–5000 | F6 (client) | Measured jitter |
| JITTER_MARGIN_CAP_MS | float (ms) | 0–200 | config (default 100) | Upper bound on the added margin |

**Output Range:** 150–400 ms with the safe ranges; defaults give 200–300 ms. The client changes the delay gradually (at most ±10 ms per second) so remote motion never visibly jumps.
**Example:** 10 Hz, buffer 2, `rtt_var = 20` → `100 × 2 + min(100, 40) = 240 ms`.

### F8. Lag-compensated capture tick

The capture_tick formula is defined as:

`expected_tick = recv_tick − ((rtt_est_server / 2) + interp_delay_ms) × TICK_HZ / 1000`; `capture_tick = view_tick` if `|view_tick − expected_tick| ≤ VIEW_TOLERANCE_MS × TICK_HZ / 1000`, else `expected_tick`; then `capture_tick = clamp(capture_tick, recv_tick − MAX_REWIND_MS × TICK_HZ / 1000, recv_tick)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| recv_tick | float (ticks) | ≥ 0 | server | Session tick when `SHUTTER` passed validation |
| view_tick | float (ticks) | ≥ 0 | client (`SHUTTER` field) | Tick the client says it was rendering for subjects |
| rtt_est_server | float (ms) | 0–10000 | F6 (server's estimate for this peer) | Server-measured RTT |
| interp_delay_ms | float (ms) | 150–400 | F7, reported by the client in `MOVE` and bounded by the server to the F7 range | Client's current interpolation delay |
| TICK_HZ | float (Hz) | 20–60 | config (default 30) | Server simulation tick rate |
| VIEW_TOLERANCE_MS | float (ms) | 20–150 | config (default 60) | Allowed disagreement between claim and estimate |
| MAX_REWIND_MS | float (ms) | 200–600 | config (default 400) | Largest rewind ever applied |

**Output Range:** `capture_tick` in `[recv_tick − MAX_REWIND_MS × TICK_HZ / 1000, recv_tick]`.
**Rationale:** a client can only choose a moment within ±60 ms of what the server already believes it was seeing, so it cannot "pick the best frame" from a wide window (security compromise for security-engineer review), while an honest player at 150 ms RTT is judged on what was on screen.
**Example:** `recv_tick = 9000`, RTT 150 ms, interp 240 ms, 30 Hz → `expected_tick = 9000 − (75 + 240) × 0.03 = 8990.55`. The client claims 8991.2: |0.65| ≤ 1.8 → `capture_tick = 8991.2`. A claim of 8985.0 (−5.55 ticks) is clamped to 8990.55 and +0.5 violation. Rewind floor: 9000 − 12 = 8988; both results are above it.

### F9. Idempotency store and history buffer

The idempotency_store formula is defined as:

`store_entries ≈ Σ over active accounts of (requests per second × IDEMPOTENCY_WINDOW_S)`; and the history buffer is `history_len = ceil(MAX_REWIND_MS × TICK_HZ / 1000) + 2` (F9b)

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| IDEMPOTENCY_WINDOW_S | int (s) | 60–86400 | config (default 600) | How long a `rid` outcome is kept and returned on retry |
| requests per second | float | 0–RATE_c sum | measured | State-changing requests per account |
| MAX_REWIND_MS, TICK_HZ | — | see F8 | config | — |
| history_len | int (ticks) | 6–40 | calculated | Ticks of subject and player state kept per session |

**Output Range:** `history_len` = 14 with defaults. Store size is an ops figure to measure; at the default shutter cap a single account produces at most 6 000 entries per window (10/s × 600 s), typically far fewer.
**Example:** 400 ms × 30 Hz / 1000 = 12 → `history_len = 14` (two spare ticks so interpolation at the oldest tick has a neighbour).

### F10. Movement allowance

The movement_allowance formula is defined as:

`A_now = min(A_CAP, A_prev + V_MAX × (1 + SPEED_TOLERANCE) × (t_now − t_prev))`, where `A_CAP = V_MAX × (1 + SPEED_TOLERANCE) × ALLOWANCE_WINDOW_S + POSITION_SLACK_M`; a `MOVE` of horizontal distance `d` is accepted if `d ≤ A_now`, then `A_after = A_now − d`.

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| V_MAX | float (m/s) | > 0 | Player Movement & Exploration (fastest legal movement mode) | Top legal speed |
| SPEED_TOLERANCE | float | 0.05–0.5 | config (default 0.15) | Headroom for client frame timing |
| ALLOWANCE_WINDOW_S | float (s) | 0.5–3 | config (default 1.0) | How much stored allowance a TCP burst may spend at once |
| POSITION_SLACK_M | float (m) | 0–1 | config (default 0.25) | Fixed slack for float and collision differences |
| d | float (m) | ≥ 0 | calculated (accepted position → new position) | Distance claimed by this `MOVE` |
| t_now − t_prev | float (s) | ≥ 0 | server clock (receipt times) | Time since the previous allowance update |

Vertical movement (slopes, stairs, any jump) is validated against Player Movement's rules once that GDD exists (Open Questions).

**Output Range:** accept or `CORRECTION`; `A` stays in `[0, A_CAP]`.
**Example (placeholder `V_MAX = 4 m/s`, owned by Player Movement):** `A_CAP = 4 × 1.15 × 1.0 + 0.25 = 4.85 m`. After a 1 s TCP stall, 15 queued `MOVE`s totalling 4.2 m arrive at once: allowance is full (4.85), all accepted, 0.65 m left. A teleport of 10 m fails: `CORRECTION` to the last accepted position, +2 violation.

### F11. Correction and reconciliation

The correction formula is defined as:

`e = |p_client(seq_ack) − p_server(seq_ack)|`; if `e ≤ CORRECTION_DEADBAND_M`: no change; if `CORRECTION_DEADBAND_M < e ≤ SNAP_THRESHOLD_M`: rebase to `p_server`, replay unacknowledged inputs, and blend the rendered position to the result over `CORRECTION_TIME_S`; if `e > SNAP_THRESHOLD_M`: rebase, replay and snap immediately.

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| p_client(seq_ack) | Vector3 (m) | world bounds | client input history | Where the client had itself at the acknowledged `seq` |
| p_server(seq_ack) | Vector3 (m) | world bounds | `CORRECTION` message | Server's accepted position at that `seq` |
| CORRECTION_DEADBAND_M | float (m) | 0–0.2 | config (default 0.05) | Errors below this are ignored |
| SNAP_THRESHOLD_M | float (m) | 0.5–5 | config (default 2.0) | Above this, blending would look like sliding through the world |
| CORRECTION_TIME_S | float (s) | 0.05–0.5 | config (default 0.2) | Blend duration |
| INPUT_HISTORY_LEN | int | 15–120 | config (default 60 = 4 s at 15 Hz) | Unacknowledged inputs the client keeps for replay |

**Output Range:** no correction, smooth correction, or snap.
**Example:** correction with `e = 0.8 m` → rebase to the server position, replay the 4 inputs sent since `seq_ack`, blend over 0.2 s. With `e = 6 m` (rejected teleport) → snap.

### F12. Scoring queue budget

The scoring_load formula is defined as:

`load = Σ over peers of shots_per_s × SCORE_MS / 1000`; a `SHUTTER` is refused with `ERR_SERVER_BUSY` (retryable; the shot is not consumed) if `queue_len ≥ SCORING_QUEUE_MAX`.

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| shots_per_s | float | 0–SHUTTER_RATE_CAP | measured | Shots per second from one peer |
| SCORE_MS | float (ms) | 1–100 | measured; research §5.4 budget < 20 ms | Server time to score and roll one recipe |
| queue_len | int | ≥ 0 | measured | Validated shots waiting to be scored in this process |
| SCORING_QUEUE_MAX | int | 4–200 | config (default 40) | Queue length before refusing new shots |

**Output Range:** `load` is CPU-seconds per second (1.0 = one core fully busy).
**Example:** 4 players each firing a 10 fps burst for 1 s at 20 ms per score → `load = 4 × 10 × 0.02 = 0.8` for that second; the 40 shots queue (≤ 40), drain in 0.8 s, and the last result arrives about 800 ms after its press. A fifth concurrent burst would exceed the queue: those shots get `ERR_SERVER_BUSY` and the client offers them again automatically once (same `rid`).

### F13. Downstream bandwidth per player

The bandwidth_down formula is defined as:

`bw_down = SNAPSHOT_HZ × (SNAP_HEADER_B + n_entities × ENTITY_B + FRAME_OVERHEAD_B) + bw_events + bw_control`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| SNAPSHOT_HZ | float (Hz) | 5–20 | config (default 10) | — |
| SNAP_HEADER_B | int (bytes) | 4–32 | protocol ADR (estimate 12: type, seq, tick) | Per-snapshot header |
| n_entities | int | 1–40 | calculated (other players + subjects in session) | Entities in one snapshot |
| ENTITY_B | int (bytes) | 8–64 | protocol ADR; estimate 11 quantized (id 2, position 3×2 at 1 cm, yaw 2, state 1), about 40 if sent as unquantized engine values (**UNVERIFIED**, measure in the spike) | Bytes per entity |
| FRAME_OVERHEAD_B | int (bytes) | 20–100 | estimate: WebSocket server frame header 2–4 B + TLS 1.3 record about 22 B; TCP/IP headers (about 40 B per segment) add to egress | Per-message transport overhead (approx. 30 B app-level; 70 B including TCP/IP) |
| bw_events | float (B/s) | 0–1000 | measured | Reliable `EVENT`s, `SHUTTER_RESULT`s |
| bw_control | float (B/s) | 0–100 | calculated (PONGs, CORRECTIONs) | Control traffic |

**Output Range:** target `bw_down ≤ BW_DOWN_BUDGET` (10 KB/s, research §5.4). Upstream target `≤ BW_UP_BUDGET` 2 KB/s (`MOVE` at 15 Hz × about 100 B with overhead ≈ 1.5 KB/s).
**Example:** crew of 4 (3 other players + 8 subjects = 11 entities), 10 Hz, quantized: `10 × (12 + 11 × 11 + 70) = 2 030 B/s`, plus about 300 B/s events and control ≈ **2.3 KB/s**. Unquantized at 40 B/entity: `10 × (12 + 440 + 70) = 5 220 B/s` ≈ **5.5 KB/s**. Both are inside the 10 KB/s budget; quantization is a margin, not a necessity, at crew size.

### F14. Monthly server egress (ops input for devops-engineer)

The egress_month formula is defined as:

`egress_GB = avg_concurrent_players × bw_down_avg × 2 592 000 / 10^9`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| avg_concurrent_players | float | 0–1000 | measured / forecast | Players connected on average over the month |
| bw_down_avg | float (B/s) | 0–10 000 | F13, measured | Average downstream per player |
| 2 592 000 | constant (s) | — | 30 days | Seconds in a month |

**Output Range:** GB per month.
**Example:** 3 players on average at 2.3 KB/s → `3 × 2 300 × 2 592 000 / 10^9 ≈ 17.9 GB/month`. That is far above the 1 GB/month free egress quoted for one cloud option (research §6, S27, third-party), which rules that option out for anything beyond a test.

## Edge Cases

**Handshake and versions**

- **If the client's `pv` is outside `[PROTOCOL_MIN_SUPPORTED, PROTOCOL_CURRENT]`**: the server sends `REJECT ERR_VERSION_MISMATCH` with the required version and closes; the client enters `Rejected` and shows the reload prompt; no automatic retry.
- **If `content_version` differs**: same outcome as a protocol mismatch (hard reject, reload prompt).
- **If `ladder_version` differs but protocol and content match**: the connection is accepted; `HELLO_ACK` carries the server's identity table and `update_available`; the client shows the soft update banner and renders any tier ID it cannot parse as the neutral "?" badge with no colour, no blades and no comparison until it reloads.
- **If the client is newer than the server** (a deploy is half done, the client page was updated first): the server rejects with `ERR_VERSION_MISMATCH`; the client shows "Servers are updating, retrying shortly" and retries with F5 backoff instead of asking for a reload, because reloading would not help. The `REJECT` body says which side is newer.
- **If no `HELLO` arrives within `HANDSHAKE_TIMEOUT_S`**: the server closes the socket; nothing was created, so nothing is cleaned up.
- **If any message other than `HELLO` arrives in `Pending`**: `ERR_NOT_ALLOWED` and the socket closes (unauthenticated peers get no violation score; the per-IP connect bucket limits retries).
- **If the ticket is expired, already used, or for another session**: `REJECT ERR_AUTH_INVALID`; the client goes back to `Ticketing` once; a second failure shows "Couldn't join, please sign in again".
- **If the session is full when a valid ticket arrives** (two tickets raced for the last seat): `REJECT ERR_SESSION_FULL`; the client requests a new ticket (MVP solo sessions cannot be full).

**Validation and abuse**

- **If a client message carries an unknown tier ID** ("sss", " S", "4", null where a tier is required, an ID from a newer ladder): the message is rejected with `ERR_UNKNOWN` (or `ERR_UNSET`) naming the field; no state changes; the violation score gains `W_INVALID_TIER` (3).
- **If a client message carries a valid but inflated tier, or a score, price, balance or serial** (e.g. `tier: "SSS"` in a `SHUTTER`): the field is ignored and never read; the server computes its own value; the log gets one mismatch entry naming the client value and the server value; no violation is added (an extra field is forward-compatible noise), unless the message also fails a schema check.
- **If a numeric field is NaN or infinite**: `ERR_MALFORMED`, +5.
- **If camera settings are outside the server-known equipped gear** (e.g. f/1.4 on an f/4 lens, or the client equipped a lens locally that the server never confirmed): `ERR_OUT_OF_RANGE`; the shot is not consumed; nothing is rolled; +3.
- **If the camera position is farther than `CAMERA_REACH_M` from the server's player position at the capture tick**: `ERR_OUT_OF_RANGE`, not consumed, +3.
- **If a `MOVE` exceeds the allowance or crosses blocking collision**: `CORRECTION` to the last accepted position; the client rebases and replays; +2.
- **If `seq` skips or repeats**: `ERR_MALFORMED`, +5; the message is not processed.
- **If a `rid` is reused with a different body**: `ERR_IDEMPOTENCY_CONFLICT`, +5; the original outcome stands.
- **If a peer reaches `KICK_THRESHOLD`**: `ERROR ERR_KICKED`, socket closed, peer `Released` without grace; in-flight validated requests still complete. The client shows a neutral message ("You were disconnected because the game received unexpected data. Reload to continue.") without accusing the player.
- **If many players share one public IP** (a school, a carrier NAT) or all connections arrive through a tunnel or proxy that hides the client address: the per-IP connect bucket uses the forwarded client address only when the proxy is trusted and configured to send it (→ hosting ADR, research §7.13); otherwise the per-IP limit is disabled and per-account limits apply alone.

**Disconnection and recovery**

- **If the connection drops while a `SHUTTER` is in flight**: the server finishes scoring, rolling and saving; on resume the client sends `RESULT_QUERY` with the `rid` and receives the stored result; the player sees the photo develop as normal. The roll is never repeated.
- **If the connection drops after `SHUTTER` was sent but before the server received it**: on resume, `RESULT_QUERY` returns "unknown `rid`"; the client discards the shot and tells the player "That shot didn't reach the server" (no photo, no charge, shot count restored by Camera Model). Rule (Pillar 2): a shot without an acknowledged `rid` is **never shown as taken** — its frozen frame shows "not sent", never "developing", so the player is never told they own a photo that does not exist. It does **not** resend the shot, because the moment it captured is now outside the rewind window.
- **If the client resumes within `RECONNECT_GRACE_S`**: the resume token reclaims the seat; the player entity is still where the server last accepted it; the client rebases there.
- **If the client reconnects after grace expired**: the resume token is rejected with `ERR_AUTH_EXPIRED`; the client requests a new ticket and joins a session fresh (solo: a new session; crew: the same room if a seat is free, owned by Expedition Rooms). Results of earlier `rid`s are still available from the meta service for `IDEMPOTENCY_WINDOW_S`.
- **If the browser tab is hidden or the device sleeps**: the browser may throttle or pause the page's main loop, which stops polling and heartbeats (behaviour of Godot's web main loop when hidden is **UNVERIFIED**; verify in the spike). The server treats it like any silence (F4). On return, the client checks its state immediately and resumes within grace if possible.
- **If the player opens a second tab with the same account**: the newest successful `HELLO` wins; the older tab gets `ERR_SIGNED_IN_ELSEWHERE` and shows "Aperture is open in another tab or device" with a "Play here" button (which reconnects and displaces the other).
- **If the meta service is unreachable while the session server is up**: shutter results are delivered with `saved: false` and queued in the server's outbox for retry with the same `rid`. If the outbox reaches `OUTBOX_MAX` entries, the server sends `NOTICE service_degraded` and refuses new `SHUTTER`s with `ERR_SERVICE_DEGRADED` (retryable) until it drains; the viewfinder stays usable. Buying and selling show "Store unavailable, try again shortly". The `saved: false` message carries no score, tier or roll; these are revealed after commit (Rule 29).
- **If the session server process crashes**: clients see the socket close, enter `Reconnecting`, fail the resume (server gone), get a new ticket and a new session. Results already committed to the meta service are safe; validated-but-uncommitted shots in the crashed server's memory are lost, and `RESULT_QUERY` then reports "unknown `rid`" (handled as above). An outbox that survives a crash **→ part of the ADR on room lifecycle (research §7.8)**.
- **If a planned shutdown is announced**: `NOTICE shutting_down` with seconds left; new shots are refused `SHUTDOWN_DRAIN_S` before the end with `ERR_SHUTTING_DOWN`; in-flight shots complete; the client shows a countdown; at close it reconnects via F5 to the new build (which may trigger the reload prompt).

**Timing and load**

- **If RTT exceeds 300 ms**: play continues; the latency indicator shows "Poor"; if the capture tick estimate needs more than `MAX_REWIND_MS` of rewind, the capture is judged at the oldest allowed tick, so the moment may differ from what the player saw. This is the documented cost of a very slow connection.
- **If a TCP stall delivers a burst of queued messages**: the movement allowance and bucket bursts absorb up to `ALLOWANCE_WINDOW_S` of movement and `BURST_c` messages; excess `MOVE`s are dropped with `ERR_RATE_LIMITED` (+1 each) and the next `CORRECTION` resyncs.
- **If the server's outbound queue to a slow client backs up**: snapshots are coalesced (Rule 23); reliable `EVENT`s and results are never dropped; if the queue exceeds the transport's limit (believed `WebSocketMultiplayerPeer.max_queued_packets` / `outbound_buffer_size`; **UNVERIFIED** in 4.7), the peer is moved to `Grace` and must resume.
- **If the scoring queue is full**: `ERR_SERVER_BUSY`; the shot is not consumed; the client retries it once automatically with the same `rid` after `BUSY_RETRY_S` (the moment is preserved because the server records `capture_tick` at first validation), then reports failure.
- **If the client clock jumps** (sleep, manual change): client time is never used for gameplay; `view_tick` is in server ticks; F6 re-estimates the offset from the next PONG.

## Dependencies

**Cross-system requirement:** Darkroom & Gallery UI must hold its develop animation for at least 600 ms, so that a normal server result (p95 ≤ 400 ms at 150 ms RTT, see Game Feel) never makes the player wait. That GDD must list this requirement.

**Upstream (this system depends on):**

| System / dependency | Hard / soft | Interface | Status |
|---|---|---|---|
| Rarity Tier Ladder | Hard | identity table, `ladder_version`, `parse` (Rules 8, 13, 20) | Designed (`rarity-tier-ladder.md`). Note: `systems-index.md` row 3 lists no dependency; the ladder GDD lists this one as a hard dependent. The index should add it (not edited here). |
| Engine: WebSocket (`WebSocketMultiplayerPeer`, `WebSocketPeer`), `HTTPRequest`, `SceneMultiplayer` | Hard | transport, auth hook | Web behaviour with threads OFF is **NOT SOURCEABLE** (research §3.3); spike required |
| Meta service (product chosen by ADR) | Hard | accounts, tickets, transactions, service-only path | ADR not written |
| Player Movement & Exploration | Soft (for F10 constants) | `V_MAX`, collision, walkable bounds | Not started |
| Gear Catalog & Specs | Soft (for Rules 25–26) | setting ranges, `burst_fps` | Not started |

**Downstream (systems that depend on this one):** Accounts & Server Persistence (6), Photo Recipe & Re-render (9), Inventory & Loadout (10), Currency & Wallet (11), Photo Scoring (12), Capture Tier Resolution (13), Gallery (15), Photo Pricing & NPC Clients (16), Gear Shop (17), Found Photos (25), Leaderboards (24), Expedition Rooms (29), Supply Caps & Gear Serials (32), First-Claim & Image Serials (34), Co-op Crew Roles (36), Player-to-Player Trading & Market (37), Moderation & Reporting (39), Economy Telemetry (41), Server-Wide Events (45), and the UI systems that show connection state (19, 20, 21, 40).

**Bidirectional note:** the Rarity Tier Ladder already lists this system. Every downstream GDD, when authored, must list "depends on Network Transport & Server Authority" and state which Rules it relies on.

## Tuning Knobs

All values live in the network configuration resource (path set by the protocol ADR). Values a client needs to self-throttle are sent in `HELLO_ACK`, so client and server never disagree.

| Knob | Default | Safe range | Affects | Too low / too high |
|---|---|---|---|---|
| `PROTOCOL_CURRENT` / `PROTOCOL_MIN_SUPPORTED` | equal | min ≤ current | Which clients may connect | Window 0: every deploy forces a reload. Wide window: the server must keep old message handlers forever |
| `HARD_FRAME_CAP` | 4096 B | 1024–16384 | Memory per message; abuse surface | Too low: legitimate `HELLO_ACK`/tables fail. Too high: payload-stuffing attacks |
| Per-type caps (`CAP_type`) | F3 table | 16 B to hard cap | Same, per type | Too low: valid recipes rejected after a schema addition |
| `RATE_c`, `BURST_c` | F1 table | F1 ranges | Responsiveness vs abuse | Too low: honest clients rate-limited after stalls. Too high: spam and scoring load |
| `SHUTTER_SLACK`, `SHUTTER_RATE_FLOOR`, `SHUTTER_RATE_CAP`, `SHUTTER_BURST` | 1.25, 1/s, 10/s, 5 | F1b ranges | Burst shooting feel; server CPU | Cap too low: fast bodies feel throttled (Pillar 1). Too high: one player can saturate scoring |
| `V_HALF_LIFE_S` | 60 s | 10–600 | How long misbehaviour is remembered | Too short: slow abuse never trips. Too long: an honest bad-connection session accumulates |
| `THROTTLE_THRESHOLD` / `KICK_THRESHOLD` / `KICKS_TO_FLAG` / `THROTTLE_DURATION_S` | 10 / 30 / 3 per 24 h / 30 s | 5–50 / 15–100 / 1–10 / 10–300 | Anti-cheat strictness | Too low: false kicks (players lose trust). Too high: tampering goes unchecked |
| Violation weights `W_k` | F2 table | 0–30 | Relative seriousness | — |
| `PING_INTERVAL_S` / `STALL_TIMEOUT_S` / `DROP_TIMEOUT_S` | 2 / 6 / 15 s | F4 ranges and constraint | Detection speed vs false alarms | Too short: flapping on mobile Wi-Fi. Too long: players stare at a frozen world |
| `HANDSHAKE_TIMEOUT_S` | 5 s | 2–15 | Slow-loris resistance vs slow networks | — |
| `BACKOFF_BASE_S` / `BACKOFF_CAP_S` / `BACKOFF_JITTER` / `RECONNECT_MAX_ATTEMPTS` | 1 s / 30 s / 0.25 / 8 | F5 ranges | Recovery speed; thundering herd after restart | Too aggressive: server swamped after a restart. Too slow: players give up |
| `RECONNECT_GRACE_S` | 60 s | 15–300 | How long a seat and state are held | Too short: a tab switch loses the crew seat. Too long: dead seats block crews |
| `TICKET_TTL_S` | 60 s | 10–300 | Ticket replay window | — |
| `IDEMPOTENCY_WINDOW_S` | 600 s | 60–86400 | How long retries are safe | Too short: a slow resume can double-execute. Too long: storage |
| `TICK_HZ` | 30 | 20–60 | Simulation granularity; history size; CPU | — |
| `SNAPSHOT_HZ` | 10 | 5–20 | Smoothness of remote motion; bandwidth | Too low: spirits look jerky; larger interp delay. Too high: bandwidth and TCP queueing |
| `INTERP_BUFFER_SNAPSHOTS` / `JITTER_MARGIN_CAP_MS` | 2 / 100 ms | 1.5–3 / 0–200 | Remote smoothness vs how far behind | Too low: stutter on jitter. Too high: subjects lag further behind and rewind grows |
| `MAX_REWIND_MS` / `VIEW_TOLERANCE_MS` | 400 / 60 ms | 200–600 / 20–150 | Fairness of the decisive moment vs exploitability | Rewind too small: slow players miss moments. Tolerance too large: frame-picking |
| `MOVE_SEND_HZ` | 15 | 10–30 | Own-position update rate | — |
| `SPEED_TOLERANCE` / `ALLOWANCE_WINDOW_S` / `POSITION_SLACK_M` | 0.15 / 1.0 s / 0.25 m | F10 ranges | False corrections vs speed hacks | Too tight: rubber-banding. Too loose: small speed hacks pass |
| `CAMERA_REACH_M` | 1.0 m | 0.5–3 | Camera pose plausibility | Too tight: rejects legitimate held-out or raised camera poses (coordinate with Camera Model) |
| `CORRECTION_DEADBAND_M` / `SNAP_THRESHOLD_M` / `CORRECTION_TIME_S` / `INPUT_HISTORY_LEN` | 0.05 m / 2.0 m / 0.2 s / 60 | F11 ranges | Visual smoothness of corrections | — |
| `SCORING_QUEUE_MAX` / `BUSY_RETRY_S` | 40 / 1.0 s | 4–200 / 0.25–5 | Burst handling vs latency | — |
| `OUTBOX_MAX` | 200 entries | 20–5000 | How long a meta outage is tolerated | — |
| `SHUTDOWN_DRAIN_S` | 10 s | 3–60 | In-flight completion before deploy | — |
| `LOG_SUMMARY_INTERVAL_S` | 60 s | 10–600 | Log volume | — |
| `BW_DOWN_BUDGET` / `BW_UP_BUDGET` | 10 KB/s / 2 KB/s | — | Budget the profiler checks against | — |
| Latency indicator bands | Good ≤ 150 ms, Fair ≤ 300 ms, Poor > 300 ms | — | UI only | — |

## Visual/Audio Requirements

This system has minimal presentation; the art bible owns the look. Tone words in this document ("calm", "quiet gallery") are provisional until the user confirms the game's tone.

- A small **connection indicator** with four looks: Good, Fair, Poor, Offline/Reconnecting. It uses a shape cue as well as colour (for example 3/2/1/0 bars, a pulsing ring while reconnecting); colour is never the only cue. Suitable for `/asset-forge` SVG UI.
- A **"developing" placeholder** for a photo whose server result has not arrived, and a **"saving" mark** for `saved: false`. Both reuse Darkroom visuals (owned by Darkroom & Gallery UI).
- The neutral **"?" tier badge** for unparseable IDs is defined by the Rarity Tier Ladder; this system only triggers it.
- Audio: no alarm sounds for network problems (the game's tone is calm). Optional soft cue when reconnected, owned by Audio: SFX & Ambience. The shutter sound always plays locally at the press, never waiting for the server.

## Game Feel

Latency budgets the player feels (designed to 150 ms RTT; D12):

| Action | Where it runs | Budget | How it feels |
|---|---|---|---|
| Viewfinder: zoom, focus, exposure preview, framing | Client only | ≤ 1 frame, no network | Instant; the camera is never laggy |
| Own movement | Client-predicted | 0 ms perceived | Immediate; corrections invisible below 5 cm, blended under 2 m |
| Shutter press: sound, frame freeze | Client only | ≤ 1 frame | The press is always acknowledged at once |
| Score and tier reveal | Server | p95 ≤ 400 ms after the press at 150 ms RTT (RTT + queue + scoring ≤ 20 ms) | Hidden inside the develop animation; recommend Darkroom's minimum develop time ≥ 600 ms so a normal result never makes the player wait |
| Slow result | Server | after 5 s: "Still developing, it's safe" | Calm, no spinner panic; the result appears when ready |
| Buy, sell, equip | Meta service | pending state ≤ 100 ms; confirmation p95 ≤ 1 s | Button changes at once; the money moves only when it is real |
| Remote players and spirits | Interpolated snapshots | about 200–300 ms behind the server | Smooth at walking pace; the moment of capture is rewound (F8) so this delay costs nothing |
| Reconnect after a short drop | Client + server | first attempt within ~1 s; back in place within grace | "A hiccup, not a disaster" |

## UI Requirements

This system owns no screen; it supplies states and messages that UI systems display. All text is localisation keys; wording below is draft.

- **Connection indicator** (Viewfinder HUD and menus): Good / Fair / Poor from `rtt_est` bands; "Reconnecting…" with attempt progress during `Reconnecting`; "Offline" in `Offline`/`Failed`. Text tooltip with RTT in ms.
- **Shutter paused overlay** (Viewfinder HUD): shown in any state except `Synced`: "Reconnecting, shutter paused". The viewfinder stays live.
- **Hard version mismatch modal** (`ERR_VERSION_MISMATCH`, client older): "A new version of Aperture is available. Reload to keep playing." Single primary button **Reload** (reloads the page). Not dismissible, because no gameplay is possible. Mentions that photos and items are safe.
- **Servers updating notice** (client newer than server): "Servers are updating. Reconnecting shortly…" with automatic retry; no reload button.
- **Soft ladder update banner** (`ladder_version` differs): dismissible banner "An update is ready. Reload when convenient." Play continues; "?" badges may appear until reload.
- **Reconnect failed panel** (`Failed`): "Couldn't reconnect." Buttons **Retry** and **Back to menu**.
- **Signed in elsewhere** (`ERR_SIGNED_IN_ELSEWHERE`): "Aperture is open in another tab or device." Button **Play here**.
- **Disconnected after unexpected data** (`ERR_KICKED`): neutral, non-accusatory text and **Reload**.
- **Shutdown countdown** (`NOTICE shutting_down`): small banner with seconds left.
- **Photo states** (Darkroom & Gallery UI): developing → result; "saving" mark while `saved: false`; "That shot didn't reach the server" toast for unknown `rid` after resume.
- **Store unavailable** (Shop UI) during meta outage or `ERR_SERVICE_DEGRADED`.
- Accessibility: every state has text, not colour alone; modals take keyboard focus; whether AccessKit screen-reader support (4.5+) works in the web export is **UNVERIFIED** (Settings & Accessibility).

📌 **UX Flag — Network Transport & Server Authority**: the connection indicator, version modal and reconnect panel are shared components. In Pre-Production, include them in `/ux-design` for the HUD and the interaction pattern library before writing UI epics.

## Cross-References

| Referenced document | What is used | Where |
|---|---|---|
| `docs/architecture/research-web-networking.md` §2, §3.1–3.3 | Web transport limits (`wss://`, no custom WS headers, CORS, threads off), `auth_callback`, `server_relay` | Core Rules 1–3, 19, 33; Edge Cases |
| same, §4.1, §5.1, §5.4 | Analytic server scoring; session + meta topology; budgets (10–15 Hz, < 10 KB/s, < 512 B recipe, < 20 ms scoring) | Rules 3, 7; F3, F7, F12, F13 |
| same, §6, §7, §8, §9 | Hosting egress figures; ADR titles; risks; spike items | F14; Open Questions |
| `design/gdd/rarity-tier-ladder.md` Core Rules 9–10, Edge Cases, Interactions, AC 4–5 | `ladder_version` handshake, server table wins, "?" badge, `ERR_UNKNOWN`, invalid IDs feed anti-cheat, server recomputes tiers | Rules 6, 8, 13, 20; F2 `W_INVALID_TIER`; Interactions; AC A, B |
| `design/gdd/game-concept.md` Online play, Technical considerations, Risks | Crews 2–4; server owns inventories, trades, prices, scores, rolls, counters; score cheating and trading abuse mitigations | Overview, Rule 6, Interactions |
| `design/gdd/systems-index.md` row 3, rationale 3, A2, High-Risk Systems | MVP server authority; dependents | Overview, Dependencies |
| `.claude/rules/network-code.md` | Authority, versioning, validation of sizes and ranges, rate-limited logs, replication strategy, bandwidth budget | Throughout |
| `docs/engine-reference/godot/modules/networking.md` | RPC authority pattern, `auth_callback`; ENet sections do not apply to the web client | Rules 2, 33 |

## Acceptance Criteria

Tags: **[Logic]** automated gdUnit4 unit test (suggested name given) · **[Integration]** integration test or documented playtest · **[UI]** retained screenshot in `production/qa/evidence/`. *(provisional)* = depends on a system or ADR not yet written. Fixture values come from a test config resource, not inline numbers, except boundary tests.

**A. Handshake and versions (Rules 11–13, 32–35)**

1. [Logic] **GIVEN** server `PROTOCOL_CURRENT = PROTOCOL_MIN_SUPPORTED = 3`, **WHEN** `HELLO` with `pv` 2, 3 and 4 is evaluated, **THEN** 3 is accepted and 2 and 4 are rejected with `ERR_VERSION_MISMATCH`, and the reject body says which side is newer. `test_handshake_protocol_outside_window_rejects_version_mismatch`
2. [Logic] **GIVEN** matching protocol and a different `content_version`, **WHEN** the handshake is evaluated, **THEN** it is rejected with `ERR_VERSION_MISMATCH`. `test_handshake_content_version_differs_rejects`
3. [Logic] **GIVEN** matching protocol and content and client `ladder_version` 1 vs server 2, **WHEN** the handshake is evaluated, **THEN** it is accepted, `HELLO_ACK` contains the server identity table and `ladder_version` 2, and `update_available` is true. `test_handshake_ladder_version_differs_accepts_with_server_table`
4. [Logic] **GIVEN** a client holding ladder v1 receives tier ID "X" (only in v2), **WHEN** the badge data is resolved, **THEN** it is the neutral "?" badge with no colour token, zero blades and no comparison result. `test_unknown_ladder_id_after_mismatch_resolves_neutral_badge`
5. [Logic] **GIVEN** a peer in `Pending`, **WHEN** `HANDSHAKE_TIMEOUT_S` elapses with no `HELLO` (simulated clock), **THEN** the peer is closed and no session state exists for it. `test_pending_peer_handshake_timeout_closes`
6. [Logic] **GIVEN** a ticket already consumed, **WHEN** it is presented again, **THEN** `ERR_AUTH_INVALID`. `test_ticket_reuse_rejects_auth_invalid`
7. [Logic] **GIVEN** account A has an `Active` peer, **WHEN** a second valid `HELLO` for A arrives, **THEN** the older peer is closed with `ERR_SIGNED_IN_ELSEWHERE` and the new peer is `Active`. `test_second_session_same_account_newest_wins`
8. [Integration] *(provisional: spike)* **GIVEN** the single-threaded web export on an HTTPS page and a headless 4.7.2 server behind TLS, **WHEN** the client connects to the `wss://` URL, **THEN** the handshake completes and the ticket is carried in the `HELLO` body (verified by server log), not in a header or URL.

**B. Validation (Rules 6, 8, 14–21)**

9. [Logic] **GIVEN** `HARD_FRAME_CAP = 4096` and `SHUTTER` cap 512, **WHEN** frames of 512, 513 and 4097 bytes are checked, **THEN** 512 passes, 513 is `ERR_OVERSIZE`, and 4097 closes the connection without parsing. `test_size_check_boundaries_reject_and_close`
10. [Logic] **GIVEN** a `SHUTTER` whose tier filter or any tier field holds "sss", **WHEN** validated, **THEN** it is rejected with `ERR_UNKNOWN` naming the field, no state changes, and the violation score rises by `W_INVALID_TIER`. `test_unknown_tier_id_rejects_err_unknown_and_adds_violation`
11. [Integration] *(provisional: Capture Tier Resolution)* **GIVEN** a `SHUTTER` carrying `tier: "SSS"` whose recipe and server loadout resolve to "B", **WHEN** processed, **THEN** the stored tier is "B" and exactly one mismatch log entry names "SSS" and "B".
12. [Logic] **GIVEN** a `MOVE` with a NaN coordinate, **WHEN** validated, **THEN** `ERR_MALFORMED` and +5 violation. `test_nan_field_rejects_malformed`
13. [Logic] **GIVEN** messages with `seq` 1, 2, 4, **WHEN** validated in order, **THEN** 1 and 2 pass and 4 is `ERR_MALFORMED`. `test_seq_gap_rejects_malformed`
14. [Logic] **GIVEN** a known type with one extra unknown field, **WHEN** validated, **THEN** it passes, the field is ignored, and one log entry is written per session. `test_unknown_field_ignored_logged_once`
15. [Logic] **GIVEN** a lens with maximum aperture f/4 in the server loadout, **WHEN** a `SHUTTER` requests f/2.8, **THEN** `ERR_OUT_OF_RANGE`, the shot is not consumed and no roll occurs. `test_shutter_settings_outside_server_gear_rejects`
16. [Logic] **GIVEN** a `SHUTTER` before `HELLO_ACK`, **WHEN** validated, **THEN** `ERR_NOT_ALLOWED`. `test_shutter_before_handshake_rejects_not_allowed`
17. [Integration] **GIVEN** a test harness that sends each invalid message from items 9–16, **WHEN** the server processes them, **THEN** a snapshot of all server-owned state (inventory, wallet, gallery, counters) is byte-identical before and after.

**C. Rate limits and violations (F1, F1b, F2, Rule 36–37)**

18. [Logic] **GIVEN** a movement bucket (BURST 30, RATE 20/s) full at t = 0, **WHEN** 31 messages arrive at t = 0 and one more at t = 0.05 s, **THEN** 30 are accepted, the 31st is `ERR_RATE_LIMITED`, and the one at 0.05 s is accepted. `test_token_bucket_burst_exhausted_then_refills`
19. [Logic] **GIVEN** `burst_fps` 3 and 12 with defaults, **WHEN** `RATE_shutter` is computed, **THEN** 3.75/s and 10/s. `test_shutter_rate_follows_gear_and_caps`
20. [Logic] **GIVEN** V = 20 at t = 0 and `V_HALF_LIFE_S = 60`, **WHEN** evaluated at t = 60 with a weight-3 violation, **THEN** V = 13. `test_violation_score_decays_by_half_life`
21. [Logic] **GIVEN** the F2 example sequence (11 invalid tier IDs, 1 s apart), **WHEN** applied, **THEN** the peer is `Throttled` after the 4th and kicked with `ERR_KICKED` at the 11th. `test_repeated_invalid_tier_ids_throttle_then_kick`
22. [Logic] **GIVEN** an honest-client fixture (5 rate-limit drops during a stall), **WHEN** applied, **THEN** V stays below `THROTTLE_THRESHOLD`. `test_honest_stall_never_reaches_throttle`
23. [Logic] **GIVEN** 100 identical anomalies in 1 s, **WHEN** logged, **THEN** at most `BURST_log` lines are written and one summary line with the suppressed count follows within `LOG_SUMMARY_INTERVAL_S`. `test_anomaly_log_rate_limited_with_summary`

**D. Liveness and reconnection (F4, F5, Rules 34, 28)**

24. [Logic] **GIVEN** last inbound at t = 100 s with defaults, **WHEN** the state is evaluated at 104, 106.5 and 115 s, **THEN** Synced, Stalled, and Reconnecting. `test_liveness_states_at_timeout_boundaries`
25. [Logic] **GIVEN** jitter u = 0, **WHEN** `delay(n)` is computed for n = 1..8, **THEN** 1, 2, 4, 8, 16, 30, 30, 30 s; with u = ±1 each delay stays within ±25 %. `test_reconnect_backoff_doubles_caps_and_jitters`
26. [Logic] **GIVEN** a valid resume token, **WHEN** used at grace − 1 s and at grace + 1 s, **THEN** the first reclaims the seat and the second returns `ERR_AUTH_EXPIRED`. `test_resume_token_valid_only_within_grace`
27. [Integration] **GIVEN** a `SHUTTER` validated by the server, **WHEN** the client socket is closed before `SHUTTER_RESULT` is sent and the client resumes, **THEN** `RESULT_QUERY` returns the same score and tier the server stored, and the roll log shows exactly one roll for that `rid`.
28. [Integration] *(provisional: spike)* **GIVEN** a web client in `Synced`, **WHEN** the tab is hidden for 30 s and shown again, **THEN** the client is back in `Synced` within 5 s with the same seat.

**E. Idempotency and authority (Rules 7, 27, 29–31)**

29. [Logic] **GIVEN** a processed `rid` R with result X, **WHEN** R is received again with the same body, **THEN** X is returned and no handler runs; with a different body, `ERR_IDEMPOTENCY_CONFLICT`. `test_idempotent_retry_returns_stored_result`
30. [Logic] **GIVEN** a `SHUTTER` from the client, **WHEN** the server assembles the recipe, **THEN** gear IDs, world time, weather, subject IDs and poses come from server state and none is copied from the client message. `test_recipe_assembly_uses_server_authoritative_fields`
31. [Integration] **GIVEN** the meta service is stopped, **WHEN** a shot is taken, **THEN** `SHUTTER_RESULT` arrives with `saved: false` and no score, tier or roll; after the meta service restarts, exactly one photo record exists for the `rid` and the client receives `saved: true` with the result.
32. [Integration] **GIVEN** an attempt to call the service-only write path with a client token, **WHEN** made, **THEN** `ERR_AUTH_INVALID`, no record is written and the peer is kicked.

**F. Movement and lag compensation (F8, F10, F11)**

33. [Logic] **GIVEN** the F8 example (recv 9000, RTT 150, interp 240, 30 Hz), **WHEN** `view_tick` 8991.2 and 8985.0 are evaluated, **THEN** results are 8991.2 and 8990.55. `test_capture_tick_within_tolerance_uses_claim_else_clamps`
34. [Logic] **GIVEN** an estimate that would need 600 ms of rewind with `MAX_REWIND_MS = 400`, **WHEN** evaluated, **THEN** `capture_tick = recv_tick − 12`. `test_capture_tick_clamped_to_max_rewind`
35. [Logic] **GIVEN** `V_MAX = 4` and defaults with a full allowance, **WHEN** a burst totalling 4.2 m and then a 10 m jump arrive, **THEN** the burst is accepted and the jump produces `CORRECTION`. `test_movement_allowance_absorbs_burst_rejects_teleport`
36. [Logic] **GIVEN** errors of 0.03 m, 0.8 m and 6 m at the acknowledged `seq`, **WHEN** a correction is applied, **THEN** none, blend with replay of unacknowledged inputs, and snap with replay. `test_correction_deadband_blend_snap_with_replay`
37. [Integration] *(provisional: Subject & Spirit Behaviour)* **GIVEN** a subject whose pose changes between ticks 8990 and 8992 and a client at 150 ms simulated RTT, **WHEN** the shutter is pressed while the client renders tick 8991, **THEN** the stored recipe has the subject pose of tick 8991 (interpolated).

**G. Budgets (F12, F13)**

38. [Integration] *(provisional: spike)* **GIVEN** a crew of 4 with 8 subjects at 10 Hz, **WHEN** measured for 60 s, **THEN** average downstream per client ≤ 10 KB/s and upstream ≤ 2 KB/s.
39. [Integration] **GIVEN** `SCORING_QUEUE_MAX = 40`, **WHEN** 41 shots are validated before any is scored, **THEN** the 41st gets `ERR_SERVER_BUSY`, is not consumed, and succeeds on its automatic retry.

**H. UI (UI Requirements)**

40. [UI] **GIVEN** a client older than the server, **WHEN** it connects, **THEN** the non-dismissible reload modal is shown (screenshot).
41. [UI] **GIVEN** the client in `Reconnecting`, **WHEN** the viewfinder is open, **THEN** the indicator shows the reconnecting look and the "shutter paused" overlay is visible while framing still works (screenshot).
42. [UI] **GIVEN** a `ladder_version` mismatch, **WHEN** the client is in play, **THEN** the soft update banner is visible and a "?" badge is shown for an unknown tier (screenshot).
43. [UI] **GIVEN** each indicator state (Good, Fair, Poor, Offline), **WHEN** displayed, **THEN** each is distinguishable in a greyscale screenshot.

## Open Questions

**Design questions** (see Decisions to confirm for options and recommendations): solo session model (D1), movement authority (D2), lag compensation (D3), protocol window (D4), content lockstep (D5), ladder mismatch policy (D6), multi-tab rule (D7), shots during a drop (D8), meta outage behaviour (D9), violation thresholds (D10), first-claim ordering (D11), latency target (D12), snapshot rate (D13), grace length (D14), economy optimism (D15).

**Other open questions**

1. Vertical movement validation (slopes, stairs, jumps) waits on Player Movement & Exploration.
2. `CAMERA_REACH_M` must be agreed with Camera Model (can the player hold a camera overhead or at arm's length?).
3. Burst shooting: one `SHUTTER` per frame, or one message per burst with N frames? Affects F1b, F3 and F12 (Camera Model and Photo Scoring).
4. Does a shared hub (Full Vision) need relevancy filtering and a different snapshot budget? Not designed here.
5. Security-engineer review of: the view-tick tolerance compromise (F8), the violation thresholds (F2), and the ticket/resume token design.
6. Devops-engineer needs the network-side contract only: `wss://` on 443 via the reverse proxy with path routing to session servers, HTTPS for the meta service with CORS for the page origin, `TICK_HZ` 30, `SNAPSHOT_HZ` 10, ≤ 10 KB/s down and ≤ 2 KB/s up per player, egress per F14.

**Items to verify in the first spike** (research §9; all NOT SOURCEABLE or UNVERIFIED): `WebSocketMultiplayerPeer` and `HTTPRequest` working in a threads-OFF web build; `MultiplayerSynchronizer` over WebSocket on web; how the `unreliable` mode behaves over WebSocket; existence and behaviour in 4.7 of `SceneMultiplayer.allow_object_decoding`, `auth_timeout`, and `WebSocketMultiplayerPeer.inbound_buffer_size`, `outbound_buffer_size`, `max_queued_packets`, `handshake_timeout`; web main-loop behaviour when the tab is hidden; real bytes per entity (F13); room process RAM; scoring time on the target VM.

**ADR candidates** (titles from research §7; this GDD states the behaviour each must satisfy):

| ADR (research §7) | Behaviour this GDD requires of it |
|---|---|
| 1. Network transport for web clients | `wss://` session channel, HTTPS meta channel, no P2P (Rules 1–2) |
| 2. Server topology | Authoritative session servers + meta service; service-only write path (Rules 3–4) |
| 3. Meta backend selection | Transactions, idempotent `rid` handling, CORS, rate limits per account (Rules 27–30, F1) |
| 4. Authentication, tickets and token flow | Single-use tickets in `HELLO` body, resume tokens, one session per account (Rules 32–35) |
| 5. Photo recipe schema and versioning | Server-side assembly split (Rule 7), 512 B cap (F3) |
| 7. Client/server build lockstep | Protocol window and content version (Rules 11–12) |
| 8. Room lifecycle and process model | Solo sessions, grace, outbox durability, scoring queue (D1, F12) |
| 9. Economy transaction integrity | Exactly-once outcomes under retry (Rule 27) |
| 10. Server RNG authority and audit log | Roll recorded before send, never per-client seed (Rules 27, 31) |
| 11. Message protocol, validation and rate limiting | Envelope, serialization format, config resource, F1–F3 |
| 12. Web export configuration | Threads OFF, `HTTPRequest.use_threads = false` |
| 13. Hosting, reverse proxy and TLS | Domain + certificate, forwarded client address (Edge Cases), egress (F14) |

## Decisions to confirm

> **DECIDED 2026-11-03 (user):** D1 = A (solo play runs in a 1-player server session); capture-time authority = this system's F8 (World Time, Weather & Light reads the resolved tick and has no window of its own); all other decisions = the recommended option.

Each item below was confirmed by the user on 2026-11-03 (see the DECIDED note above).

**D1. How a solo (MVP) player's shots are made authoritative.**
- A. Every player, solo included, plays inside a server session (a room of capacity 1) that simulates subjects and world time; shots are validated against that state.
- B. Solo play runs locally; the client sends recipes to a stateless "score this recipe" endpoint, and the server re-derives subject poses from a deterministic seed and timestamp.
- C. Solo play runs locally and the server trusts client-reported subject poses within tolerance.
- **Recommendation: A.** It is the only option where subject pose (part of the score) is never client-reported, and Alpha crews reuse the same code. Cost: a server session per active player; measure RAM in the spike. B is the fallback if hosting cost is too high, but it requires Subject & Spirit Behaviour to be fully deterministic. C conflicts with "the client never reports its own results".

**D2. Who simulates the player's movement.**
- A. Client-predicted movement, server-validated with a movement allowance, collision shape cast and corrections with input replay.
- B. Fully server-simulated movement: the client sends inputs only; the server runs the character controller; the client predicts and reconciles.
- C. Client-authoritative movement with no validation.
- **Recommendation: A.** Walking pace makes speed and collision checks enough, and it avoids depending on identical Jolt behaviour between the web client and the server (research §3.4, unverified). B is stronger against cheats but doubles movement work and needs physics parity. C makes camera position and first-claim presence trivially fakeable.

**D3. Lag compensation for the moment of capture.**
- A. Rewind subjects to the tick the client was viewing, accepting the client's claim only within ±60 ms of the server's estimate, capped at 400 ms.
- B. No rewind: judge the shot at the server's current tick on receipt.
- C. Rewind to the client's claimed tick with only the 400 ms cap.
- **Recommendation: A.** B means a 150 ms player systematically misses decisive moments (against Pillar 1). C lets a client pick the best frame from a 400 ms window. A is the security/fairness compromise to put to security-engineer.

**D4. Protocol compatibility window.**
- A. Exact match (`PROTOCOL_MIN_SUPPORTED = PROTOCOL_CURRENT`); every protocol change forces a reload.
- B. Support the current and the previous version.
- **Recommendation: A for MVP.** One developer, one project, two export presets; keeping old handlers is cost with no benefit until there is a live audience. Revisit before open beta.

**D5. Content version check.**
- A. Hard reject when the client's content hash differs from the server's.
- B. Soft: allow play and rely on server scoring alone.
- **Recommendation: A.** A client seeing different scenes than the server scores is judged on things it cannot see.

**D6. Ladder version mismatch.**
- A. Soft: accept, send the server table, prompt to update, "?" badge for unparseable IDs. *(used in this draft; matches the Rarity Tier Ladder edge case exactly)*
- B. Hard reject like a protocol mismatch.
- **Recommendation: A.** It is what the Rarity Tier Ladder GDD specifies, and it is safe because every gameplay tier is recomputed by the server. Under D5-A it only triggers when the ladder changes without a content change.

**D7. Same account in two tabs or devices.**
- A. Newest connection wins; the older gets "open elsewhere" with a "Play here" button.
- B. Oldest wins; the new connection is refused.
- C. Both allowed.
- **Recommendation: A.** Matches what players expect from web games; B strands a player whose old tab is frozen; C doubles rate limits and complicates per-account state.

**D8. Shots while the connection is down.**
- A. Shutter disabled outside `Synced`; the viewfinder stays usable.
- B. Queue shots locally and submit them on reconnect.
- **Recommendation: A.** A queued shot's moment is outside any safe rewind window, so the server cannot validate it; B would invite disconnect tricks.

**D9. Meta service outage while a session is live.**
- A. Keep shooting; results shown as "saving" and retried from a bounded outbox; refuse new shots when the outbox is full.
- B. Pause the shutter immediately when the meta service is unreachable.
- **Recommendation: A.** Short outages stay invisible to players; the outbox cap bounds the risk. B is simpler if the process-model ADR cannot make the outbox survive a crash.

**D10. Response to misbehaving clients.**
- A. Graduated: throttle at 10, kick at 30, flag the account for moderator review after 3 kicks in 24 h; no automatic bans.
- B. Kick on the first schema violation.
- C. Log only, never act automatically.
- **Recommendation: A.** B risks kicking honest players after a bug or a version edge case; C leaves abuse unchecked. Thresholds to be reviewed by security-engineer.

**D11. Ordering of competing first-claims (Alpha).**
- A. Order by lag-compensated capture tick; captures from the same crew within `VIEW_TOLERANCE_MS` of each other are a **joint claim** (shared crew credit), and only cross-crew ties fall back to server receive order, so latency never turns crewmates into rivals (Pillar 3).
- B. Order by server receive order only.
- **Recommendation: A.** B rewards the player with the better connection, not the faster eye (Pillar 1). Final call belongs with the First-Claim GDD and the open first-claim question (B7 in the systems index).

**D12. Latency target.**
- A. Responsive up to 150 ms RTT; playable to 300 ms; "Poor" above. *(used in this draft; studio default, no project figure exists)*
- B. A tighter target (e.g. 100 ms), which would justify shorter interpolation and a smaller rewind.
- C. A looser target (e.g. 250 ms) for players far from the server.
- **Recommendation: A**, recorded in `project.yaml` performance settings by the user if accepted (not edited here).

**D13. Snapshot rate.**
- A. 10 Hz with a 2-snapshot interpolation buffer.
- B. 15 Hz (smoother spirits; about 50 % more downstream; smaller interpolation delay).
- **Recommendation: A**, the low end of the research range (10–15 Hz); raise to 15 Hz if spirit motion looks stepped in the spike. Both fit the bandwidth budget (F13).

**D14. Reconnect grace period.**
- A. 60 s.
- B. 30 s.
- C. 180 s.
- **Recommendation: A.** Covers a tab switch or a Wi-Fi blip without holding crew seats for long. Revisit with Expedition Rooms.

**D15. Economy display.**
- A. Never optimistic: pending state at once, balance and items change only on server confirmation.
- B. Optimistic update with rollback on failure.
- **Recommendation: A.** A balance that goes up and then down again damages trust in exactly the thing this system protects; the 1 s budget is acceptable for shop actions.

**D16. Dependency on the Rarity Tier Ladder.**
- A. List the ladder as a hard upstream dependency of this system (as the ladder GDD already does) and ask for `systems-index.md` row 3 to be updated. *(used in this draft; the index was not edited)*
- B. Treat the ladder table as plain data carried in the handshake, with no dependency recorded.
- **Recommendation: A.** The handshake and validation rules cannot be implemented without the ladder's `parse` and identity table.

**D17. Unknown fields inside known message types.**
- A. Ignore and log once per session (forward compatible).
- B. Reject as malformed.
- **Recommendation: A** under D4-A it rarely matters; it keeps a future version window (D4-B) possible without changing the validator. Unknown message *types* are still rejected.
