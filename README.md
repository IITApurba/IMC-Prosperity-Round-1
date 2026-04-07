# IMC Prosperity Round 1 - Trading Strategy Repository

## Repository Purpose
This repository maintains the actively evolving algorithmic trading strategies for the IMC Prosperity challenge. The primary trading logic is located in [trader.py](./trader.py).

**AI Note / System Prompt:** 
When analyzing this repository for future algorithmic improvements, review the `Iteration Log` below. It tracks previous hypotheses, quantitative PnL scores, and post-simulation discoveries regarding the order book behavior (spreads, adverse selection). This context must strictly heavily influence future code generation to prevent reverting to failed techniques.

---

## The Iteration Log 📈

*This log is updated per simulation run to document findings systematically.*

### 🟢 Iteration: Strategy V2 (Current)
* **Strategy Goal:** Switch to passive market making and widen spreads to avoid adverse selection.
* **PnL Outcome:** ~1900
* **Asset Insights:**
  * **EMERALDS:** True value is locked at `10,000`. Instead of aggressive market orders, quoting limit orders slightly inside the typical simulation spread (Bid at `9996`, Ask at `10004`) successfully captures spread value with zero directional risk.
  * **TOMATOES:** The natural spread is very large (avg 13 ticks). By placing our quotes exactly `best_bid + 1` and `best_ask - 1` rather than narrowing around the exact midpoint, we buffer against strong directional movements and securely combat adverse selection.


### 🔴 Iteration: Strategy V1
* **Strategy Goal:** Simple naive algorithmic pegging (1-tick tightness for Tomatoes, strict crossing for Emeralds).
* **PnL Outcome:** ~450
* **Asset Insights:**
  * **EMERALDS:** Never placed a single trade. The logic relied on the market makers crossing `10,000` tightly, but the simulation system actually maintains a permanent massive spread (Bid: `9992`, Ask: `10008`) which shielded our aggressive logic from triggering. 
  * **TOMATOES:** Yielded positive PnL but suffered intense max drawdowns. The tight (`mid + 1` / `mid - 1`) quoting behavior deeply suffered adverse selection inside the massive 13-tick natural spread.

---

## Development Workflow
1. Execute simulation run on IMC Prosperity environment.
2. Download logs securely, provide raw `.log` CSV/JSON sets to Antigravity AI.
3. Determine localized findings, extract key PnL drivers vs limit orders behaviors.
4. Modify `trader.py` algorithmically and update this `README.md`'s Iteration Log.
5. Commit and push the snapshot into Git for historical preservation without hoarding raw log files locally.
