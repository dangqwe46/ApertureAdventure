# Currency & Wallet

> **Status**: Designed 2026-11-05 (pending `/design-review` in a fresh session)
> **Author**: economy-designer (agent draft for user review); inputs from `accounts-server-persistence.md` and `network-transport-server-authority.md` (both binding), `gear-catalog-specs.md`, `systems-index.md`, `game-concept.md`
> **Last Updated**: 2026-11-05
> **Last Verified**: 2026-11-04
> **Creative Director Review (CD-GDD-ALIGN)**: REVISED 2026-11-05 — CONCERNS fixed: pacing promise, phone framing, price wording, sink-plan owner, stale text. NOT ASSESSED: MDA target; Pillar 3 only lightly tested.
> **Implements Pillar**: Pillar 2 "Every photo matters" (a sale pays real, permanent money that the player can trace, and that money is what turns a photo into the next lens); supports Pillar 1 "Seeing is the skill" (earnings come from photos, and money buys a ceiling, never a result) and the anti-pillar "not pay-to-win" (no real-money path into the wallet, no tier for sale, no paid random reward)

## Summary

Currency & Wallet defines Aperture's one soft currency (**Glints**), counted in whole integers, and the wallet each account holds it in. It sets the rules every money movement must obey: balance limits, the negative-balance policy, starting balances, the closed catalogue of faucets and sinks with an owner for each, and the shared budget table that Photo Pricing and Gear Shop cite. It also defines the economy-health numbers Economy Telemetry will watch. It sets no prices (Photo Pricing, Gear Shop) and stores no ledger rows (Accounts & Server Persistence): it says what may move and why, and Accounts proves that it moved.

> **Quick reference** — Layer: `Core` · Priority: `MVP` · Key deps: `Accounts & Server Persistence` (ledger storage, F3 invariants, system wallets, reconciliation, effect keys), `Network Transport & Server Authority` (authority table, `rid` idempotency, Rule 30 and D15 never-optimistic display) · Soft inputs: `Gear Catalog & Specs` (model and tier counts for the buy-out figure), `Starting Choice` (kit charge) · All money figures in this document are **placeholders** for the later balance pass.

## Overview

The core loop turns photos into gear through money. This system is the middle of that sentence. It is small on purpose: one currency, one wallet per account, one rule set.

The split of responsibility is strict.

- **Accounts & Server Persistence owns storage.** The double-entry, append-only ledger (Rule 27), the cached balance (Rule 28), atomic transactions (Rule 26), corrections as new entries (Rule 29), permanent effect keys (Rule 30), reconciliation (Rule 33) and the invariants of its F3 are reused here unchanged. This document does not redefine them.
- **Network Transport owns the wire.** Balances and prices are server-owned (authority table), every spend or sale carries a `rid` (Rule 27), and the client never shows a money change before the server confirms it (Rule 30, D15).
- **Photo Pricing, Gear Shop and every other faucet or sink owner set amounts.** They decide how much. This system decides whether the movement is legal and which named system wallet it runs through.
- **This system owns the meaning of money:** its name, its unit, its limits, the list of legal movements, the budget those movements must fit, and the numbers that tell the team whether the economy is healthy.

Binding user decisions this GDD implements: one soft currency and no premium currency in MVP (systems index A13); never sell tier; no paid random rewards; guests allowed with limits (Accounts D1); double-entry append-only ledger (Accounts D6); economy display never optimistic (Network D15).

**Current verdict on balance: not yet balanced.** MVP sinks are all exhaustible. A player who buys everything keeps earning with nothing left to spend on, and the planned Alpha sinks do not fully close that gap (F9). That is acceptable for closed playtests and must be resolved before the gates in Rule 32. See Decisions to confirm D9.

## Player Fantasy

Money is not the fantasy. The fantasy is photography, and the wallet's job is to make the work feel respected. The feeling it protects is **"my eye paid for this lens."**

- **"That photo bought this."** A player can look at a lens and remember the shot that paid for it. Each entry in the wallet history names what happened in plain words, so the link between a photo and a purchase stays visible (Pillar 2).
- **"The money adds up."** This is the promise from Accounts. Every Glint came from somewhere and went somewhere, and a number on screen is always a number the server has confirmed.
- **"I can't get stuck."** A cozy game has no bankruptcy. There is no debt, no negative balance and no bill that can stop a player from shooting. At zero Glints the camera still works and photos still sell (Rule 12). The design leans on loss aversion by removing it: nothing the player holds is taken away for being away or for being poor.
- **"It's a little further than I can reach."** The next useful piece of gear should feel within reach: a few sessions early on, with later upgrades taking longer (see the pacing bands in Rule 28). A phone start holds 600 Glints, enough to make a camera kit one possible goal among others (the phone remains a valid way to play; Open Question 5 is a playtest gate), which uses the endowed-progress effect: a goal already partly filled pulls harder than an empty one, and the goal-gradient effect makes effort rise as it nears.
- **"Nobody can buy what I earned."** No real money enters the wallet, so a rival's gear says something true about their work.

The tone target is a small tin of savings on a darkroom shelf: modest, warm, exact, and never the centre of attention. There is no money in the viewfinder (UI Requirements). Income is a stated price for finished work with no random payout, not a slot machine. The surprise in this game lives in what the lens finds, not in what the wallet does.

## Detailed Design

### Core Rules

**A. The currency**

1. **One currency.** Aperture has exactly one currency, a soft currency earned and spent in play. There is no premium currency in MVP (systems index A13). A second currency needs a new user decision and a revision of this GDD.
2. **Name (D1).** Proposed display name: **Glint** (singular), **Glints** (plural): a small catch of light, the thing a photographer spends their life chasing. It avoids camera vocabulary the player must learn with a different meaning (exposure, stop, frame, print), avoids the Lumen cyan colour role in the art bible, and has no collision in any existing GDD. The name is display data held in localisation keys. No schema, ledger kind or API uses it, so a rename costs only text.
3. **Whole units only.** One Glint is the smallest unit and equals the "minor unit" in Accounts Rule 27. There are no fractions, decimals or sub-units anywhere: not in the ledger, not in the display, not in a price. Amounts are 64-bit integers (Accounts F3).
4. **Rounding belongs to the producer and favours no minting.** A system that computes an amount with percentages or multipliers must return an integer before calling the wallet, using integer arithmetic. Payouts round down, charges round up, so rounding can never create money. A split between several recipients (crew credit, Alpha) must sum exactly to the amount being split; the remainder goes to the lowest seat number, by the same deterministic rule every time.
5. **Money cannot be bought (binding).** No ledger kind may represent real money coming in. No faucet may be triggered by a payment. If a paid store ever exists it is a new system (A13) that sells only cosmetics and does not touch this wallet. Adding a faucet tied to payment requires creative-director approval and a user decision, and it remains forbidden to sell tier.
6. **No paid random rewards (binding).** A spend may buy an item, a service or access with a stated result. No sink may return a randomised reward, buy a rarity roll, buy a re-roll, or improve the odds of one. Taking a photo always stays free, so the capture roll is never a paid roll. This holds for Glints as well as any future paid item, because the stricter rule is cheaper than arguing where the regulatory line sits. Every new kind added to the catalogue passes this check (Rule 18).

**B. The wallet**

7. **One wallet per account, owned by the server.** A wallet exists for every account from creation, guests included (Accounts catalogue: "one player wallet per account"). The `wallet_id`, not the `account_id`, is what the ledger references (Accounts Rule 27). The balance is the Accounts `cached_balance`, always equal to the ledger sum (Accounts F3). The client holds only a copy of the last confirmed value (Network authority table).
8. **Wallet operations run inside the caller's transaction.** The wallet offers one operation, `apply(rid, kind, legs)`, called by the faucet or sink owner inside the single transaction of its action (Accounts Rule 26). A sale writes its ledger legs and its photo state in one commit; a purchase writes its legs and its item in one commit. No system writes `ledger_entry` rows directly, and no standalone "add money" request exists on the client API.
9. **Checks.** Every `apply` passes F1 for each player wallet it touches. A failed check aborts the whole transaction, so the photo stays unsold or the item stays unbought. Checks run in this fixed order, and the first failure decides the error:

| Order | Check | Failure |
|---|---|---|
| 1 | Kind is in the catalogue (Rule 16) and the caller owns it | `ERR_NOT_ALLOWED`, logged as a server defect |
| 2 | Wallet state allows the write (States and Transitions) | `ERR_SCOPE_FROZEN`, `ERR_BANNED`, `ERR_ACCOUNT_PENDING_DELETION` or `ERR_NOT_ALLOWED` |
| 3 | Amount is a whole number and `0 < |Δ| ≤ MAX_TX_AMOUNT` | `ERR_OUT_OF_RANGE` |
| 4 | Result is not below `BALANCE_FLOOR` | `ERR_INSUFFICIENT_FUNDS` |
| 5 | A credit does not pass `WALLET_CAP` | `ERR_WALLET_FULL` (new code) |

10. **Idempotency is inherited.** The same `rid` with the same body returns the original outcome and moves no money; the same `rid` with a different body is `ERR_IDEMPOTENCY_CONFLICT` (Network Rules 21, 27). After `IDEMPOTENCY_WINDOW_S` the permanent key `(wallet_id, rid, leg)` still blocks a duplicate (Accounts Rule 30). See Open Question 3 on keying system-wallet legs.
11. **Every confirmed response carries the new balance.** A response to any money action includes `balance_after` and the wallet's latest `entry_id`. The client keeps the value with the highest `entry_id`, so a late response can never move the display backwards (Accounts Edge Cases: ordering uses database sequence IDs, not clocks).

**C. Negative balance and debt (B4 → D4)**

12. **The no-stranding rule.** `BALANCE_FLOOR = 0` for every player wallet. There is no debt, overdraft, loan or negative balance. A player at 0 Glints must always be able to shoot and sell. No mandatory sink may exist: every spend is a choice, or has a free alternative (a free home zone for travel; a usable basic kit when other gear needs repair). Every future sink owner must state how it meets this rule.
13. **The starting camera is paid up front (recommended answer to B4).** The kit charge comes out of the starting grant in the same transaction as the grant (Rule 15). No obligation outlives the start. This keeps `BALANCE_FLOOR` at 0 as Accounts expects, needs no debt state, no repayment rule and no answer to "what happens to an account deleted in debt", and fits the cozy tone.

**D. Starting balances**

14. **One grant for everyone, once.** Every account receives `START_GRANT` from `faucet:start_grant` when Starting Choice commits. The grant is once per `account_id` (Accounts Rule 4 and its Starting Choice row), enforced as a one-per-wallet constraint on the kind and not only by `rid`, because a modified client could send a fresh `rid`. Guest upgrade never re-grants.
15. **The camera costs starting money.** A camera start pays `KIT_CHARGE` to `sink:start_kit` in the same transaction as the grant. One transaction, four legs:

| Start | `faucet:start_grant` | Player | `sink:start_kit` | Starting balance |
|---|---|---|---|---|
| Phone | −600 | +600 | — | **600 Glints** |
| Entry camera | −600 | +600, then −500 | +500 | **100 Glints** |

The balances `START_BALANCE_PHONE = 600` and `START_BALANCE_CAMERA = 100` are this system's targets. `KIT_CHARGE = 500` is a placeholder price that Starting Choice owns; if it moves, this table moves with it (F2). The reasoning:

- 600 is about 1.5 hours of C-band income: a real cushion, and 40% of the kit's shop value, but not enough to buy the kit on day one (`START_GRANT < P_kit`, F2). If the phone start could buy the kit at once, it would hold everything a camera start has plus more cash, and the camera choice would be a trap.
- 100 is about 15 minutes of C-band income: enough that the wallet is not empty on the first screen, while "you spent your savings on this camera" stays true.
- The kit charge sits below the kit's shop value on purpose (F3). The camera start buys depth and a shorter road to the first lens; the phone start buys a cushion and an easier early game. Whether those are equal is a playtest question, not arithmetic (Open Question 5).

**E. Catalogue of faucets and sinks**

16. **The catalogue is closed.** A ledger kind that is not in this table is illegal. Each kind becomes a system wallet (Accounts Interactions row: "the ledger kinds it names become system wallets here"). Each has one owner, which sets its amounts and triggers. This GDD sets none of those amounts.

**Faucets** (money enters; the system wallet goes negative):

| System wallet | Owner | From | Trigger | Bounded? | Notes |
|---|---|---|---|---|---|
| `faucet:start_grant` | Starting Choice (14) | MVP | Starting choice commits | Once per account | Rule 14 |
| `faucet:npc_sale` | Photo Pricing & NPC Clients (16) | MVP | A photo sells to an NPC, including client requests | Limited by diminishing returns and demand | **Main faucet.** Named in Accounts Rule 27 |
| `faucet:gear_buyback` | Gear Shop (17) | Reserved; off in MVP (D10) | Shop buys gear back | Must obey Rule 19 | Only if D10 changes |
| `faucet:theme_prize` | Daily Themes & Player Judging (23) | Vertical Slice | Theme placement | Fixed prize pool per theme | Registered accounts only (Accounts Rule 3) |
| `faucet:claim_participation` | First-Claim & Image Serials (34) | Alpha, if B7 allows | Presence at a claimed appearance | Per appearance | Depends on B7. Guests hold no claims |
| `faucet:event_reward` | Server-Wide Events (45) | Full Vision | Event completion | Per event | Structure with live-ops-designer |
| `faucet:compensation` | Operator (producer decision) | MVP | Announced make-good after a restore | Manual | Accounts Open Question 16 |

**Sinks** (money leaves; the system wallet goes positive):

| System wallet | Owner | From | Trigger | Capacity | Notes |
|---|---|---|---|---|---|
| `sink:start_kit` | Starting Choice (14) | MVP | Camera start | One-time | Excluded from `sink_ratio` (F7) |
| `sink:gear_shop` | Gear Shop (17) | MVP | Gear purchase | **Exhaustible** (catalogue can be bought out, F6) | Named in Accounts Rule 27 |
| `sink:storage` | Gallery (15) | MVP hook, if stocked | Storage expansion | **Exhaustible** (stops at `MAX_PHOTO_RECORDS`) | Placement per A12 |
| `sink:travel` | Zone Access & Travel (22) | Vertical Slice | Paid travel | Recurring | Rule 12: a free home zone must remain |
| `sink:maintenance` | Gear Condition & Maintenance (31) | Alpha | Routine upkeep | Recurring, grows with tier | Rich-get-richer damper |
| `sink:repair` | Gear Condition & Maintenance (31) | Alpha | Repair | Recurring | Named in Accounts Rule 27. Depends on B6 |
| `sink:craft_fee` | Gear Crafting (33) | Alpha | Merge fee | Recurring | Fixed result only (Rule 6) |
| `sink:market_fee` | Player-to-Player Trading & Market (37) | Alpha | Fee on a completed trade | Recurring, scales with trade volume | Fee legs commit with the trade |
| `sink:account_closed` | Accounts (purge step) | MVP | Balance swept at purge (D8) | One-time per account | Needs an Accounts change; not a player spend, so excluded from `sink_ratio` |

**Neutral wallets** (not faucets or sinks; money is held or corrected):

| System wallet | Owner | From | Trigger | Notes |
|---|---|---|---|---|
| `escrow:market` | Player-to-Player Trading & Market (37) | Alpha | Money locked in an open offer | Still counted in the F3 identity as a system wallet; Telemetry reports it as held money, not as sunk |
| `escrow:commission` | Commission Board (42) | Full Vision | Player-posted commission | Same |
| `adjust:correction` | Operator | MVP | Accounts Rule 29 `adjustment` | Requires a reason and operator. Should stay near zero (F8) |

17. **System wallet floors.** `faucet:*` and `adjust:*` are unbounded below (Accounts F3). `sink:*` and `escrow:*` have a floor of 0, so a sink can never pay out more than it took in.
18. **Adding a kind.** A new kind needs an entry here, a named owner, a stated capacity, a no-stranding statement (Rule 12), and a pass of Rules 5 and 6. Each new faucet must also say which sink capacity pays for it.
19. **No arbitrage.** No sequence of legal actions may return more money than it spent. For any resale path, `resale_price ≤ BUYBACK_MAX_PCT × price_paid`, rounded down. Starter gear paid for below shop value is measured against `KIT_CHARGE`, not shop value. In MVP there is no gear buy-back at all (D10).
20. **Player-to-player money (Alpha).** A transfer has two player legs, or runs through `escrow:market` (Accounts Rule 27). Guests are never a party to one: any player-to-player leg on a guest wallet fails with `ERR_NOT_ALLOWED` (Accounts Rule 3). Trading owns the rest, including the price floors and ceilings from the game concept.

**F. Guests**

21. **Guest wallets are real wallets with one limit.** A guest earns, spends and holds Glints by the same rules, and the wallet survives guest upgrade unchanged (Accounts Rule 4). The limit: guests have no player-to-player legs, and no faucet that needs registration (theme prizes, claim rewards). Because a guest cannot send money to anyone, the throwaway-account grant farm has no outlet, so no lower guest cap is needed (D7).
22. **Guest expiry.** A purged guest's balance is handled as any purge (D8).

**G. Limits**

23. **`WALLET_CAP` (D5).** A wallet holds at most `WALLET_CAP = 9,999,999` Glints. The cap is a safety limit, not a game mechanic: at the top of the A band with no spending it takes about 8,333 played hours to reach (F10). It bounds the damage of an exploit and keeps the number inside a seven-digit UI field.
24. **A credit that would pass the cap is refused whole.** The action fails with `ERR_WALLET_FULL`, the photo stays unsold, and nothing is lost. Money is never silently clipped, because that would be a hidden sink and a broken promise that the money adds up.
25. **Debits are never blocked by the cap.** Lowering the cap never trims a balance. A wallet above a lowered cap may spend freely and may not receive until it is below the cap.
26. **`MAX_TX_AMOUNT`.** No single movement exceeds `MAX_TX_AMOUNT = 1,000,000`. This catches a mistyped price or a bad multiplier before it reaches a player. It is about 830 hours of top-band income and sits far above any plausible MVP amount.
27. **No daily earn cap (D11).** Income is limited by Photo Pricing's diminishing returns, not by a hard limit in the wallet. A cap would punish the player's best day. Abnormal earning is a Telemetry alarm, not a block.

**H. Shared budget table**

28. **This is the single table Photo Pricing and Gear Shop cite** (systems index, Circular Dependencies). Its figures are planning placeholders. They are **envelopes, not prices**: each owner sets real amounts and must either fit these or request a change here.

**Target earn rate** (one placeholder band per gear ceiling; F4):

| Gear ceiling | Low | Mid | High | Implied mean payout at 10 sales per hour |
|---|---|---|---|---|
| C (phone, entry kit) | 300 | 400 | 500 | 30–50 |
| B | 500 | 650 | 800 | 50–80 |
| A | 800 | 1,000 | 1,200 | 80–120 |

All in Glints per active hour. The top of each band touches the bottom of the next, so a skilled player on lesser gear can match a careless one on better gear: Pillar 1 and the concept's "a skilled phone player should beat a careless camera owner". The whole ladder from C to A spans 2.5× at the mids, which keeps the primary positive feedback loop mild.

**Planning envelopes for gear** (inputs to F5 and F6; Gear Shop owns the real prices):

| Kind | C | B | A | Models (C/B/A) | Subtotal |
|---|---|---|---|---|---|
| Body | — | 1,200 | 4,000 | 0 / 2 / 2 | 10,400 |
| Lens | 300 | 700 | 2,400 | 3 / 5 / 2 | 9,200 |
| Adapter | — | 200 | 800 | 0 / 2 / 1 | 1,200 |
| Phone (`phone_basic_c_01`) | not sold | — | — | 1 / 0 / 0 | 0 |
| **All 18 enabled models** | | | | 4 / 9 / 5 | **20,800** |

The model counts match Gear Catalog Rule 26 (C 4, B 9, A 5).

**Pacing targets** (camera start, first-playable path; F5):

| Step | Envelope | Income used | Low band | Mid band | High band |
|---|---|---|---|---|---|
| U1 KR 50 mm (first B ceiling) | 700 | C | 2.0 h | 1.5 h | 1.2 h |
| U2 KR 85 mm | 2,400 | B | 4.8 h | 3.7 h | 3.0 h |
| U3 Lantern (first A ceiling) | 4,000 | B | 8.0 h | 6.2 h | 5.0 h |
| **Cumulative to A ceiling** | 7,100 | | **14.8 h** | **11.3 h** | **9.2 h** |
| Sessions at `SESSION_H_PLAN` = 0.5 h | | | 30 | 23 | 19 |
| Phone start, adds the start gap (F3) | | | +3.3 h | +2.5 h | +2.0 h |

`SESSION_H_PLAN` is an assumption. The repository has no session-length target.

**Resource flow per phase** (faucet rate, sink capacity, projected surplus):

| Phase | Faucet rate (A band) | Sink capacity | Exhausted after | Projected surplus |
|---|---|---|---|---|
| First playable, shop stocks only the 3 upgrades | 800–1,200 per h | 7,100 (camera), 8,600 (phone, also buys the kit) | 9.2–14.8 h (camera) | **Unbounded** after that: the whole faucet, 800–1,200 per h |
| MVP, all enabled models stocked | 800–1,200 per h | 19,300 (camera), 20,800 (phone); storage expansion not yet priced | 19.4–30.1 h (camera) | **Unbounded** after that: 800–1,200 per h |
| Vertical Slice, adds travel | 800–1,200 per h | Target recurring share 10% | Never | 720–1,080 per h |
| Alpha, adds upkeep, repair, market fee | 800–1,200 per h | Target recurring share 40% (below) | Never | 480–720 per h, **still positive**: sink question open |

**Target recurring sink shares after buy-out** (of faucet; planning only):

| Sink | Target share | Why this size |
|---|---|---|
| `sink:maintenance` + `sink:repair` | 25% | Grows with tier; large enough to damp the top, small enough not to read as a tax |
| `sink:travel` | 10% | A real choice, never a toll on the home zone |
| `sink:market_fee` + `sink:craft_fee` + `sink:storage` | 5% | Scales with activity |
| **Recurring total** | **40%** | `RECURRING_SINK_MAX`: above this, players feel taxed, which fights the cozy tone |
| New exhaustible content (S and above, seasonal gear) | 45% | Must be supplied by the Alpha catalogue; **no system yet commits to this** |
| Allowed net growth | 15% | Gives a target long-run `sink_ratio` of 0.85 |

29. **Exhaustible sinks must be counted as exhaustible.** Any sink a player can buy out is reported with its total capacity, not as a rate (F6). Gear Catalog Open Question 7 is answered by F6.

**I. Economy health**

30. **The numbers are defined here; Economy Telemetry collects them.** F7 and F8 define the metrics, their healthy bands and the alarm for each. Telemetry reads aggregates only (Accounts Interactions row). Before Economy Telemetry exists (Alpha), the same numbers come from read-only ledger queries during playtests.
31. **Metrics are observations.** A metric never moves a price, changes a rate or blocks a player automatically. A person reads it and makes a tuning change, documented with its rationale.
32. **Gates (D9).** A recurring sink plan that takes `sink_ratio` for players past buy-out to the target band must exist and be approved **before** any of these: player-to-player trading ships; `enabled_cap` rises above A; the game opens to the public. Until then the budget table stays "not balanced" and may not be marked Approved. Owner of the recurring-sink plan: economy-designer with the producer (2026-11-05). Playtesters must be told that after buy-out at about 19–30 hours, MVP sales buy nothing further.

### States and Transitions

**Wallet state.** Most states follow the account (Accounts lifecycle). `Frozen` is the per-scope flag from reconciliation (Accounts Rule 33).

| State | Meaning | Entered when | Leaves to | Credits | Debits | Reads |
|---|---|---|---|---|---|---|
| `Unfunded` | Wallet exists at balance 0; no starting choice yet | Account created | `Active` when the start transaction commits; `Closed` on purge | Start transaction only | Start transaction only | Yes |
| `Active` | Normal | Start transaction commits; thaw; suspension lifted; deletion cancelled | `Frozen`; `Locked`; `Closed` | Yes | Yes | Yes |
| `Frozen` | Reconciliation mismatch on this wallet | Rule 33 finds a mismatch | `Active` after an audited fix (Accounts Rule 29) | No: `ERR_SCOPE_FROZEN` | No: `ERR_SCOPE_FROZEN` | Yes, ledger-derived value with a "being checked" note |
| `Locked` | Account is `Suspended` or `PendingDeletion` | Account state change | `Active` on lift or cancel; `Closed` on purge | No: `ERR_BANNED` or `ERR_ACCOUNT_PENDING_DELETION` | Same | Yes, by the owner where the account may sign in |
| `Closed` | Account purged; owner link removed; wallet and ledger remain (Accounts Rule 44) | Purge commits | — (terminal) | No: `ERR_NOT_ALLOWED` | No, except the purge sweep inside the same transaction (D8) | Aggregates only |

Guest and registered wallets share every state. Upgrade changes no wallet state (Accounts Rule 4).

**Client display state** (Network Rule 30, D15). This is a state of the display only and never of the money.

| State | Shows | Entered when | Leaves to |
|---|---|---|---|
| `Confirmed` | The last server-confirmed balance | A confirmed response or read | `Pending`; `Stale` |
| `Pending` | The **unchanged** confirmed balance, plus a pending mark on the action button, within 100 ms of the click | Player sends a money action | `Confirmed` on success or refusal |
| `Stale` | The last confirmed balance, marked "Not up to date" | Meta channel unreachable, or `restore_epoch` rose and the refetch has not returned | `Confirmed` when a read succeeds |

There is no state in which the client shows a predicted balance. A retry after a drop reuses the same `rid`, so `Pending` may last longer without any risk of double payment.

### Interactions with Other Systems

| System | This system provides | This system receives | Contract notes |
|---|---|---|---|
| **Accounts & Server Persistence** | The list of system wallets (Rule 16), `BALANCE_FLOOR = 0`, `WALLET_CAP`, `MAX_TX_AMOUNT`, wallet state rules | Ledger storage, zero-sum and floor constraints, `cached_balance`, reconciliation, `wallet_owner`, effect keys | Everything in F3, Rules 26–34 and 44 is reused. Requested additions are in Open Question 2 |
| **Network Transport & Server Authority** | `ERR_WALLET_FULL` for the closed code list; `balance_after` and `entry_id` in money responses | `rid`, idempotency, authority rule, pending and confirmation budgets | All economy writes are meta-service transactions. Never optimistic (Rule 30, D15) |
| **Starting Choice** (14) | `START_GRANT`, balance targets, the two start transaction shapes | `KIT_CHARGE`, which start was chosen | One transaction, once per account |
| **Photo Pricing & NPC Clients** (16) | Earn-rate bands, `faucet:npc_sale`, `apply` | Payout amounts | Must fit the band or request a change. Owns diminishing returns and demand |
| **Gear Shop** (17) | Budget envelopes, `sink:gear_shop`, Rule 19 | Prices, stock | Must report total stocked value so F6 stays true |
| **Gear Catalog & Specs** (5) | Answer to its Open Question 7 (F6) | Model and tier counts | Prices stay outside the catalog |
| **Inventory & Loadout** (10) | — | Item writes in the same transaction | One purchase commits money and item together |
| **Gallery** (15) | `sink:storage` | Expansion price and limit | Limit stays at or below `MAX_PHOTO_RECORDS` |
| **Shop, Sell & Inventory UI** (21) | Balance, display states, history entries and their labels | — | See UI Requirements |
| **Zone Access & Travel** (22) | `sink:travel`, Rule 12 | Travel costs | Home zone stays free |
| **Daily Themes & Player Judging** (23) | `faucet:theme_prize` | Prize amounts | Prizes are fixed, never paid-entry lotteries (Rule 6) |
| **Gear Condition & Maintenance** (31) | `sink:maintenance`, `sink:repair`, target share | Costs by tier | Must meet Rule 12: broken gear can never leave a player unable to shoot |
| **Gear Crafting** (33) | `sink:craft_fee` | Fees | Result must be stated in advance (Rule 6) |
| **First-Claim & Image Serials** (34) | `faucet:claim_participation` | Amounts, per B7 | Splits follow Rule 4 |
| **Player-to-Player Trading & Market** (37) | Rules 19, 20, `sink:market_fee`, `escrow:market` | Trade rules, fee rates | Guests excluded. Both sides commit atomically |
| **Economy Telemetry** (41) | Metric definitions and bands (F7, F8) | Aggregates for reading | Observations only (Rule 31) |
| **Commission Board** (42) | `escrow:commission` | Commission rules | Full Vision |
| **Server-Wide Events** (45), live-ops-designer | `faucet:event_reward`, reward value sizing | Event structure | Event schedule stays with live-ops |
| **Moderation & Reporting** (39) | Wallet `Locked` behaviour | Suspension state | No confiscation path is defined here (Open Question 8) |

## Formulas

Sign convention, wallet sums and the money supply identity are Accounts F3, reused without change. Amounts are whole Glints unless stated.

### F1. Wallet write check

The wallet_accept formula is defined as:

`wallet_accept(w, Δ) = state_ok(w) AND is_integer(Δ) AND 0 < |Δ| ≤ MAX_TX_AMOUNT AND (B + Δ ≥ BALANCE_FLOOR) AND (Δ ≤ 0 OR B + Δ ≤ WALLET_CAP)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| w | wallet ID | player wallet | `wallet` table | Wallet being changed |
| Δ | int64 (Glints) | ±`MAX_TX_AMOUNT` | caller, as the net of its legs on `w` | Signed change |
| B | int64 (Glints) | 0 to `WALLET_CAP` (higher only after the cap is lowered) | `cached_balance` | Balance before the write |
| BALANCE_FLOOR | int64 | 0 | this GDD (Accounts F3) | Lowest legal player balance |
| WALLET_CAP | int64 | 1,000,000–99,999,999 | config (default 9,999,999) | Highest balance a credit may reach |
| MAX_TX_AMOUNT | int64 | 100,000–10,000,000 | config (default 1,000,000) | Largest single movement |
| state_ok(w) | bool | true or false | wallet state table | The state allows this write |

**Output Range:** true (write proceeds) or false (whole transaction aborts with the first failing code in Rule 9).
**Example:** `B = 250`, buying a 300 lens: `Δ = −300`, `250 − 300 = −50 < 0` → `ERR_INSUFFICIENT_FUNDS`. `B = 9,999,950`, a 120 sale: `Δ = +120`, `10,000,070 > 9,999,999` → `ERR_WALLET_FULL`, photo stays unsold. `B = 12,000,000` after the cap was lowered, a 200 purchase: `Δ = −200` passes, because the cap applies only to credits.

### F2. Starting balance

The start_balance formula is defined as:

`start_balance(choice) = START_GRANT − kit_charge(choice)`, where `kit_charge(phone) = 0`, `kit_charge(camera) = KIT_CHARGE`, subject to `0 ≤ KIT_CHARGE ≤ START_GRANT < P_kit`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| choice | enum | `phone`, `camera` | Starting Choice | Which start was taken |
| START_GRANT | int (Glints) | 200–1,200 | config (default 600) | Grant to every account, once |
| KIT_CHARGE | int (Glints) | 0–`START_GRANT` | Starting Choice (placeholder 500) | Price of the kit at the start |
| P_kit | int (Glints) | > `START_GRANT` | budget table (1,200 + 300 = 1,500) | Shop value of the Hearth and the kit lens |

**Output Range:** 0 to `START_GRANT`. With defaults, 600 (phone) or 100 (camera).
**Example:** `start_balance(phone) = 600 − 0 = 600`; `start_balance(camera) = 600 − 500 = 100`. The constraint holds: `600 < 1,500`, so a phone start cannot buy the kit at once.

### F3. Start gap

The start_gap formula is defined as:

`start_gap = max(0, P_kit + start_balance(camera) − start_balance(phone)) / E(C)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| P_kit | int (Glints) | see F2 | budget table | Shop value of the kit |
| start_balance(·) | int (Glints) | see F2 | F2 | The two starting balances |
| E(C) | int (Glints per hour) | 300–500 | budget table | C-band earn rate |
| start_gap | float (hours) | 0–`START_GAP_MAX` target | calculated | Income a phone start needs to match the camera start's minute-zero position |

**Output Range:** ≥ 0 hours. Target at or below `START_GAP_MAX = 4` hours at every point of the band.
**Example:** `(1,500 + 100 − 600) = 1,000` Glints: 3.3 h at 300 per hour, 2.5 h at 400, 2.0 h at 500. A skilled phone player earning at the top of the band is 2 hours behind a camera start in assets, in exchange for easier early shooting. This number is the price of the choice and does not prove the two starts are equal (Open Question 5).

### F4. Target earn rate

The earn_rate formula is defined as:

`earn_rate(c) = S_H × V(c)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| c | tier ID | C, B, A in MVP | Gear Catalog F12 (`gear_ceiling`) | The player's gear ceiling |
| S_H | float (sales per active hour) | 6–14 | Photo Pricing, planning default 10 | Photos sold per active hour |
| V(c) | int (Glints) | C 30–50, B 50–80, A 80–120 | Photo Pricing, within this band | Mean payout after diminishing returns |
| earn_rate(c) | int (Glints per hour) | 300–1,200 at `S_H = 10` | calculated | Target income |

**Output Range:** the budget table bands: C 300–500, B 500–800, A 800–1,200.
**Example:** bottom of the range, C ceiling: `10 × 30 = 300`. Middle, B ceiling: `10 × 65 = 650`. Top, A ceiling: `10 × 120 = 1,200`. The measured form used by Telemetry is F8.

### F5. Time to afford

The hours_to_afford formula is defined as:

`hours_to_afford(P, B, c) = max(0, P − B) / earn_rate(c)`, and `sessions_to_afford = ceil(hours_to_afford / SESSION_H_PLAN)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| P | int (Glints) | 0–`MAX_TX_AMOUNT` | Gear Shop, or budget table envelope | Item price |
| B | int (Glints) | 0–`WALLET_CAP` | wallet | Current balance |
| c | tier ID | C, B, A | gear ceiling | Band that applies while saving |
| SESSION_H_PLAN | float (hours) | 0.25–1.5 | planning default 0.5 (**assumption**; no project target exists) | Planned session length |

**Output Range:** 0 hours upward. Pacing target: U1 within 4 sessions at the mid band; A ceiling within 20 hours even at the low band.
**Example:** camera start, `B = 100`, U1 `P = 700`, C ceiling at mid: `600 / 400 = 1.5` h → 3 sessions. At the low end `600 / 300 = 2.0` h → 4 sessions; at the high end `600 / 500 = 1.2` h → 3 sessions. Later steps use the B band, because a B ceiling arrives with U1, and the Hearth holds the loadout at B until U3 replaces it. Full path in the pacing table.

### F6. Catalogue buy-out (exhaustible sink capacity)

The buyout_hours formula is defined as:

`buyout_hours = T_path + (C_total − C_owned − C_path) / earn_rate(A)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| T_path | float (hours) | 9.2–14.8 for a camera start | F5 pacing table | Time to reach the A ceiling on the first-playable path |
| C_total | int (Glints) | 20,800 at planning envelopes | budget table | Value of all stocked models |
| C_owned | int (Glints) | 1,500 camera start, 0 phone start | budget table | Value of the starting kit |
| C_path | int (Glints) | 7,100 | budget table | Value of U1, U2, U3 |
| earn_rate(A) | int (Glints per hour) | 800–1,200 | budget table | Income once at the A ceiling |

**Output Range:** with planning envelopes, 19.4–30.1 hours (camera start), 21.4–33.4 hours (phone start, adding F3's gap).
**Example:** remaining after the path: `20,800 − 1,500 − 7,100 = 12,200`. Low band: `14.8 + 12,200/800 = 14.8 + 15.25 = 30.05` h. Mid: `11.35 + 12.2 = 23.55` h (48 sessions). High: `9.2 + 10.17 = 19.37` h. If the shop stocks only the three first-playable upgrades, capacity is 7,100 and it runs out at 9.2–14.8 hours. This is the upper bound on gear demand: most players will not want every model, so the real sink runs dry sooner. It also assumes the bands hold; diminishing returns may stretch it.

### F7. Sink ratio

The sink_ratio formula is defined as:

`sink_ratio(T) = Σ sink_inflow(T) / Σ faucet_outflow(T)`, excluding `faucet:start_grant`, `sink:start_kit`, `sink:account_closed`, and all `escrow:*` and `adjust:*` wallets

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| T | time window | 7 days default | Telemetry | Measurement window |
| sink_inflow(T) | int (Glints) | ≥ 0 | ledger aggregate | Money entering sink wallets in `T` |
| faucet_outflow(T) | int (Glints) | ≥ 0 | ledger aggregate | Money leaving faucet wallets in `T` |

**Output Range:** 0 upward; reported as "no data" when `faucet_outflow(T) = 0`. Above 1 means money is shrinking, below 1 means it is growing.
**Example:** in a week faucets pay 1,000,000 and sinks take 850,000: `sink_ratio = 0.85`, and the money supply `M` (Accounts F3) grew by 150,000. Bottom of the range: an all-saving week with 0 spent gives 0. Top: a new-gear launch with 1,500,000 spent gives 1.5, which is healthy only briefly.

### F8. Economy health metrics

The stockpile_hours formula is defined as:

`stockpile_hours(w) = B(w) / E(c(w))`, and the measured earn rate is `measured_earn_rate = Σ faucet credits to players (excluding start grant and compensation) / active_hours`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| B(w) | int (Glints) | 0–`WALLET_CAP` | wallet | Balance |
| c(w) | tier ID | C, B, A | gear ceiling of the current loadout | Band for this player |
| E(c) | int (Glints per hour) | 400, 650, 1,000 | budget table mids | Target income for that band |
| active_hours | float (hours) | ≥ 0 | Telemetry; default definition: time in session state `Synced` | Time actually played |

**Output Range:** `stockpile_hours` from 0 to about 25,000 hours (9,999,999 / 400). Measured earn rate from 0 upward, compared to the bands.
**Example:** `B = 2,600`, B ceiling: `2,600 / 650 = 4.0` hours of savings. An empty wallet gives 0. A player at the cap on a C ceiling gives 25,000, which is an alarm by itself.

**Health table.** Bands are placeholders until the first playtest provides real data. Each metric is sliced by gear ceiling, and by guest or registered. Any wallet in state `Closed` is excluded.

| Metric | Definition | Healthy band | Alarm | First response (a person decides) |
|---|---|---|---|---|
| Measured earn rate | F8, median by ceiling | Inside band | Outside band 7 days running | Review Photo Pricing |
| Top-earner rate | p99 of measured earn rate | ≤ 2.5× the band high | Above that | Check for an exploit, then a grind spot |
| `sink_ratio` | F7, all players | 0.70–1.05 once past launch | < 0.5 or > 1.3 for 14 days | Add or adjust sinks |
| `sink_ratio`, past buy-out | F7, players who own all stocked models | 0.70–1.05 (Rule 32) | Below 0.4 | Expected in MVP; blocks the Rule 32 gates |
| Money per active player | `M` (excluding closed wallets) / weekly active players | Rises slower than 10% per week after launch | Above 25% per week | Inflation check |
| Stockpile | `stockpile_hours`, median and p90 | Median ≤ 8 h, p90 ≤ 40 h | Median > 20 h | Nothing to buy: add sinks or content |
| Time to first upgrade | Hours and sessions from start to first `sink:gear_shop` entry, median | ≤ 2 h, ≤ 4 sessions | > 4 h | Raise early payouts |
| Time to A ceiling | Hours to first A-ceiling loadout, median | 9–15 h | < 6 h or > 25 h | Review prices and bands |
| Start balance | Ratio of phone to camera starts, and F3 measured | Neither below 25% of starts; gap ≤ 4 h | A start below 15% | Review `KIT_CHARGE` and early scoring |
| Stranded players | Active wallets below the cheapest stocked item for over 3 h of play | Under 2% | Above 5% | Early-income fix |
| Wealth concentration | Share of `M` held by the top 1% | Under 30% | Above 50% | Rich-get-richer review |
| Exhausted players | Share of active players past buy-out | Watch only | Above 25% | Content or sink priority |
| Adjustment volume | Σ `|adjust:*|` / Σ faucet outflow | Under 0.1% | Above 1% | Defect investigation |
| Reconciliation | Mismatches found by Accounts Rule 33 | 0 | Any | Incident |
| Wallet-full refusals | Count of `ERR_WALLET_FULL` | 0 | Any | Exploit check |

### F9. Projected surplus

The surplus formula is defined as:

`surplus(h) = earn_rate(c) × h × (1 − r)`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| h | float (hours) | ≥ 0 | scenario | Played hours past buy-out |
| earn_rate(c) | int (Glints per hour) | 800–1,200 | budget table, A band | Income |
| r | float | 0–1 | scenario | Share of income going to non-exhausted sinks |
| surplus(h) | int (Glints) | ≥ 0 | calculated | Added to the wallet |

**Output Range:** 0 to `WALLET_CAP`.
**Example, at `h = 100`:**

| `r` | Scenario | 800 per h | 1,000 per h | 1,200 per h |
|---|---|---|---|---|
| 0 | MVP past buy-out (no recurring sink) | 80,000 | 100,000 | 120,000 |
| 0.40 | Alpha recurring sinks at `RECURRING_SINK_MAX` | 48,000 | 60,000 | 72,000 |
| 0.85 | Alpha plus new exhaustible content at target | 12,000 | 15,000 | 18,000 |

The middle row is the honest gap: recurring sinks alone leave 48,000–72,000 unspent per 100 hours, about 2.3 to 3.5 times the value of the whole enabled catalogue (20,800). Closing it needs new high-tier content that no GDD yet commits to.

### F10. Time to cap

The hours_to_cap formula is defined as:

`hours_to_cap = (WALLET_CAP − B) / (earn_rate(c) × (1 − r))`, for `r < 1`

**Variables:**
| Variable | Type | Range | Source | Description |
|----------|------|-------|--------|-------------|
| WALLET_CAP | int (Glints) | see F1 | config | Cap |
| B | int (Glints) | 0–`WALLET_CAP` | wallet | Starting balance of the scenario |
| earn_rate(c), r | see F9 | see F9 | F9 | Income and sink share |

**Output Range:** 0 hours upward.
**Example:** `B = 0`. Fastest honest case, `E = 1,200`, `r = 0`: `9,999,999 / 1,200 ≈ 8,333` h. Mid, `E = 1,000`, `r = 0.40`: `≈ 16,667` h. Slowest in the table, `E = 800`, `r = 0.85`: `≈ 83,333` h. Honest players never meet the cap, which is its purpose.

## Edge Cases

**Spending and earning**

- **If a purchase costs exactly the balance**: it succeeds; balance becomes 0, which is legal.
- **If a purchase costs 1 Glint more than the balance**: `ERR_INSUFFICIENT_FUNDS`; nothing is written; the item stays in the shop.
- **If two devices spend the last Glints at once**: the database serialises them; the first commits; the second gets `ERR_INSUFFICIENT_FUNDS` (Accounts Edge Cases); no negative balance is ever written.
- **If a sale would pass `WALLET_CAP`**: `ERR_WALLET_FULL`; the photo stays unsold in the gallery; the message tells the player to spend before selling.
- **If a credit lands exactly on `WALLET_CAP`**: it succeeds.
- **If `WALLET_CAP` is lowered below a player's balance**: the balance is untouched; debits work; credits fail with `ERR_WALLET_FULL` until the balance is under the new cap.
- **If a system computes a fractional amount**: that is a defect in the caller; `apply` refuses it with `ERR_OUT_OF_RANGE`, nothing commits, and the event is logged. The wallet never rounds on the caller's behalf.
- **If an amount of 0 is sent** (a free item, a 0-value photo): `apply` is not called and no ledger entry exists; the owner completes its action without money legs. A call with 0 is refused with `ERR_OUT_OF_RANGE`.
- **If an amount exceeds `MAX_TX_AMOUNT`**: `ERR_OUT_OF_RANGE`; logged as an alarm because no honest price comes close.
- **If a client sends a price or a balance in a request**: it is ignored and logged (Network Rule 6); the server uses its own price.
- **If a player lacks money for any optional sink at 0 Glints**: they keep shooting and selling; no state, gear or access they already hold is lost (Rule 12).

**Retries and failures**

- **If a buy request is retried with the same `rid` inside the window**: the stored response is returned; money moves once.
- **If it is retried after the window**: the unique key makes the insert a no-op and the original response is rebuilt from existing rows (Accounts Rule 30).
- **If the same `rid` arrives with a different amount or item**: `ERR_IDEMPOTENCY_CONFLICT`; nothing moves.
- **If the connection drops after the click and before the response**: the client stays `Pending`, reconnects, retries with the same `rid`, and shows the true result. The balance never changes on a guess.
- **If the meta service is down**: `ERR_SERVICE_DEGRADED`; the display goes `Stale`; shooting continues where a live session allows, and selling waits.
- **If responses arrive out of order across two tabs**: the client keeps the highest `entry_id`; the older response never overwrites the newer balance.
- **If a transaction fails after the money check**: everything rolls back, including the ledger legs (Accounts Rule 26), so no refund is ever needed.
- **If a player spends on one device while another shows an old balance**: the second device's button may look affordable; the server refuses with `ERR_INSUFFICIENT_FUNDS`, and the refusal response carries the true balance, which the client shows.

**Starting choice and guests**

- **If a player closes the tab before choosing a start**: the wallet stays `Unfunded`, balance 0, and the choice is shown on return.
- **If a modified client sends a second start transaction with a new `rid`**: the one-per-wallet constraint on `faucet:start_grant` refuses it with `ERR_NOT_ALLOWED`; no second grant exists.
- **If a guest upgrades to a registered account**: wallet, balance and history stay as they are; no second grant (Accounts Rule 4).
- **If a guest tries to attach an identity already in use**: refused (Accounts Rule 5); the guest wallet stays with the guest; wallets are never merged.
- **If a guest expires holding Glints**: the balance is swept at purge under D8; the money is gone with the account.
- **If a guest attempts any player-to-player leg (Alpha)**: `ERR_NOT_ALLOWED`.
- **If one person repeatedly creates guests for the grant**: each grant is stranded in its own wallet, because guests cannot transfer; the cost is a little storage, removed after `GUEST_IDLE_D`.
- **If a person registers many accounts to feed one main account (Alpha)**: each costs an email, and trading is the outlet; Trading must carry the limit (Open Question 7).

**Account states**

- **If reconciliation freezes a wallet**: writes fail with `ERR_SCOPE_FROZEN`; reads show the ledger-derived balance with a "being checked" note; shooting continues; photos can be held unsold.
- **If a faucet owner must pay a `Frozen` or `Suspended` wallet** (for example a theme prize): the owner holds the payment and retries with the same `rid` once the wallet is `Active`; the wallet never queues money itself. If the wallet reaches `Closed`, the payment is void.
- **If a player requests deletion with a positive balance**: the wallet is `Locked` during grace; **Cancel deletion** restores it unchanged; at purge the balance is swept under D8; the deletion flow already says money will be removed (Accounts UI).
- **If deletion is requested while a money action is in flight**: the action either commits first or fails with `ERR_ACCOUNT_PENDING_DELETION`; the transaction order decides, and no partial state exists.
- **If a restore rolls back purchases or sales**: those ledger entries no longer exist; the client sees a higher `restore_epoch`, discards its copy and refetches (Accounts Rule 39). A photo sold after the snapshot is unsold again. Compensation, if any, uses `faucet:compensation` and is a manual, announced decision.
- **If a `restore_epoch` change lands while a money action is `Pending`**: the client refetches first, then shows the true outcome of that `rid`.

**Economy shape**

- **If a player buys out the stocked catalogue**: income continues and the balance grows; nothing breaks; the player counts as "exhausted" in F8; this is the known gap in Rule 32.
- **If Photo Pricing proposes payouts above the band**: this GDD's table must be changed first, with rationale, or the prices are out of contract.
- **If a new sink would leave a player unable to shoot**: it fails Rule 12 and may not ship.
- **If a sink would return a random item**: it fails Rule 6 and may not ship, whatever the currency.
- **If gear buy-back is ever enabled and a starter item is sold**: Rule 19 uses `KIT_CHARGE`, not shop value, so the start cannot be turned into profit.
- **If a sum over a system wallet nears int64 limits**: at 2^62 Glints this is not reachable in any modelled scenario; `faucet:*` wallets have no floor by design.

## Dependencies

**Upstream (this system depends on):**

| System / dependency | Hard / soft | Interface | Status |
|---|---|---|---|
| Accounts & Server Persistence | Hard | Ledger, F3, Rules 26–34, 44, 46, `wallet_owner`, reconciliation, effect keys | Designed. Lists this system as downstream |
| Network Transport & Server Authority | Hard | Authority table, Rules 6, 21, 27, 30, D15, error code list | Designed. Lists this system in Interactions |
| Gear Catalog & Specs | Soft (budget only) | Model and tier counts, Rule 26; Open Question 7 | Designed. Lists this GDD as owner of that question |
| Economy integrity ADR (research §7.9) | Hard before implementation | Database-level constraints | Not written |

**Downstream (systems that depend on this one):** per the systems index: Starting Choice (14), Photo Pricing & NPC Clients (16), Gear Shop (17), Shop, Sell & Inventory UI (21), Zone Access & Travel (22), Daily Themes & Player Judging (23), Gear Condition & Maintenance (31), Player-to-Player Trading & Market (37), Economy Telemetry (41), Commission Board (42). Also through the catalogue, though the index does not list them: Gallery (15, `sink:storage`), Gear Crafting (33, `sink:craft_fee`), First-Claim (34, `faucet:claim_participation`), Server-Wide Events (45, `faucet:event_reward`).

**Bidirectional note:** every downstream GDD, when authored, must list "depends on Currency & Wallet", name its catalogue kinds, and state its Rule 12 behaviour. All of them are Not Started. The existing Accounts rows already point here. The changes that existing documents need are listed in Open Question 2.

## Tuning Knobs

| Knob | Default | Safe range | Affects | Too low / too high |
|---|---|---|---|---|
| `START_GRANT` | 600 | 200–1,200, and below `P_kit` | First hours; phone cushion (F2) | Too low: a thin phone start, no choice in the first shop visit. Too high: reaches `P_kit`, and the camera choice becomes a trap |
| `START_BALANCE_CAMERA` | 100 (derived from `KIT_CHARGE`) | 0–300 | Camera start's first shop visit | 0: an empty wallet on the first screen. Too high: no cost to the choice |
| `START_GAP_MAX` | 4 h | 1–6 h | Target for F3 | Too low: choice has no cost. Too high: phone reads as a penalty |
| `BALANCE_FLOOR` | 0 | **Not a knob**; changing it reopens B4 | Negative-balance policy | — |
| `WALLET_CAP` | 9,999,999 | 1,000,000–99,999,999 | Exploit blast radius, UI width (F1, F10) | Too low: real players meet it. Too high: UI overflow and a larger exploit ceiling |
| `MAX_TX_AMOUNT` | 1,000,000 | 100,000–10,000,000 | Guard against bad prices | Too low: blocks late-game prices. Too high: guard catches nothing. Review when `enabled_cap` rises |
| Earn band C / B / A | 300–500 / 500–800 / 800–1,200 per h | ±50% before review of all envelopes | Pace of the whole game (F4) | Too low: grind. Too high: the catalogue runs out sooner |
| `S_H` (planning) | 10 per h | 6–14 | Converts bands to payouts (F4) | Planning value; replace with measured data |
| `SESSION_H_PLAN` | 0.5 h | 0.25–1.5 | Session counts (F5) | Assumption. Replace with measured data |
| `BUYBACK_MAX_PCT` | 50% (unused while D10 = no buy-back) | 0–70% | Arbitrage guard (Rule 19) | Too high: buy-and-resell cycles become cheap, weakening the shop as a sink |
| `RECURRING_SINK_MAX` | 40% of income | 25–50% | Ceiling on recurring sinks | Too low: a bigger surplus. Too high: feels like a tax, fights the cozy tone |
| `SINK_RATIO_TARGET` | 0.85 long run; 0.70–1.05 band | 0.6–1.1 | Long-run money supply growth (F7) | Too low: inflation. Too high: deflation, and players feel poorer each week |
| `WALLET_HISTORY_PAGE` | 50 entries | 20–200 | Wallet history read cost | Too low: the photo-to-lens link is lost. Too high: slow read |

Every money value above is a placeholder. Budget envelopes (Rule 28) are inputs owned here until Gear Shop's real prices replace them.

## Visual/Audio Requirements

Presentation is small, and the art bible owns the look.

- **Glint icon:** a small four-point sparkle in Golden Hour Amber, the art bible's colour for value, money, reward and a sale. It must not use aperture blades, which belong to tier badges, and must not use Lumen cyan, which the art bible forbids for money. SVG, suitable for `/asset-forge`.
- **Colour contrast:** amber numbers appear on Darkroom Ink. The art bible rules out amber text on Paper White, so on light panels the number is Ink, with the amber icon outlined in Ink.
- **Sound (Vertical Slice, Audio):** one soft sale cue (a warm tick, like a coin set on a wooden shelf) and one softer purchase cue. No casino sounds, no rising jackpot sweeps, no sound for a refused action beyond the standard UI cue. All audio needs a human listen.
- **No particle showers** for money. A sale's moment belongs to the photo.

## Game Feel

| Moment | Budget | Feel |
|---|---|---|
| Press Sell or Buy | Pending mark ≤ 100 ms (Network Rule 30) | The button responds at once; the money number does not move |
| Server confirms | p95 ≤ 1 s (Network Game Feel) | The number then counts to the new value in 300–500 ms; the count starts only after confirmation |
| Refusal | Same budget | The number stays put; a calm line says why; no shake, no red flash |
| Wallet history open | ≤ 1 s | A plain list, like a small ledger book |

The count-up is decoration on a true value. It always starts from a confirmed balance and ends on a confirmed balance, and with reduced motion enabled the number changes at once. A sale should feel like being paid for good work: warm, certain, quiet.

## UI Requirements

Screens belong to Shop, Sell & Inventory UI (21). All text is localisation keys; wording is draft.

- **Wallet chip:** icon plus balance, shown in the shop, sell, inventory and darkroom screens. **Never in the viewfinder or Viewfinder HUD** (Pillar 1: while shooting, the player looks at light, not money).
- **Number format:** whole numbers with locale digit grouping (`12,450`), no abbreviation, no decimals. Must fit seven digits plus grouping at every supported UI scale.
- **Pending:** the button shows "Selling…" or "Buying…"; the balance is unchanged; repeat presses do nothing while pending. No predicted balance or "after purchase" figure on the chip. A shop card may show the item's price and whether the last confirmed balance covers it, labelled as a hint; the server still decides.
- **Stale:** the chip shows the last confirmed balance with "Not up to date".
- **Frozen:** "Your balance is being checked. Your money is safe. Buying and selling are paused." Balance is shown with a small note.
- **Refusal copy:**
  - `ERR_INSUFFICIENT_FUNDS`: "Not enough Glints yet."
  - `ERR_WALLET_FULL`: "Your wallet is full. Spend some Glints before selling this photo. The photo is still yours."
  - `ERR_SCOPE_FROZEN`: the Frozen line above.
- **Wallet history (MVP, D12):** the last `WALLET_HISTORY_PAGE` entries, newest first: time, plain label, signed amount, resulting balance. Labels name the thing: "Sold a photo to a client" (with the subject's name once Photo Pricing supplies it), "Bought Kanro KR 50mm f/1.8", "Starting savings", "Hearth kit". Paging older entries is allowed. A deleted item keeps its label from the entry.
- **Starting Choice screen** (owned by Starting Choice): shows both resulting balances before the player commits. The transaction is final after commit.
- **Guests:** the wallet looks the same. The "Keep my progress" banner (Accounts UI) appears after the first sale.
- **Accessibility:** every state has text as well as colour; the chip has a screen-reader label such as "12,450 Glints"; the count-up respects reduced motion (AccessKit on web is **UNVERIFIED**, per Accounts).

**UX Flag — Currency & Wallet:** the wallet chip, pending button pattern and wallet history are shared components. Run `/ux-design` for them with the Shop, Sell & Inventory UI spec before writing UI epics.

## Cross-References

| Document | Section | Relationship |
|---|---|---|
| `design/gdd/accounts-server-persistence.md` | Rules 3, 4, 26–34, 44, 46; F3; record catalogue; D1, D6 | Storage rules reused here. Not redefined |
| `design/gdd/network-transport-server-authority.md` | Rule 6 and authority table; Rules 21, 27, 30; F9; Game Feel; D15 | Authority, idempotency, display rule |
| `design/gdd/gear-catalog-specs.md` | Rule 26 (MVP catalog); Open Question 7; D13 | Model counts; buy-out answered by F6 |
| `design/gdd/game-concept.md` | Starting choice; Selling photos; Balance; Risks; Open questions | Source of sinks, anti-pillars and the camera-cost question |
| `design/gdd/systems-index.md` | Row 11; Circular Dependencies; A12; A13; B2; B4 | Scope, budget table placement, sink placement |
| `design/art/art-bible.md` | Colour roles and contrast rules | Amber means money; Lumen cyan never does |
| `design/registry/entities.yaml` | constants, items | Candidates listed in Open Question 9; `guest_idle_days` and `deletion_grace_days` read |

## Acceptance Criteria

**Wallet rules**

1. [Logic] **GIVEN** a wallet with balance 500, **WHEN** a debit of 500 is applied, **THEN** it commits and the balance is 0. `test_debit_exact_balance_reaches_zero`
2. [Logic] **GIVEN** a wallet with balance 500, **WHEN** a debit of 501 is applied, **THEN** it returns `ERR_INSUFFICIENT_FUNDS` and no row is written. `test_debit_above_balance_rejected_no_rows`
3. [Logic] **GIVEN** a wallet at `WALLET_CAP − 100`, **WHEN** a credit of 100 is applied, **THEN** it commits and the balance equals `WALLET_CAP`. `test_credit_to_exact_cap_accepted`
4. [Logic] **GIVEN** a wallet at `WALLET_CAP − 100`, **WHEN** a credit of 101 is applied, **THEN** it returns `ERR_WALLET_FULL`, no partial credit is written, and the balance is unchanged. `test_credit_over_cap_refused_whole`
5. [Logic] **GIVEN** a balance above a lowered `WALLET_CAP`, **WHEN** a debit that leaves the balance above the cap is applied, **THEN** it commits. `test_debit_above_lowered_cap_allowed`
6. [Logic] **GIVEN** any wallet, **WHEN** an amount of 0, a non-integer, or an amount above `MAX_TX_AMOUNT` is applied, **THEN** it returns `ERR_OUT_OF_RANGE` and writes nothing. `test_invalid_amount_rejected_out_of_range`
7. [Logic] **GIVEN** a transaction failing two checks, **WHEN** applied, **THEN** the error is the earliest in Rule 9's order. `test_check_order_first_failure_decides`
8. [Logic] **GIVEN** a kind not in the catalogue, **WHEN** applied, **THEN** it returns `ERR_NOT_ALLOWED` and logs a defect. `test_unknown_kind_rejected_and_logged`
9. [Logic] **GIVEN** a sink wallet with balance 100, **WHEN** a leg would take it below 0, **THEN** the transaction aborts. `test_sink_wallet_floor_enforced`
10. [Logic] **GIVEN** a split of 100 Glints over 3 seats, **WHEN** computed, **THEN** the parts are whole numbers summing to 100 and the remainder goes to the lowest seat. `test_split_remainder_lowest_seat_sums_exact`

**Formulas**

11. [Logic] **GIVEN** defaults, **WHEN** `start_balance` is computed, **THEN** phone = 600 and camera = 100. `test_start_balance_defaults_phone_camera`
12. [Logic] **GIVEN** a config with `START_GRANT ≥ P_kit` or `KIT_CHARGE > START_GRANT`, **WHEN** data is validated, **THEN** validation fails. `test_start_config_invalid_fails_validation`
13. [Logic] **GIVEN** the bands, **WHEN** `start_gap` is computed at E(C) = 300, 400, 500, **THEN** the results are 3.33, 2.5 and 2.0 hours. `test_start_gap_band_values`
14. [Logic] **GIVEN** the planning envelopes, **WHEN** `buyout_hours` is computed for a camera start at low, mid and high bands, **THEN** the results are about 30.05, 23.55 and 19.37 hours. `test_buyout_hours_band_values`
15. [Logic] **GIVEN** faucet outflow 1,000,000 and sink inflow 850,000 plus excluded start-kit and escrow entries, **WHEN** `sink_ratio` is computed, **THEN** it is 0.85. `test_sink_ratio_excludes_start_and_escrow`
16. [Logic] **GIVEN** zero faucet outflow in the window, **WHEN** `sink_ratio` is computed, **THEN** it reports "no data" and does not divide by zero. `test_sink_ratio_zero_faucet_no_data`
17. [Logic] **GIVEN** `B = 2,600` on a B ceiling, **WHEN** `stockpile_hours` is computed, **THEN** it is 4.0. `test_stockpile_hours_band_b_example`
18. [Logic] **GIVEN** the budget table's model counts, **WHEN** compared with Gear Catalog data, **THEN** the counts are C 4, B 9, A 5. `test_budget_model_counts_match_catalog`

**Starting and accounts**

19. [Integration] **GIVEN** a new account, **WHEN** the camera start commits, **THEN** one transaction holds four legs summing to 0, the balance is 100, the kit item exists, and on any failure none of these exist.
20. [Integration] **GIVEN** an account that already has a start grant, **WHEN** a second start request arrives with a new `rid`, **THEN** it is refused and the balance is unchanged.
21. [Integration] **GIVEN** a guest with a balance and history, **WHEN** the guest attaches an email, **THEN** `wallet_id`, balance and ledger are unchanged and no second grant exists.
22. [Integration] **GIVEN** a guest wallet, **WHEN** any player-to-player leg is attempted (Alpha), **THEN** it returns `ERR_NOT_ALLOWED`.
23. [Integration] **GIVEN** a wallet frozen by reconciliation, **WHEN** a sale and a purchase are attempted, **THEN** both return `ERR_SCOPE_FROZEN`, reads still work, and the photo stays unsold.
24. [Integration] **GIVEN** an account in `PendingDeletion` with a balance, **WHEN** deletion is cancelled, **THEN** the balance is unchanged; **WHEN** it instead purges, **THEN** (if D8 = A) one sweep transaction takes the balance to 0 and the wallet is `Closed`.
25. [Integration] **GIVEN** the money supply identity, **WHEN** a scripted session of grants, sales, purchases and an adjustment runs, **THEN** `M = −Σ system balances` and every `tx_id` sums to 0 (Accounts F3).

**Idempotency and retries**

26. [Integration] **GIVEN** a purchase, **WHEN** the same `rid` is retried inside the window and again after it, **THEN** money and the item move exactly once and the same result returns both times.
27. [Integration] **GIVEN** two devices with balance 300, **WHEN** both buy a 200 item at once, **THEN** exactly one commits, the other gets `ERR_INSUFFICIENT_FUNDS`, and the balance is 100.
28. [Integration] **GIVEN** a sale in flight, **WHEN** the connection drops before the response and the client retries, **THEN** the sale happened once and the shown balance equals the server's.

**Display**

29. [UI] **GIVEN** a Sell press at 150 ms RTT, **WHEN** the response is pending, **THEN** a pending mark shows within 100 ms and the balance digits do not change until confirmation. Evidence: screenshot sequence.
30. [UI] **GIVEN** an `ERR_WALLET_FULL` refusal, **WHEN** shown, **THEN** the draft copy appears, the balance is unchanged and the photo is still listed as unsold. Evidence: screenshot.
31. [UI] **GIVEN** the Viewfinder HUD during shooting, **WHEN** a sale confirms on another device, **THEN** no balance is shown in the viewfinder. Evidence: screenshot.
32. [UI] **GIVEN** a seven-digit balance, **WHEN** shown at each supported UI scale, **THEN** it fits with grouping and without abbreviation. Evidence: screenshot.
33. [UI] **GIVEN** a meta outage, **WHEN** the shop is open, **THEN** the chip shows the last confirmed balance with "Not up to date". Evidence: screenshot.
34. [UI] **GIVEN** a wallet with a sale, a purchase and a start grant, **WHEN** the history opens, **THEN** each entry shows time, plain label, signed amount and resulting balance, newest first. Evidence: screenshot.

**Guardrails (review checks)**

35. [Logic] **GIVEN** the catalogue data, **WHEN** validated, **THEN** every kind has an owner, a class and a stated capacity, and no kind carries a real-money or random-outcome flag. `test_catalogue_kinds_complete_no_paid_random`

## Open Questions

| # | Question | Owner | Resolve by |
|---|---|---|---|
| 1 | **Sink gap.** F9 shows 48,000–72,000 unspent per 100 hours past buy-out even with recurring sinks at 40%. What content or sink provides the other 45%? | economy-designer + game-designer | Before the Rule 32 gates |
| 2 | **Changes needed in other documents (not edited here).** Accounts: add `ERR_WALLET_FULL` to its code list; add the `WALLET_CAP` constraint beside the floor; extend system wallet floors to cover `sink:*`, `escrow:*`, `adjust:*`; one-per-wallet constraint on `faucet:start_grant`; a purge sweep step if D8 = A (Rule 44 currently leaves the balance in place, so `M` would count money no one can spend). Network: add the same code; `balance_after` and `entry_id` in money responses. Systems index: row 11 status and link; mark A12, A13 and B4 as decided if the user agrees (A13 is still listed under "Assumptions to confirm"); add Gallery, Gear Crafting, First-Claim and Server-Wide Events as dependents. Gear Catalog: close Open Question 7 after approval. | producer (Change Propagation), with user approval | After this GDD is approved |
| 3 | **Possible effect-key collision.** `rid` is client-generated, and idempotency is scoped by account (Network F9), yet Accounts' permanent key `(wallet_id, rid, leg)` on a shared system wallet is not. Two accounts sending the same `rid` could collide on `sink:gear_shop`, and the second buyer would be treated as a retry. `item.acquired_rid` has the same shape. Suggested fix: the server derives the stored key from `account_id` and `rid`. | network-programmer + security-engineer (economy integrity ADR) | Before implementing the ledger |
| 4 | Does the entry camera start also keep the phone? If yes, the camera start's asset value rises and F3 grows. | game-designer (Starting Choice) | Starting Choice design |
| 5 | Is phone versus camera actually even? F3 prices the choice, but only playtests of early earn rates show whether phone assists offset the gap. Depends on B3. | economy-designer + playtest | First playable |
| 6 | Real data for `S_H`, session length and sale rates. All bands are placeholders until Photo Pricing and a first playtest exist. | economy-designer, Photo Pricing | Pricing design, then playtest |
| 7 | Multi-account feeding at Alpha: does Trading need an account-age or earned-money hold before a registered account can send money? | economy-designer + Trading GDD | Alpha |
| 8 | Can Moderation remove money gained by cheating? It would be an audited `adjust:correction`, but the policy is unset. | Moderation GDD + producer | Alpha |
| 9 | **Registry candidates**, once approved (not edited here): constants `balance_floor` (0), `wallet_cap` (9,999,999), `max_tx_amount` (1,000,000), `start_grant` (600), `start_balance_phone` (600), `start_balance_camera` (100); item `glint` (currency); formulas `wallet_accept`, `start_balance`, `sink_ratio`. | economy-designer, with user approval | After approval |
| 10 | Does B2 (player-to-player photo selling) add faucets or only transfers? As written it adds transfers only, and no new money. | Trading GDD | Alpha |
| 11 | Compensation budget after a restore: who decides, and is it capped? (Accounts Open Question 16.) | producer | Before Alpha |
| 12 | If a cosmetic store is added later (A13), confirm it stays outside this wallet. | creative-director + user | When the business model is decided |

## Decisions to confirm

> **DECIDED 2026-11-05 (user):** every item = the recommended option; D1: the currency is Glints.

> Monetization items, if ever added, need creative-director approval as well.

**D1. Currency name.**
- A. **Glints:** a small catch of light. Warm, fits shy spirits and light-chasing, collides with no photography term or GDD.
- B. **Silver:** from silver-halide film. Grounded and photographic, but suggests a metal ranking and reads flatter.
- C. **Prints:** the money is what you make. Charming, but a "print" is easily confused with a photo for sale.
- **Recommendation: A.** The name is display-only, so this is cheap to change. "Lumens" was rejected because Lumen cyan is the art bible's "lens sees something" colour and is forbidden for money, and "Exposures" because it collides with a core mechanic.

**D2. Unit.**
- A. One Glint is the smallest unit: whole numbers, no fractions anywhere.
- B. A hidden minor unit (like cents), shown as whole numbers.
- **Recommendation: A.** It matches the brief and Accounts' integer rule, and it removes every rounding question at display time. B adds precision the economy does not need, and hidden fractions would break "the money adds up".

**D3. Starting balances.**
- A. One grant of 600. Phone keeps 600; camera pays a 500 kit charge in the same transaction and keeps 100.
- B. Separate grants of 600 and 100, with no kit charge entry.
- C. Equal cash for both starts, with the camera free.
- **Recommendation: A.** It honours the concept's "costs starting money" in the player's own history, and Telemetry can see the choice. B gives the same balances with one fewer leg, but it hides the cost. C removes the choice, since the camera would simply be better. In all options `START_GRANT` must stay below the kit's shop value, or the phone can buy the camera at once and the camera start becomes a trap.

**D4. Does debt exist? (open question B4)**
- A. No debt. The starting camera is paid up front, `BALANCE_FLOOR = 0`.
- B. A separate "apprentice loan" record: wallet never negative, a share of each sale repays it.
- C. A negative wallet balance that sales refill.
- **Recommendation: A.** It fits the cozy tone, meets Accounts' floor, and needs no repayment or deleted-while-in-debt rules. B is fairer on paper, because camera starts would pay full value and F3's gap would shrink, but it adds a state and makes early sales feel docked. C breaks the floor constraint and the "cannot get stuck" promise.

**D5. Wallet cap and behaviour at the cap.**
- A. Hard safety cap of 9,999,999; a credit past it is refused whole and the photo stays unsold.
- B. No cap beyond the int64 limit.
- C. A low gameplay cap of 100,000 with upgrades, or clipped credits.
- **Recommendation: A.** Honest players never meet it (about 8,333 hours at best), it limits exploit damage and fixes the UI width. B leaves the exploit ceiling open. C turns a safety limit into a mechanic, and clipping would be a hidden sink.

**D6. Target earn rate (placeholder band).**
- A. C 300–500, B 500–800, A 800–1,200 Glints per active hour: A ceiling in 9–15 hours, catalogue buy-out in 19–30 hours.
- B. Slower by about half: A ceiling in about 18–30 hours. More runway from the same content, but slower early rewards.
- C. Faster by about half: A ceiling in about 6–10 hours. A better short playtest, but the sinks run out sooner.
- **Recommendation: A** as the working band, to be replaced by playtest data. Early upgrades land inside a few sessions, and adjacent bands touch so that skill can match gear.

**D7. Guest wallet limits.**
- A. Same wallet rules; guests have no player-to-player legs and no registered-only faucets.
- B. Also a lower guest cap (for example 5,000 Glints).
- C. Also a smaller guest grant.
- **Recommendation: A.** Blocking transfers already removes the abuse outlet, and Accounts D1 already sets those limits. B and C penalise exactly the visitors the game wants to convert, and B would make a guest's sale fail for a reason they cannot understand.

**D8. A purged account's balance.**
- A. Sweep the balance to `sink:account_closed` inside the purge transaction, as a new ledger entry.
- B. Leave it in the ownerless wallet and have Telemetry exclude closed wallets.
- **Recommendation: A.** The ledger stays append-only, and `M` keeps meaning "money players can spend". B needs no Accounts change, but `M` slowly overstates supply, especially with guest expiry. A requires a small change to Accounts Rule 44.

**D9. MVP sink gap.**
- A. Ship MVP with exhaustible sinks only, and treat recurring sinks as a hard gate before trading, `enabled_cap` above A, or public launch (Rule 32).
- B. Add one small recurring MVP sink, such as paid film or a darkroom fee.
- C. Pull Gear Condition & Maintenance forward into MVP.
- **Recommendation: A.** MVP has no trading, so surplus harms no other player, and the systems index accepts this for MVP. It does mean the economy is **not balanced past 19–30 hours** and this GDD says so. B adds a cost to the core loop with no matching fun. C adds scope before the loop is proven.

**D10. Gear buy-back in MVP.**
- A. None. Every purchase is final; `faucet:gear_buyback` stays reserved.
- B. Buy-back at up to 50% of the price paid, with starter gear priced from the kit charge.
- **Recommendation: A**, final call with the Gear Shop GDD. Three upgrades give little need to resell, and it removes the arbitrage path. B forgives a wrong purchase, but it adds a faucet and shrinks the already small sink.

**D11. Daily earn limit.**
- A. None. Diminishing returns in Photo Pricing limit income, and Telemetry alarms catch outliers.
- B. A hard daily cap on sales income.
- **Recommendation: A.** A hard cap punishes the best session and adds a timer the cozy tone does not want. B is a stronger bot defence, which can return if Telemetry shows the need.

**D12. Wallet history in MVP.**
- A. Show the last 50 entries to the player in MVP.
- B. Keep it internal until the Alpha data export.
- **Recommendation: A.** "The money adds up" is a promise, and the labelled history links photos to purchases (Pillar 2). The data already exists, so the cost is one simple list screen.
