# 🧠 Memory Hierarchy Explorer

An interactive Streamlit web app that teaches the **Memory Hierarchy** (registers, cache, RAM and secondary storage) by letting you experiment with a real cache simulator instead of just reading about it.

| | |
|---|---|
| **Course** | Computer Organization & Assembly Language (COAL) |
| **Instructor** | Bilal Ahmed |
| **Semester** | 5 |
| **University** | Aror University, Sukkur |
| **Topic** | Memory Hierarchy: capacity, speed and access latency |

🔗 **Live app:** `https://<your-app-name>.streamlit.app`

---

## 🎯 Purpose

Programmers want memory that is large, fast and cheap, but no single technology provides all three. This app shows how computers combine several memory levels and why caching works, using hands-on demonstrations.

## ✨ Features

| Tab | What you can do |
|---|---|
| **Concept** | Learn the hierarchy, locality of reference (temporal and spatial), hits and misses |
| **Compare Levels** | See size, latency and technology of registers, L1/L2/L3, RAM, SSD and HDD on log-scale charts; use the "human-time" latency slider |
| **Cache Simulator** | Set cache lines, block size and associativity (direct-mapped to 4-way, LRU); pick or type an access pattern; step through each hit or miss with tag/index/offset breakdown and live cache contents |
| **AMAT Calculator** | Compute Average Memory Access Time for a two-level cache and see the speed-up over RAM only |
| **Worked Example** | Enter any address and see how it maps to a cache line, including a conflict-miss demo |
| **Check Understanding** | 5-question quiz with explanations, plus an exercise |
| **References** | Textbooks and sources used |

## 🧮 Core Logic

For a cache with `B`-byte blocks and `S` sets, each address is split as:

```
| tag | index (log2 S bits) | offset (log2 B bits) |
```

- A **hit** occurs when the tag is found in the set selected by the index.
- On a **miss** the block is fetched and, if the set is full, the least-recently-used way is evicted.
- `AMAT = T_L1 + m1 × (T_L2 + m2 × T_RAM)`

## 🚀 Run Locally

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
streamlit run memory_hierarchy_app.py
```

## ☁️ Deploy on Streamlit Community Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **Create app**.
3. Select the repo, branch `main`, and main file `memory_hierarchy_app.py`.
4. Click **Deploy**.

## 📁 Structure

```
├── memory_hierarchy_app.py   # Streamlit application
├── requirements.txt          # Dependencies
└── README.md
```

## 📚 References

- D. Patterson & J. Hennessy, *Computer Organization and Design: The Hardware/Software Interface*, Ch. 5
- W. Stallings, *Computer Organization and Architecture*, Memory Hierarchy and Cache chapters
- J. Hennessy & D. Patterson, *Computer Architecture: A Quantitative Approach*, Appendix B
- R. Bryant & D. O'Hallaron, *Computer Systems: A Programmer's Perspective*, Ch. 6
- COAL (CSC-324) lecture slides, Bilal Ahmed

> Latency and size values are typical textbook approximations, not measurements of a specific machine.

## 👤 Author

**Mahboob Ali**, BS Artificial Intelligence, Aror University Sukkur
Group members: 

AI tools were used for coding assistance. The code, simulation logic and COAL concepts were reviewed and understood by the author.
