# 🏏 IPL Roster Optimizer

![IPL Roster Optimizer](https://img.shields.io/badge/Status-Active-brightgreen) ![Tech Stack](https://img.shields.io/badge/Stack-React%20%7C%20FastAPI-blue) ![License](https://img.shields.io/badge/License-MIT-purple)

## 📋 Project Summary
A full-stack, AI-powered web application designed to help IPL franchises optimize their player rosters. It identifies undervalued talent and enables data-driven decisions regarding trades and contracts using machine learning and mathematical optimization.

---

## 🎯 The Problem
IPL teams operate under a strict ₹100 crore salary cap and must select the best possible 25-player squad from hundreds of contracted athletes. Manual analysis of these options is incredibly time-consuming and often prone to human bias, making it difficult for teams to identify which players provide the best value for money.

## 💡 The Solution
The IPL Roster Optimizer utilizes machine learning algorithms to predict future player performance. It then applies mathematical optimization models to build the perfect squad, maximizing total team performance while strictly adhering to budget constraints.

---

## ✨ Key Features
- **Smart Roster Building:** Upload player data, set your franchise budget, and receive an AI-optimized squad.
- **Value Analysis:** Quickly identify undervalued "hidden gems" and flag overpaid players taking up valuable cap space.
- **Trade Simulator:** Compare players head-to-head to see the direct impact of a trade on overall team performance and salary cap flexibility.
- **Contract Intelligence:** Make informed decisions on which players to extend and which to release into the auction pool.

---

## ⚙️ How It Works

1. **Upload Data** ➡️ Input data for 182+ players with historical stats.
2. **AI Prediction** ➡️ Machine learning models predict future performance metrics.
3. **Calculate Value** ➡️ Determines the Value Index (Performance ÷ Salary).
4. **Squad Optimization** ➡️ Mathematical algorithms solve for the optimal combination of players under the cap.
5. **Dashboard Visualization** ➡️ Review results via interactive charts, tables, and insights.

---

## 💻 Tech Stack

### Frontend
- **Framework:** React
- **Styling:** Tailwind CSS
- **Visualization:** Recharts
- **Hosting:** Netlify

### Backend
- **Framework:** Python FastAPI
- **Machine Learning:** Scikit-learn (Linear Regression)
- **Optimization:** PuLP (Mixed-Integer Linear Programming - MILP)
- **Hosting:** Render

---

## 📊 The Value Index System
Our proprietary metric determines a player's worth by dividing their predicted performance by their salary cost: `Performance ÷ Salary = Value Index`.

| Value Index | Category | Action |
| :--- | :--- | :--- |
| **> 0.5** | Elite | Must Keep |
| **0.3 - 0.5** | Good | Monitor |
| **0.1 - 0.3** | Fair | Squad Filler |
| **< 0.1** | Poor | Trade Away |

### Example Insight
* ❌ **Bad Deal:** Rahul Chahar - ₹525L salary, 0.03 performance → Value **0.0001**
* ✅ **Great Deal:** Rajat Patidar - ₹20L salary, 31.41 performance → Value **1.4956**
* 🧠 **Smart Trade:** Swap Chahar for Patidar → *Save ₹505L + Gain 31.38 performance points!*

---

## 📈 Real Results (Sample Run)

* **Players Analyzed:** 182
* **Optimal Squad Size:** 21 players selected
* **Budget Used:** ₹5 crores *(Only 5% of the ₹100 crore cap utilized!)*
* **Total Performance Score:** 183.13
* **Top Value Player:** Rajat Patidar (1.4956 Value Index)

---

## 👥 Use Cases

* **Team Managers:** Optimize starting rosters while remaining compliant with the salary cap.
* **Analysts:** Identify lucrative trading opportunities before the deadline.
* **Scouts:** Uncover undervalued talent hidden in the data.
* **Owners:** Make financially sound contract extension and release decisions.

---

## 🚀 Technical Highlights
- [x] Full-stack web application architecture.
- [x] AI/ML predictive modeling integration.
- [x] Mathematical optimization (MILP) solving complex constraints.
- [x] RESTful API featuring 20+ robust endpoints.
- [x] Interactive, client-side data visualizations.
- [x] Fully cloud-deployed and production-ready.

---
*Built with data, designed for championships.* 🏆