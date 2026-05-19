🏏 IPL Roster Optimizer - Project Summary
What It Is
A full-stack AI-powered web application that helps IPL teams optimize their player rosters, identify undervalued talent, and make data-driven decisions about trades and contracts.

<<<<<<< HEAD
---

The Problem
IPL teams have ₹100 crore salary caps and need to select the best 25-player squad from hundreds of contracted players. Manual analysis is time-consuming and prone to bias. Teams struggle to identify which players provide the best value for money.

---

The Solution
IPL Roster Optimizer uses machine learning to predict player performance and mathematical optimization to build the perfect squad that maximizes team performance within budget constraints.

---

Key Features:
=======
The Problem
IPL teams have ₹100 crore salary caps and need to select the best 25-player squad from hundreds of contracted players. Manual analysis is time-consuming and prone to bias. Teams struggle to identify which players provide the best value for money.

The Solution
IPL Roster Optimizer uses machine learning to predict player performance and mathematical optimization to build the perfect squad that maximizes team performance within budget constraints.

Key Features
>>>>>>> 9461aff7f67b84974c801d6f4e4891221d94b0a6

Smart Roster Building - Upload player data, set budget, get AI-optimized 25-player squad
Value Analysis - Identify undervalued gems and overpaid players
Trade Simulator - Compare players, see trade impact on performance and salary
Contract Intelligence - Know which players to extend and which to release

<<<<<<< HEAD
---

How It Works
Upload Player Data (182 players with stats)
↓
AI Predicts Performance (Machine Learning)
↓
Calculates Value Index (Performance ÷ Salary)
↓
Optimizes Squad (Mathematical Algorithm)
↓
Visual Dashboard (Charts, Tables, Insights)

---

=======

How It Works
Upload Player Data (182 players with stats)
           ↓
AI Predicts Performance (Machine Learning)
           ↓
Calculates Value Index (Performance ÷ Salary)
           ↓
Optimizes Squad (Mathematical Algorithm)
           ↓
Visual Dashboard (Charts, Tables, Insights)

>>>>>>> 9461aff7f67b84974c801d6f4e4891221d94b0a6
Tech Stack
Frontend: React + Tailwind CSS + Recharts
Backend: Python FastAPI + Scikit-learn + PuLP
Deployment: Netlify (Frontend) + Render (Backend)
Algorithm: Linear Regression (ML) + MILP Optimization

<<<<<<< HEAD
---

Real Results:
=======
Real Results
>>>>>>> 9461aff7f67b84974c801d6f4e4891221d94b0a6

Players Analyzed: 182
Optimal Squad: 21 players selected
Budget Used: ₹5 crores (only 5% of ₹100 crore cap!)
Performance Score: 183.13
Top Value Player: Rajat Patidar (1.4956 value index)

<<<<<<< HEAD
---
=======
>>>>>>> 9461aff7f67b84974c801d6f4e4891221d94b0a6

Value Index System
Performance ÷ Salary = Value Index

<<<<<<< HEAD
> 0.5 → Elite (Must Keep)
> 0.3-0.5 → Good (Monitor)
> 0.1-0.3 → Fair (Squad Filler)
> < 0.1 → Poor (Trade Away)

---

Use Cases:
=======
> 0.5  → Elite (Must Keep)
0.3-0.5 → Good (Monitor)
0.1-0.3 → Fair (Squad Filler)
< 0.1  → Poor (Trade Away)

Use Cases

>>>>>>> 9461aff7f67b84974c801d6f4e4891221d94b0a6
Team Managers: Optimize rosters under salary cap
Analysts: Identify trading opportunities
Scouts: Find undervalued talent
Owners: Make smart contract decisions

<<<<<<< HEAD
---
=======
>>>>>>> 9461aff7f67b84974c801d6f4e4891221d94b0a6

Example Insight
Bad Deal: Rahul Chahar - ₹525L salary, 0.03 performance → Value 0.0001 ❌
Great Deal: Rajat Patidar - ₹20L salary, 31.41 performance → Value 1.4956 ✅
Smart Trade: Swap Chahar for Patidar → Save ₹505L + Gain 31.38 performance!

Technical Highlights
✅ Full-stack web application
✅ AI/ML predictive modeling
✅ Mathematical optimization (MILP)
✅ RESTful API with 20+ endpoints
✅ Interactive data visualizations
✅ Cloud-deployed and production-ready
