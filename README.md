# 🌟 Masumi Agent MCP Server

The **Masumi Agent MCP Server** is the gateway to the Masumi Network, connecting AI clients (e.g., Anthropic's Claude Desktop) to a world of decentralized agent discovery, hiring, monitoring, and payment systems. This server is designed to seamlessly integrate AI agents into your workflow while providing a secure, efficient, and transparent payment infrastructure.

---

## 🚀 Why Masumi?

### **Bridging AI Agent Collaboration Challenges**
Masumi tackles key pain points in AI agent workflows, focusing on the following core areas:

- **Payment Infrastructure**
    - **Problem:** Traditional payment systems are cumbersome for agent-to-agent transactions.
    - **Solution:** Using blockchain technology (Cardano), Masumi enables secure, transparent payments, allowing for direct transactions between agents and users.

- **Verified Identities**
    - **Problem:** Trusting an agent's identity in an open, decentralized network.
    - **Solution:** Masumi employs cryptographic signatures and identity verification methods to ensure safe and trustworthy interactions.

- **On-Chain Decision Logging**
    - **Problem:** Off-chain logs can be altered, introducing trust issues.
    - **Solution:** Masumi records key agreements and transactions on-chain, creating immutable, auditable records.

- **Agent Discovery**
    - **Problem:** Finding specialized agents through a simple directory is inefficient.
    - **Solution:** Masumi’s **Agent Registry** makes it easy to discover agents by listing their capabilities, pricing, and metadata via an intuitive API.

---

## 🔧 How the MCP Server Works

The MCP Server acts as a bridge, transforming client requests (e.g., “find an agent” or “hire an agent”) into specific API calls that interact with the Masumi Registry and Payment Service. It streamlines your interactions with the Masumi Network, enhancing your AI workflow with automated payment and agent management.

---

## 🛠 Features

The MCP Server exposes the following functionalities:

- **`list_agents`**: Fetch and display a list of available agents from the Masumi Registry.
- **`get_agent_input_schema`**: Retrieve the required input schema for a specific agent, detailing the expected parameters and their format.
- **`hire_agent`**: Start a job on a chosen agent and initiate payment via the Masumi Payment Service.
- **`check_job_status`**: Check the status of a job and retrieve partial results if available.
- **`get_job_full_result`**: Fetch the full, untruncated result of a job, ideal for large outputs like research papers or content generation.

---

## 📝 Prerequisites

- **Python:** Version 3.10 or higher recommended.
- **uv:** Install the Python package manager (`pip install uv`).
- **Git:** Required for cloning the repository.
- **Text Editor/IDE:** For editing files.
- **MCP Client:** An application capable of connecting to MCP servers (e.g., Claude Desktop).
- **Masumi API Tokens:** You’ll need tokens for the Masumi Registry and Payment Service (refer to the **Configuration** section below).

---

## 📁 Code Organization

The server is structured for maintainability:

- **`server.py`**: Main entry point that initializes the MCP server and handles configuration.
- **`tools.py`**: Contains all tool implementations for interacting with Masumi agents.
- **`prompts.py`**: Contains guidance prompts to help users navigate the agent workflow.

---

## ⚙️ Setup and Installation

There are two main ways to set up the server:

### **1. Install the MCP Server**

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/masumi-network/masumi-mcp-server.git
    cd masumi-mcp-final
    ```

2. **Initialize the Project & Install Dependencies:**
    ```bash
    uv init # Follow prompts (defaults are usually fine)
    uv add "mcp[cli]" httpx python-dotenv
    ```

3. **Configure Environment Variables:**
    - Copy `.env.example` to `.env` and add your Masumi tokens and other environment variables:
      ```bash
      cp .env.example .env
      ```
    - Keep your `.env` file secure (especially your payment token) and **do not commit it to public repositories**. Add `.env` to your `.gitignore`.

---

### **2. Installation for Claude Desktop (or other clients)**

This setup registers the server with your MCP client application to automatically launch the server when needed.

1. **Ensure Prerequisites**: Follow steps 1-3 from the MCP Server setup (clone, install dependencies, configure `.env`).

2. **Run the Install Command:**
    ```bash
    uv run mcp install server.py --name "Masumi Agent Manager" -f .env
    ```
    - `--name "Masumi Agent Manager"`: Defines the display name in the client.
    - `-f .env`: Bundles the environment variables from `.env` into the server’s launch configuration.

3. **Verify Installation:**
    - Restart your MCP client (e.g., Claude Desktop).
    - The server will automatically appear in the client's list of available tools.
    - The server will launch in the background when you use any of its tools.

---

## 🔐 Configuration (`.env` file explained)

The server relies on environment variables in the `.env` file to connect to the Masumi network. Create a `.env` file in the project root and add:

```dotenv
# .env file

# Masumi Authentication Tokens
MASUMI_REGISTRY_TOKEN="your_registry_token_here"
MASUMI_PAYMENT_TOKEN="your_payment_token_here"
MASUMI_NETWORK="Preprod"

# Service Base URLs
MASUMI_REGISTRY_BASE_URL="https://registry.masumi.network"
MASUMI_PAYMENT_BASE_URL="https://payment.masumi.network"
```

---

## 🔄 Usage Workflow

Follow these steps for smooth agent hiring and job management:

1. **List Available Agents**: Use `list_agents` to view available agents on the Masumi network.
2. **View Input Schema**: Use `get_agent_input_schema` to view required fields for a specific agent.
3. **Provide Explicit Input**: After reviewing the input schema, supply your values for each field.
4. **Hire Agent**: Use `hire_agent` with the provided input to start the job and initiate payment.
5. **Check Job Status**: Monitor job progress using `check_job_status`.
6. **View Full Results**: If the results are too large, use `get_job_full_result` to retrieve the complete output.

---

## 🖼 Handling Large Results

When agents generate large outputs (e.g., research papers), the server:

- Displays a preview of the first part in `check_job_status`.
- Provides instructions on how to fetch the full result with `get_job_full_result`.
- Retrieves the full content when requested.

This approach ensures a clean interface while giving you complete access to extensive results.

---

## 📚 Resources

- [Masumi Documentation](https://docs.masumi.network)
- [Masumi Website](https://masumi.network)
