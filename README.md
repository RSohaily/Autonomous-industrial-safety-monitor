#  Overview
This is an Autonomous Visual Inspection System built to automate safety auditing and inventory mapping in industrial warehouse environments. The system identifies mechanical components and classifies environmental hazards into risk-based categories (Safe, Caution, Danger).
2. Technical Stack
 * Vision Core: Vision Transformer (GPT-5.2/Gemini 3 Flash) for semantic image analysis.
 * Logic: Python-based risk stratification engine.
 * Frontend: React.js featuring a historical audit log and "drill-down" analysis capabilities.
3. Key Features
 * Risk Stratification: Automatically categorizes detected threats into Low, Medium, or High Danger levels based on contextual proximity to machinery or walkways.
 * Historical Audit Logging: Implements a database-driven "Recent Analyses" system that archives every scan for long-term safety trend analysis.
 * Actionable Insights: Beyond detection, the system provides immediate safety protocols (e.g., "Deploy Spill Kit" or "Clear Fire Exit").
4. System Architecture
 * Image Upload: Frontend sends high-resolution industrial photos to the backend.
 * Analysis: Python logic processes the vision data to detect objects and safety breaches.
 * Persistence: Results are serialized into a JSON ledger for the history sidebar.
 * Reporting: The UI renders risk gauges and detailed reports for the facility manager.
How to use these for your CV:
Instead of saying you used a tool, use these descriptions:
 * "Developed a Multi-Agent System for energy trading with a dynamic pricing engine."
 * "Engineered an Autonomous Visual Inspection System with a three-tier risk stratification logic."
