# AI OS Kernel Specification
### Personal AI OS — Version 0.1 (MVP)

*This document specifies the Kernel: the runtime engine that everything else in the Personal AI OS depends on. It is derived from and subordinate to the Personal Constitution (why the system exists), the Engineering Constitution (how it is built), and the MVP Definition (what ships first). Where this spec is silent, those three documents govern.*

*This is a design document. It contains no code, no API signatures, and no folder structures — only the concepts, boundaries, and lifecycles the implementation must respect.*

---

## 1. What the Kernel Is

The Kernel is the smallest possible piece of software that must exist for the AI OS to exist at all. It is not intelligent. It is not domain-aware. It does not know what a résumé is, what a good commit message looks like, or how to debug code.

The Kernel is the thing that starts before intelligence begins and outlives every individual task. Its entire job is orchestration: bring the runtime up, figure out where the user is, restore what it remembers, connect the pieces that do the real thinking, and get out of the way.

Think of it the way a Linux kernel relates to the applications running on top of it. Linux doesn't know what a text editor is — it schedules processes, manages memory, and provides a stable set of contracts that editors, browsers, and compilers are all built on. The AI OS Kernel plays the same role for skills, memory, context, and models. **The measure of a good Kernel is how little it does, not how much.**

Per the MVP Definition, this is the literal MVP claim: *"the kernel knows nothing about résumés, coding, or research — it only manages the runtime."* Everything intelligent is a module that plugs into the Kernel, never a feature bolted onto it.

---

## 2. What It Owns

The Kernel owns **orchestration and contracts**, not domain logic. Specifically:

| Owned by the Kernel | What that means |
|---|---|
| **Runtime state** | Whether the OS is booting, ready, busy, or shutting down; which session is active; uptime. |
| **The module registry** | The list of engines and tools currently loaded, and the lifecycle contract each one must implement to register. |
| **The lifecycle contracts themselves** | The defined stages (init → ready → active → teardown) that every module is measured against — not what each module *does* inside those stages. |
| **The routing layer** | The map of "this kind of request goes to this module" — not the logic inside any destination. |
| **The event bus** | The single channel through which modules notify each other — not the meaning of any given event. |
| **Configuration loading** | Reading config and handing the relevant slice to each module — not interpreting domain-specific settings. |
| **The Model Adapter boundary** | The contract "ask a model something and get a response" — not any provider's specific API. |
| **Startup and shutdown sequencing** | The order in which modules come up and go down, and what "ready" means. |

If it can be described as "the rule for how things connect," it belongs to the Kernel. If it can be described as "what a thing actually does," it does not.

---

## 3. What It Never Owns

- **Domain knowledge.** Career advice, code review, writing assistance — none of this is Kernel logic. It lives in skills, which are consumers of the Kernel, not part of it.
- **Memory judgment.** The Kernel triggers memory lifecycle events (restore, commit, prune) but never decides *what* is worth remembering or *how long* it should live. That judgment belongs to the Memory Engine, per the Personal Constitution's memory-tier philosophy.
- **Context interpretation.** Detecting that a directory is a git repo, what branch it's on, what project it belongs to — this is the Context Engine's job. The Kernel only knows "a context object exists and needs to be attached to this session."
- **Provider-specific logic.** The Kernel never knows Claude's API shape any more than GPT's. That is entirely inside the Model Adapter.
- **Tool implementations.** The Kernel knows a tool was invoked and what came back. It does not know how the Git tool talks to Git.
- **Presentation.** Anything printed to the terminal — formatting, spinners, checkmarks — is the Interactive Terminal's responsibility, not the Kernel's.
- **Persistence internals.** Where and how memory or session data is physically stored is an implementation detail of the Memory and Session Engines, not the Kernel.

This boundary is the single most important rule in this specification. Every future design mistake in this system will trace back to violating it in one direction or the other.

---

## 4. Runtime Lifecycle

The runtime lifecycle is the outermost lifecycle — it wraps the entire life of the Kernel process, independent of any one session.

```
Boot
  ↓
Load configuration
  ↓
Initialize module registry
  ↓
Register core modules (Context, Memory, Session, Model Adapter, Tool Engine, Event Bus)
  ↓
Runtime Ready
  ↓
Accept session(s)
  ↓
Shutdown signal received
  ↓
Drain active session → flush modules → teardown
  ↓
Halt
```

In the MVP, one invocation of `aios` maps to one runtime lifecycle wrapping exactly one session — the process starts, runs a session, and exits. This is a deliberate simplification, not a permanent constraint: the runtime lifecycle is defined independently of the session lifecycle specifically so that a future long-running daemon (accepting multiple sessions, or running in the background) requires **zero changes to the Kernel** — only a change to how often "Boot" and "Halt" occur.

---

## 5. Session Lifecycle

A session is one continuous unit of interactive work, matching the MVP's defined flow:

```
Launch
  ↓
Load Context
  ↓
Load Memory
  ↓
Interactive Work
  ↓
Update Memory
  ↓
Save Session
  ↓
Exit
```

The Kernel's job at each stage:

- **Launch** — assign a session identity (session ID + workspace fingerprint), mark runtime state as "active session."
- **Load Context** — ask the registered Context Engine to detect the workspace and hand back a context object; attach it to the session.
- **Load Memory** — ask the registered Memory Engine to restore relevant memory for this context; attach it to the session.
- **Interactive Work** — enter the ready loop: accept input from the Interactive Terminal, route each request (to a skill, a tool, or a model), return the result.
- **Update Memory** — as work happens, forward relevant events to the Memory Engine so it can decide what to retain (the Kernel does not filter this itself).
- **Save Session** — commit session state (what was worked on, what changed) so it can be resumed later.
- **Exit** — release the context, flush the event bus, return runtime state to idle.

**Interrupted sessions:** if a session ends abnormally (crash, kill signal), the Kernel's only responsibility is to leave enough of a trail — via whatever the Session Engine last committed — that the next launch can detect an incomplete session and offer to resume it. The Kernel does not attempt to reconstruct lost state itself.

---

## 6. Context Lifecycle

Context is not the same as memory — memory is what the system remembers across time; context is what it perceives *right now*.

```
Detect → Resolve → Attach → Refresh → Release
```

- **Detect** — at session launch, the Kernel asks the Context Engine to inspect the current workspace.
- **Resolve** — the Context Engine turns raw signals (directory, git state, open files) into a single context object. The Kernel never inspects these signals itself.
- **Attach** — the Kernel binds that context object to the active session so every routed request can reference it.
- **Refresh** — if the workspace changes mid-session (branch switch, directory change), the Context Engine emits an event; the Kernel re-attaches an updated context object. The Kernel does not decide *when* a refresh is warranted — it only reacts to the event.
- **Release** — at session end, the context object is detached and discarded. It is not memory and does not persist on its own; anything from it worth keeping must already have passed through the Memory Engine.

---

## 7. Memory Lifecycle

Memory follows the tiered model defined in the Personal Constitution (permanent, long-lived, short-lived), but the Kernel is deliberately blind to those tiers — it only triggers the lifecycle; the Memory Engine makes every judgment call.

```
Restore → Observe → Update → Commit → Prune
```

- **Restore** — at session launch, the Kernel asks the Memory Engine to load whatever is relevant to the current context.
- **Observe** — throughout the session, the Kernel forwards relevant events (a decision was made, a task was completed) to the Memory Engine. The Kernel does not decide what counts as "relevant enough to remember" — it forwards everything and trusts the Memory Engine to filter.
- **Update** — the Memory Engine updates its internal state in response to observed events, on its own schedule, not the Kernel's.
- **Commit** — at session end (or at defined checkpoints), the Kernel tells the Memory Engine to persist its state.
- **Prune** — periodically (not necessarily every session), the Kernel triggers a prune cycle; the Memory Engine applies the tier expiration rules from the Personal Constitution. The Kernel enforces *that* pruning happens, never *what* gets pruned.

---

## 8. Tool Lifecycle

Every capability the system can act with — Git, filesystem, web, GitHub — is a tool, and every tool follows the same lifecycle regardless of what it does:

```
Register → Validate → Invoke → Return → Release
```

- **Register** — a tool declares itself to the Kernel at boot (or dynamically later): its name, what kind of input it expects, what kind of output it produces, and what class of side effect it has (read-only, mutating, external-network).
- **Validate** — before any invocation, the Kernel checks the request against the tool's declared contract. This is where the Engineering Constitution's security and error-handling rules are enforced centrally, once, rather than inside every tool.
- **Invoke** — the Kernel (or the router acting on its behalf) is the *only* thing that ever calls a tool. Skills never call tools directly. This single-chokepoint rule is what makes logging, permissions, and future safety controls possible without touching every skill.
- **Return** — the tool's result flows back through the Kernel to whatever requested it.
- **Release** — the Kernel does not hold onto tool results; whatever needs them (a skill, the Memory Engine) is responsible for keeping what it needs.

New tools "simply register themselves," exactly as the MVP specifies — adding a tool never requires modifying the Kernel.

---

## 9. Event Lifecycle

Events are how modules talk about things that happened without knowing who, if anyone, cares.

```
Emit → Publish → Dispatch → Handle → Discard
```

- **Emit** — any module can emit an event ("workspace changed," "tool executed," "memory updated," "error occurred").
- **Publish** — the event goes onto the Kernel's single event bus. There is exactly one bus — no module maintains its own private channel to another module.
- **Dispatch** — the Kernel delivers the event to whatever modules have subscribed to that event type. The Kernel does not interpret the event's content.
- **Handle** — each subscriber decides what, if anything, to do. A module that isn't listening simply never hears about it.
- **Discard** — unless a subscriber chooses to persist something as a result of handling the event, the event itself is ephemeral. The event bus is not a log; if an event needs a permanent record, that's a deliberate action by the Memory Engine, not a default.

---

## 10. How Modules Communicate

**Rule: modules never call each other directly.** All communication passes through the Kernel, via exactly two channels:

1. **Routed requests (synchronous)** — a module asks the Kernel for something it needs right now (a skill asking "what's the current context?"), and the Kernel forwards the request to the owning module and relays the response.
2. **Events (asynchronous)** — a module announces that something happened, without expecting or waiting for a response, and the Kernel dispatches it to anyone listening.

There is no shared global state. A module only ever sees what the Kernel explicitly hands it. This is the direct runtime expression of the Engineering Constitution's module design rule — *"modules communicate through contracts, not shared state"* — and it's what makes the Modular and Extensible principles from the Personal Constitution actually true at runtime, not just true on paper.

---

## 11. What Happens When I Type `aios`

Walking the whole stack end to end, in order:

1. The shell resolves `aios` and starts the Kernel process. **Runtime lifecycle** begins: Boot.
2. The Kernel loads configuration and initializes the module registry.
3. Core modules register: Context Engine, Memory Engine, Session Engine, Model Adapter, Tool Engine, Event Bus. Runtime state becomes **Ready**.
4. A new session is created. **Session lifecycle** begins: Launch.
5. The Kernel asks the Context Engine to detect the workspace — current directory, git repo, branch, project. This satisfies the terminal's `✓ Detecting workspace` line.
6. The Kernel asks the Memory Engine to restore whatever memory is relevant to that context — satisfying `✓ Loading previous session`.
7. The Kernel asks the Model Adapter to establish a connection to the configured provider — satisfying `✓ Connecting models`. If this fails, the session still proceeds (see Section 15 — graceful degradation), flagged as running without model access rather than refusing to start.
8. Context and memory are attached to the session. The Interactive Terminal prints the workspace summary and hands control to the prompt: `>`.
9. The Kernel is now idle-but-ready, waiting for input. Every line the user types becomes a routed request: the Kernel determines whether it's destined for a skill, a tool, or a direct model query, and forwards it — it does not process the request's meaning itself.
10. On exit (explicit quit, or terminal close), the **Session lifecycle** completes: memory is committed, the session is saved, context is released.
11. The process terminates. **Runtime lifecycle** completes: Halt.

Nothing in this sequence involves the Kernel understanding a single word of what the user actually asked for. It only understands *that a request exists and where it should go.*

---

## 12. How the Kernel Can Grow Without Becoming Monolithic

- **The default answer to "does this belong in the Kernel?" is no.** New capability is a new module registered through the existing contracts — never a new Kernel code path.
- **A hard tripwire:** if adding a feature requires editing Kernel code rather than adding or updating a module, that is a signal the module boundary is being violated. Stop and find the boundary that was skipped, rather than making the exception.
- **The Kernel's public surface — its lifecycle contracts, routing rules, and event schema — should change far more slowly than everything built on top of it.** After the MVP stabilizes, Kernel changes should be rare, deliberate, and heavily scrutinized, precisely because everything depends on them (this mirrors the Engineering Constitution's rule that breaking a public interface always requires a major version bump).
- **The Kernel and its modules version independently.** A new skill, a new tool, or a new memory backend should never force a Kernel release, and a Kernel patch should never force every skill to be revalidated.
- **Growth happens outward, not upward.** More skills, more tools, more model providers — all of these make the *system* bigger without making the *Kernel* bigger. That asymmetry is the entire point of a kernel/module split, and it's what lets the system scale from a 30-day MVP to the 10-year vision in the Personal Constitution without ever needing a rewrite of its core.

---

## 13. Which Responsibilities Belong Outside the Kernel

| Responsibility | Owner |
|---|---|
| Detecting workspace, git state, project identity | Context Engine |
| Deciding what/when/how long to remember | Memory Engine |
| Session persistence format and storage | Session Engine |
| Talking to Claude, GPT, Gemini, Ollama specifically | Model Adapter |
| Git, filesystem, web, GitHub, Supabase, n8n actions | Tool Engine (individual tools) |
| Career advice, code review, writing help, research synthesis | Skills |
| Printing, prompts, formatting, startup messages | Interactive Terminal |
| Authentication, permissions | Explicitly out of MVP scope; future module, not Kernel |
| Scheduling, automation, multi-agent coordination | Explicitly out of MVP scope; future module, not Kernel |

If it's on this list, it is never implemented inside the Kernel, no matter how small or tempting the addition seems.

---

## 14. Common Design Mistakes

- **Letting the Kernel absorb "just one" piece of domain logic.** This is how kernels rot — every exception feels small in isolation and catastrophic in aggregate.
- **Modules calling each other directly** instead of going through the Kernel's routing or event bus, creating invisible coupling that only surfaces when someone tries to remove or replace one of them.
- **Treating memory as conversation history.** The Personal Constitution is explicit that memory is not chat logs — collapsing the two turns the Memory Engine into a transcript store instead of a curated model of the user.
- **Coupling the Kernel to one AI provider's API shape**, even implicitly (e.g., assuming a specific response format), which quietly breaks the "zero Kernel changes to swap providers" guarantee.
- **Merging Context and Session into one concept.** Context is what's true right now; session is the continuous thread of work. Conflating them makes workspace switching and session resumption fight each other.
- **Confusing tools with skills.** A tool is a capability (`git commit`); a skill is judgment about when and why to use one or more tools. Building this distinction into the Kernel's execution model prevents skills from silently reimplementing tool logic.
- **Ignoring memory tiers and persisting everything indefinitely** — turning the Memory Engine into an archive instead of an intelligence, which the Personal Constitution explicitly rules out.
- **Building presentation logic (formatting, spinners, colors) into the Kernel or an Engine** instead of leaving it entirely to the Interactive Terminal, which makes future interfaces (a future GUI, voice, etc.) impossible without touching the runtime.
- **Over-building the event system prematurely** — adding priority queues, retries, or distributed messaging before there is any evidence the simple version is insufficient. This directly violates the Engineering Constitution's "no speculative generality" principle.

---

## 15. Design Principles

- **The Kernel is dumb on purpose.** Its value comes from what it reliably orchestrates, not from what it knows.
- **Everything pluggable is a module, with no exceptions carved out for convenience.**
- **Dependencies point one way: modules depend on Kernel contracts; the Kernel never depends on any module's internals.** This is what makes every "swap the provider / swap the storage / swap the tool" promise in the Engineering Constitution actually enforceable at runtime.
- **The Kernel's surface should be boring and stable.** Novelty belongs in modules; the Kernel is the last place that should ever feel experimental.
- **Session, context, and memory are lifecycles the Kernel orchestrates — never features it implements.**
- **Fail loud, degrade gracefully.** If the Model Adapter can't reach a provider, the session still starts — flagged, not fatal. If the Context Engine can't detect a workspace, the session still starts — with an empty context, not a crash. The Kernel keeps the system usable even when a module is unhealthy.
- **Kernel changes are rare and expensive on purpose.** Every other principle in this document exists to keep the Kernel small enough that this stays true for ten years, not just for the MVP.
- **The Kernel is never a black box.** Every routing decision, every lifecycle transition, every dispatched event should be inspectable — because the Personal Constitution's non-negotiable line is a system that hides why it's doing what it's doing, and the Kernel is where that trust is either built or broken first.

---

*AI OS Kernel Specification · Version 0.1 · Derived from the Personal Constitution, the Engineering Constitution, and the MVP Definition*
