# Accounts & Server Persistence

> **Status**: Designed 2026-11-04 (pending `/design-review` in a fresh session)
> **Author**: systems-designer (agent draft for user review); inputs from `network-transport-server-authority.md` (binding) and the technical-director research note
> **Last Updated**: 2026-11-03
> **Last Verified**: 2026-11-03
> **Creative Director Review (CD-GDD-ALIGN)**: REVISED 2026-11-04 — CONCERNS fixed: results withheld until commit (with Network), deletion spares the requesting device, guest sign-out hidden, overpromises softened, guests excluded from leaderboards and scarce results, co-credit deferred to First-Claim, stale references. NOT ASSESSED: MDA aesthetics target (none stated).
> **Implements Pillar**: Pillar 2 "Every photo matters" (a photo, a lens or a balance is real because it is durably stored once, owned by exactly one account, and survives crashes, retries and restores); supports the anti-pillar "not pay-to-win" (no record can be created, duplicated or edited outside a server transaction) and the anti-pillar "not a photo-upload or social-media app" (the game stores as little personal data as it can)

## Summary

Accounts & Server Persistence is the meta service's half of the server: who a player is (account, sign-in identity, tokens), and how every server-owned record is stored (inventory, wallet ledger, photo records and recipes, rarity rolls, serials, counters, claims, idempotency records). It defines the account lifecycle (guest, registered, suspended, pending deletion, deleted), the transaction rules that keep the economy exact (one action = one atomic transaction; an append-only, zero-sum ledger; permanent de-duplication by request ID), backups and restore, schema migration, and how long each kind of data is kept and how it is erased.

> **Quick reference** — Layer: `Core` · Priority: `MVP` · Key deps: `Network Transport & Server Authority` (channels, `rid` idempotency, service-only path, tickets, D7/D9/D15), `Rarity Tier Ladder` (tier IDs only, never ranks; legacy null tier rule) · Backend product, database engine and hosting are **not decided here**; each is required behaviour marked **→ becomes an ADR**. PocketBase (research §5.1) is the leading **candidate**, not a decision. Claims about backend features not sourced in the repo are marked **UNVERIFIED**.

## Overview

The Network Transport GDD splits the server into session servers (live world, scoring, rolls) and a **meta service** reached over HTTPS. This GDD specifies the meta service's identity and storage rules. It does not choose the product: the research note recommends PocketBase (an embedded SQLite database plus built-in auth in one binary) and names Nakama and a custom service as alternatives (research §4.2, §5.1–5.2). Whatever is chosen must satisfy the behaviour below.

The system covers six things:

1. **Identity.** An account is a random, opaque `account_id`. A player can start as a **guest** (no personal data at all) and later attach a sign-in identity (an email one-time code in MVP; OAuth providers later). Sign-up and sign-in are a single flow.
2. **Sessions and tokens.** Short-lived access tokens and rotating refresh tokens, at the behaviour level. Session tickets and resume tokens remain owned by Network Transport (Rules 33–35).
3. **Record persistence.** A catalogue of every server-owned record, its owner system, its key, its uniqueness constraints and its lifecycle.
4. **Transaction integrity.** Every economy action commits as one atomic database transaction. Money moves through an append-only, double-entry ledger. Every effect row carries the request ID (`rid`) that caused it under a permanent unique constraint, so a retry can never duplicate money, items, photos or rolls, however late it arrives.
5. **Backups, restore and migration.** Hourly local snapshots, daily off-host copies, monthly restore drills; forward-only schema migrations with a mandatory pre-migration backup.
6. **Retention and deletion.** What is kept, for how long, and what happens to a deleted account's photos, gear and ledger history, including in backups.

Hard constraints from the user and the project: **no paid services** beyond what the user already has; **one developer** runs everything; **store minimal personal data** and support **account deletion**. Nothing in this GDD is legal advice; age, region and privacy-law items are listed as Open Questions for a qualified reviewer.

## Player Fantasy

Players meet this system directly only twice: when they sign in and if they ever delete their account. The rest of the time its job is to be invisible. The feeling it protects is **"my photos and gear are safe, and they are truly mine."**

- **"It's still there tomorrow."** The SSS spirit photographed last night is in the gallery this morning, with the same score and the same serial. Closing the tab, a crashed session server or a hosting move does not touch it (Pillar 2). A disaster restore can lose at most the backup window (D7), and players are told honestly when it happens (D12).
- **"Nobody else has my lens."** A serialised body is owned by one account. It cannot be copied by a double click, a retry or a lag spike.
- **"The money adds up."** Every coin in the wallet came from somewhere and every spend went somewhere. The history can be shown, and it never changes after the fact.
- **"I can just play."** A first-time visitor presses Play and is photographing within seconds, without a form. When they decide the game is worth keeping, one email code makes it permanent, and nothing they made is lost on the way, as long as they attach it before clearing browser storage or the guest expires.
- **"I'm in control of my data."** The game asks for an email and a display name, nothing more. "Delete my account" really deletes it, explains exactly what happens to photos already on a leaderboard, and gives a short window to change one's mind.

The target is the quiet trust of a good bank vault that happens to hold photographs: nobody admires the vault, and nobody worries about it either.

## Detailed Design

### Core Rules

**A. Identity and accounts**

1. **An account is an opaque ID.** Every account has an `account_id` of 128 random bits, generated by the server, never sequential and never derived from personal data. All other records refer to accounts (or to wallets, Rule 27) by ID only. Display names are never keys.
2. **Personal data is minimal and closed.** The only personal data an account may hold is: one or more **sign-in identities** (a verified email address, or an OAuth provider name + provider subject ID), a **display name** with a short tag, a preferred language, `created_at` and `last_seen_at` (UTC, day precision is enough for `last_seen_at`). No birth date, real name, phone number, postal address, avatar upload or free-text bio is stored. Adding any new personal field requires a change to this GDD (Decisions to confirm D2, D9; Open Questions on age).
3. **Guest accounts (Decisions to confirm D1).** "Play as guest" creates an account with **no** sign-in identity. The guest's only credential is its refresh token, stored in the browser's persistent storage (Godot `user://`, which maps to browser storage in web exports; persistence across sessions and inside an itch.io iframe is **UNVERIFIED**, spike item). A guest can play the full MVP loop (shoot, develop, sell, buy, equip). A guest **cannot**: trade with players (Alpha), vote or enter player-judged contests (VS), post commissions (Full Vision), or change their auto-generated display name. Guest photos may appear on leaderboards under the auto-generated name. Decided 2026-11-04: guests' photos are scored and tiered, but guests cannot hold leaderboard places or receive serials or first-claims; existing eligible results count once the account is registered.
4. **Guest upgrade keeps the account.** Attaching a sign-in identity to a guest turns it into a registered account **in place**: the `account_id`, gallery, wallet, inventory and history are unchanged; nothing is copied or merged. One-time grants that were already given (for example the Starting Choice grant) are not given again.
5. **No account merging.** If the identity a guest tries to attach already belongs to another account, the attach is refused with `ERR_IDENTITY_IN_USE`. The player may sign in to the other account instead; the guest account stays on this device until it expires (Rule 46). Two accounts are never merged, because merging wallets, serials and claims has no safe general rule.
6. **Sign-in method in MVP: email one-time code (D2).** The player enters an email address; the server sends a numeric code of `OTP_DIGITS` digits valid for `OTP_TTL_S`; the player types the code into the game. The game does not use magic links in MVP, because a link opens a new browser tab outside the game's iframe and would need cross-tab hand-off (**UNVERIFIED** in a Godot web export). Passwords are not used at all.
7. **One flow for sign-up and sign-in.** Entering an email that has no account creates a registered account only **after** the code is verified. The response to "send me a code" is identical whether or not the address has an account ("If this address can receive email, a code is on its way"), so the endpoint cannot be used to discover who plays.
8. **Code verification limits.** A code may be tried at most `OTP_MAX_ATTEMPTS` times, then it is void. Each email address may receive at most `OTP_SENDS_PER_HOUR` codes per hour and may accumulate at most `OTP_FAILS_PER_DAY` failed attempts per UTC day; beyond that, code sign-in for that address is refused until the next UTC day with `ERR_RATE_LIMITED` (F7). Each sent code email says "If you didn't ask for this, ignore it; your account is safe."
9. **OAuth later (D2).** Google and Discord OAuth are the recommended additions at Vertical Slice, as extra identities on the same account. OAuth inside a Godot web export (popup or redirect, token hand-back through `JavaScriptBridge`) is **NOT SOURCEABLE** in this repo; it needs a spike before it is promised.
10. **Email delivery is an external dependency.** Sending codes requires an email-sending service. The hard constraint allows only free options. Which one (and its daily limit) **→ becomes an ADR** (Open Questions). Until it exists, playtests run on guest accounts only.
11. **Display names (D9).** A registered player picks a display name of `NAME_MIN_LEN`–`NAME_MAX_LEN` characters; the server appends a random 4-digit tag (shown as `Mira#4821`). Names are not unique; name + tag is. Guests get an auto-generated name from a word list (e.g. `Wandering Lens#0193`). A name change is allowed once per `NAME_CHANGE_COOLDOWN_D`. Text filtering is owned by Moderation & Reporting; until that GDD exists, a static block list is applied.

**B. Sessions and tokens** (Network Transport Rule 32 delegates lifetime and refresh here)

12. **Two token kinds.** Signing in returns an **access token** (lifetime `ACCESS_TOKEN_TTL_S`) and a **refresh token** (sliding idle lifetime `REFRESH_IDLE_D`, hard limit `REFRESH_ABSOLUTE_D`; F6). Access tokens authorise meta-channel requests and ticket requests. Refresh tokens are used only to get a new pair.
13. **Rotation and reuse detection.** Every refresh returns a **new** refresh token and invalidates the old one. If an invalidated refresh token is presented again, the server treats the whole token family as stolen: every token in that family is revoked and the device must sign in again. Concurrent refreshes from the same device within `REFRESH_RACE_GRACE_S` return the same new pair (so two simultaneous HTTP requests from one tab do not trip reuse detection).
14. **Token storage on the client.** Tokens are stored in browser persistent storage (via `user://`), not in cookies, because the game page may be served inside a third-party iframe where cookies are partitioned or blocked (**UNVERIFIED** for the chosen host). This is weaker against script injection than an httpOnly cookie; the mitigation is that the game loads no third-party scripts and renders no player-written HTML. Final choice **→ part of the auth ADR (research §7.4)**.
15. **Many devices, one live session.** An account may hold up to `MAX_DEVICES` refresh-token families (one per device or browser). Meta-channel requests from several devices are allowed. Only one live **session channel** exists at a time; the newest connection wins (Network Transport Rule 35, D7). This GDD does not change that rule.
16. **Instant revocation.** Each account has an integer `token_epoch`. Access tokens carry the epoch they were issued under; a request whose epoch is lower than the account's current epoch is rejected with `ERR_AUTH_EXPIRED` and the client refreshes. "Sign out everywhere", a suspension, a deletion request and a detected token theft all increment `token_epoch`, which invalidates every access token within one request, and revoke all refresh families. Exception: a deletion request spares the requesting device's family (Rule 44a), so a guest or a player on that device can still cancel within grace.
17. **Service credentials.** Session servers write to the meta service through the service-only path (Network Transport Rule 4) with a per-server credential. Credentials are stored only on the server host, rotated at least every `SERVICE_CRED_ROTATE_D`, and each one is individually revocable. A client token on a service path is `ERR_AUTH_INVALID` and a violation (Network Transport Rule 4).

**C. What is persisted** — the record catalogue

18. **The meta database is the only durable store.** Session servers hold no durable state: anything not yet committed by the meta service does not exist (Network Transport Rule 29: "a photo exists only once the database has saved it"). Session-server outboxes (Network Transport D9) are retry queues, not storage.
19. **Record catalogue.** Every server-owned record type, the system that owns its meaning, and the storage rules this system enforces: Added 2026-11-05: the player record stores `frames_prev` and `frames_ts_ms`, written in the photo commit (Camera Model F18); `loadout` holds the fields in Inventory Rule 14 with `phone_item_id NOT NULL`; the field lease is set at ticket issue (Inventory Rules 21, 24).

| Record | Meaning owned by | Key | Uniqueness / integrity constraints enforced here | Mutable? |
|---|---|---|---|---|
| `account` | this system | `account_id` | — | state, `token_epoch`, `last_seen_at` |
| `identity` | this system | (`kind`, `value`) | unique per (`kind`, `value`): one email or OAuth subject → one account | delete only |
| `profile` | this system | `account_id` | unique (`display_name`, `tag`) | name, language |
| `refresh_family` | this system | `family_id` | ≤ `MAX_DEVICES` per account | rotate, revoke |
| `wallet` | Currency & Wallet | `wallet_id` | one player wallet per account; `cached_balance ≥ BALANCE_FLOOR` (F3) | `cached_balance` only, inside a ledger transaction |
| `wallet_owner` | this system | `wallet_id` | links a player wallet to an `account_id` | delete on purge |
| `ledger_entry` | Currency & Wallet | `entry_id` | **append-only**; unique (`wallet_id`, `rid`, `leg`); legs of one `tx_id` sum to 0 (F3) | never |
| `item` (gear instance) | Inventory & Loadout; Gear Catalog for `model_id` | `item_id` | unique (`account_id`, `acquired_rid`, `acquired_slot`); unique (`model_id`, `season_id`, `serial`) when serialised | owner, condition, state | <!-- 2026-11-05: see Rule 30 for the amended key; `catalog_id` renamed `model_id`; no tier column. -->
| `loadout` | Inventory & Loadout | `account_id` | equipped items must be owned by the same account | yes |
| `photo` | Gallery; Photo Recipe for `recipe`; Photo Scoring for `score` | `photo_id` | unique (`capture_rid`); `recipe` and `recipe_version` immutable; `score` and `scoring_version` frozen at capture; `image_tier` is a tier ID | owner, gallery state, edition fields |
| `roll` | Capture Tier Resolution | `rid` | unique (`rid`); written **before** the result is sent (Network Transport Rule 27) | never |
| `counter` (supply, image serial, edition) | Supply Caps, First-Claim, Photo Pricing | (`counter_kind`, `scope_id`) | `value ≤ cap`; only incremented inside the transaction that issues the serial | increment only |
| `claim` | First-Claim & Image Serials | (`appearance_id`) | unique per appearance (or per joint claim group) | never |
| `idempotency` | Network Transport (F9) | (`account_id`, `rid`) | stores the response; kept `IDEMPOTENCY_WINDOW_S` | expires |
| `moderation_flag` | Moderation & Reporting | `flag_id` | — | status |
| `deletion_journal` | this system | `account_id` | one per deleted account; replayed after any restore (Rule 43) | never |
| `schema_meta` | this system | singleton | `schema_version`, `restore_epoch`, last migration | on migration/restore |

20. **Only tier IDs are stored, never ranks** (Rarity Tier Ladder Core Rule 2). Every tier column (`photo.image_tier`, `roll.result_tier`, supply counter scope) holds the ladder's string ID. A column holding a rank integer is a schema defect. Writes re-parse every tier ID with the ladder's `parse`; `ERR_UNKNOWN` or `ERR_UNSET` aborts the transaction. Gear items store no tier at all (2026-11-05): tier is read from the catalog by `model_id`.
21. **No null tier at rest.** A tier column that a record requires is `NOT NULL`. Legacy or migrated data with a null or empty tier is never given a runtime default; the migration that encounters it assigns an explicit tier (usually C) in a **logged** migration step, as the Rarity Tier Ladder edge case requires (Rule 43).
22. **Recipes are opaque here.** This system stores the recipe bytes and `recipe_version` exactly as the session server assembled them, enforces the size cap (Network Transport F3, 512 B), and never rewrites them. Reading old versions is Photo Recipe & Re-render's job.
23. **Frozen score.** The score, its parts and `scoring_version` are stored at capture and never recomputed in place. A re-score for a dispute writes a new audit row; it does not overwrite (High-Risk Systems: "freeze the score at capture time with the version that produced it").
24. **Author and owner are separate.** A photo stores `author_ref` (who took it; a `profile` reference) and `owner_account_id` (who holds it now). In MVP they are always equal. When player trading arrives (Alpha, open question B2), only the owner changes.
25. **Server time only.** Every timestamp is set by the meta service clock in UTC. No client-supplied time is stored.

**D. Transaction integrity**

26. **One action, one transaction.** Every state-changing request (buy, sell, equip, a saved shot, a claim, a trade confirm, a deletion step) runs as **one** database transaction that writes all its rows (ledger legs, cached balance, items, counters, photo, roll link, idempotency record) or none. A request that fails any check commits nothing and returns an error code.
27. **Double-entry, append-only ledger (D6).** Money only moves as a **ledger transaction**: two or more legs whose amounts sum to zero (F3). The counterparty of every faucet or sink is a named **system wallet** (e.g. `faucet:npc_sale`, `faucet:start_grant`, `sink:gear_shop`, `sink:repair`); a player-to-player transfer has two player legs. Ledger entries reference `wallet_id`, not `account_id`; the `wallet_owner` link is what connects a wallet to a person (this is what makes deletion possible without editing the ledger, Rule 44). Amounts are 64-bit integers in the currency's smallest unit; floating-point money is forbidden.
28. **Cached balance, same transaction.** Each wallet row holds `cached_balance`, updated in the same transaction as its ledger legs. Reads use the cached balance; reconciliation (Rule 33) proves it equals the ledger sum.
29. **Corrections are new entries.** A wrong ledger entry is never edited or deleted. A correction is a new ledger transaction (kind `adjustment`, with a reason and the operator who made it). The same rule applies to items and photos: an operator grant or removal is an audited transaction, never a direct row edit.
30. **Permanent effect keys (D10).** Every effect row carries the `rid` that caused it under a **permanent** unique constraint (`photo.capture_rid`, `roll.rid`, `item.acquired_rid`, `ledger_entry (wallet_id, rid, leg)`). The idempotency record (Network Transport F9) only caches the **response** for `IDEMPOTENCY_WINDOW_S`. If a retry arrives after the window (for example a session-server outbox draining after a long meta outage), the unique constraint makes the insert a no-op, and the server rebuilds the original response from the existing rows. A retry can therefore never duplicate an effect, however late. Amended 2026-11-05: `rid` is client-generated and only unique per account, so every permanent key is **scoped by account**: the server derives the stored key from (`account_id`, `rid`), including ledger rows on shared system wallets and `item` rows. A multi-item grant uses (`acquired_rid`, `acquired_slot`). `loadout.rev` is the effect key for equips (Inventory F5).
31. **Database constraints, not just code.** The invariants in the catalogue (balance floor, unique serials, `counter.value ≤ cap`, unique effect keys, `NOT NULL` tier IDs, equipped items owned by the same account) are enforced by the database schema itself, so a bug in a hook cannot break them. Which constraints the chosen backend can express natively **→ part of the economy integrity ADR (research §7.9)**.
32. **Short write transactions.** A write transaction makes no network call and no file I/O besides the database, and must finish within `TX_MAX_MS`. Work that is slow (sending an email, notifying a session server) happens after commit, from a post-commit queue. Transient conflicts (database busy or locked) are retried per F4; constraint violations are never retried.
33. **Nightly reconciliation.** Every `RECONCILE_INTERVAL_H` a read-only job checks: every `tx_id` sums to zero; every `cached_balance` equals its ledger sum; every supply counter equals the number of items holding a serial in that scope; every image-serial counter equals the number of photos holding one; every equipped item is owned by its loadout's account. Any mismatch **freezes economy writes for the affected wallet, item or counter scope** (reads continue), records an incident, and alerts the developer. Nothing is auto-corrected (D14). Added 2026-11-05: reconciliation also checks that `item.state` agrees with the loadout, every Bag item is owned, and each account has exactly one bound phone. Credits past `WALLET_CAP` return `ERR_WALLET_FULL`; system wallet floors cover `sink:*`, `escrow:*` and `adjust:*`; `faucet:start_grant` is once per wallet.
34. **Non-optimistic display is preserved.** This system confirms a write only after commit. The client's pending state (Network Transport Rule 30, D15) ends when this system's commit response arrives. Read-your-writes: the next read by the same account after a confirmed write reflects it.

**E. Backups and restore**

35. **Backup cadence (D7).** The meta database is snapshotted every `SNAPSHOT_INTERVAL_H` to the server's local disk using a method that produces a consistent copy of a live database (for SQLite this is the online backup API or `VACUUM INTO`; which method the chosen backend exposes is **UNVERIFIED** and **→ ADR research §7.15**). Every `OFFHOST_INTERVAL_H` the newest snapshot is compressed, encrypted and copied **off the host** (destination: Open Questions). Retention: `KEEP_HOURLY` local, `KEEP_DAILY` and `KEEP_WEEKLY` off-host (F5).
36. **Targets.** Recovery point objective (RPO): at most `SNAPSHOT_INTERVAL_H` of committed data lost while the host disk survives; at most `OFFHOST_INTERVAL_H` if the host is lost. Recovery time objective (RTO): service restored within `RTO_TARGET_H` **from the moment the developer starts the restore** (detection time is outside the target for a solo developer; F5).
37. **Backups are verified.** Every off-host copy is checked after upload (checksum match), and a full restore is rehearsed on a scratch machine every `RESTORE_DRILL_D` days: restore, run reconciliation (Rule 33), start the meta service, sign in with a test account. A backup that has never been restored is not counted as a backup.
38. **Restore procedure.** (a) Put the meta service in maintenance (all requests get `ERR_SERVICE_DEGRADED`, retryable; session servers stop accepting shots with `NOTICE service_degraded`). (b) Restore the chosen snapshot. (c) **Replay the deletion journal** (Rules 44, 48). (d) Increment `restore_epoch`. (e) Run reconciliation. (f) Leave maintenance. Session-server outbox entries that arrive afterwards are applied normally (their `rid`s are new to the restored database).
39. **Restore epoch notice.** Every meta response carries `restore_epoch`. A client that last saw a lower epoch discards its cached view, refetches wallet, inventory and gallery, and shows the restore notice once (UI Requirements). Compensation for lost items is a producer/community decision, not automatic (Open Questions).

**F. Schema migration**

40. **Versioned schema.** The database carries `schema_version`. Each migration is a numbered, forward-only script that runs inside one transaction and is logged in `schema_meta`.
41. **Migration procedure.** A deploy that changes the schema (a) takes a fresh local snapshot and confirms it, (b) enters maintenance, (c) runs pending migrations in order, (d) runs reconciliation, (e) leaves maintenance. A failed migration rolls back its transaction; the service stays on the old schema and the deploy stops. Rollback after a successful migration is a **restore of the pre-migration snapshot**, never a hand-written down-migration.
42. **Refuse to run on a newer schema.** A meta service whose code expects schema `N` refuses to start against a database at `N + 1` or higher. This prevents an old build from writing records it does not understand after a rollback of code alone.
43. **Migration rules for game data.** Migrations never rewrite `recipe`, `recipe_version`, frozen scores or `scoring_version` (Rules 22–23). A migration that touches tier columns re-parses each value with the ladder's `parse`; a null or empty legacy tier gets an explicit tier with one log line per record changed (Rule 21). A migration never stores a rank. Because client and server ship in lockstep (Network Transport D4), no migration needs to support two client versions at once.

**G. Retention and deletion**

44. **Account deletion (D3, D4, D5).** A signed-in player may request deletion. The request (a) increments `token_epoch` and revokes all refresh families except the requesting device's, (b) moves the account to `PendingDeletion`, (c) immediately hides the account's photos from leaderboards and from public galleries, and (d) cancels any open market listing or trade (Alpha) with items returned to their owners. After `DELETION_GRACE_D` days the **purge** runs in one transaction: Photos with shared crew credit are deferred to the First-Claim & Image Serials GDD, which must define how a co-credited photo survives one member's deletion. Added 2026-11-05: at purge the wallet balance is swept to `sink:account_closed`, so the money supply never counts unspendable money (Currency & Wallet D8).
    - `identity`, `profile`, `refresh_family`, `loadout`, `idempotency` and the `wallet_owner` link are deleted. The `wallet` row and its ledger entries **stay**, now owned by nobody, so every other wallet's history and the ledger's zero-sum still hold (Rule 27).
    - Photos **owned** by the account are deleted (recipe included) and their leaderboard entries removed; boards recompute and the next entries move up. Image serials those photos held are **retired**, never reissued, so "#12 of 100" stays unique forever.
    - Photos the account **authored but no longer owns** (Alpha trading) stay with their owners; their author is shown as "Former photographer" (the `author_ref` points to a tombstone profile with no name).
    - Gear the account owned: unserialised items are deleted; serialised items are **released** through Supply Caps' `release_serial` (recommended; D4) or retired if the Supply Caps GDD decides otherwise.
    - Roll records and claims are kept with the account reference replaced by the tombstone (they are audit evidence and hold no personal data).
    - A `deletion_journal` row (`account_id`, `wallet_id`, `purged_at`) is written. It holds no personal data and exists so the purge can be re-applied after a restore.
45. **Cancel within grace.** Signing in during `PendingDeletion` shows the pending-deletion screen with **Cancel deletion**. Cancelling returns the account to `Registered` (or `Guest`), restores visibility, and does not restore cancelled listings.
46. **Guest expiry.** A guest account not seen for `GUEST_IDLE_D` days is purged exactly like a deletion (Rule 44), without a grace period (nobody can be contacted). Each time a guest plays, the game shows how many days of inactivity are left and offers "Keep my progress" (attach an email).
47. **Registered accounts do not expire** for inactivity in MVP (D13). Pillar 2 promises that photos persist.
48. **Deleted data in backups.** Purged data still exists in backups taken before the purge until they age out. No backup is edited. Instead, every restore replays the deletion journal (Rule 38c), so a purged account never comes back to life. The time until purged data is gone from every copy is F8.
49. **Retention table.** Data not listed in the catalogue is kept only as long as below.

| Data | Kept for | Why |
|---|---|---|
| Account, profile, wallet, items, photos | While the account exists | Pillar 2 |
| Ledger entries | Forever (owner link removed on purge) | Zero-sum history, other players' records |
| Roll records | Forever (tombstoned on purge) | Audit of rarity outcomes (research §7.10) |
| Idempotency responses | `IDEMPOTENCY_WINDOW_S` | Network Transport F9 |
| Unused or expired sign-in codes | `OTP_TTL_S`, then deleted | Security |
| Server logs with account IDs or IP addresses | `LOG_RETENTION_D` | Debugging and abuse handling |
| Rate-limit state per IP or email | In memory; ≤ 24 h | Rule 8, Network Transport F1 |
| Moderation flags and evidence | Owned by Moderation & Reporting | Open Questions |
| Local snapshots / off-host backups | F5 retention | Recovery |
| Deletion journal | Forever | Rule 48 |

50. **Data export (D15).** From Alpha, a registered player can download their account data (profile, identities, photos with recipes and scores, items, ledger history) as one JSON file. Rate-limited to once per `EXPORT_COOLDOWN_H`.

### States and Transitions

**Account lifecycle**

| State | Meaning | Entered when | Leaves to | Can play? | Economy writes? |
|---|---|---|---|---|---|
| `Guest` | Account with no sign-in identity | "Play as guest" | `Registered` (identity attached); `PendingDeletion` (player requests); `Purged` (idle `GUEST_IDLE_D`) | Yes | Yes (no P2P trading) |
| `Registered` | Account with ≥ 1 verified identity | Code verified for a new email, or guest upgrade | `Suspended`; `PendingDeletion` | Yes | Yes |
| `Suspended` | Blocked by Moderation (temporary or permanent ban) | Moderation action | `Registered` when lifted; `PendingDeletion` (player may still request deletion) | No (`ERR_BANNED` with reason and end date) | No; data kept |
| `PendingDeletion` | Deletion requested, inside grace | Player confirms deletion | `Registered`/`Guest` on cancel; `Purged` after `DELETION_GRACE_D` | No (only the cancel screen) | No |
| `Purged` | Personal data and owned photos removed; tombstone and journal remain | Purge transaction commits | — (terminal; the `account_id` is never reused) | No | No |

A `Suspended` account that requests deletion keeps any moderation evidence for the period Moderation & Reporting defines (Open Questions); its personal data is otherwise purged on schedule.

**Refresh-token family**

| State | Entered when | Leaves to |
|---|---|---|
| `Active` | Sign-in, or a rotation issued a new token | `Rotated` (old token) on refresh; `Expired` (F6); `Revoked` |
| `Rotated` | A newer token replaced it | `Revoked` (whole family) if this token is presented again after `REFRESH_RACE_GRACE_S` |
| `Expired` | Idle or absolute limit reached | — (sign in again) |
| `Revoked` | Sign out, sign out everywhere, suspension, deletion request (except the requesting device, Rule 44a), reuse detected, `MAX_DEVICES` exceeded (oldest family) | — |

**Photo record (persistence view; gameplay states such as listed or sold are owned by Gallery)**

| State | Entered when | Leaves to |
|---|---|---|
| (not a record) | Shot validated on the session server, not yet committed; may sit in the outbox (`saved: false`) | `Saved` on commit; nothing if the session server crashes before commit (Network Transport Edge Cases) | Decided 2026-11-04: the player sees only a "developing" state here; score, tier and roll are computed and revealed only after commit, so a session crash can never lose or re-roll a result the player has seen.
| `Saved` | Commit with a new `capture_rid` | `Hidden` (owner `PendingDeletion` or moderation hold); `Transferred` (Alpha); `Removed` |
| `Hidden` | Owner requested deletion, or Moderation hold | `Saved` (cancel / hold lifted); `Removed` |
| `Transferred` | Owner changed by a trade transaction (Alpha) | `Saved` under the new owner |
| `Removed` | Owner purged, guest expired, or the owner discarded it (Gallery rules) | — (row deleted; serial retired; `capture_rid` uniqueness kept via the roll record) |

Note: because the photo row is deleted on `Removed`, the permanent de-duplication of a late outbox retry for that `rid` relies on the `roll` row (which is kept, Rule 49). A late retry whose roll exists but whose photo was removed returns "removed", never re-creates the photo.

**Item record**: `Owned` → `Equipped` (in a loadout) ↔ `Owned`; `Owned` → `Escrowed` (Alpha trade) → `Owned` (new or same owner); any → `Retired` (broken, merged, owner purged and not released). Rules for breaking and merging are owned by Gear Condition and Gear Crafting.

**Meta service operating states**: `Serving` → `Maintenance` (migration, restore; every request `ERR_SERVICE_DEGRADED`, retryable) → `Serving`. `Serving` → `FrozenScope` is not a service state but a per-scope flag set by reconciliation (Rule 33).

### Interactions with Other Systems

| System | This system provides | This system receives | Contract notes |
|---|---|---|---|
| **Network Transport & Server Authority** | Access/refresh tokens and their lifetimes (its Rule 32); ticket issue backed by an account; durable commit of every service-path write; permanent effect keys; `restore_epoch` | `rid` on every state-changing request; idempotency window F9; service-only path (Rule 4); outbox retries (D9) | Commit happens before `saved: true` (its Rule 29). Its "newest tab wins" (D7) and "never optimistic" (D15) are unchanged. Late outbox retries are safe because of Rule 30 here. New error codes for its closed list: `ERR_IDENTITY_IN_USE`, `ERR_CODE_INVALID`, `ERR_CODE_EXPIRED`, `ERR_INSUFFICIENT_FUNDS`, `ERR_QUOTA`, `ERR_ACCOUNT_PENDING_DELETION`, `ERR_SCOPE_FROZEN` (→ protocol ADR). |
| **Rarity Tier Ladder** | Storage of tier IDs only; logged migration of null tiers | `parse`, identity table | Rules 20, 21, 43. A rank column is a defect. |
| **Gear Catalog & Specs** | Item rows keyed by `catalog_id` | Catalog IDs; which items are serialised | Specs are read from catalog data, never copied into item rows (except instance fields such as condition). |
| **Inventory & Loadout** | Atomic item writes; loadout ownership constraint | Equip rules, mount validation | Equip is a transaction with a `rid`. |
| **Currency & Wallet** | Ledger storage, zero-sum and floor constraints, cached balance, reconciliation | List of system wallets (faucets, sinks), `BALANCE_FLOOR` (0 unless open question B4 adds debt) | The faucet/sink budget table lives in that GDD; the ledger kinds it names become system wallets here. |
| **Photo Recipe & Re-render** | Opaque, immutable recipe storage; size cap | Recipe bytes and `recipe_version` | Migrations never rewrite recipes (Rule 43). |
| **Photo Scoring** | Frozen score and `scoring_version` storage | Score and parts | Re-scores are new audit rows. |
| **Capture Tier Resolution** | `roll` rows, written before the result is sent | Roll inputs and result | `roll.rid` is the permanent de-duplication anchor for shots. |
| **Gallery** | Photo rows, owner/author split, hide/remove on deletion | Gameplay limits (storage sink), edition and sold states, discard rules | Gallery's gameplay limit must be ≤ `MAX_PHOTO_RECORDS` (F1). |
| **Photo Pricing & NPC Clients, Gear Shop** | Transactions combining ledger legs and item/photo changes | Prices, which system wallets to use | One sale or purchase = one transaction (Rule 26). |
| **Starting Choice** | One-time grant guarantee per `account_id` (not per identity) | The grant contents | Guest upgrade never re-grants (Rule 4). |
| **Leaderboards** (VS) | Hide on `PendingDeletion`; remove on purge; "Former photographer" for authored-not-owned photos | Board queries | Boards recompute after removal. |
| **Daily Themes & Player Judging** (VS) | `Registered`-only gate for voting and entry | — | Guests cannot vote (anti-collusion with throwaway accounts). |
| **Found Photos** (VS) | Storage of placed photo references | Placement records | A placed photo of a purged owner disappears with it. |
| **Expedition Rooms, Co-op Crew Roles** (Alpha) | Account identity for seats; nothing durable in rooms | Room membership | Rooms hold no durable state (Rule 18). |
| **Photographer Reputation** (Alpha) | Storage of reputation per account | Reputation rules | Deleted with the account. |
| **Supply Caps & Gear Serials** (Alpha) | Counter rows, unique serial constraint, `release_serial` call on purge | Cap scopes, release policy | D4. |
| **First-Claim & Image Serials** (Alpha) | Claim rows, image-serial counters, retirement on purge | Claim rules | Serials are never reissued (Rule 44). |
| **Seasons** (Alpha) | `season_id` scoping of counters and serials | Season boundaries | — |
| **Player-to-Player Trading & Market** (Alpha) | Escrow state, two-sided atomic commit, cancellation on deletion | Trade rules | Both legs and both item moves in one transaction. Guests cannot trade (Rule 3). |
| **Moderation & Reporting** (Alpha) | `Suspended` state, `token_epoch` revocation, flag storage | Suspension decisions, evidence retention policy | Flags from Network Transport kicks are stored here. |
| **Economy Telemetry** (Alpha) | Read-only ledger aggregates by system wallet (money supply identity, F3) | — | Aggregates only; no personal data leaves the meta service. |
| **Darkroom & Gallery UI, Shop/Sell/Inventory UI, Settings** | Sign-in, guest, account, deletion and restore states | — | See UI Requirements. |

## Formulas

All constants are tuning knobs (Tuning Knobs) held in the meta service's configuration, not in code. Storage figures are **estimates** to be replaced by measurements in the first spike.

### F1. Storage per account and the technical photo quota

The account_bytes formula is defined as:

`account_bytes = n_photos × PHOTO_ROW_B + n_ledger_tx × LEDGER_TX_B + n_items × ITEM_ROW_B + n_rolls × ROLL_ROW_B + ACCOUNT_BASE_B`; a new photo commit is refused with `ERR_QUOTA` if `n_photos ≥ MAX_PHOTO_RECORDS`.

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| n_photos | int | 0–MAX_PHOTO_RECORDS | measured | Photo records the account owns |
| PHOTO_ROW_B | int (bytes) | 600–1200 | estimate: recipe ≤ 512 B (Network Transport F3) + IDs, score parts, tier, timestamps ≈ 200 B | Bytes per photo row |
| n_ledger_tx | int | ≥ 0 | measured | Ledger transactions touching this wallet |
| LEDGER_TX_B | int (bytes) | 150–400 | estimate: 2 legs × ~100 B | Bytes per ledger transaction (both legs) |
| n_items | int | ≥ 0 | measured | Item rows owned |
| ITEM_ROW_B | int (bytes) | 150–500 | estimate | Bytes per item row |
| n_rolls | int | ≥ 0 | measured | Roll records (one per scored shot, kept forever) |
| ROLL_ROW_B | int (bytes) | 80–250 | estimate | Bytes per roll row |
| ACCOUNT_BASE_B | int (bytes) | 1000–4000 | estimate | Account, identity, profile, wallet, loadout |
| MAX_PHOTO_RECORDS | int | 1000–50 000 | config (default 10 000) | Technical safety cap, well above Gallery's gameplay limit |

**Output Range:** unbounded above in principle; in practice bounded by `MAX_PHOTO_RECORDS` for photos, while rolls and ledger grow with play time. At `MAX_PHOTO_RECORDS` with defaults the photo part is ≈ 7.2 MB.
**Example (placeholder heavy player after ~50 h):** 600 photos × 720 + 1 500 tx × 200 + 30 items × 300 + 3 000 rolls × 150 + 2 048 = 432 000 + 300 000 + 9 000 + 450 000 + 2 048 ≈ **1.19 MB**. Rolls are the largest single item; if storage ever matters, roll rows for discarded C-tier shots are the first candidate for a shorter retention (Decisions to confirm D16).

### F2. Database size

The db_bytes formula is defined as:

`db_bytes = (Σ over accounts of account_bytes) × INDEX_FACTOR + GLOBAL_B`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| account_bytes | int (bytes) | F1 | calculated | Per-account rows |
| INDEX_FACTOR | float | 1.2–2.0 | estimate (default 1.4) | Indexes and page overhead |
| GLOBAL_B | int (bytes) | ≥ 0 | measured | Counters, system wallets, schema meta, journal |

**Output Range:** ≥ `GLOBAL_B`; unbounded, grows linearly with accounts and play time.
**Example:** MVP playtest, 100 accounts averaging 1.19 MB → `100 × 1.19 MB × 1.4 ≈ 167 MB`. At 1 000 such accounts: ≈ **1.67 GB**. Both fit easily on one small VM disk; the cost that grows is backup egress (F5).

### F3. Ledger invariants and money supply

The ledger formula is defined as:

`Σ_{e ∈ tx} e.amount = 0` for every ledger transaction `tx`; `balance(w) = Σ_{e : e.wallet = w} e.amount`; `cached_balance(w) = balance(w)` (checked by reconciliation); a transaction is accepted only if `balance_after(w) ≥ BALANCE_FLOOR(w)` for every player wallet `w` it touches; and the money supply is `M = Σ_{player wallets} balance(w) = − Σ_{system wallets} balance(s)`.

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| e.amount | int64 (currency minor units) | −2^62 to 2^62 | calculated | Signed amount of one leg |
| tx | set of legs | ≥ 2 legs | request handler | One ledger transaction |
| w | wallet ID | player or system wallet | `wallet` table | Wallet being summed |
| BALANCE_FLOOR(w) | int64 | 0 for player wallets (MVP); unbounded below for faucet system wallets | Currency & Wallet | Lowest legal balance |
| M | int64 | ≥ 0 | calculated | Total money held by players |

**Output Range:** accept or `ERR_INSUFFICIENT_FUNDS` (no rows written). `M` is exact by construction, so Economy Telemetry can read faucet and sink totals directly from system wallet balances.
**Example:** an NPC buys a photo for 120: legs `faucet:npc_sale −120`, `player +120` (sum 0). The player then tries to buy a 300 lens with balance 250: `250 − 300 = −50 < 0`, rejected, nothing written. After a 200 lens purchase: legs `player −200`, `sink:gear_shop +200`; player balance 50; `M` fell by 200 and `sink:gear_shop` shows 200 absorbed.

### F4. Transaction retry

The tx_retry formula is defined as:

`delay(n) = min(TX_RETRY_CAP_MS, TX_RETRY_BASE_MS × 2^(n−1)) × (1 + TX_RETRY_JITTER × u)` before attempt `n + 1`, for `n = 1 … TX_MAX_ATTEMPTS − 1`; the request fails with `ERR_SERVICE_DEGRADED` (retryable, same `rid`) when attempts are exhausted or elapsed time would exceed `META_DEADLINE_MS`. Only transient conflicts (database busy or locked) are retried.

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| n | int | 1–TX_MAX_ATTEMPTS−1 | calculated | Failed attempts so far |
| TX_RETRY_BASE_MS | int (ms) | 5–100 | config (default 20) | First delay |
| TX_RETRY_CAP_MS | int (ms) | 100–2000 | config (default 500) | Largest single delay |
| TX_RETRY_JITTER | float | 0–0.5 | config (default 0.25) | Spread to avoid lockstep retries |
| u | float | −1 to 1 | server random, uniform | Jitter sample |
| TX_MAX_ATTEMPTS | int | 1–10 | config (default 5) | Total attempts including the first |
| TX_MAX_MS | int (ms) | 10–200 | config (default 50) | Longest allowed write transaction (Rule 32) |
| META_DEADLINE_MS | int (ms) | 500–5000 | config (default 2000) | Server-side budget for one meta request |

**Output Range:** each delay in `[TX_RETRY_BASE_MS × (1 − J), TX_RETRY_CAP_MS × (1 + J)]`.
**Example (u = 0):** delays 20, 40, 80, 160 ms → 300 ms of waiting; with 5 attempts at the 50 ms cap, worst case ≈ 300 + 250 = **550 ms**, inside Network Transport's p95 ≤ 1 s for buy/sell. A duplicate-serial constraint violation is not retried: it returns its error at once.

### F5. Backup cadence, storage, egress and RTO

The backup formula is defined as:

`RPO_host_ok = SNAPSHOT_INTERVAL_H`; `RPO_host_lost = OFFHOST_INTERVAL_H`; `backup_B = db_bytes × COMPRESS_RATIO`; `local_store_B = backup_B × KEEP_HOURLY`; `offhost_store_B = backup_B × (KEEP_DAILY + KEEP_WEEKLY)`; `offhost_egress_month_B = backup_B × 720 / OFFHOST_INTERVAL_H`; `RTO = t_provision + backup_B / restore_bw + t_verify ≤ RTO_TARGET_H`.

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| SNAPSHOT_INTERVAL_H | float (h) | 0.25–24 | config (default 1) | Local snapshot cadence |
| OFFHOST_INTERVAL_H | float (h) | 1–168 | config (default 24) | Off-host copy cadence |
| db_bytes | int (bytes) | F2 | calculated | Live database size |
| COMPRESS_RATIO | float | 0.2–0.8 | estimate (default 0.35; measure) | Compressed size / raw size |
| KEEP_HOURLY | int | 6–72 | config (default 24) | Local snapshots kept |
| KEEP_DAILY / KEEP_WEEKLY | int | 3–30 / 0–12 | config (default 7 / 4) | Off-host copies kept |
| 720 | constant (h) | — | 30 days | Hours per month |
| t_provision | float (h) | 0.25–3 | measured in drills | Scripted deploy of a fresh host |
| restore_bw | float (B/s) | ≥ 1 MB/s | measured | Download speed from off-host storage |
| t_verify | float (h) | 0.1–1 | measured in drills | Reconciliation + smoke sign-in |
| RTO_TARGET_H | float (h) | 1–24 | config (default 4) | Target from start of restore |

**Output Range:** RPO 1 h (host intact) / 24 h (host lost) with defaults; storage and egress linear in `db_bytes`.
**Example A (MVP, 100 accounts):** `db_bytes` 167 MB → `backup_B ≈ 58 MB`; local 24 × 58 MB ≈ **1.4 GB**; off-host 11 × 58 MB ≈ **0.64 GB**; egress 30 × 58 MB ≈ **1.75 GB/month**. RTO: provision 1 h + 58 MB at 10 MB/s (≈ 6 s) + verify 0.5 h ≈ **1.5 h ≤ 4 h**.
**Example B (1 000 accounts):** `backup_B ≈ 0.58 GB`; local ≈ 14 GB; off-host ≈ 6.4 GB; egress ≈ **17.5 GB/month**, about the same as all gameplay egress (Network Transport F14, ≈ 17.9 GB/month at 3 concurrent players). At that scale, full daily copies should give way to incremental or continuous replication (D7 option C) before the free host's limits are hit.

### F6. Token lifetimes

The token_expiry formula is defined as:

`access_expires_at = issued_at + ACCESS_TOKEN_TTL_S`; `refresh_expires_at = min(last_refresh_at + REFRESH_IDLE_D × 86 400, family_created_at + REFRESH_ABSOLUTE_D × 86 400)`; an access token is valid only if `now < access_expires_at` **and** `token.epoch = account.token_epoch`.

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| ACCESS_TOKEN_TTL_S | int (s) | 300–86 400 | config (default 3 600) | Access token lifetime |
| REFRESH_IDLE_D | int (days) | 1–90 | config (default 30) | Sliding idle limit |
| REFRESH_ABSOLUTE_D | int (days) | 7–365 | config (default 90) | Hard limit for a token family |
| REFRESH_RACE_GRACE_S | int (s) | 0–30 | config (default 10) | Window in which a just-rotated token still returns the same new pair |
| token_epoch | int | ≥ 0 | `account` row | Incremented on revoke-all events (Rule 16) |

**Output Range:** timestamps; validity is boolean.
**Example:** sign-in on day 0; the player plays every few days. Each refresh pushes the idle limit forward 30 days, but on day 90 the absolute limit is reached and a new code is needed. A guest's refresh family has the same limits: a guest who plays at least once every 30 days keeps the token until day 90, when it is re-issued silently (guests have no identity to re-verify, so a guest family is **renewed** on refresh at the absolute limit instead of expiring; the protection for guests is `GUEST_IDLE_D`, F8).

### F7. Sign-in code guessing bound

The otp_guess formula is defined as:

`p_day ≤ OTP_FAILS_PER_DAY / 10^OTP_DIGITS`; `p_horizon ≈ days × p_day` (for small values)

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| OTP_DIGITS | int | 6–8 | config (default 6) | Code length |
| OTP_TTL_S | int (s) | 120–1 800 | config (default 600) | Code lifetime |
| OTP_MAX_ATTEMPTS | int | 3–10 | config (default 5) | Tries per code |
| OTP_SENDS_PER_HOUR | int | 1–10 | config (default 3) | Codes per address per hour |
| OTP_FAILS_PER_DAY | int | 5–50 | config (default 10) | Failed tries per address per UTC day across all codes |
| days | int | ≥ 1 | attack duration | Days an attacker keeps trying one address |

**Output Range:** probability in [0, 1].
**Example:** defaults → `p_day = 10 / 10^6 = 1 × 10^−5`; over a year of continuous attack on one address `≈ 365 × 10^−5 ≈ 0.37 %`, and the victim receives every code email meanwhile. With 8 digits the year figure is ≈ 0.0037 %. Flag for security-engineer review (Open Questions).

### F8. Retention and erasure timeline

The erasure formula is defined as:

`purge_at = requested_at + DELETION_GRACE_D`; `guest_purge_at = last_seen_at + GUEST_IDLE_D`; `erased_everywhere_at = purge_at + max_backup_age`, where `max_backup_age = max(KEEP_HOURLY × SNAPSHOT_INTERVAL_H / 24, KEEP_DAILY × OFFHOST_INTERVAL_H / 24, KEEP_WEEKLY × 7)` days.

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| DELETION_GRACE_D | int (days) | 0–30 | config (default 14) | Cancel window |
| GUEST_IDLE_D | int (days) | 7–180 | config (default 30) | Guest inactivity before purge |
| GUEST_WARN_D | int (days) | 1–GUEST_IDLE_D | config (default 7) | When the in-game countdown turns prominent |
| KEEP_* , *_INTERVAL_H | — | F5 | config | Backup retention |
| LOG_RETENTION_D | int (days) | 7–90 | config (default 14) | Logs with account IDs or IPs |

**Output Range:** dates; `erased_everywhere_at − requested_at` = grace + oldest backup.
**Example:** defaults → `max_backup_age = max(1, 7, 28) = 28` days; a deletion requested on 1 March is purged on 15 March and is gone from every backup by 12 April (42 days). Any restore before then replays the deletion journal, so the account never reappears.

## Edge Cases

**Sign-in and identity**

- **If a player requests a code for an address with no account**: the response is the same as for an existing account; a code is sent; the account is created only when the code is verified.
- **If a code is entered after `OTP_TTL_S`**: `ERR_CODE_EXPIRED`; "That code has expired. Send a new one."; the failure does not count toward `OTP_FAILS_PER_DAY`.
- **If a wrong code is entered `OTP_MAX_ATTEMPTS` times**: the code is void; `ERR_CODE_INVALID`; the player must request a new one (subject to `OTP_SENDS_PER_HOUR`).
- **If `OTP_FAILS_PER_DAY` is reached for an address**: code sign-in for it returns `ERR_RATE_LIMITED` until 00:00 UTC; existing signed-in devices are unaffected.
- **If the email service is down or its free daily limit is used up**: "We can't send codes right now. You can keep playing as a guest." The send request returns `ERR_SERVICE_DEGRADED`; nothing is stored; guests are unaffected.
- **If a guest attaches an email that already has an account**: `ERR_IDENTITY_IN_USE`; the game offers "Sign in to that account" (the guest stays on this device until it expires) or "Use a different email". No merge.
- **If a player loses access to their email address**: there is no other recovery path in MVP (no passwords, no security questions). A second identity (OAuth, VS) is the mitigation; support-assisted recovery is an Open Question.
- **If a display name fails the block list**: rejected with `ERR_OUT_OF_RANGE` naming the field; the previous name stays.

**Tokens**

- **If two requests from the same tab refresh at once**: the second, within `REFRESH_RACE_GRACE_S`, receives the same new pair; no theft is detected.
- **If an old (rotated) refresh token is presented after the grace**: the whole family is revoked; every device using it must sign in again; a security log entry is written.
- **If an access token expires mid-play**: the next meta request gets `ERR_AUTH_EXPIRED`; the client refreshes and retries with the same `rid` (Network Transport retryable codes); the player sees nothing.
- **If a ninth device signs in with `MAX_DEVICES = 8`**: the least recently used family is revoked.
- **If browser storage is cleared on a guest's only device**: the guest account is unreachable; it is purged after `GUEST_IDLE_D`. This is the documented cost of guest play and is why the game keeps prompting "Keep my progress" (UI).

**Transactions and integrity**

- **If two purchases from two devices race for the last coins**: the database serialises them; the first commits; the second fails with `ERR_INSUFFICIENT_FUNDS`; no negative balance is ever written.
- **If two buyers race for the last serial of a capped item**: the counter's `value ≤ cap` constraint lets exactly one commit; the other gets the Supply Caps "sold out" outcome; no serial is issued twice.
- **If a session-server outbox retries a photo write after `IDEMPOTENCY_WINDOW_S`**: the `capture_rid` (or `roll.rid`) unique constraint turns the insert into a no-op; the server rebuilds the response from the existing rows and returns `saved: true` with the original photo; no duplicate.
- **If a late retry arrives for a photo that has since been removed** (owner discarded it, or the owner was purged): the roll row still exists, so the response is "removed"; the photo is not re-created.
- **If a database write is busy**: retried per F4; if the deadline passes, `ERR_SERVICE_DEGRADED` (retryable, same `rid`); the client stays in its pending state and retries.
- **If a hook or handler throws halfway through an action**: the transaction rolls back; no partial rows exist; the error is logged with `rid`.
- **If reconciliation finds a mismatch** (e.g. cached balance 500, ledger sum 480): economy writes for that wallet are frozen (`ERR_SCOPE_FROZEN` on writes; reads continue showing the ledger-derived 480 with a "being checked" note); the developer is alerted; any fix is an audited adjustment transaction (Rule 29).
- **If the server clock jumps backwards**: timestamps are display and retention inputs only, never ordering keys; ordering uses database sequence IDs, so no integrity rule depends on wall-clock order.
- **If a write carries an unknown or null tier ID**: the transaction aborts with `ERR_UNKNOWN` / `ERR_UNSET`; nothing is written (Rule 20).
- **If an account reaches `MAX_PHOTO_RECORDS`**: the session server is told before the shot is consumed (the quota is part of the ticket's session config), and the shutter shows "Gallery full" (Gallery owns the wording and the discard flow); no photo is lost after being shown.

**Deletion and retention**

- **If a player requests deletion while a shot is in flight**: the in-flight shot commits normally (Network Transport Rule 28); it is then hidden and purged with everything else.
- **If a player requests deletion while holding a top-100 leaderboard photo**: it is hidden immediately; at purge it is removed and the board recomputes; the warning in the deletion flow names how many leaderboard entries will be lost.
- **If a deleted account authored photos now owned by others (Alpha)**: those photos stay; author shown as "Former photographer"; their serials stay valid.
- **If a player signs in during the grace period**: the pending-deletion screen appears; **Cancel deletion** restores the account; otherwise the player can only sign out.
- **If a suspended account requests deletion**: deletion proceeds on schedule; moderation evidence is kept as Moderation & Reporting defines (Open Questions).
- **If a guest returns on day `GUEST_IDLE_D − 1`**: `last_seen_at` resets; the countdown restarts.
- **If a backup taken before a purge is restored**: the deletion journal is replayed before the service leaves maintenance; the purged account stays purged.

**Backups, restore and migration**

- **If the host disk is lost**: restore the newest off-host copy (up to `OFFHOST_INTERVAL_H` of data lost), replay the journal, bump `restore_epoch`; clients see the restore notice.
- **If a restore rolls back purchases or photos**: those records are simply gone; outbox retries from session servers may re-commit very recent shots; serials issued after the snapshot may be reissued to other players later (the old holder's record no longer exists). Compensation is a manual, announced decision (Open Questions).
- **If an off-host upload fails or its checksum differs**: the copy is marked failed; the next cadence retries; two consecutive failures alert the developer; the local snapshots are untouched.
- **If a migration fails**: its transaction rolls back, the service stays on the old schema and the old build, and the deploy stops (Rule 41).
- **If an old build is started against a migrated database**: it refuses to start (Rule 42).
- **If a migration finds a legacy record with a null tier**: it writes an explicit tier (usually C) and one log line per record changed; it never leaves the null in place and never adds a runtime default.

## Dependencies

**Upstream (this system depends on):**

| System / dependency | Hard / soft | Interface | Status |
|---|---|---|---|
| Network Transport & Server Authority | Hard | `rid` and idempotency (Rules 21, 27, F9), service-only path (Rule 4), tickets/resume (Rules 33–35), outbox (D9), auth handoff (Rule 32), error code list | Designed (binding). Its Interactions row for this system already exists. |
| Rarity Tier Ladder | Hard | `parse`, tier IDs, null-tier migration rule | Designed. That GDD does not yet list this system as a dependent; it should (not edited here). |
| Meta backend product | Hard | auth, transactions, constraints, backup method | ADR not written (research §7.3; PocketBase candidate) |
| Email-sending service (free) | Hard for registered accounts; none for guests | send code | Not chosen (Open Questions) |
| Off-host backup destination (free) | Hard for RPO_host_lost | upload/download | Not chosen (Open Questions) |
| Currency & Wallet | Soft (for system wallet list, `BALANCE_FLOOR`) | ledger kinds | Not started |
| Gallery | Soft (for gameplay limits and discard) | limits ≤ `MAX_PHOTO_RECORDS` | Not started |

**Downstream (systems that depend on this one; systems index lists 10):** Inventory & Loadout (10), Currency & Wallet (11), Gallery (15), Daily Themes & Player Judging (23), Leaderboards (24), Expedition Rooms (29), Photographer Reputation (30), Player-to-Player Trading & Market (37), Moderation & Reporting (39), plus Starting Choice (14), Photo Pricing (16), Gear Shop (17), Supply Caps (32), First-Claim (34), Seasons (35) and Economy Telemetry (41) through the record catalogue. The systems index does not list Starting Choice, Supply Caps, First-Claim or Seasons as depending on this system even though they persist records here; the index should consider adding them (not edited here).

**Bidirectional note:** every downstream GDD, when authored, must list "depends on Accounts & Server Persistence" and name the records (Rule 19) and rules it relies on.

## Tuning Knobs

| Knob | Default | Safe range | Affects | Too low / too high |
|---|---|---|---|---|
| `OTP_DIGITS` / `OTP_TTL_S` / `OTP_MAX_ATTEMPTS` | 6 / 600 s / 5 | 6–8 / 120–1800 / 3–10 | Sign-in security vs friction (F7) | Too short or loose: guessable. Too long: typing errors; too-short TTL fails slow mail |
| `OTP_SENDS_PER_HOUR` / `OTP_FAILS_PER_DAY` | 3 / 10 | 1–10 / 5–50 | Abuse of the mail quota; guessing (F7) | Too low: honest players locked out after typos. Too high: guessing and mail-quota drain |
| `ACCESS_TOKEN_TTL_S` | 3 600 | 300–86 400 | Revocation latency vs refresh traffic | Mostly moot because of `token_epoch`; too low adds refresh traffic |
| `REFRESH_IDLE_D` / `REFRESH_ABSOLUTE_D` | 30 / 90 | 1–90 / 7–365 | How often players re-enter a code | Too short: annoying. Too long: a stolen token lasts |
| `REFRESH_RACE_GRACE_S` | 10 | 0–30 | False theft detection | 0: parallel requests revoke families. Too high: wider replay window |
| `MAX_DEVICES` | 8 | 2–20 | Concurrent signed-in browsers | Too low: players signed out on a new device. Too high: more tokens to steal |
| `SERVICE_CRED_ROTATE_D` | 90 | 7–365 | Session-server credential exposure | — |
| `NAME_MIN_LEN` / `NAME_MAX_LEN` / `NAME_CHANGE_COOLDOWN_D` | 3 / 20 / 30 | 1–5 / 12–32 / 0–90 | Display names on boards | Too long: UI overflow on leaderboards |
| `GUEST_IDLE_D` / `GUEST_WARN_D` | 30 / 7 | 7–180 / 1–30 | Guest lifetime; storage | Too short: casual returners lose work. Too long: abandoned guests accumulate |
| `DELETION_GRACE_D` | 14 | 0–30 | Regret window vs speed of erasure | 0: no recovery from mistakes or a stolen session. Too long: weaker erasure promise |
| `MAX_PHOTO_RECORDS` | 10 000 | 1 000–50 000 | Storage safety cap (F1) | Must stay above Gallery's gameplay limit |
| `TX_MAX_MS` / `TX_RETRY_BASE_MS` / `TX_RETRY_CAP_MS` / `TX_RETRY_JITTER` / `TX_MAX_ATTEMPTS` / `META_DEADLINE_MS` | 50 / 20 / 500 / 0.25 / 5 / 2 000 | F4 ranges | Write latency under contention | Too few attempts: spurious failures. Too many: requests hang past the 1 s feel budget |
| `RECONCILE_INTERVAL_H` | 24 | 1–168 | How fast drift is caught | Too rare: a defect spreads before it is frozen |
| `SNAPSHOT_INTERVAL_H` / `OFFHOST_INTERVAL_H` | 1 / 24 | 0.25–24 / 1–168 | RPO (F5) | Too rare: more data lost. Too frequent: disk and egress (F5) |
| `KEEP_HOURLY` / `KEEP_DAILY` / `KEEP_WEEKLY` | 24 / 7 / 4 | F5 ranges | Backup storage; erasure timeline (F8) | Too few: no clean point before a slow-spreading bug. Too many: storage and slower erasure |
| `COMPRESS_RATIO` | 0.35 (measure) | 0.2–0.8 | Backup size estimate | — |
| `RTO_TARGET_H` / `RESTORE_DRILL_D` | 4 / 30 | 1–24 / 7–90 | Recovery promise; drill frequency | — |
| `LOG_RETENTION_D` | 14 | 7–90 | Debug window vs personal data held | Too long: more personal data (IPs) held |
| `EXPORT_COOLDOWN_H` | 24 | 1–168 | Server load from exports (Alpha) | — |

## Visual/Audio Requirements

Minimal presentation; the art bible owns the look. Tone confirmed as cozy and reflective (game concept), so all account messages are calm and reassuring.

- Sign-in and account screens use the standard menu panel style; no new art beyond a small envelope icon for "code sent" and a shield or lock icon for the account panel (SVG UI, suitable for `/asset-forge`).
- A **guest badge** (small "Guest" chip next to the display name) and a soft **"Keep my progress"** banner. Colour is never the only cue.
- A **restore notice** and a **pending-deletion** screen in the same calm style.
- Audio: no alarm sounds. Optional soft confirmation chime when an account is saved (guest upgrade), owned by Audio: SFX & Ambience.

## Game Feel

| Moment | Budget | How it feels |
|---|---|---|
| First visit → photographing as a guest | ≤ 2 clicks (Play → Play as guest); guest account created in one meta request, p95 ≤ 1 s | No form stands between the player and the camera |
| Request a code | Button changes to "Sending…" ≤ 100 ms; email arrives p95 ≤ 60 s (depends on the email service; measure) | The game says where to look and offers "Send again" after 30 s |
| Enter code → signed in | p95 ≤ 1 s | Immediate; returns the player to where they were |
| Guest upgrade | p95 ≤ 1 s; nothing on screen changes except the badge and name | "Nothing moved; it's just safe now" |
| Silent token refresh | invisible | The player is never asked to sign in mid-session |
| Buy/sell commit | within Network Transport's p95 ≤ 1 s (F4 worst case 550 ms server-side) | Money moves only when it is real |
| Restore notice | once, dismissible | Honest and calm, never alarming |

## UI Requirements

All text is localisation keys; wording below is draft. Screens belong to the menu flow (no owner UI system exists yet in the index for account screens; the systems index should decide whether Shop, Sell & Inventory UI or a Settings screen hosts them).

- **Title / sign-in screen:** primary **Play** (continues the stored account if a token exists). With no stored token: **Play as guest** and **Sign in with email**. (VS: OAuth buttons below.)
- **Email entry:** one field, **Send code**. Neutral confirmation: "If this address can receive email, a code is on its way." Link "Use a different email".
- **Code entry:** `OTP_DIGITS` boxes, paste supported, numeric keyboard on touch devices. Errors: "That code isn't right (N tries left)", "That code has expired", "Too many tries today; try again tomorrow or keep playing as a guest". **Send again** enabled after 30 s.
- **Guest badge and "Keep my progress" banner:** visible in the gallery and after the first sale; shows days left before an idle guest is removed when fewer than `GUEST_WARN_D`. Button opens email entry and attaches the identity in place.
- **Account panel** (settings): display name + tag with **Change** (cooldown shown), sign-in identities, **Sign out**, **Sign out everywhere**, **Delete account**, (Alpha) **Download my data**. For guests, both sign-out actions are hidden: the token is the guest's only credential, so signing out would destroy the account.
- **Delete account flow:** step 1 explains what happens, with counts: "N photos will be deleted, including M on leaderboards. Gear and money will be removed. Photos you sold to other players stay with them, credited to 'Former photographer'. You have 14 days to change your mind." Step 2: type your display name to confirm, then **Delete my account** (destructive style) and **Keep my account** (default focus).
- **Pending-deletion screen** (on sign-in during grace): "Your account will be deleted on [date]." **Cancel deletion** / **Sign out**.
- **Restore notice:** "We restored the game from a backup made at [time UTC]. Anything after that may be missing. Sorry for the trouble." Single **OK**.
- **Maintenance notice:** "Aperture is being updated. Your photos and gear are safe." (Shown on `ERR_SERVICE_DEGRADED` during planned maintenance only.) During a restore, use separate copy: "We're restoring from a backup; a little recent progress may be undone."
- **Suspended screen:** reason category and end date from Moderation; **Sign out**; link to request deletion.
- Accessibility: every state has text; modals take keyboard focus; the destructive button is never the default; code boxes accept paste and screen-reader labels (AccessKit on web **UNVERIFIED**, Settings & Accessibility).

📌 **UX Flag — Accounts & Server Persistence**: sign-in, guest upgrade, account panel and deletion flow are new screens. In Pre-Production, run `/ux-design` for them and add the "type to confirm destructive action" pattern to the interaction pattern library.

## Cross-References

| Referenced document | What is used | Where |
|---|---|---|
| `design/gdd/network-transport-server-authority.md` Rules 4, 18, 21, 27–35; F9; Edge Cases (outbox, crash); D4, D7, D9, D15 | Channels, `rid`, permanent commit before `saved: true`, service-only path, tickets, newest tab wins, never-optimistic display, outbox | Rules 12–18, 26–34, 38; Interactions; Edge Cases |
| `docs/architecture/research-web-networking.md` §4.2, §5.1–5.2 | Backend options; PocketBase as candidate; Nakama alternative | Overview; ADR candidates |
| same, §6, §8 risks 2–3, §7.3/7.4/7.9/7.13/7.15 | Fragile free hosting; nightly off-host backup; economy integrity mitigations; ADR titles | Rules 26–41; F5; Open Questions |
| `design/gdd/rarity-tier-ladder.md` Core Rules 2, 9; Edge Cases (null tier, rank+ID disagree) | Tier IDs only, never ranks; explicit logged migration for null tiers | Rules 20–21, 43; AC |
| `design/gdd/systems-index.md` row 6, rationale 6, bottleneck table, A2, A13, B2, B4, B5, B6 | MVP server authority; 10 dependents; one soft currency; open questions that change records | Summary, Dependencies, Open Questions |
| `design/gdd/game-concept.md` Online play, Technical considerations, Risks, anti-pillars | Accounts and a database; trading abuse; loot-box rules; not a social-media app | Overview, Rules 2–3, 27 |

## Acceptance Criteria

Tags: **[Logic]** automated gdUnit4 unit test (suggested name) · **[Integration]** integration test or documented drill · **[UI]** retained screenshot in `production/qa/evidence/`. *(provisional)* = depends on an ADR or GDD not yet written. Fixture values come from a test config resource, except boundary tests.

**A. Identity and sign-in (Rules 1–11)**

1. [Logic] **GIVEN** 10 000 generated account IDs, **WHEN** inspected, **THEN** all are distinct, 128-bit, and no two consecutive IDs differ by a constant. `test_account_ids_random_unique_not_sequential`
2. [Logic] **GIVEN** an email with no account and one with an account, **WHEN** "send code" is requested for each, **THEN** both responses are byte-identical in status and body. `test_send_code_response_identical_for_new_and_existing`
3. [Logic] **GIVEN** a code with `OTP_MAX_ATTEMPTS = 5`, **WHEN** 5 wrong codes and then the right code are entered, **THEN** the 6th attempt returns `ERR_CODE_INVALID` and no session is issued. `test_code_void_after_max_attempts`
4. [Logic] **GIVEN** a code issued at t = 0 with `OTP_TTL_S = 600`, **WHEN** the right code is entered at 599 s and (fresh code) at 601 s, **THEN** the first succeeds and the second is `ERR_CODE_EXPIRED`. `test_code_ttl_boundary`
5. [Logic] **GIVEN** `OTP_FAILS_PER_DAY = 10`, **WHEN** the 11th failure occurs the same UTC day, **THEN** further code sign-in returns `ERR_RATE_LIMITED` until 00:00 UTC. `test_daily_fail_cap_blocks_until_utc_midnight`
6. [Logic] **GIVEN** a guest with photos, money and items, **WHEN** an unused email is attached, **THEN** `account_id`, photo IDs, wallet balance and item IDs are unchanged and no second Starting Choice grant exists. `test_guest_upgrade_in_place_no_regrant`
7. [Logic] **GIVEN** an email already attached to account B, **WHEN** guest A tries to attach it, **THEN** `ERR_IDENTITY_IN_USE` and neither account changes. `test_attach_identity_in_use_refused_no_merge`
8. [Logic] **GIVEN** a guest account, **WHEN** it requests a trade, a vote or a name change, **THEN** each is rejected and shooting, selling and buying are allowed. `test_guest_permissions_match_rule_3`
9. [Integration] **GIVEN** the account schema, **WHEN** its columns are listed, **THEN** it contains no field outside Rule 2's closed list.

**B. Tokens (Rules 12–17, F6)**

10. [Logic] **GIVEN** a refresh token R1 rotated to R2, **WHEN** R1 is presented 5 s later and again 15 s later (`REFRESH_RACE_GRACE_S = 10`), **THEN** the first returns the same pair as R2's issue and the second revokes the whole family. `test_refresh_reuse_after_grace_revokes_family`
11. [Logic] **GIVEN** an access token with epoch 3, **WHEN** the account's `token_epoch` becomes 4, **THEN** the next request with that token is `ERR_AUTH_EXPIRED`. `test_token_epoch_increment_invalidates_access_tokens`
12. [Logic] **GIVEN** a family created day 0 and refreshed every 20 days, **WHEN** evaluated on day 89 and day 91 (defaults), **THEN** valid then expired (registered account); a guest family is renewed instead. `test_refresh_absolute_limit_registered_vs_guest`
13. [Logic] **GIVEN** `MAX_DEVICES = 8` families, **WHEN** a 9th sign-in occurs, **THEN** the least recently used family is revoked and 8 remain. `test_max_devices_revokes_lru_family`
14. [Integration] **GIVEN** a client access token, **WHEN** used on the service-only photo write path, **THEN** `ERR_AUTH_INVALID` and no row is written (mirrors Network Transport AC 32).

**C. Transactions and ledger (Rules 26–34, F3, F4)**

15. [Logic] **GIVEN** any committed ledger transaction in a randomised fixture of 1 000 sales, purchases and adjustments, **WHEN** summed, **THEN** each `tx_id` sums to 0 and each `cached_balance` equals its ledger sum. `test_ledger_zero_sum_and_cached_balance_match`
16. [Logic] **GIVEN** balance 250, **WHEN** a 300 purchase is attempted, **THEN** `ERR_INSUFFICIENT_FUNDS`, and the row counts of ledger, item and wallet tables are unchanged. `test_purchase_over_balance_writes_nothing`
17. [Logic] **GIVEN** a purchase handler that throws after writing the ledger legs but before the item row, **WHEN** run, **THEN** the transaction rolls back and no ledger leg exists for that `rid`. `test_handler_failure_rolls_back_all_rows`
18. [Integration] **GIVEN** two concurrent purchases from two devices totalling more than the balance, **WHEN** executed, **THEN** exactly one commits and the other returns `ERR_INSUFFICIENT_FUNDS`; the balance is never negative.
19. [Integration] *(provisional: Supply Caps)* **GIVEN** a counter at cap − 1 and 10 concurrent purchases, **WHEN** executed, **THEN** exactly one item gets the last serial and the counter equals cap.
20. [Logic] **GIVEN** a photo committed for `rid` R, **WHEN** the same write arrives after `IDEMPOTENCY_WINDOW_S` has expired, **THEN** no new row is created and the response equals the original photo. `test_late_retry_after_window_no_duplicate_photo`
21. [Logic] **GIVEN** a removed photo whose roll row exists, **WHEN** a late retry for its `rid` arrives, **THEN** the response is "removed" and no photo row is created. `test_late_retry_for_removed_photo_not_recreated`
22. [Logic] **GIVEN** jitter u = 0 and defaults, **WHEN** `delay(n)` is computed for n = 1..4, **THEN** 20, 40, 80, 160 ms; a constraint violation is returned without retry. `test_tx_retry_backoff_transient_only`
23. [Logic] **GIVEN** an attempt to update or delete a ledger entry through the data layer, **WHEN** executed, **THEN** it is rejected; an adjustment is accepted only as a new transaction with reason and operator. `test_ledger_append_only_corrections_as_new_entries`
24. [Integration] **GIVEN** a fixture where one cached balance is altered by direct database edit, **WHEN** reconciliation runs, **THEN** that wallet's writes return `ERR_SCOPE_FROZEN`, reads continue, other wallets are unaffected, and an alert is recorded.

**D. Tier storage (Rules 20–21, 43)**

25. [Logic] **GIVEN** an item write with tier "sss" or null, **WHEN** committed, **THEN** the transaction aborts with `ERR_UNKNOWN` / `ERR_UNSET` and nothing is written. `test_write_with_invalid_tier_aborts`
26. [Integration] **GIVEN** the full schema, **WHEN** inspected, **THEN** no table has a tier rank column and every required tier column is `NOT NULL` text holding a ladder ID.
27. [Logic] **GIVEN** a legacy fixture with 3 records whose tier is null, **WHEN** the migration runs, **THEN** each gets an explicit tier and exactly 3 migration log lines are written. `test_migration_null_tier_assigned_and_logged`

**E. Deletion and retention (Rules 44–49, F8)**

28. [Logic] **GIVEN** an account with 5 owned photos (2 on a leaderboard), 1 serialised item and a ledger history shared with another wallet, **WHEN** the purge runs, **THEN** identities, profile and owned photos are gone, the board no longer lists the 2 photos, the serial is released (or retired per D4), the other wallet's history and every `tx_id` still sum to 0. `test_purge_removes_personal_data_keeps_ledger_zero_sum`
29. [Logic] **GIVEN** a deletion requested at day 0 with `DELETION_GRACE_D = 14`, **WHEN** the scheduler runs on day 13 and day 14, **THEN** no purge then purge. `test_purge_runs_after_grace_boundary`
30. [Logic] **GIVEN** an account in `PendingDeletion`, **WHEN** it signs in and cancels, **THEN** it is `Registered`, its photos are visible again, and no purge is scheduled. `test_cancel_deletion_restores_visibility`
31. [Logic] **GIVEN** a purged photo that held image serial #12, **WHEN** the next image serial in that scope is issued, **THEN** it is #(counter + 1), never #12. `test_purged_image_serial_never_reissued`
32. [Logic] **GIVEN** a guest last seen on day 0 with `GUEST_IDLE_D = 30`, **WHEN** evaluated on day 29 and day 30, **THEN** kept then purged. `test_guest_idle_purge_boundary`
33. [Integration] **GIVEN** a backup taken before account X was purged, **WHEN** it is restored per Rule 38, **THEN** X is purged again before the service leaves maintenance and `restore_epoch` increased by 1.

**F. Backups and migration (Rules 35–43, F5)**

34. [Integration] **GIVEN** the scripted restore drill, **WHEN** run from the newest off-host copy on a fresh machine, **THEN** the service is serving, reconciliation passes and a test account signs in within `RTO_TARGET_H`; the drill record is kept.
35. [Integration] **GIVEN** a live database under write load, **WHEN** a snapshot is taken, **THEN** restoring it yields a database that passes reconciliation (consistent copy).
36. [Logic] **GIVEN** a meta service built for schema 7, **WHEN** started against a database at schema 8, **THEN** it refuses to start with a clear error. `test_service_refuses_newer_schema`
37. [Integration] **GIVEN** a migration script that fails halfway, **WHEN** the deploy runs, **THEN** the schema version and data are unchanged and the deploy stops.
38. [Logic] **GIVEN** any migration in the suite, **WHEN** run on a fixture with photos, **THEN** every `recipe`, `recipe_version`, score and `scoring_version` is byte-identical afterwards. `test_migrations_never_touch_recipes_or_frozen_scores`

**G. UI**

39. [UI] **GIVEN** a first visit with no token, **WHEN** the title screen loads, **THEN** **Play as guest** and **Sign in with email** are visible and a guest reaches the viewfinder in ≤ 2 clicks (screenshot of each step).
40. [UI] **GIVEN** a guest with < `GUEST_WARN_D` days left, **WHEN** the gallery opens, **THEN** the guest badge and the "Keep my progress" banner with the days left are visible (screenshot).
41. [UI] **GIVEN** an account with leaderboard photos, **WHEN** the delete flow opens, **THEN** step 1 shows the photo and leaderboard counts and the grace date, and **Keep my account** has default focus (screenshot).
42. [UI] **GIVEN** a client whose last `restore_epoch` is lower than the server's, **WHEN** it connects, **THEN** the restore notice is shown once (screenshot).

## Open Questions

**Design questions** (options and recommendations in Decisions to confirm): guest accounts (D1), sign-in methods (D2), deleted photos (D3), deleted gear (D4), deletion grace (D5), ledger model (D6), backup RPO/RTO (D7), tokens (D8), display names (D9), effect keys (D10), migration (D11), restore notice (D12), inactive accounts (D13), integrity response (D14), data export (D15), roll retention (D16).

**Legal and policy (not legal advice; need a qualified reviewer)**

1. **Minimum age and child-privacy rules** (for example COPPA in the US, age-of-consent rules under GDPR in the EU/UK): is an age gate needed, at what age, and what changes for younger players? This GDD stores no birth date by default.
2. **Privacy policy and terms**: required text, where it is shown, and consent at sign-up.
3. **Data location**: does hosting region matter for EU/UK players?
4. **Erasure in backups**: is the F8 timeline (data gone from backups after ≤ 42 days, with journal replay) acceptable?
5. **Moderation evidence retention** after a suspended account deletes itself.
6. **Account recovery** when a player loses their email: support-assisted recovery, or none?
7. **Loot-box and real-money trading** (game concept Risks): no paid random rewards exist; P2P trading (Alpha) needs a policy on real-money trading of accounts and items.

**Technical and ops**

8. Which free email-sending service, its daily limit, and its deliverability (codes landing in spam).
9. Which free off-host backup destination (another free VM, the user's own PC, a free object-storage tier); its storage limit vs F5 off-host storage.
10. Does Godot `user://` persist reliably in the chosen web host (itch.io iframe storage partitioning; private browsing)? Spike item.
11. OAuth inside a Godot web export (popup/redirect hand-back): spike before VS.
12. PocketBase specifics, if chosen: one-time-code auth support, refresh-token rotation and reuse detection, expressible constraints (CHECK, unique, triggers), consistent live backup method, hook transaction semantics. All **UNVERIFIED**; pin the version (research §8 risk 3).
13. Backup egress at scale (F5 example B) competes with gameplay egress (Network Transport F14): when to switch to incremental replication.
14. security-engineer review: F7 code length, token storage in browser storage (Rule 14), service credential handling, reconciliation freeze.
15. Who restores at 3 a.m.? RTO excludes detection; an uptime alert to the developer's phone is assumed (devops-engineer).
16. Compensation policy after a restore (producer / community-manager).
17. Systems index updates (not made here): add this system as a dependent in the Rarity Tier Ladder GDD; consider adding Starting Choice, Supply Caps, First-Claim and Seasons as dependents of this system; decide which UI system hosts account screens.

**ADR candidates** (this GDD states the behaviour each must satisfy):

| ADR | Behaviour required |
|---|---|
| Meta backend selection (research §7.3) | Rules 6–8, 12–17, 26–33; PocketBase is the candidate |
| Authentication, tickets and token flow (research §7.4) | Rules 6–17, F6, F7; token storage (Rule 14) |
| Economy transaction integrity (research §7.9) | Rules 26–34, F3, F4; database-level constraints |
| Server RNG authority and audit log (research §7.10) | `roll` records kept forever; written before send |
| Persistence backup, restore and schema migration (research §7.15) | Rules 35–43, F5 |
| Hosting, reverse proxy and TLS (research §7.13) | Off-host backup destination, uptime alerting |
| **New:** Email delivery for sign-in codes | Rule 10; free tier only |
| **New:** Data retention and deletion policy | Rules 44–50, F8, retention table |
| **New:** Identifier generation | Rule 1; random IDs, serials separate from IDs |
| Message protocol (research §7.11) | Add the new error codes listed in Interactions |

## Decisions to confirm

> **DECIDED 2026-11-04 (user):** every item = the recommended option. D1: guests allowed with restrictions (B).

**D1. Guest accounts.**
- A. No guests: sign-in required before play.
- B. Guests allowed with in-place upgrade; guests cannot trade, vote or rename; idle guests are purged after 30 days.
- C. Guests allowed with no restrictions and no expiry.
- **Recommendation: B.** A web game loses most first-time visitors at a sign-in form, and guests store no personal data at all. The restrictions block the main abuse (throwaway accounts funnelling starting money or votes), and expiry stops abandoned guests piling up. Cost: a guest who clears browser storage loses their progress, which the "Keep my progress" banner mitigates. C invites multi-account abuse; A adds friction before the first photo.

**D2. Sign-in methods.**
- A. Email one-time code in MVP; Google and Discord OAuth added at Vertical Slice; no passwords.
- B. Email + password (with email reset).
- C. OAuth only.
- **Recommendation: A.** No password storage, no credential-stuffing surface, only an email address held, and a typed code works inside an iframe without cross-tab hand-off. It needs a free email-sending service (Open Questions 8). B still needs email for resets and adds password risk; C depends on popups/redirects in a web export that are unverified, and excludes players without those accounts.

**D3. What happens to a deleted account's photos.**
- A. Remove the photos the account owns, together with their leaderboard entries (boards recompute); photos it authored but others now own stay, credited to "Former photographer"; image serials are retired, never reissued.
- B. Keep all photos as anonymous game content ("Former photographer") everywhere, including leaderboards.
- C. Remove everything the account ever authored, including photos other players now own.
- **Recommendation: A.** It matches what a player expects from "delete my account" and keeps personal history to a minimum, while never taking property away from other players (Pillar 2 for them). B keeps the hall of fame intact but leaves a deleted player's work on public display; C breaks other players' galleries.

**D4. What happens to a deleted account's serialised gear.**
- A. Released back to supply through Supply Caps' `release_serial`.
- B. Retired permanently (the serial stays used).
- **Recommendation: A**, final call with the Supply Caps GDD. Retiring turns every deletion into a permanent supply drain, which worsens the late-player lockout the concept worries about. MVP has no caps, so this only matters from Alpha.

**D5. Deletion grace period.**
- A. 14 days, cancellable by signing in; the account is hidden immediately.
- B. Immediate purge.
- C. 30 days.
- **Recommendation: A.** It protects against mistakes and against a stolen session deleting an account, while the account disappears from public view at once. B is irreversible on a misclick; C makes the erasure promise slower (F8: 42 days total with A, 58 with C).

**D6. Ledger model.**
- A. Double-entry, append-only ledger: every transaction sums to zero against named system wallets (faucets, sinks) or other players; cached balance updated in the same transaction; ledger references wallets, not accounts.
- B. Single-entry append-only log of signed amounts per player, plus a cached balance.
- C. A mutable balance column with a separate audit log.
- **Recommendation: A.** It makes the money supply exact by construction (F3), gives Economy Telemetry faucet and sink totals for free, supports player-to-player trades without a new model, and allows account deletion without editing history. B is slightly simpler but cannot prove where money came from; C lets the balance and the log drift apart.

**D7. Backup cadence and recovery targets.**
- A. Hourly local snapshots, daily encrypted off-host copy; RPO 1 h (host intact) / 24 h (host lost); RTO 4 h from the start of the restore; monthly restore drill.
- B. Nightly off-host backup only; RPO 24 h; RTO 8 h.
- C. Continuous replication of the database log to off-host storage (e.g. a Litestream-style tool); RPO about 1 minute.
- **Recommendation: A for MVP.** It costs nothing extra, keeps egress small at playtest scale (F5 example A: ≈ 1.75 GB/month), and an hour of lost purchases is survivable with a restore notice. B loses a full day of photos on any failure; C is best for an economy but needs a free object store and a tool to verify. Move to C before an open beta (F5 example B). Lost unique results after a restore (serials, claims, photos) are covered by the compensation policy (Open Question 16), which must be defined before Alpha opens scarce items.

**D8. Token lifetimes and storage.**
- A. Access token 1 h with `token_epoch` instant revocation; rotating refresh tokens with reuse detection, 30-day idle and 90-day absolute limits; stored in browser storage.
- B. Long-lived single token (e.g. 30 days), no refresh.
- C. httpOnly cookies instead of browser storage.
- **Recommendation: A.** Rotation plus reuse detection limits the damage of a stolen token, and the epoch gives instant "sign out everywhere". C is safer against script injection but cookies are unreliable in third-party iframes (unverified for the host); revisit if the game is served from its own domain. B cannot revoke cleanly.

**D9. Display names.**
- A. Free, non-unique name plus a random 4-digit tag (`Mira#4821`); guests get generated names.
- B. Globally unique names.
- **Recommendation: A.** No name squatting, no "name taken" frustration, and no need to hold names after deletion. B is friendlier on leaderboards but needs reservation and release rules.

**D10. Duplicate protection for late retries.**
- A. Permanent unique effect keys (`capture_rid`, `roll.rid`, `acquired_rid`, ledger `(wallet_id, rid, leg)`), with the idempotency window only caching responses.
- B. Rely on the idempotency window alone (Network Transport F9 default 600 s).
- **Recommendation: A.** A session-server outbox can drain long after 600 s during a meta outage (Network Transport D9). With B, a commit whose acknowledgement was lost could be applied twice. A costs one unique index per effect table.

**D11. Schema migration policy.**
- A. Forward-only migrations, each in one transaction, mandatory pre-migration snapshot, maintenance window, rollback by restoring the snapshot, service refuses a newer schema; recipes and frozen scores are never migrated.
- B. Hand-written down-migrations for rollback.
- C. Lazy migration of records when read.
- **Recommendation: A.** It is the smallest set of rules a solo developer can follow reliably, and lockstep client/server builds (Network Transport D4) remove the need to serve two schemas. B doubles migration work and is rarely tested; C leaves mixed-version data in the database indefinitely.

**D12. Restores are visible to players.**
- A. `restore_epoch` in every response; clients refetch and show a one-time notice.
- B. Silent restore.
- **Recommendation: A.** A photo that vanished without explanation destroys trust more than an honest notice (Pillar 2).

**D13. Inactive registered accounts.**
- A. Never expire for inactivity in MVP.
- B. Purge after 3 years of inactivity, with an email warning first.
- **Recommendation: A** for now (Pillar 2: photos persist); revisit with legal review (Open Questions 1–4), where B may become necessary.

**D14. Response to an integrity mismatch found by reconciliation.**
- A. Freeze economy writes for the affected scope only, keep reads, alert the developer, fix by an audited adjustment.
- B. Alert only; keep writing.
- C. Auto-correct the cached value to the ledger sum.
- **Recommendation: A.** B lets a duplication bug spread; C hides the bug that caused it. Freezing one wallet or one counter is a small, contained inconvenience.

**D15. Player data export.**
- A. "Download my data" (JSON) from Alpha.
- B. On request by email only.
- C. Not offered.
- **Recommendation: A.** Cheap to build once records are catalogued, and supports the "my data, my control" fantasy; final scope follows the legal review.

**D16. Retention of roll records.**
- A. Keep every roll record forever (audit of rarity outcomes, permanent de-duplication anchor).
- B. Keep rolls for kept photos forever; drop rolls of discarded C/B-tier shots after 90 days.
- **Recommendation: A for MVP.** At playtest scale rolls cost little (F1), and they are the anchor that stops late retries re-creating removed photos. Switch to B only if F1/F2 measurements show rolls dominating storage; B then needs another permanent anchor for discarded shots (a compact `rid` tombstone table).
