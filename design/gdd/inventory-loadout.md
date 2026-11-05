# Inventory & Loadout

> **Status**: Designed 2026-11-05 (pending `/design-review` in a fresh session)
> **Author**: user + agents (economy-designer)
> **Last Updated**: 2026-11-05
> **Last Verified**: 2026-11-04
> **Creative Director Review (CD-GDD-ALIGN)**: REVISED 2026-11-05 — CONCERNS fixed: Bag anchor timing, fixed-entry rule, revalidation notice, Starting Choice requirement. NOT ASSESSED: MDA target; F3/F4 swap timing vs mount pricing.
> **Implements Pillar**: Pillar 1 "Seeing is the skill" (which glass you carry and when you change it is a photographer's decision, and owning more gear never puts more of it in your hands at the moment); supports Pillar 2 "Every photo matters" (a photo records the gear the server knows was mounted) and the anti-pillar "not pay-to-win" (a fixed Bag caps what wealth can bring into the field)

## Summary

Inventory & Loadout is the server-owned record of which gear instances an account holds and which of them are in use. It defines three places an item can be: the **Shelf** (everything owned, no gameplay limit), the **Bag** (up to 4 lenses and adapters taken into the field, including whatever is mounted) and the **loadout** (one body + one lens + an optional adapter, or the phone). It enforces the Gear Catalog's fit rules on the server, exposes the gear ceiling to Capture Tier Resolution, and sets when gear can change: freely at home, and in the field only from the Bag, at a time cost of 800–3,700 ms and no money. Every account keeps a bound **pocket phone**, so nobody can be left without a working camera. It owns no prices, wear, serials or trades.

> **Quick reference** — Layer: `Core` · Priority: `MVP` · Key deps: `Gear Catalog & Specs` (fit rules, `gear_ceiling`, `swap_ms`, `kind`), `Accounts & Server Persistence` (`item` and `loadout` records, one action = one transaction), `Network Transport & Server Authority` (`rid`, authority table, `INTERACT`, service path) · Read by Capture Tier Resolution, Camera Model, Photo Recipe, Starting Choice, Gear Shop, Shop/Sell/Inventory UI and the Alpha economy systems · Engine: no engine API is used (records and rules); how the meta service runs the catalog's fit rules → ADR

## Overview

The Gear Catalog says what a lens *is*. This system says whose it is, where it is right now, and whether it is on the camera. It answers four questions, always on the server:

1. **What do you own?** Each owned item is one instance row pointing to a catalog model. A row adds identity and ownership, never tier or specs.
2. **What do you have with you?** Owning a lens and carrying it are different things. The Shelf holds everything; the Bag holds what comes on this outing.
3. **What is on the camera right now?** The loadout is one record per account, changed only by a legal, atomic request.
4. **What can this camera reach?** The server resolves the active loadout and hands Capture Tier Resolution its gear ceiling, using Gear Catalog F12.

Three design choices shape the system.

**Wealth buys options at home, not power in the field.** The Bag has the same 4 slots for every player. A player who owns all 18 enabled models carries the same amount as one who owns 6. This is the concept's anti rich-get-richer rule applied to carrying, and it means gear choice stays a decision about today rather than a matter of having everything.

**Time is the only price of changing your mind.** A field swap costs no money and no wear. It costs the seconds in which the viewfinder is closed, and those seconds are sized against subject timing. A bayonet swap started on the anticipation cue still catches the decisive pose, while a thread swap does not (F4).

**The phone is the floor.** A bound phone that cannot be sold, traded or lost means no sequence of purchases, sales or breakages can leave a player unable to shoot and earn. It also keeps the concept's promise that the phone stays a valid street style later.

**Resource flow.** This system moves no money in MVP: swaps, equips and storage are all free. Its flows are items only.

| Flow | Source | Amount | Notes |
|---|---|---|---|
| Item faucet | Starting Choice grant | 1 item (phone path) or 3 items (phone, Hearth, kit zoom) | Once per `account_id`; recommended contents, Starting Choice owns the grant |
| Item faucet | Gear Shop purchase | 1 item per purchase | Limited by money and stock |
| Item sink | Gear Shop sell-back, if it exists | 1 item | Not decided; Gear Shop owns it |
| Item sink (Alpha) | Breakage, crafting input | 1 or more items | Gear Condition and Gear Crafting own the rules |
| Neutral (Alpha) | Trading | 0 net | Moves ownership only |

**Sink status: not closed.** Item counts are stable in MVP because they are bounded by a small catalog and by money. The larger question stays open: once a player owns what they want, nothing here absorbs money. This system adds no sink, and the buy-out time must be stated in Currency & Wallet's budget table (Gear Catalog Open Question 7). A paid Shelf is the one lever this system could offer, and it is deliberately not used (Decision D2).

## Player Fantasy

**Framing: direct.** The player packs the Bag before every outing and reaches into it in the field.

**"I chose what to bring."** (This moment arrives once a player owns 5 or more attachable items; the first-playable set never reaches it.) The anchor moment: before dusk the player stands at the Shelf and packs for the evening. The kit zoom for the walk out, the KR 85 for the lantern light, and the old Hollin with its ring, which takes two of four slots but gives the swirl nothing else gives. That choice is the first creative act of the outing, made before any spirit appears. This serves the core fantasy, *"I see what others miss, and I choose what's worth keeping."*

**"A breath to change, and I chose when."** On the rocks, the spirit stirs and the anticipation pulse shows. There is time for one quick twist of a bayonet mount and no time for a thread. Deciding to swap, or to trust the lens already on, is a small act of judgement that belongs to the player's eye (Pillar 1).

**"It's always in my pocket."** Whatever is on the camera, the phone is one quick move away, and it never takes a Bag slot. When the moment is now and the wrong lens is mounted, the phone gets a shot, honestly limited to its C ceiling.

**"My gear is where I left it."** The loadout, the Bag and the Shelf are the same tomorrow as tonight, on any device. If a saved set can no longer be used, the game says so in a calm notice when it moves the player to the phone.

**Language.** Cozy, never inventory-speak. "Your Bag has room for one more", not "Inventory 3/4". "Back at home you can change this", not "Action not permitted". "Your lens is ready for more" when the ceiling binds, never "Locked" (ladder language rule). The Bag is never described as a weight or a burden.

## Detailed Design

### Core Rules

**A. Ownership**

1. **An item is one owned instance.** Each `item` row (Accounts Rule 19) holds `item_id`, `owner_account_id`, `model_id`, `state`, `bound` (bool), `acquired_rid`, `acquired_slot`, `acquired_source` (for example `start_grant`, `gear_shop`, `operator`) and `acquired_at`. Supply Caps adds `serial` and `season_id`; Gear Condition adds `condition`. This system reads those fields and never writes them. (The Accounts and Gear Catalog GDDs name these fields differently; see Decision D12.)
2. **Model data is never copied into a row.** Tier, mount, kind and specs are read from the catalog by `model_id` at the moment they are needed (Gear Catalog Rules 3 and 7), so a spec revision or a signed-off tier migration touches no item rows.
3. **The server owns all of this.** The client proposes a target loadout or Bag and displays the last confirmed state. It never asserts ownership, tier, ceiling or legality (Network Rule 6 and its authority table). Any client copy is a cache.
4. **Items are created only through `mint_item`.** `mint_item(account_id, model_id, source, rid, slot)` runs inside the calling system's transaction (Accounts Rule 26). It checks that the model is producible (Gear Catalog Rule 20) and that the quota holds (F7), then inserts the row in state `Owned`. New items land on the Shelf and are never equipped automatically, with two exceptions: the Starting Choice grant, which equips the kit in the same transaction, and the pocket phone.
5. **One action may create several items.** Each item's permanent effect key is (`acquired_rid`, `acquired_slot`), with `slot` numbered from 0 inside the action, in the same way ledger legs use (`wallet_id`, `rid`, `leg`). The Accounts catalogue currently says unique (`acquired_rid`), which would make the three-item camera grant impossible under one `rid`. This needs a change to Accounts (Decision D11).
6. **Items leave only through `release_item`.** `release_item(item_id, reason, rid)` runs inside the calling system's transaction and moves the item to `Retired`. It refuses with `ERR_ITEM_LOCKED` when the item is `Equipped` (reason `EQUIPPED`), in the Bag while the account is in the field (`IN_FIELD_BAG`), `Escrowed` (`ESCROWED`) or `bound` (`BOUND`). At home, a Bag item that is not mounted leaves the Bag in the same transaction. `Retired` rows are kept, because their `acquired_rid` must keep blocking a late retry (Accounts Rule 30). The purge in Accounts Rule 44 is the only path that deletes them. Trading uses `transfer_owner`, under the same locks.
7. **Duplicates are allowed.** An account may own two instances of a model. They are separate rows, which later matters for serials and condition. In MVP a second copy adds nothing, so the shop UI warns "You already own one" before the purchase (Decision D13).
8. **Guests have the same inventory rules, with three limits.** A guest owns, equips, packs and swaps exactly as a registered player does, with the same Bag and Shelf. A guest cannot trade (`transfer_owner` refuses with `ERR_NOT_ALLOWED`), cannot hold a serialised item (Supply Caps and Gear Shop must not issue one to a guest), and cannot place on leaderboards (Accounts Rule 3, owned there). Guest upgrade changes nothing here: items, loadout and `rev` carry over in place (Accounts Rule 4).

**B. Shelf, Bag and pocket**

9. **The Shelf is everything owned.** It is a view, not a record: all items in `Owned` or `Equipped` state. It has no gameplay limit in MVP, only the technical `MAX_ITEM_RECORDS` (F7), which plays the same role as `MAX_PHOTO_RECORDS`. The concept's "storage" money sink stays in Gallery (systems index A12).
10. **The Bag is what comes on the outing.** `loadout.bag` is a list of at most `BAG_SLOTS` = 4 lenses and adapters, and it **includes the mounted lens and adapter** (F2). Every lens or adapter costs 1 slot. Bodies and the phone never go in the Bag. Because mounted gear counts, a field swap only rearranges items already in the Bag, so it can never overflow it.
11. **The Bag may hold gear that does not fit the current body.** It is allowed and flagged ("Doesn't fit the KR mount"), never refused, so changing body at home does not destroy a packed Bag.
12. **The pocket phone.** Every account owns exactly one `bound = true` phone, `phone_basic_c_01`, granted on every Starting Choice path (Decisions D5 and D6). It is always `Equipped` in the pocket slot, takes no Bag slot, and cannot be sold, traded, escrowed, merged or broken. It stays a fully working tier C camera for the life of the account. It is deleted only by the purge.
13. **No account can lose the ability to shoot.** Rule 12 is the guarantee: at any moment `active = PHONE` is a legal loadout. This is the soft-lock floor. A player with no money, no camera and no lens can still shoot, sell and climb back. Bound also closes the arbitrage of selling a free granted item.

**C. The loadout**

14. **One loadout record per account.** The `loadout` record (Accounts Rule 19, key `account_id`) holds:

    | Field | Type | Notes |
    |---|---|---|
    | `rev` | int | Starts at 1, rises by 1 on every committed change (F5) |
    | `active` | `CAMERA` or `PHONE` | Which device is in hand |
    | `phone_item_id` | item ID, never null | The pocket slot |
    | `body_item_id`, `lens_item_id` | item ID or null | The camera set; both null or both set in any player request |
    | `adapter_item_id` | item ID or null | Only when the fit needs it |
    | `bag` | list of item IDs, length 0–`BAG_SLOTS` | Includes the mounted lens and adapter |
    | `lease_id`, `lease_until` | ID, server time | The field lease (Rule 21, F6) |

15. **The camera set stays on while the phone is out.** With `active = PHONE` the camera set is kept, unchanged, ready for the switch back. A phone-start player simply has a null camera set. An item is `Equipped` exactly when the loadout names it, including a camera set while the phone is in hand.
16. **A target must be legal as a whole.** A request names the complete target, and the server evaluates it as one unit, in this order, stopping at the first failure. Nothing is written on a failure.

    | # | Check | Refusal |
    |---|---|---|
    | 1 | Account state allows economy writes | `ERR_ACCOUNT_PENDING_DELETION`, `ERR_BANNED`, `ERR_SCOPE_FROZEN` |
    | 2 | `expected_rev` equals `loadout.rev` (F5) | `ERR_LOADOUT_STALE`, with the current state |
    | 3 | Path matches location (Rules 21–23) | `ERR_IN_FIELD`, or `ERR_NOT_ALLOWED` for a field swap that changes the body or Bag |
    | 4 | Every named item is owned by this account and is `Owned` or `Equipped` | `ERR_INVALID_LOADOUT`, reason `NOT_OWNED` |
    | 5 | Every item's `kind` suits its slot | `ERR_INVALID_LOADOUT`, reason `WRONG_KIND` |
    | 6 | Camera set is empty, or Gear Catalog validity is `VALID_DIRECT` or `VALID_ADAPTED` after Rule 17 | `ERR_INVALID_LOADOUT`, reason `INVALID_MOUNT`, `INVALID_ADAPTER` or `INCOMPLETE` |
    | 7 | `active = CAMERA` needs a non-empty camera set | `ERR_INVALID_LOADOUT`, reason `INCOMPLETE` |
    | 8 | Bag check passes (F2) | `ERR_INVALID_LOADOUT`, reason `BAG_FULL`, or `NOT_IN_BAG` in the field |

17. **An unneeded adapter is dropped before validation.** If the target's lens fits the body directly, the adapter is removed from the mounted set, as the Gear Catalog edge case requires, and stays in the Bag if it is listed there. An unneeded adapter never lowers the ceiling.
18. **One action, one transaction, one revision.** A committed change writes the `loadout` row and every affected `item.state` in one transaction (Accounts Rule 26) and raises `rev` by exactly 1. The target is applied whole or not at all. There is no partial equip.
19. **Display is never optimistic.** The client shows a pending state within 100 ms and changes the lens name, gear ceiling chip and Bag contents only when the server confirms (Network Rule 30, Accounts Rule 34). A "would be" ceiling preview is allowed, because it is labelled as a preview and is never presented as current state.
20. **The phone's module and mode are not loadout.** The active module and computational mode are camera settings, chosen in the viewfinder and validated at `SHUTTER` (Gear Catalog Rule 19, Network Rule 25). Switching module costs `module_switch_ms`, owned by Camera Model, and writes nothing here.

**D. When and where gear changes**

21. **Home and Field.** An account is **in the Field** while it holds a live lease, and **at Home** otherwise. The meta service sets the lease when it issues a session ticket, the session server renews it, and it clears when the session is `Released` or expires (F6). Home is a state, not a place in the world, so the rule stays exact and testable.
22. **At Home, changes are free and instant.** The client sends `equip` on the meta channel (rate class `meta_write`, with `rid`), naming the full target: `active`, camera set, `phone_item_id` and `bag`. Any item on the Shelf can be used. There is no time cost.
23. **In the Field, only the Bag.** A field swap may change `active`, the lens and the adapter, using items already in the Bag. It may not change the body, the Bag's contents or the phone. Bodies change only at Home (Decision D4). The meta service refuses a meta-channel `equip` during a live lease with `ERR_IN_FIELD`. Without this, a client could skip the swap time and the Bag limit by calling the meta channel directly.
24. **A field swap travels through the session server.** Sequence:
    1. The client sends `INTERACT` with `kind: field_swap`, `rid`, `expected_rev`, and the target `active`, `lens_item_id` and `adapter_item_id` (rate class `interact`; well under the 256 B cap).
    2. The session server pre-checks against its cached loadout and starts the lock at once (F4).
    3. It sends the write to the meta service on the service-only path with `lease_id`. The meta service runs Rule 16 and commits.
    4. When both the commit result and `swap_time_ms` are complete, the session server applies the new set and sends `EVENT` `loadout_changed` (new `rev`, new set, gear ceiling), or `ERROR` if the swap failed.

    Using the ordered session socket removes any race between a swap and a shot: `SHUTTER` and `INTERACT` arrive in the order they were sent (Network Rule 23: everything is reliable and ordered). This adds no new message type.
25. **The swap costs time, and nothing else.** `swap_time_ms` (F3) comes from the mounts involved. During the lock the viewfinder cannot be raised and the session refuses `SHUTTER` with `ERR_NOT_ALLOWED`, reason `swapping` (Network Rule 17). The shot is not consumed. A swap costs no money and adds no wear in MVP.
26. **A swap can be started on the move and cannot be cancelled.** It can be started in any view state except during a traversal move. If the viewfinder is raised, it lowers at once and the lowering runs inside the lock. The player can keep moving (Decision D14). Once sent, a swap runs to its end, because the commit is already under way. A second swap request during the lock is refused with `ERR_NOT_ALLOWED`. Swapping has no effect on subjects (Subject & Spirit AC 9: gear never affects subjects).
27. **A lost mounted item leaves the loadout `INCOMPLETE`.** Players cannot create this state (Rule 16), but breakage (Alpha) or an operator removal can. The transaction that retires the item clears its slot and raises `rev`. The shutter is disabled, and the HUD offers "Use your phone" and any fitting Bag lens. The loadout is not changed for the player without their choice (Decision D15).
28. **Loadout presets are deferred to Vertical Slice (Decision D7).** The last-used loadout and Bag already persist, which covers the first playable's small gear set. When presets arrive: `PRESET_SLOTS` = 3 named targets, stored server-side in a new Accounts record, applied at Home only as one normal `equip` transaction. If a preset names an item no longer owned, it is refused with `NOT_OWNED` naming the item. It is never partly applied.

**Rule (fixed entry, decided 2026-11-05).** After going Home, the player rejoins the field at a fixed entry point, never where they stood, so packing the Bag is a real decision. Player Movement and Zone Access must honour this, tested by checking that returning Home costs a real outing decision.

**E. Contract with capture**

29. **The session server holds a working copy.** At `HELLO` it reads `rev`, the loadout and the Bag through the service path, and refuses the join with `ERR_SERVICE_DEGRADED` (retryable) if that read fails. The copy is updated by its own field swaps, by post-commit notices from the meta service (Accounts Rule 32) and by the `rev` returned on each lease renewal. The meta record stays authoritative.
30. **Capture reads the server's set.** Capture Tier Resolution calls `capture_gear_ceiling(account_id)` (F1), Photo Recipe reads gear `model_id` and `spec_rev` (Network Rule 7), and Network reads ranges and `burst_deci` (its Rules 25–26). All of these use the same resolved set, with no meta call in the shutter path. Nothing from the client is read.
31. **The set is the one in force when `SHUTTER` is validated.** Lag compensation rewinds subjects and world state to `capture_tick` (Network Rule 24). It never rewinds the loadout. Because shots and swaps share one ordered socket and shots are refused during the lock, the set at validation is also the set the player was holding at the press. A shot just after a swap may have a `capture_tick` up to `MAX_REWIND_MS` before the lock ended; that is allowed, because the player really did see that moment through the new lens on their delayed display.
32. **A shot in flight keeps its gear.** A `SHUTTER` that passed validation finishes with the gear it was validated with, even if a swap follows at once (Network Rule 28).

**F. Not owned here.** Prices, sell-back and stock (Gear Shop, Photo Pricing); money (Currency & Wallet); condition, repairs and breakage rules (Gear Condition); serials and caps (Supply Caps); trades and escrow rules (Trading); merging (Gear Crafting); what the Starting Choice grant costs and contains; fit rules, specs and `swap_ms` values (Gear Catalog); viewfinder behaviour during a lock (Camera Model); the final image tier (Capture Tier Resolution).

### States and Transitions

**Item record** (names from Accounts States and Transitions)

| State | Meaning | Entered when | Leaves to |
|---|---|---|---|
| `Owned` | On the Shelf, not named by the loadout (may be in the Bag) | `mint_item`; unequipped; trade completes | `Equipped`; `Escrowed` (Alpha); `Retired` |
| `Equipped` | Named by the loadout | A committed change names it | `Owned` on a change that drops it; `Retired` only by breakage or operator action (Rule 27) |
| `Escrowed` (Alpha) | Held by an open trade | Trading opens escrow | `Owned` (same or new owner) |
| `Retired` | No longer usable; row kept | `release_item`, breakage, merge | — (terminal) |

The Bag is not an item state. A Bag item is `Owned` or `Equipped`.

**Loadout validity, as seen by capture** (derived from Gear Catalog States and Transitions)

| `active` | Camera set | Validity | Can shoot | `capture_gear_ceiling` |
|---|---|---|---|---|
| `PHONE` | any | `VALID_PHONE` | yes | phone tier |
| `CAMERA` | body + lens | `VALID_DIRECT` | yes | F12 |
| `CAMERA` | body + lens + adapter | `VALID_ADAPTED` | yes | F12 |
| `CAMERA` | body, lens lost | `INCOMPLETE` (Rule 27 only) | no | `ERR_INCOMPLETE` |
| `CAMERA` | set failed revalidation | invalid (see Edge Cases) | not reachable: moved to `PHONE` on load | — |

**Location**

| State | Condition | Entered when | Leaves to | Allowed changes |
|---|---|---|---|---|
| `Home` | No live lease | Session `Released`; lease expired | `Field` on ticket issue | Any legal target, meta channel |
| `Field` | `now < lease_until` | Ticket issued | `Home` | Field swap only |

**Field swap** (per session, on the session server)

| State | Entered when | Leaves to | Shutter |
|---|---|---|---|
| `Ready` | Session joined; a swap finished | `Swapping` on an accepted `INTERACT` | allowed if the set is valid |
| `Swapping` | Pre-check passed | `Ready` with the new set when commit succeeded and `swap_time_ms` passed; `Ready` with the old set if the commit failed | refused |

### Interactions with Other Systems

| System | This system provides | This system receives | Contract notes |
|---|---|---|---|
| **Gear Catalog & Specs** | Server-held set of items for its functions | Fit rules 14–17, validity, F12, F13, `kind`, `swap_ms`, producibility (Rule 20) | Enforces at equip time, on the server; never re-implements the rules differently |
| **Accounts & Server Persistence** | Meaning of `item` and `loadout`; reconciliation checks | Atomic writes, constraints, purge, restore, guest upgrade | Needs catalogue changes (Dependencies, required changes) |
| **Network Transport & Server Authority** | Loadout at capture time; `INTERACT field_swap` semantics | `rid`, idempotency, rate classes, `EVENT`, service path | The loadout in the recipe always comes from the server |
| **Capture Tier Resolution** | `capture_gear_ceiling(account_id)` (F1) | nothing | An error makes the capture invalid; it is never C by default |
| **Camera Model** | Resolved set, lock start and end, `INCOMPLETE` state | `raise_time` through Movement; settings are its own | Limits its dials to the resolved set; closes the viewfinder during a lock |
| **Photo Recipe & Re-render** | `model_id` and `spec_rev` per mounted item | nothing | Stores model IDs, never `item_id`, so a sold lens leaves old photos intact |
| **Starting Choice** | `mint_item`, loadout setup in one transaction | Grant contents; which set starts equipped | Must include the pocket phone on every path (Rule 12) |
| **Gear Shop** | `mint_item`, `release_item`, quota check | Purchases and any sell-back | Mint and ledger legs commit together; a quota refusal moves no money |
| **Currency & Wallet** | nothing | nothing | No money moves here in MVP |
| **Shop, Sell & Inventory UI** | Shelf, Bag, loadout, rev, previews (F2, F8) | Requests | See UI Requirements |
| **Viewfinder HUD** | Active device, gear ceiling, lock state, Bag list | Field swap input | See UI Requirements |
| **Player Movement & Exploration** | Forces the viewfinder to lower and blocks raising during a lock | `raise_time`, traversal state | No speed change during a swap |
| **Zone Access & Travel** (VS) | Bag and ownership reads for access hints | Travel cost | Returning Home is what travel may later charge for |
| **Gear Condition & Maintenance** (Alpha) | Item rows; Rule 27 path | `condition`; breakage events | The bound phone is exempt from breakage |
| **Supply Caps & Gear Serials** (Alpha) | Item rows | `serial`, `season_id`; guests receive none | `release_serial` on purge stays in Accounts Rule 44 |
| **Gear Crafting** (Alpha) | `release_item`, `mint_item` | Merge rules | One merge is one transaction; locked items refuse |
| **Player-to-Player Trading** (Alpha) | `transfer_owner`, escrow state, locks | Trade rules | Equipped, bound and in-field Bag items cannot be escrowed; guests refused |
| **Expedition Rooms, Co-op Crew Roles** (Alpha) | Same lease and field swap per player | Room lifecycle | Crews do not share Bags |
| **Economy Telemetry** (Alpha) | Ownership counts per model and tier; swap counts | — | See Open Question 6 |

## Formulas

### F1. Capture gear ceiling

The capture_gear_ceiling formula is defined as:

`capture_gear_ceiling(a) = gear_ceiling(L(a))`, where `L(a) = {phone}` if `loadout.active = PHONE`, otherwise `L(a) = {body, lens} ∪ ({adapter} if set)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| a | account ID | any account | session | The shooter |
| loadout.active | enum | CAMERA, PHONE | session copy of the `loadout` record | Device in hand |
| phone, body, lens, adapter | item → model | owned, in the loadout | session copy, catalog | Resolved models |
| gear_ceiling | function | — | Gear Catalog F12 | Lowest tier of the set, or an error |
| capture_gear_ceiling | tier ID or error | C–SSS, or `ERR_INCOMPLETE`, `ERR_INVALID_LOADOUT` | calculated | Handed to Capture Tier Resolution |

**Output Range:** a ladder ID, or an error that makes the capture invalid (never C by default). This system applies no clamp; Capture Tier Resolution owns `clamp_to_enabled`.
**Example:** Hearth + kit, `active = CAMERA` → **C**. Lantern + KR 85, `active = CAMERA` → **A**; the same loadout with `active = PHONE` → **C**. Lantern + H42 ring + Hollin 58 → **B**. Hearth whose lens broke (Alpha) → **ERR_INCOMPLETE**.

### F2. Bag check

The bag_ok formula is defined as:

`bag_ok = (|bag| ≤ BAG_SLOTS) AND ({lens, adapter} − {null} ⊆ bag) AND (each x in bag is unique, owned, and x.kind ∈ {LENS, ADAPTER})`;  `bag_free = BAG_SLOTS − |bag|`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| bag | list of item IDs | 0–BAG_SLOTS entries | `loadout.bag` or the request | Items carried, mounted ones included |
| BAG_SLOTS | int | 2–8; default 4 | data file (tuning) | Carry limit, the same for every player |
| lens, adapter | item ID or null | — | target loadout | Mounted items |
| x.kind | enum | BODY, LENS, PHONE, ADAPTER | Gear Catalog | Kind of each item |
| bag_free | int | 0–BAG_SLOTS | calculated | Slots left, shown in the UI |

**Output Range:** bool; `bag_free` 0–4 at the default.
**Example (worked at both ends and where it first binds):**

| Player | Bag | Used | Result |
|---|---|---|---|
| Phone start, no camera | empty | 0 of 4 | passes, `bag_free` 4 |
| Camera start | kit | 1 of 4 | passes, `bag_free` 3 |
| First-playable full set | kit, KR 50, KR 85 | 3 of 4 | passes, `bag_free` 1 |
| Vintage outing | kit, KR 85, Hollin 58, H42 ring | 4 of 4 | passes, `bag_free` 0 |
| All KR glass | kit, KR 50, KR 85, KR 100–300, KR 40 | 5 of 4 | refused, `BAG_FULL` |
| Hollin 58 mounted, not listed | kit, KR 50 | — | refused: the mounted lens is not in the Bag |

The limit never binds on the first-playable set, and first binds at 5 attachable items, so new players never meet it. All 8 items usable on a KR body would need 8 slots, so half must stay home. That is the intended late choice.

### F3. Swap time

The swap_time_ms formula is defined as:

`swap_time_ms = device_step + lens_step`, where `device_step = PHONE_DRAW_MS` if `from.active ≠ to.active`, else 0; and `lens_step = 0` if lens and adapter are unchanged, else `max(swap_ms[mount(from.lens)], swap_ms[mount(to.lens)]) + (ADAPTER_STEP_MS if from.adapter ≠ to.adapter, else 0)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| from, to | loadout | any legal set | session copy; request | Current and target sets |
| swap_ms | map mount → int (ms) | 500–4000; 1200 bayonet, 1500 MF, 2500 thread | Gear Catalog mount table | Time for that mount; a null lens counts as 0 |
| mount(lens) | mount_id | mount table | Gear Catalog | The lens's own mount, not the adapter's |
| PHONE_DRAW_MS | int (ms) | 500–1500; default 800 | data file (tuning) | Time to change between camera and phone |
| ADAPTER_STEP_MS | int (ms) | 0–1000; default 400 | data file (tuning) | Fitting or removing an adapter |
| swap_time_ms | int (ms) | 0, or 800–3700 on MVP data | calculated | Time cost of the swap |

**Output Range:** 0 means nothing changes: the request succeeds with no write and no `rev` change. Otherwise the shortest MVP swap is 800 ms (phone) and the longest is 800 + 2500 + 400 = 3,700 ms (phone to a Hollin through a ring).
**Example:**

| Swap | Working | swap_time_ms |
|---|---|---|
| Camera → phone (or back, same lens) | 800 + 0 | 800 |
| Kit → KR 50 | max(1200, 1200) | 1,200 |
| KR 85 via smart adapter → NZ 24–70 on the Kestrel | max(1200, 1200) + 400 | 1,600 |
| Hollin 58 → Hollin 28 on the same ring | max(2500, 2500) | 2,500 |
| KR 50 → Hollin 58 + H42 ring | max(1200, 2500) + 400 | 2,900 |
| Phone → camera with kit changed to Hollin 58 + ring | 800 + 2,500 + 400 | 3,700 |

### F4. Swap lock and time to ready

The swap_lock formula is defined as:

`lock_ms = max(swap_time_ms, min(commit_ms, META_DEADLINE_MS))`;  `felt_ready_ms = rtt_ms + lock_ms + raise_time_ms`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| swap_time_ms | int (ms) | F3 | calculated | Time cost |
| commit_ms | int (ms) | ≥ 0; target p95 ≤ `FIELD_COMMIT_P95_MS` (500, **UNVERIFIED**, measure) | measured | Session → meta write and reply |
| META_DEADLINE_MS | int (ms) | 500–5000; default 2000 | Accounts F4 | After this the swap fails and the old set stays |
| rtt_ms | int (ms) | 0–300+; design point 150 | Network F6 | Client round trip |
| raise_time_ms | int (ms) | 100–400; default 220 | Player Movement knob `raise_time` | Raising the viewfinder again |
| lock_ms | int (ms) | 800–3700 normally | calculated | How long the session refuses shots |
| felt_ready_ms | int (ms) | ≥ lock_ms | calculated | Press of the swap to being able to shoot |

**Output Range:** `lock_ms` equals `swap_time_ms` whenever the commit is faster, so the swap time hides the commit and a non-optimistic write adds no visible wait. A slow commit only lengthens a swap shorter than `META_DEADLINE_MS`, up to 2,000 ms.
**Example:** values at 150 ms RTT with a 100 ms commit, compared with the time from the anticipation cue to the end of the decisive pose. Halo Keeper has `ANT_MS` 1,000 and `DEC_MS` 1,200, so its decisive pose lies 1,000–2,200 ms after the cue. The shortest legal species (`ANT_MS` 1,000, `DEC_MS` 800) ends at 1,800 ms.

| Swap started on the cue | lock_ms | felt_ready_ms | Halo Keeper | Shortest legal species |
|---|---|---|---|---|
| Phone | 800 | 1,170 | catches it, 1,030 ms left | catches it, 630 ms left |
| Bayonet lens | 1,200 | 1,570 | catches it, 630 ms left | catches it, 230 ms left |
| Bayonet + adapter | 1,600 | 1,970 | catches it, 230 ms left | misses by 170 ms |
| Thread lens | 2,500 | 2,870 | misses by 670 ms | misses by 1,070 ms |
| Thread + ring | 2,900 | 3,270 | misses by 1,070 ms | misses by 1,470 ms |

**Design target from this table:** a plain bayonet swap must stay reachable from the cue on every species at the 150 ms design point: `swap_ms ≤ 1,800 − 150 − 220 = 1,430`. The Gear Catalog default of 1,200 meets it. A thread swap is meant to fail this test, which matches "the vintage lens is a commitment". In practice a swap is safe in idle time: Halo Keeper's idle is 14,000 ms.

### F5. Revision check

The rev_check formula is defined as:

`accept = (request.expected_rev = loadout.rev)`;  on commit `loadout.rev' = loadout.rev + 1`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| request.expected_rev | int | ≥ 1 | client, from the last confirmed state | The state the player was looking at |
| loadout.rev | int | ≥ 1 | `loadout` record | Current revision |
| accept | bool | — | calculated | False returns `ERR_LOADOUT_STALE` with the current state; nothing is written |

**Output Range:** `rev` rises by exactly 1 per committed change. It is the permanent effect key for equips. The `loadout` row is mutable, so it has no effect row of its own to hold a `rid` (Accounts Rule 30). Once an equip commits, `expected_rev` can never match again, so a late retry can never re-apply it.
**Example:** `rev` = 41. A client equips with `rid` X and `expected_rev` 41; the commit makes 42 and the response is lost. A retry within `IDEMPOTENCY_WINDOW_S` (600 s) returns the stored response. The same retry 20 minutes later, after the player has also changed to `rev` 43, fails the check: 41 ≠ 43, nothing is written, and the current set stands. If the first attempt never committed and `rev` is still 41, the retry applies normally, which is correct.

### F6. Field lease

The lease_ttl formula is defined as:

`LEASE_TTL_S = RECONNECT_GRACE_S + LEASE_RENEW_S`;  `in_field = (now < lease_until)`;  each renewal sets `lease_until = now + LEASE_TTL_S`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| RECONNECT_GRACE_S | int (s) | 15–300; default 60 | Network knobs | How long a dropped seat is held |
| LEASE_RENEW_S | int (s) | 10–60; default 30 | data file (tuning) | How often the session server renews |
| LEASE_TTL_S | int (s) | 25–360; default 90 | calculated | Must be ≥ `TICKET_TTL_S` (60) |
| now, lease_until | server time | — | meta service clock | Server time only (Accounts Rule 25) |

**Output Range:** a normal session end clears the lease at once. After a session server crash, the longest wait before Home changes are allowed is `LEASE_TTL_S`, 90 s by default.
**Example:** the session server crashes 10 s after renewing at `t` = 0, so `lease_until` = 90. The player cannot use the Shelf until `t` = 90 and sees "Your gear is on its way back". At the extremes of the ranges, grace 15 s with renewal 10 s gives 25 s, which breaks the rule against `TICKET_TTL_S` 60 and is refused at config load; grace 300 s with renewal 60 s gives 360 s, the longest wait.

### F7. Item quota and storage

The item_quota formula is defined as:

`item_count = count(items where owner = a and state ∈ {Owned, Equipped, Escrowed})`;  a mint of `n_new` items is refused with `ERR_QUOTA` if `item_count + n_new > MAX_ITEM_RECORDS`;  `item_bytes = item_count × ITEM_ROW_B`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| item_count | int | 0–MAX_ITEM_RECORDS | measured | Live items held |
| n_new | int | 1–10 | calling system | Items created in this action |
| MAX_ITEM_RECORDS | int | 100–2000; default 200 | data file (tuning) | Technical safety cap, not a gameplay limit |
| ITEM_ROW_B | int (bytes) | 150–500; estimate 300 | Accounts F1 | Bytes per item row |

**Output Range:** `item_bytes` from 300 B (phone only) to 60,000 B at the cap. `Retired` rows do not count toward the quota, though they stay stored.
**Example:**

| Player | item_count | item_bytes |
|---|---|---|
| Phone start | 1 | 300 B |
| Camera start | 3 | 900 B |
| One of every enabled model | 18 | 5,400 B |
| Accounts F1 heavy player | 30 | 9,000 B |
| At the cap | 200 | 60,000 B |

200 is about 6.7 times the Accounts heavy-player estimate and about 11 times the enabled catalog, so only duplicate-buying reaches it. Even at the cap the cost is small next to Accounts' 1.19 MB example account, which is why no gameplay limit is needed for storage reasons.

### F8. Kit reach (display only)

The kit_reach formula is defined as:

`kit_reach = tier_max({phone.tier} ∪ {gear_ceiling(body, l, d) : l ∈ bag lenses, d ∈ bag adapters ∪ {none}, the set is valid})`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| body | item → model or none | owned | loadout | The camera for this outing |
| l, d | item → model | in the Bag | `loadout.bag` | Lens and optional adapter |
| phone.tier | tier ID | C in MVP | Gear Catalog | Always in the set, so the result is never empty |
| tier_max | function | — | Rarity Tier Ladder | Highest tier of a non-empty set |
| kit_reach | tier ID | C–SSS | calculated | The best gear ceiling this Bag can give |

**Output Range:** C to SSS, never an error. Display only; capture always uses F1.
**Example:** Lantern with kit, KR 50, KR 85 → {C, C, B, A} → **A**. Hearth with the same Bag → {C, C, B, B} → **B**, and the UI shows the body as the limit. Lantern with kit and Hollin 58 but no ring → the Hollin set is invalid, so {C, C} → **C**, and the Hollin is flagged "needs the H42 ring". Phone start with an empty Bag → **C**.

## Edge Cases

**Equip and legality**

- **If a target mounts a lens on a body with a different mount and no matching adapter**: refused with `ERR_INVALID_LOADOUT`, reason `INVALID_MOUNT`; the previous loadout stays equipped (Gear Catalog AC 27).
- **If a target names two adapters, or an adapter that does not match lens and body**: refused with reason `INVALID_ADAPTER`; adapters never chain.
- **If a target includes an adapter the lens does not need**: the adapter is dropped from the mounted set before validation and the commit succeeds as `VALID_DIRECT`; if listed in the Bag it stays there.
- **If a target names a body with no lens** (a phone starter who just bought a Hearth): refused with reason `INCOMPLETE`; the player stays on their current loadout and the UI says "This body needs a lens".
- **If a target names a phone in the lens or body slot, or a lens in the body slot**: refused with reason `WRONG_KIND`.
- **If a target names an item the account does not own, or a dormant model it could not own**: refused with reason `NOT_OWNED`; the violation score gains the proposed `W_INVALID_ITEM` (Gear Catalog edge case; Network has no such weight yet).
- **If a target is identical to the current loadout**: the request succeeds with no write; `rev` does not change.
- **If two devices send different equips at Home at the same moment**: the database serialises them; the first commits; the second fails F5 with `ERR_LOADOUT_STALE`, and that client shows the current set.
- **If a client retries an equip after `IDEMPOTENCY_WINDOW_S`**: F5 refuses it if the first attempt committed; nothing changes (F5 example).
- **If a request reuses a `rid` with a different target**: `ERR_IDEMPOTENCY_CONFLICT`; the original outcome stands (Network Edge Cases).

**Field**

- **If a field swap names a lens or adapter not in the Bag**: refused with reason `NOT_IN_BAG`; no lock starts.
- **If a field swap tries to change the body or the Bag**: refused with `ERR_NOT_ALLOWED`, and the session pre-check rejects it before any commit.
- **If a client sends a meta-channel `equip` during a live lease**: refused with `ERR_IN_FIELD`; no violation is added, because a stale menu can produce this honestly.
- **If a `SHUTTER` arrives during a lock**: refused with `ERR_NOT_ALLOWED`, reason `swapping`; the shot is not consumed, nothing is rolled, and the weight is 5, because a correct client waits for `loadout_changed` before raising the viewfinder.
- **If a `SHUTTER` passed validation just before the swap request arrived**: it finishes with the old set (Rule 32).
- **If the player closes the tab or the connection drops during a lock**: the swap finishes and commits (Network Rule 28); on resume the client reads the outcome with `RESULT_QUERY`, and the new set is in place.
- **If the meta service fails or passes `META_DEADLINE_MS` during a swap**: the old set stays; the lock ends when both the deadline and `swap_time_ms` have passed; the client gets `ERR_SERVICE_DEGRADED` and shows "Couldn't change lens, try again".
- **If the commit succeeded but the session server crashed before applying it**: the new session reads the committed set at `HELLO`; the player finds the new lens on the camera, which is the true state.
- **If a session pre-check passes but the meta service refuses** (the cached copy was stale): the lock ends at once, the old set is kept, and the session server reloads the loadout and sends `EVENT` `loadout_changed`.
- **If a second tab takes over the session** (Network Rule 35): the new ticket replaces `lease_id`; a swap still in flight from the old session fails the `lease_id` check, or F5, and writes nothing.
- **If the session server crashes**: the lease runs out within `LEASE_TTL_S`, or is replaced at once if the player rejoins; until then Home changes show "Your gear is on its way back" (F6).
- **If a ticket is issued but never used**: the lease expires after `LEASE_TTL_S`, with the same message.
- **If renewal fails because the meta service is down**: the session keeps running on its copy, and field swaps refuse with `ERR_SERVICE_DEGRADED`; on recovery the renewal returns the current `rev`, and a mismatch makes the session reload.
- **If a player buys gear during a session**: the purchase commits normally and the item lands on the Shelf; it cannot be used until Home, and the UI says "It'll be on your Shelf when you're home".
- **If a player starts a swap during a traversal move**: the input is ignored until the move ends.
- **If a phone-start player with an empty Bag opens the field swap**: only the phone is listed; the control is disabled with "Nothing else in your Bag".

**Ownership and removal**

- **If a sale, trade or merge targets an equipped item**: `release_item` refuses with `ERR_ITEM_LOCKED`, reason `EQUIPPED`; the whole action rolls back, including money. The player must change the loadout first (Decision D10).
- **If a sale targets an unmounted Bag item at Home**: it succeeds, and the item leaves the Bag in the same transaction, with `rev` + 1.
- **If a sale targets a Bag item in the Field**: refused with reason `IN_FIELD_BAG`.
- **If any system tries to release, trade or merge the bound phone**: refused with reason `BOUND`.
- **If a player sells their only camera**: at Home they switch to `active = PHONE`, clear the camera set, and sell; every step is legal, and the phone keeps them earning.
- **If a mint would pass `MAX_ITEM_RECORDS`**: `ERR_QUOTA`; the whole purchase rolls back, so no money moves, and the shop says "Your Shelf is full. Let something go first".
- **If a late retry of a purchase arrives after the item was sold**: the `Retired` row keeps (`acquired_rid`, `acquired_slot`) in place, so nothing is minted twice.
- **If a mounted lens is lost to breakage or operator action** (Alpha or operator): Rule 27 applies; `rev` rises, the session copy updates, and `SHUTTER` is refused with `ERR_INCOMPLETE`, shot not consumed.
- **If a mounted adapter is lost**: the same transaction clears the adapter and the validity becomes `INVALID_MOUNT`, so the lens slot is cleared too, the lens stays in the Bag, and the state is `INCOMPLETE`.
- **If a Bag item that is not mounted is lost**: it is removed from the Bag in the same transaction.

**Accounts and data**

- **If a guest attaches an email**: nothing here changes; `account_id`, items, loadout and `rev` stay as they were. No second phone is granted.
- **If a guest requests a transfer**: `ERR_NOT_ALLOWED`.
- **If an account is `PendingDeletion` or `Suspended`**: every write here is refused with that state's code, and rows are kept until the purge, which deletes the loadout and unserialised items, including the phone (Accounts Rule 44).
- **If reconciliation freezes an item or the loadout**: changes that touch it refuse with `ERR_SCOPE_FROZEN`; the last set keeps working in the viewfinder; nothing is auto-corrected (Accounts Rule 33).
- **If a restore rolls back purchases**: the loadout and items come from the same snapshot, so they stay consistent; the client refetches on the new `restore_epoch`.
- **If a catalog update makes a stored camera set invalid** (for example a mount correction in a new `spec_rev`): on load, the server moves the account to `active = PHONE`, clears the camera set, leaves its items on the Shelf and in the Bag, raises `rev`, logs it, and shows "Your gear needs a look" once.
- **If a model is retired or `enabled_cap` is lowered**: owned items stay fully usable (Gear Catalog Rule 20; ladder Edge Cases).
- **If a stored item's `model_id` cannot be loaded by the server**: the item is shown with a neutral silhouette and "?" badge, it cannot be equipped, and the server logs it; it is never replaced by another model.
- **If an account somehow has no bound phone**: `phone_item_id NOT NULL` makes this impossible by constraint; reconciliation reports any breach as an incident (no automatic grant).

## Dependencies

**Upstream (this system depends on):**

| System | Hard / soft | Interface | GDD status |
|---|---|---|---|
| Gear Catalog & Specs | Hard | Rules 14–17 and 20, validity states, F12, F13, `kind`, `swap_ms` | Designed |
| Accounts & Server Persistence | Hard | `item`, `loadout`, Rules 26, 30–34, 44, 46, restore | Designed |
| Network Transport & Server Authority | Hard | `rid`, Rules 17, 21, 24–28, 30, 35, `INTERACT`, `EVENT`, service path, `meta_write`, `interact` | Designed |
| Rarity Tier Ladder | Hard (through the catalog) | `tier_max` (F8), tier display | Designed |
| Player Movement & Exploration | Soft | `raise_time`, traversal state, view states | Designed |
| Subject & Spirit Behaviour | Soft (tuning reference only) | `ANT_MS`, `DEC_MS` for F4's target | Designed |

**Downstream (systems that depend on this one):**

| System | Hard / soft | Interface | GDD status |
|---|---|---|---|
| Capture Tier Resolution | Hard | `capture_gear_ceiling` (F1) | Not started |
| Camera Model | Hard | resolved set, lock state | Not started |
| Photo Recipe & Re-render | Hard | mounted `model_id` and `spec_rev` | Not started |
| Starting Choice | Hard | `mint_item`, first loadout | Not started |
| Gear Shop | Hard | `mint_item`, `release_item`, quota | Not started |
| Shop, Sell & Inventory UI | Hard | Shelf, Bag, loadout, previews | Not started |
| Viewfinder HUD | Hard | active device, ceiling, lock, Bag list | Not started |
| Zone Access & Travel (VS) | Soft | ownership and Bag reads | Not started |
| Gear Condition (Alpha) | Hard | item rows, Rule 27 | Not started |
| Supply Caps & Gear Serials (Alpha) | Hard | item rows; guest rule | Not started |
| Gear Crafting (Alpha) | Hard | `mint_item`, `release_item` | Not started |
| Player-to-Player Trading (Alpha) | Hard | `transfer_owner`, locks | Not started |
| Economy Telemetry (Alpha) | Soft | ownership counts | Not started |

**Required changes to other documents (not edited in this run):**

| Document | Change | Why |
|---|---|---|
| `accounts-server-persistence.md` Rule 19 | `item`: replace unique (`acquired_rid`) with unique (`acquired_rid`, `acquired_slot`) | The camera grant creates 3 items under one `rid` (Rule 5, D11) |
| same, Rules 19–20 | Remove `item.tier`; rename `catalog_id` to `model_id` | Tier is per model and has one source (D12) |
| same, Rule 19 | `loadout`: add the fields in Rule 14; `phone_item_id NOT NULL` | New structure |
| same, Rule 30 | Name `loadout.rev` as the effect key for equips | Equips have no effect row (F5, D9) |
| same, Rule 33 | Add checks: `item.state` agrees with the loadout; every Bag item is owned; one bound phone per account | New invariants |
| same, ticket issue | Set the lease at ticket issue; service-path lease renewal and field-swap write | Rules 21, 24 |
| `gear-catalog-specs.md` Rule 1 | `item_uid` → `item_id` | D12 |
| same, F12 variable `L` | "at the capture tick" → "when `SHUTTER` is validated" | Rule 31 |
| `network-transport-server-authority.md` Rule 4 | Allow field-swap writes and lease calls on the service path | Rule 24 |
| same, Rule 10, F2 | Add `INTERACT kind: field_swap` and `EVENT loadout_changed`; add `W_INVALID_ITEM` (3 proposed) | Rule 24; Gear Catalog edge case |
| same, closed error list | Add `ERR_INVALID_LOADOUT` and `ERR_INCOMPLETE` (both already named by Gear Catalog F12), `ERR_LOADOUT_STALE`, `ERR_ITEM_LOCKED`, `ERR_IN_FIELD` | Rules 6, 16, 27 |
| Starting Choice (when authored) | Grant the pocket phone on every path; state its cost is 0 | Rule 12 |
| `design/registry/entities.yaml` | Proposed: `capture_gear_ceiling`, `swap_time_ms` (formulas); `bag_slots`, `phone_draw_ms`, `adapter_step_ms` (constants); `phone_basic_c_01` (item); add this file to `gear_ceiling.referenced_by` | Cross-system facts |
| `design/gdd/systems-index.md` row 10 | Status and Design Doc link | Normal progress update |

Bidirectional note: Gear Catalog, Accounts and Network already list this system. Every downstream GDD must list "depends on Inventory & Loadout" when authored.

## Tuning Knobs

| Knob | Current value | Safe range | Affects | Too low / too high |
|---|---|---|---|---|
| `BAG_SLOTS` | 4 | 2–8 | How much of the collection comes on an outing; anti rich-get-richer | 2: a mounted lens plus one, and adapted lenses are nearly impossible. 6+: all a typical mount's glass fits, and the packing choice disappears. Below 3 the first-playable set no longer fits |
| `PHONE_DRAW_MS` | 800 | 500–1500, and ≥ `FIELD_COMMIT_P95_MS` | The phone as an emergency camera | Too low: the phone is a free second body and commits show as waits. Too high: "always in my pocket" stops being true |
| `ADAPTER_STEP_MS` | 400 | 0–1000 | The cost of fitting or removing an adapter | 0: adapters cost only a slot. Above about 800: smart-adapter swaps fall well behind the anticipation cue on most species |
| `swap_ms` per mount (Gear Catalog) | 1200 bayonet, 2500 thread | 500–4000; bayonet ≤ 1,430 for the F4 target | Whether a swap beats the cue | Owned by Gear Catalog; listed here because F4 sets a tighter target |
| `FIELD_COMMIT_P95_MS` | 500 (target, **UNVERIFIED**) | 100–800 | Whether swaps hide the commit | Measure on the chosen backend. Above `PHONE_DRAW_MS` the phone swap shows the commit as a wait |
| `LEASE_RENEW_S` | 30 | 10–60 | Lease write load; wait after a crash (F6) | Too low: needless writes. Too high: a longer wait after a crash |
| `MAX_ITEM_RECORDS` | 200 | 100–2000 | Storage safety only (F7) | Too low: collectors hit a technical wall in Alpha. Too high: more abuse surface, though still small |
| `PRESET_SLOTS` (VS) | 3 | 0–6 | Convenience | Too many: a menu that nobody reads |

**Not knobs:** the rule that mounted gear counts toward the Bag, the pocket phone's bound status, and the no-partial-equip rule are structure, not tuning. Prices and condition are knobs in their owning GDDs.

## Visual/Audio Requirements

- **Swap presentation.** The viewfinder closes with a soft aperture-iris wipe, shows the outgoing and incoming lens silhouettes, and opens on the new view. MVP needs no rigged hand animation, which is outside what `/asset-forge` can produce. A character animation can be added later without changing the rules.
- **Length follows the rule.** The transition plays for the whole lock, so thread swaps visibly take longer.
- **The Bag and Shelf.** A simple canvas Bag with 4 visible pockets and a wooden Shelf, as SVG UI suitable for `/asset-forge`. Gear shown as Gear Catalog F14 side silhouettes. Filled and empty pockets differ by shape as well as by colour.
- **Bound phone mark.** A small pocket icon on the phone's card, with no rarity implication.
- **Audio.** The mount sounds already specified by Gear Catalog: bayonet twist-click, slower thread screw. Add a soft pocket rustle for the phone and a quiet Bag sound on packing. No error buzzers; a refusal is a soft, low tap. Audio: SFX & Ambience owns the sounds, and they need a human listen.

## Game Feel

| Moment | Budget | How it feels |
|---|---|---|
| Home equip | pending state ≤ 100 ms; confirmation p95 ≤ 1 s (Network Game Feel) | The card lifts at once and settles on the camera when it is real |
| Field swap press | transition starts ≤ 1 frame on the client | The press is always acknowledged; the transition is the pending state |
| Field swap complete | `lock_ms` + RTT (F4): 1,350 ms for a bayonet at 150 ms RTT | "Takes a breath"; the commit is hidden inside the swap |
| Phone draw | 800 ms + RTT | Quick enough to grab a moment, not free |
| Viewfinder ready after a swap | `raise_time` 220 ms, as normal | No extra penalty on top of the swap |
| Refusal | ≤ 1 s, gentle wording, nothing moves | A nudge, never a failure screen |

The player must always be able to read the cost before pressing: the field swap list shows how long each option takes, as "quick", "a breath" or "a while".

## UI Requirements

All text is localisation keys; wording here is draft. Shop, Sell & Inventory UI owns the screens and Viewfinder HUD owns the field control; this system supplies states and rules.

- **Gear screen (Home).** Three areas: the loadout (body, lens, adapter, and the pocket phone), the Bag (4 pockets, with mounted gear marked "on the camera"), and the Shelf (all owned gear, filterable by kind, mount and tier, using the shared gear card). Gear that does not fit is never hidden (Gear Catalog UI rule).
- **Packing.** Add to and remove from the Bag with one action each. Equipping from the Shelf with a full Bag replaces the outgoing mounted item in the target the client sends, so the common case never shows `BAG_FULL`.
- **Readouts.** "Gear ceiling: B" for the current set; a labelled preview, "Your gear ceiling would be A", before committing; and kit reach (F8), "This Bag reaches up to A". When the body or adapter is the limit, say which, in ladder language.
- **Pending and confirmed.** While a request is pending the control shows it, and the lens name, ceiling and Bag stay on the last confirmed values.
- **In the Field, the gear screen is read-only**, with the note "Back at home you can change this". The Shelf stays browsable.
- **Field swap control (HUD).** Lists the Bag's lenses that fit, the phone, the time word for each, and the F1 ceiling each would give. Default binding is owned by the Movement input table; a touch button is required. Works without pointer lock. Unfitting Bag items are shown disabled with the reason.
- **Mounted gear in the HUD.** Lens name, gear ceiling chip, and "crop mode" where it applies (Gear Catalog edge case).
- **`INCOMPLETE` banner.** "No lens on the camera", with buttons for the phone and any fitting Bag lens.
- **Refusal copy.** `BAG_FULL`: "Your Bag is full. Take something out first." `INVALID_MOUNT`: "This lens doesn't fit the KR mount." `ERR_LOADOUT_STALE`: silent refresh, then "Your gear changed on another device." `ERR_IN_FIELD`: "Back at home you can change this." `ERR_ITEM_LOCKED`: "Take this off the camera first." or, for the phone, "Your phone stays with you."
- **Accessibility.** Every state has text, not colour alone. The Bag and the field swap control work by keyboard, gamepad and touch. The swap time word has a tooltip with the seconds.

📌 **UX Flag — Inventory & Loadout**: the Gear screen and field swap control are new. Run `/ux-design` for them with the Shop, Sell & Inventory UI spec before writing UI epics.

## Cross-References

| Referenced document | What is used | Where |
|---|---|---|
| `design/gdd/game-concept.md`: Starting choice; Gear specs; Balance; Limited gear | "Neither is a trap", phone stays valid later, mounts and adapters, anti rich-get-richer, storage as a sink | Overview, Rules 9, 12 |
| `design/gdd/gear-catalog-specs.md`: Rules 1, 3, 7, 14–17, 19–22; mount table; Loadout validity; F12; F13; Edge Cases; Game Feel; AC 24–27 | Instance fields, fit rules, ceiling, `swap_ms`, refusal wording, "takes a breath" | Rules 1–2, 16–17, 20; F1, F3 |
| `design/gdd/accounts-server-persistence.md`: Rules 3–4, 19–20, 25–26, 30–34, 44, 46; F1, F4; Item record | Records, transactions, effect keys, guest limits, purge, `ITEM_ROW_B`, `META_DEADLINE_MS` | Rules 1, 5–8, 18; F4, F7 |
| `design/gdd/network-transport-server-authority.md`: authority table; Rules 4, 6, 7, 10, 17, 21, 23–28, 30, 35; F1, F2, F3, F9; Game Feel | Authority split, message list, rate classes, weights, ordering, idempotency, 100 ms and 1 s budgets | Rules 3, 19, 21–25, 29–32; F5, F6 |
| `design/gdd/systems-index.md`: rows 10, 13, 14, 17, 21, 22, 31–33, 37; A12, B3, B6 | Dependents; storage placement; open phone path | Dependencies, Rule 9, Open Questions |
| `design/gdd/subject-spirit-behaviour.md`: F11 variables and example; AC 9 | `ANT_MS`, `DEC_MS`, Halo Keeper timing; gear never affects subjects | F4, Rule 26 |
| `design/gdd/player-movement-exploration.md`: R1, view states, `raise_time`, traversal | Viewfinder rules and timing | Rule 26, F4 |
| `design/gdd/rarity-tier-ladder.md`: `tier_max`, language rule, Rule 9 | Kit reach; "ready for more"; no default tier | F1, F8, Player Fantasy |
| `design/project-context.md` | Binding decisions: tier per model, phone tier C, server owns inventories | Throughout |

## Acceptance Criteria

Tags: **[Logic]** automated gdUnit4 unit test (suggested name given) · **[Integration]** integration test or documented playtest · **[UI]** retained screenshot in `production/qa/evidence/`. Criteria marked *(provisional)* depend on a system that is not designed yet.

**A. Ownership (Rules 1–8)**

1. [Logic] **GIVEN** a grant of phone, Hearth and kit under one `rid`, **WHEN** `mint_item` runs for slots 0, 1 and 2, **THEN** three rows exist; repeating the same `rid` and slots creates none. `test_mint_multi_item_grant_deduplicates_by_slot`
2. [Logic] **GIVEN** a model above `enabled_cap`, **WHEN** `mint_item` runs, **THEN** it is refused and no row is written. `test_mint_non_producible_model_refused`
3. [Logic] **GIVEN** any item row, **WHEN** its fields are inspected, **THEN** it has no tier or spec field, and tier comes from the catalog by `model_id`. `test_item_row_stores_no_model_data`
4. [Logic] **GIVEN** a mounted lens, **WHEN** `release_item` runs, **THEN** `ERR_ITEM_LOCKED` reason `EQUIPPED` is returned and the state is unchanged. `test_release_equipped_item_refused`
5. [Logic] **GIVEN** the bound phone, **WHEN** release, transfer or merge is requested, **THEN** each is refused with reason `BOUND`. `test_bound_phone_cannot_leave_account`
6. [Logic] **GIVEN** an unmounted Bag lens at Home, **WHEN** `release_item` runs, **THEN** the item is `Retired`, it has left the Bag, and `rev` rose by 1. `test_release_bag_item_at_home_clears_bag`
7. [Integration] **GIVEN** a sold item, **WHEN** the original purchase is retried after `IDEMPOTENCY_WINDOW_S`, **THEN** no new item is minted and no money moves.
8. [Integration] **GIVEN** a guest with gear, **WHEN** an email is attached, **THEN** every item, the loadout and `rev` are unchanged, and no second phone exists.
9. [Logic] **GIVEN** a guest, **WHEN** `transfer_owner` runs, **THEN** `ERR_NOT_ALLOWED` is returned. `test_guest_transfer_refused`
10. [Logic] **GIVEN** `item_count` = 199, **WHEN** a mint of 1 runs, **THEN** it succeeds; **WHEN** a mint of 2 runs at 199, **THEN** `ERR_QUOTA`. `test_item_quota_boundary`
11. [Integration] *(provisional: Gear Shop)* **GIVEN** an account at `MAX_ITEM_RECORDS`, **WHEN** it buys gear, **THEN** `ERR_QUOTA` is returned and the wallet is unchanged.

**B. Bag (F2, Rules 9–11)**

12. [Logic] **WHEN** F2 runs on the table in F2, **THEN** each row gives the stated result, including the five-lens refusal and the mounted-but-unlisted refusal. `test_bag_check_reference_cases`
13. [Logic] **GIVEN** a body or phone placed in `bag`, **WHEN** F2 runs, **THEN** it fails. `test_bag_rejects_body_and_phone`
14. [Logic] **GIVEN** a Bag holding a lens that does not fit the new body, **WHEN** the body changes at Home with a fitting mounted lens, **THEN** the change commits and the lens is reported as not fitting. `test_bag_keeps_unfitting_lens_on_body_change`
15. [Logic] **GIVEN** a full Bag with Hollin + ring mounted, **WHEN** a field swap mounts another Bag lens, **THEN** `|bag|` is unchanged. `test_field_swap_never_changes_bag_size`

**C. Loadout legality (Rules 14–19)**

16. [Logic] **WHEN** Rule 16 runs on each check's failing fixture, **THEN** the listed code and reason are returned and nothing is written; a fixture failing two checks returns the earlier one. `test_target_validation_order_and_codes`
17. [Logic] **GIVEN** Hearth + Hollin 58 with no ring, **WHEN** equipped, **THEN** `ERR_INVALID_LOADOUT` reason `INVALID_MOUNT`, and the previous loadout stays. `test_equip_invalid_mount_keeps_previous`
18. [Logic] **GIVEN** Hearth + KR 50 + H42 ring in the target, **WHEN** equipped, **THEN** the adapter is dropped, validity is `VALID_DIRECT` and the ceiling is B. `test_unneeded_adapter_dropped_before_validation`
19. [Logic] **GIVEN** a body with no lens in the target, **WHEN** equipped, **THEN** it is refused with reason `INCOMPLETE`. `test_player_cannot_create_incomplete_loadout`
20. [Logic] **GIVEN** a change of lens, adapter and Bag in one target where the Bag check fails, **WHEN** processed, **THEN** no field changes and `rev` is unchanged. `test_equip_is_all_or_nothing`
21. [Logic] **GIVEN** `rev` = 41, **WHEN** an equip with `expected_rev` 41 commits and is retried after `rev` = 43, **THEN** the retry returns `ERR_LOADOUT_STALE` and changes nothing. `test_late_equip_retry_refused_by_rev`
22. [Logic] **GIVEN** a target identical to the current loadout, **WHEN** processed, **THEN** it succeeds with `rev` unchanged. `test_no_op_equip_writes_nothing`
23. [Integration] **GIVEN** two devices at Home, **WHEN** both send equips with the same `expected_rev`, **THEN** exactly one commits and the other gets `ERR_LOADOUT_STALE`.
24. [Integration] **GIVEN** the shared fit-rule fixtures, **WHEN** the client, session server and meta service each evaluate them, **THEN** all three give the same validity (the meta service may use another language; Open Question 1).

**D. Gear ceiling and capture (F1, Rules 29–32)**

25. [Logic] **WHEN** F1 runs, **THEN** Hearth + kit = C; Lantern + KR 85 = A; the same with `active = PHONE` = C; Lantern + H42 ring + Hollin 58 = B; lens lost = `ERR_INCOMPLETE`, never the body's tier. `test_capture_gear_ceiling_reference_loadouts`
26. [Logic] **WHEN** F8 runs on its four examples, **THEN** it gives A, B, C and C, and never an error. `test_kit_reach_reference_bags`
27. [Integration] *(provisional: Capture Tier Resolution)* **GIVEN** a client that claims a lens the server never confirmed, **WHEN** it shoots, **THEN** the recipe and ceiling use the server's set.
28. [Integration] **GIVEN** a `SHUTTER` validated before a swap request, **WHEN** the swap then commits, **THEN** the photo records the old lens.
29. [Logic] **GIVEN** a swap that completed at tick T, **WHEN** a `SHUTTER` has a `capture_tick` before T, **THEN** the current set is used and the loadout is not rewound. `test_capture_rewind_does_not_rewind_loadout`

**E. Field swap (F3–F6, Rules 21–27)**

30. [Logic] **WHEN** F3 runs on the six rows of its table, **THEN** it returns 800, 1200, 1600, 2500, 2900 and 3700. `test_swap_time_reference_swaps`
31. [Logic] **WHEN** F4 runs with `commit_ms` 100 and `swap_time_ms` 1200, **THEN** `lock_ms` = 1200 and, at RTT 150, `felt_ready_ms` = 1570; with `commit_ms` 3000 and `swap_time_ms` 800, **THEN** `lock_ms` = 2000. `test_swap_lock_hides_commit_and_caps_at_deadline`
32. [Logic] **GIVEN** the MVP mount table, **WHEN** the F4 target is checked, **THEN** every enabled bayonet `swap_ms` ≤ 1,430 at default `raise_time`. `test_bayonet_swap_meets_anticipation_target`
33. [Logic] **GIVEN** a live lease, **WHEN** a meta-channel `equip` arrives, **THEN** `ERR_IN_FIELD` is returned; after expiry the same request commits. `test_meta_equip_refused_during_lease`
34. [Logic] **GIVEN** a field swap naming a lens not in the Bag, **WHEN** processed, **THEN** it is refused with `NOT_IN_BAG` and no lock starts. `test_field_swap_limited_to_bag`
35. [Logic] **GIVEN** a field swap changing the body, **WHEN** processed, **THEN** `ERR_NOT_ALLOWED`. `test_field_swap_cannot_change_body`
36. [Logic] **GIVEN** a state of `Swapping`, **WHEN** a `SHUTTER` or second swap arrives, **THEN** each is refused with `ERR_NOT_ALLOWED`, and the shot is not consumed. `test_swap_lock_refuses_shutter_and_second_swap`
37. [Logic] **WHEN** F6 is evaluated with defaults, **THEN** `LEASE_TTL_S` = 90; a config giving less than `TICKET_TTL_S` is refused at load. `test_lease_ttl_covers_grace_and_ticket`
38. [Integration] **GIVEN** a swap in flight, **WHEN** the client disconnects, **THEN** the commit completes, and on resume `RESULT_QUERY` reports it and the new set is shown.
39. [Integration] **GIVEN** the meta service is down, **WHEN** a field swap runs, **THEN** the old set stays, `ERR_SERVICE_DEGRADED` is returned, and the viewfinder works once the lock ends.
40. [Integration] **GIVEN** a new tab that takes over the session during a swap, **WHEN** the old session's write reaches the meta service, **THEN** it writes nothing.
41. [Integration] **GIVEN** a session server killed mid-session, **WHEN** `LEASE_TTL_S` has passed, **THEN** a Home equip commits.
42. [Integration] *(provisional: Camera Model)* **GIVEN** a playtest of a Halo Keeper at 150 ms RTT, **WHEN** a bayonet swap starts on the anticipation cue, **THEN** the player can shoot within the decisive pose, and a thread swap cannot.

**F. Soft-lock floor (Rules 12–13, 27)**

43. [Logic] **GIVEN** every Starting Choice path, **WHEN** the grant commits, **THEN** the account has exactly one bound phone in the pocket slot and a valid loadout. *(provisional: Starting Choice)* `test_every_start_path_has_pocket_phone`
44. [Logic] **GIVEN** an account that clears its camera set and sells all its gear, **WHEN** the sequence finishes, **THEN** `active = PHONE`, the validity is `VALID_PHONE` and F1 returns C. `test_account_can_always_shoot_after_selling_all`
45. [Logic] **GIVEN** a mounted lens lost by operator removal, **WHEN** the transaction commits, **THEN** the validity is `INCOMPLETE`, `rev` rose by 1, and `active` is unchanged. `test_lost_lens_leaves_incomplete_without_auto_switch`
46. [Logic] **GIVEN** a stored camera set made invalid by a catalog fixture, **WHEN** the loadout loads, **THEN** `active = PHONE`, the camera set is cleared, the items are still owned, and `rev` rose by 1. `test_invalid_stored_set_falls_back_to_phone`

**G. UI**

47. [UI] *(provisional: Shop, Sell & Inventory UI spec)* **GIVEN** the Gear screen with a full Bag, **WHEN** shown, **THEN** the loadout, 4 filled pockets, mounted marks, Shelf, gear ceiling and kit reach are visible. Evidence: screenshot.
48. [UI] **GIVEN** a pending equip, **WHEN** shown, **THEN** the lens name and ceiling show the old values with a pending state; after confirmation they update. Evidence: two screenshots.
49. [UI] *(provisional: Viewfinder HUD)* **GIVEN** the field swap control, **WHEN** opened, **THEN** it lists fitting Bag lenses, the phone, time words and ceilings; unfitting items appear disabled with the reason. Evidence: screenshot.
50. [UI] **GIVEN** a player in the Field, **WHEN** the Gear screen opens, **THEN** it is read-only with "Back at home you can change this". Evidence: screenshot.

Coverage notes: fit rules themselves are tested in Gear Catalog (ACs 22–27); this document tests that they are enforced. Rate limits and idempotency mechanics are tested in Network.

## Open Questions

> 2026-11-05 (pillar check): Starting Choice must show what the phone path gains, because camera starters get everything phone starters get plus a camera (D6). Check that faster mounts do not become a paid advantage once Gear prices exist.

| # | Question | Owner | Resolve by |
|---|---|---|---|
| 1 | The meta service must run fit rules 15–16 and F13. If it is not Godot (PocketBase is the candidate), they must be ported or pre-computed as a table of legal pairs, and AC 24 must prove parity. | technical-director → ADR | Architecture phase |
| 2 | What does returning Home cost? In MVP, leaving and rejoining takes only seconds, so the Bag limit is soft unless rejoining places the player at a fixed entry point rather than where they stood. Recommend the fixed entry point; Zone Access may add travel cost in VS. | game-designer (Player Movement, Zone Access) | Before the Bag is playtested | **Closed 2026-11-05: fixed entry point (see Core Rules D).**
| 3 | Is `FIELD_COMMIT_P95_MS` = 500 achievable on the chosen backend? **UNVERIFIED**. | network-programmer | First backend spike |
| 4 | Does the Gear Shop buy gear back? If it does, sell-back is the only MVP item sink and needs a price below purchase. If not, mistakes are permanent. | economy-designer (Gear Shop) | Gear Shop design |
| 5 | Phone path (B3): later B or A phones would use the pocket slot as normal unbound items, with the bound Pebble staying on the Shelf as the floor. Rule 12 allows this but it is untested. | game-designer + user | Before Starting Choice |
| 6 | Economic health metrics to track once telemetry exists: share of outings with a full Bag, swaps per outing by type, share of accounts with duplicate models, and share of shots on the phone after a camera is owned. No target values yet: they need playtest data. | analytics-engineer | Alpha |
| 7 | Should a phone starter's first camera be sold as a body + lens bundle? From the phone they need two items to reach a B ceiling (Hearth + KR 50), while a camera starter needs one. `mint_item` already supports it through `acquired_slot`. | economy-designer (Gear Shop, Starting Choice) | Gear Shop design |
| 8 | Accessories (tripod, filters, reflector; Gear Catalog Open Question 4): do they take Bag slots? Recommend yes. | game-designer | Alpha |
| 9 | Does `Suspended` or a reconciliation freeze need a read-only "my gear" view? Reads continue, but no screen is specified. | ux-designer | `/ux-design` |

## Decisions to confirm

> **DECIDED 2026-11-05 (user):** every item = the recommended option. Open Question 2 settled: after going Home, the player rejoins the field at a fixed entry point, so the Bag limit is a real choice.

- **D1. Carry limit.** (a) **A Bag of 4 lens and adapter slots from MVP, mounted gear included, the same for everyone.** It never binds on the first-playable set, and adding a limit to a live game later is felt as a loss. It also stops wealth from turning into field power. Cost: one extra screen and one rule. (b) No carry limit in MVP, so all owned lenses are reachable in the field and `swap_ms` is the only cost; add the Bag at Vertical Slice. Cheaper now, but a later limit takes something away from players. (c) Only the mounted set comes along, with no field swaps at all. Simplest, but it removes the "which glass" moment that Gear Catalog's Game Feel promises. **Recommendation: (a).**
- **D2. Storage limit.** (a) **No gameplay limit on the Shelf; only a technical `MAX_ITEM_RECORDS` of 200.** Storage costs 60 KB per account at most, and the index places the storage sink in Gallery (A12). (b) A Shelf limit with paid expansion from MVP, which adds a money sink but taxes collecting, a core pleasure, and pushes new players into storage management. (c) No limit now, with a paid Shelf for Alpha as a sink that scales with tier. A real later option, though it needs care with hoarded serialised gear. **Recommendation: (a), keeping (c) in reserve for Currency & Wallet's budget.**
- **D3. Field lens swapping and its cost.** (a) **Allowed anywhere from the Bag, for time only: `swap_ms` by mount (1,200 bayonet, 2,500 thread), +400 ms for an adapter, viewfinder closed, no money and no wear.** The decision stays about timing, and F4 ties it to the anticipation cue. (b) Allowed, with a chance of wear or dust on each swap: more realistic, but a penalty that feels punishing in a cozy game. (c) Only at Home. Simplest, but the viewfinder never gets its "takes a breath" moment. **Recommendation: (a).**
- **D4. Field body changes.** (a) **Bodies change only at Home; the phone is the one second device.** One body per outing keeps bag rules, burst rate changes and the mount choice simple, and makes the body a real daily decision. (b) A spare body in the Bag at 1 slot, with a longer swap time: true to real two-body shooters, but it adds a case to every rule. (c) Two bodies always available. **Recommendation: (a).**
- **D5. The phone once a camera is owned.** (a) **A bound pocket phone: kept for life, no Bag slot, 800 ms to draw in the field, never sold, traded or broken.** This keeps the concept's "valid street style", removes every soft-lock, and closes resale of a free item. (b) An ordinary item that can be sold and needs a Bag slot: simple, but a player can sell away their only way to shoot. (c) Retired when the first camera is bought: clean, but it breaks the concept's "stays valid later". **Recommendation: (a).**
- **D6. Do camera starters also get the phone?** (a) **Yes, on every path.** One rule, and the soft-lock floor holds for everyone. Since the Gear Catalog calls it the free starting phone, it costs the camera starter nothing. If Starting Choice gives the phone a real cost, this needs another look. (b) Phone starters only, with camera starters given a separate safety net. Keeps the two paths more distinct, but needs a second rule to prevent a soft-lock. **Recommendation: (a).**
- **D7. Loadout presets.** (a) **Not in MVP; 3 named presets at Vertical Slice, Home only, applied as one transaction.** The last loadout and Bag already persist, and the first playable has few items. (b) Presets in MVP: more scope and a new record for a problem players do not have yet. (c) Presets usable in the field: this would bypass the Bag limit unless heavily restricted. **Recommendation: (a).**
- **D8. How a field swap reaches the server.** (a) **Through the session socket and service path, with a lease that blocks the meta-channel `equip` during a session.** No race with shots, and the swap time cannot be skipped. Costs a lease field, renewals and a new service-path call. (b) Meta channel plus a post-commit push to the session, with no lease. Less to build, but a client can skip the swap time and the Bag limit by calling the meta channel. (c) No field swaps, so the set is fixed per session (goes with D3 (c)). **Recommendation: (a).**
- **D9. Permanent key for equips.** (a) **`loadout.rev` compare-and-set (F5).** Refuses late retries forever with no new table, and also catches stale screens and two devices. (b) An append-only `loadout_event` table with unique `rid`: gives an audit trail, but adds a growing table for a free action. **Recommendation: (a).** Accounts Rule 30 must name this as an accepted exception.
- **D10. Removing an equipped item.** (a) **Refused with `ERR_ITEM_LOCKED`; the player changes the loadout first.** One rule, no surprises, and a sale can never silently change the loadout. (b) Automatic unequip inside the sale transaction: one click fewer, but it can drop a player to the phone by accident. **Recommendation: (a).**
- **D11. Effect key for multi-item actions.** (a) **Change Accounts to unique (`acquired_rid`, `acquired_slot`).** It mirrors the ledger's `leg`, and is needed for the camera grant and any bundle. (b) Give each item in a grant its own derived `rid`: no schema change, but more rules at each caller. **Recommendation: (a).** This edits a Designed GDD.
- **D12. Field naming and `item.tier`.** The GDDs disagree: Gear Catalog says `item_uid` and `model_id`, Accounts says `item_id` and `catalog_id`, and Accounts Rule 20 lists an `item.tier` column although tier is per model. (a) **Use `item_id` and `model_id`, and remove `item.tier`.** One source for tier, and a signed-off tier migration touches no item rows. (b) Keep `item.tier` as a cached copy for faster queries: cheaper telemetry, but a second source that can drift. **Recommendation: (a).** This edits two Designed GDDs.
- **D13. Duplicate models.** (a) **Allowed, with a "You already own one" warning.** Instances matter later for serials and condition, and refusing would need a rule that Trading would then have to break. (b) One per model per account in MVP: prevents mistakes, but needs removing at Alpha. **Recommendation: (a).**
- **D14. Moving during a swap.** (a) **Normal movement allowed, viewfinder lowered, no cancelling.** Keeps the outing flowing and adds no new Movement state. (b) Standing still during a swap: more deliberate, but it adds a state, and it feels like a stun in a game with no combat. (c) Allow cancelling: friendlier, but it needs a rollback of a commit already under way. **Recommendation: (a).**
- **D15. A mounted lens is lost in the field (Alpha).** (a) **The loadout becomes `INCOMPLETE` and the HUD offers the phone or a Bag lens; nothing changes without the player.** The player stays in control. (b) Automatic switch to the phone: faster, but a silent change of camera and ceiling. **Recommendation: (a).**
