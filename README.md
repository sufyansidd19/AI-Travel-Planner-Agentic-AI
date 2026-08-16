# ✈️ AI Travel Planner (Agentic AI)

An **LLM-powered Multi-Agent AI Travel Planner** built using **LangGraph**, **LangChain**, **Model Context Protocol (MCP)**, and **PostgreSQL**. The system features a centralized **Supervisor Agent** that dynamically routes user queries across specialized AI agents, integrates input guardrails, supports Human-in-the-Loop (HITL) feedback, and interacts with real-time APIs for comprehensive travel orchestration.

---

## 🚀 Key Features & Architectural Highlights

- 🧠 **Supervisor Agent Pattern:** Dynamic agent routing and execution management built on **LangGraph**.
- 🛠️ **Model Context Protocol (MCP):** Standardized tools and MCP client integration for robust tool-calling.
- 👨‍💻 **Human-in-the-Loop (HITL):** Breakpoints for human approval and feedback before finalizing travel itineraries.
- 🛡️ **Input Guardrails:** Validation layers preventing out-of-bounds, unsafe, or malformed queries from entering the agent graph.
- 🌤️ **Real-Time Weather Data:** Weather forecasts integrated via **OpenWeather API**.
- ✈️ **Flight Search Integration:** Real-time flight tracking and pricing via **AviationStack API**.
- 🔎 **Live Web Intelligence:** Deep web retrieval using **Tavily Search API**.
- 💾 **Long-Term Memory & State Management:** Persistent multi-turn conversation and state checkpointing via **PostgreSQL**.
- 💰 **Budget & Itinerary Optimization:** Multi-agent collaboration balancing accommodation, weather, flights, and activities.

---

## 🛠️ Tech Stack

- **Language:** Python
- **Orchestration:** LangGraph, LangChain
- **LLM Engine:** Groq LLM
- **Protocol & Integration:** Model Context Protocol (MCP)
- **Database / Memory:** PostgreSQL
- **APIs:** OpenWeather API, AviationStack API, Tavily Search API
- **Frontend UI:** Streamlit

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/sufyansidd19/AI-Travel-Planner-Agentic-AI.git
cd AI-Travel-Planner-Agentic-AI
```

---

## 2. Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 API Keys Setup

Create a **`.env`** file in the root directory and configure the environment variables:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
POSTGRES_DB_URI=postgresql://user:password@localhost:5432/travel_planner
```

---

# 📌 Obtaining API Keys

| Service | Setup Link | Description |
| :--- | :--- | :--- |
| **Groq API** | [consolegroq.com](https://console.groq.com/keys) | Ultra-fast LLM inference engine |
| **Tavily Search** | [app.tavily.com](https://app.tavily.com/) | Real-time web search for agents |
| **AviationStack** | [aviationstack.com](https://aviationstack.com/) | Live flight status and routes |
| **OpenWeather** | [home.openweathermap.org](https://home.openweathermap.org/users/sign_up) | Real-time weather and forecasts |

---

# ▶️ Running the Application

### Launch Streamlit Frontend

```bash
streamlit run frontend.py
```

### Run Agent Workflows Directly

```bash
python agent.py
```

---

# 📸 Application Interface

### Main User Interface
![Main UI](images/AI-Travel4.jpg)

### Agent Orchestration & Response
![Agent Response](images/AI-Travel5.jpg)

### Human-in-the-Loop (HITL) Workflow
![Human Feedback Interface](images/AI-Travel6.jpg)

---

# 🤝 Contributing

Contributions are welcome! Follow these steps to contribute:

1. Fork the repository.
2. Create your feature branch:
   ```bash
   git checkout -b feature/agent-enhancement
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add custom supervisor routing node"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/agent-enhancement
   ```
5. Open a **Pull Request**.

---

# 📄 License

This project is licensed under the **MIT License**.

---

## 👨‍💻 Author

**Sufyan Siddiqui**  
*Machine Learning Engineer & Agentic AI Specialist*

If you found this project helpful, please consider giving it a ⭐ on [GitHub](https://github.com/sufyansidd19/AI-Travel-Planner-Agentic-AI)!

