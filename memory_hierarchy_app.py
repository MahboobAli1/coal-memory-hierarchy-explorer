import math
import random

import altair as alt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Memory Hierarchy | COAL", page_icon="🧠", layout="wide")

# ----------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------
LEVELS = pd.DataFrame(
    [
        ["Registers", "~1 KB", 1024, 0.3, "Inside the CPU core", "Holds operands of the instruction being executed"],
        ["L1 Cache", "32 KB", 32 * 1024, 1, "SRAM, on-chip", "Recently used data/instructions (per core)"],
        ["L2 Cache", "256 KB", 256 * 1024, 4, "SRAM, on-chip", "Bigger, slower backup for L1"],
        ["L3 Cache", "8 MB", 8 * 1024**2, 15, "SRAM, shared on-chip", "Shared between all cores"],
        ["Main Memory (RAM)", "16 GB", 16 * 1024**3, 80, "DRAM, off-chip", "Programs and data currently running"],
        ["SSD", "512 GB", 512 * 1024**3, 100_000, "Flash, secondary storage", "Files, installed programs"],
        ["HDD", "1 TB", 1024**4, 10_000_000, "Magnetic disk", "Cheap bulk storage"],
    ],
    columns=["Level", "Typical Size", "Bytes", "Latency (ns)", "Technology", "Role"],
)


def human_time(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    if seconds < 3600:
        return f"{seconds / 60:.1f} minutes"
    if seconds < 86400:
        return f"{seconds / 3600:.1f} hours"
    if seconds < 86400 * 365:
        return f"{seconds / 86400:.1f} days"
    return f"{seconds / (86400 * 365):.1f} years"


# ----------------------------------------------------------------------------
# Cache simulator (set-associative, LRU; associativity 1 = direct-mapped)
# ----------------------------------------------------------------------------
ADDR_BITS = 16


def simulate(addresses, lines, block, assoc):
    sets = lines // assoc
    ob = int(math.log2(block))
    ib = int(math.log2(sets))
    tb = ADDR_BITS - ob - ib
    state = [[] for _ in range(sets)]  # each set: list of tags, LRU first, MRU last
    log = []
    for n, a in enumerate(addresses, 1):
        tag = a >> (ob + ib)
        idx = (a >> ob) & (sets - 1)
        off = a & (block - 1)
        ways = state[idx]
        evicted = "-"
        if tag in ways:
            result = "HIT"
            ways.remove(tag)
            ways.append(tag)
        else:
            result = "MISS"
            if len(ways) >= assoc:
                evicted = hex(ways.pop(0))
            ways.append(tag)
        bits = format(a, f"0{ADDR_BITS}b")
        log.append(
            {
                "#": n,
                "Address": a,
                "Binary (tag | index | offset)": f"{bits[:tb]} | {bits[tb:tb + ib]} | {bits[tb + ib:]}",
                "Tag": hex(tag),
                "Set": idx,
                "Offset": off,
                "Result": result,
                "Evicted tag": evicted,
            }
        )
    return log, state, (tb, ib, ob)


def preset_addresses(name, lines, block):
    if name == "Sequential scan":
        return [i * 4 for i in range(48)]
    if name == "Loop (temporal locality)":
        return [i * 4 for i in range(16)] * 3
    if name == "Large stride (poor spatial locality)":
        return [i * 64 for i in range(16)] * 2
    if name == "Conflict ping-pong (A, B, A, B...)":
        return [0, lines * block] * 8
    if name == "Random":
        rnd = random.Random(7)
        return [rnd.randrange(0, 1024, 4) for _ in range(40)]
    return []


# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.title("🧠 Memory Hierarchy – Registers, Cache, RAM & Secondary Storage")
st.caption("Interactive COAL learning resource: compare capacity, speed and access latency, then simulate a real cache.")

tabs = st.tabs(
    [
        "1️⃣ Concept",
        "2️⃣ Compare Levels",
        "3️⃣ Cache Simulator",
        "4️⃣ AMAT Calculator",
        "5️⃣ Worked Example",
        "6️⃣ Check Understanding",
        "7️⃣ References",
    ]
)

# ----------------------------------------------------------------------------
# 1. Concept
# ----------------------------------------------------------------------------
with tabs[0]:
    st.header("What is the Memory Hierarchy?")
    st.markdown(
        """
Programmers want memory that is **huge, very fast and cheap**. No single technology gives all three:

- **Fast** memory (SRAM) is **small and expensive**.
- **Large** memory (DRAM, SSD, HDD) is **cheap but slow**.

So computers combine several levels into a **hierarchy**. The CPU talks to the fastest level first; if the data is
not there, it goes one level down. Because programs show **locality of reference**, most accesses are served by the
small, fast levels, so the whole system *feels* as fast as the top and *as large as* the bottom.

**Two kinds of locality**
- **Temporal locality** – data used recently is likely to be used again soon (e.g. a loop counter).
- **Spatial locality** – data near the one just used is likely to be used soon (e.g. array elements). This is why a cache loads a whole **block**, not one byte.

**Key terms:** *hit* (data found in this level), *miss* (not found, must fetch from lower level), *hit ratio*, *miss penalty*, *block/line*.
"""
    )
    pyramid = LEVELS[["Level", "Typical Size", "Latency (ns)"]].copy()
    st.subheader("The pyramid: up = faster, smaller, costlier per byte")
    for i, row in pyramid.iterrows():
        pad = (len(pyramid) - i) * 5
        st.markdown(
            f"<div style='margin:3px auto;padding:6px;text-align:center;border-radius:6px;"
            f"background:rgba(80,130,255,{0.15 + 0.1 * (6 - i)});width:{40 + i * 9}%'>"
            f"<b>{row['Level']}</b> &nbsp;·&nbsp; {row['Typical Size']} &nbsp;·&nbsp; {row['Latency (ns)']:,} ns</div>",
            unsafe_allow_html=True,
        )

# ----------------------------------------------------------------------------
# 2. Compare levels
# ----------------------------------------------------------------------------
with tabs[1]:
    st.header("Compare capacity, speed and latency")
    st.dataframe(
        LEVELS[["Level", "Typical Size", "Latency (ns)", "Technology", "Role"]],
        use_container_width=True,
        hide_index=True,
    )
    c1, c2 = st.columns(2)
    base = alt.Chart(LEVELS)
    with c1:
        st.subheader("Access latency (log scale)")
        st.altair_chart(
            base.mark_bar().encode(
                x=alt.X("Level", sort=None),
                y=alt.Y("Latency (ns)", scale=alt.Scale(type="log", domain=[0.1, 1e8], clamp=True)),
                tooltip=["Level", "Latency (ns)"],
            ),
            use_container_width=True,
        )
    with c2:
        st.subheader("Capacity in bytes (log scale)")
        st.altair_chart(
            base.mark_bar(color="#e07b39").encode(
                x=alt.X("Level", sort=None),
                y=alt.Y("Bytes", scale=alt.Scale(type="log", domain=[100, 1e13], clamp=True)),
                tooltip=["Level", "Typical Size"],
            ),
            use_container_width=True,
        )
    st.caption("Values are typical for a modern desktop and vary by machine. Both charts use a log scale because the gaps are enormous.")

    st.subheader("⏱️ Feel the latency: human-time scale")
    pick = st.selectbox("Choose a level to access", LEVELS["Level"], index=4)
    ns_to_s = st.slider("Pretend 1 ns takes this many seconds", 1, 10, 1)
    row = LEVELS[LEVELS["Level"] == pick].iloc[0]
    reg = LEVELS.iloc[1]["Latency (ns)"]
    st.info(
        f"If an **L1 cache** access ({reg} ns) took **{ns_to_s} s**, then a **{pick}** access "
        f"({row['Latency (ns)']:,} ns) would take **{human_time(row['Latency (ns)'] / reg * ns_to_s)}**."
    )
    st.write(f"Speed ratio vs L1: **{row['Latency (ns)'] / reg:,.1f}× slower**." if row["Latency (ns)"] >= reg else "Faster than L1 cache.")

# ----------------------------------------------------------------------------
# 3. Cache simulator
# ----------------------------------------------------------------------------
with tabs[2]:
    st.header("Cache simulator (set-associative, LRU)")
    st.markdown(
        "Change the cache design and the memory access pattern, then watch hits and misses happen. "
        "Addresses are 16-bit byte addresses. Associativity **1 = direct-mapped**."
    )
    c1, c2, c3 = st.columns(3)
    lines = c1.select_slider("Number of cache lines", [4, 8, 16, 32], value=8)
    block = c2.select_slider("Block size (bytes)", [4, 8, 16, 32], value=16)
    assoc = c3.selectbox("Associativity (ways)", [1, 2, 4], index=0)
    if assoc > lines:
        assoc = lines

    patterns = [
        "Sequential scan",
        "Loop (temporal locality)",
        "Large stride (poor spatial locality)",
        "Conflict ping-pong (A, B, A, B...)",
        "Random",
        "Custom",
    ]
    pattern = st.selectbox("Memory access pattern", patterns)
    if pattern == "Custom":
        raw = st.text_input("Addresses (decimal or 0x hex, comma-separated)", "0, 4, 8, 12, 16, 0, 4, 128, 0")
        addrs = []
        try:
            addrs = [int(t, 0) % (1 << ADDR_BITS) for t in raw.replace(",", " ").split()]
        except ValueError:
            st.error("Invalid address list. Example: 0, 4, 0x10, 64")
    else:
        addrs = preset_addresses(pattern, lines, block)

    if addrs:
        step = st.slider("Step through accesses (show first N)", 1, len(addrs), len(addrs))
        log, state, (tb, ib, ob) = simulate(addrs[:step], lines, block, assoc)
        sets = lines // assoc

        hits = sum(1 for r in log if r["Result"] == "HIT")
        misses = len(log) - hits
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Accesses", len(log))
        m2.metric("Hits", hits)
        m3.metric("Misses", misses)
        m4.metric("Hit ratio", f"{hits / len(log) * 100:.1f}%")
        st.session_state["sim_miss_rate"] = misses / len(log)

        st.markdown(
            f"**Address split:** `{tb}` tag bits | `{ib}` index bits ({sets} sets) | `{ob}` offset bits "
            f"(block = {block} B). Cache capacity = {lines * block} bytes."
        )

        last = log[-1]
        (st.success if last["Result"] == "HIT" else st.error)(
            f"Access #{last['#']}: address {last['Address']} → set {last['Set']}, tag {last['Tag']} → **{last['Result']}**"
            + (f" (evicted tag {last['Evicted tag']})" if last["Evicted tag"] != "-" else "")
        )

        st.subheader("Cache contents after this access")
        rows = []
        for s in range(sets):
            r = {"Set": s}
            for w in range(assoc):
                if w < len(state[s]):
                    t = state[s][w]
                    start = ((t << ib) | s) << ob
                    r[f"Way {w}"] = f"tag {hex(t)} → bytes {start}–{start + block - 1}"
                else:
                    r[f"Way {w}"] = "— empty —"
            rows.append(r)
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.caption("Within a set, ways are listed from least-recently-used (Way 0) to most-recently-used (last way).")

        st.subheader("Access log")
        df = pd.DataFrame(log)
        st.dataframe(
            df.style.map(
                lambda v: "background-color:#d4edda;color:#155724" if v == "HIT"
                else ("background-color:#f8d7da;color:#721c24" if v == "MISS" else ""),
                subset=["Result"],
            ),
            use_container_width=True,
            hide_index=True,
        )
        st.markdown(
            "**Try this:** (1) pick *Conflict ping-pong* with associativity 1 → every access misses. "
            "Switch to 2 ways → hits appear. (2) pick *Sequential scan* and increase block size → "
            "fewer misses (spatial locality). (3) pick *Loop* → later passes hit (temporal locality)."
        )

# ----------------------------------------------------------------------------
# 4. AMAT
# ----------------------------------------------------------------------------
with tabs[3]:
    st.header("Average Memory Access Time (AMAT)")
    st.latex(r"AMAT = T_{L1} + m_{1} \times \big(T_{L2} + m_{2} \times T_{RAM}\big)")
    st.markdown("`m₁` = L1 miss rate, `m₂` = L2 local miss rate. Move the sliders to see how hit rate controls performance.")
    c1, c2 = st.columns(2)
    with c1:
        t1 = st.slider("L1 hit time (ns)", 0.5, 5.0, 1.0, 0.1)
        t2 = st.slider("L2 hit time (ns)", 2.0, 20.0, 4.0, 0.5)
        tr = st.slider("RAM access time (ns)", 40, 200, 80, 5)
    with c2:
        use_sim = st.checkbox(
            "Use miss rate from the Cache Simulator as L1 miss rate",
            value=False,
            disabled="sim_miss_rate" not in st.session_state,
        )
        if use_sim:
            m1 = st.session_state["sim_miss_rate"]
            st.write(f"L1 miss rate from simulator: **{m1 * 100:.1f}%**")
        else:
            m1 = st.slider("L1 miss rate (%)", 0.0, 50.0, 5.0, 0.5) / 100
        m2 = st.slider("L2 local miss rate (%)", 0.0, 100.0, 20.0, 1.0) / 100

    amat = t1 + m1 * (t2 + m2 * tr)
    no_cache = tr
    a, b, c = st.columns(3)
    a.metric("AMAT with caches", f"{amat:.2f} ns")
    b.metric("Without any cache (RAM only)", f"{no_cache} ns")
    c.metric("Speed-up", f"{no_cache / amat:.1f}×")
    st.latex(rf"AMAT = {t1} + {m1:.3f}\times({t2} + {m2:.2f}\times{tr}) = {amat:.2f}\ \text{{ns}}")

    sweep = pd.DataFrame(
        {"L1 miss rate (%)": [x for x in range(0, 51)], }
    )
    sweep["AMAT (ns)"] = [t1 + (x / 100) * (t2 + m2 * tr) for x in sweep["L1 miss rate (%)"]]
    st.subheader("How AMAT grows as the L1 miss rate rises")
    st.line_chart(sweep, x="L1 miss rate (%)", y="AMAT (ns)")

# ----------------------------------------------------------------------------
# 5. Worked example
# ----------------------------------------------------------------------------
with tabs[4]:
    st.header("Worked example: where does an address go?")
    st.markdown(
        "**Setup:** direct-mapped cache, 8 lines, 16-byte blocks, 16-bit addresses.  \n"
        "Offset = log₂16 = **4 bits**, Index = log₂8 = **3 bits**, Tag = 16 − 4 − 3 = **9 bits**."
    )
    ex = st.number_input("Enter a byte address (0–65535)", 0, 65535, 1234)
    ob_, ib_ = 4, 3
    bits = format(int(ex), "016b")
    tag, idx, off = int(ex) >> 7, (int(ex) >> 4) & 7, int(ex) & 15
    st.code(f"{bits[:9]} | {bits[9:12]} | {bits[12:]}\n  tag    index  offset", language="text")
    st.markdown(
        f"1. Block number = {int(ex)} ÷ 16 = **{int(ex) // 16}**\n"
        f"2. Cache line (index) = {int(ex) // 16} mod 8 = **{idx}**\n"
        f"3. Tag = {int(ex) // 16} ÷ 8 = **{tag}**\n"
        f"4. Byte within block (offset) = {int(ex)} mod 16 = **{off}**\n\n"
        f"The CPU checks line **{idx}**: if it is valid and its tag equals **{tag}** → *hit*; otherwise → *miss*, "
        f"the whole 16-byte block is fetched from RAM and the tag is replaced."
    )
    other = (int(ex) + 8 * 16 * 3) % 65536
    st.warning(
        f"Address **{other}** maps to the **same line {(other // 16) % 8}** but has a different tag "
        f"({other // 128}). If both are used alternately, they keep evicting each other: a *conflict miss*."
    )

# ----------------------------------------------------------------------------
# 6. Quiz
# ----------------------------------------------------------------------------
with tabs[5]:
    st.header("Check your understanding")
    QUIZ = [
        ("Which level of the hierarchy has the lowest latency?", ["Registers", "L2 cache", "RAM", "SSD"], 0,
         "Registers are inside the CPU and are accessed in a fraction of a nanosecond."),
        ("Why does a cache load a whole block instead of one byte?", ["To waste less memory", "To exploit spatial locality",
         "Because RAM cannot read single bytes", "To increase the tag size"], 1,
         "Nearby addresses are likely to be used soon, so one miss brings in neighbours for free."),
        ("A direct-mapped cache has 16 lines and 32-byte blocks. How many index bits does it use?", ["3", "4", "5", "9"], 1,
         "16 lines = 2^4, so 4 index bits (offset is 5 bits)."),
        ("L1 hit time 1 ns, L1 miss rate 10%, miss penalty 50 ns. What is AMAT?", ["5 ns", "6 ns", "51 ns", "1.5 ns"], 1,
         "AMAT = 1 + 0.10 × 50 = 6 ns."),
        ("Two addresses alternately map to the same line of a direct-mapped cache. This causes:", ["Compulsory misses only",
         "Capacity misses", "Conflict misses", "No misses"], 2,
         "They evict each other repeatedly: conflict misses. More associativity fixes it."),
    ]
    with st.form("quiz"):
        answers = []
        for i, (q, opts, ans, _) in enumerate(QUIZ):
            answers.append(st.radio(f"Q{i + 1}. {q}", opts, index=None, key=f"q{i}"))
        submitted = st.form_submit_button("Submit answers")
    if submitted:
        score = 0
        for i, (q, opts, ans, why) in enumerate(QUIZ):
            if answers[i] == opts[ans]:
                score += 1
                st.success(f"Q{i + 1}: Correct. {why}")
            else:
                st.error(f"Q{i + 1}: Correct answer is **{opts[ans]}**. {why}")
        st.subheader(f"Score: {score} / {len(QUIZ)}")
    st.markdown("**Exercise:** In the Cache Simulator, find a block size and associativity that gives a hit ratio above 80% on the *Sequential scan* pattern. Explain why it works.")

# ----------------------------------------------------------------------------
# 7. References
# ----------------------------------------------------------------------------
with tabs[6]:
    st.header("References")
    st.markdown(
        """
- D. Patterson & J. Hennessy, *Computer Organization and Design: The Hardware/Software Interface* – Ch. 5, Large and Fast: Exploiting Memory Hierarchy.
- W. Stallings, *Computer Organization and Architecture* – chapters on Memory Hierarchy and Cache Memory.
- J. Hennessy & D. Patterson, *Computer Architecture: A Quantitative Approach* – Appendix B (Cache basics, AMAT).
- R. Bryant & D. O'Hallaron, *Computer Systems: A Programmer's Perspective* – Ch. 6, The Memory Hierarchy.
- Course lecture slides for COAL (add your instructor's slide titles here).
- Latency/size figures are typical textbook-style approximations, not measurements of a specific machine.
"""
    )
    st.caption("Built with Python & Streamlit. AI tools were used for coding assistance; logic reviewed by the author.")
