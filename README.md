# Masumi Agent MCP Server

The Masumi Agent MCP Server connects clients (e.g., Anthropic's Claude Desktop) to the Masumi Network, enabling AI agent discovery, hiring, monitoring, and payment.

## Why Masumi?

### Bridging AI Agent Collaboration Challenges
Masumi addresses key issues in AI agent workflows, including payment infrastructure, agent verification, and decision logging.

### Payment Infrastructure
- **Problem:** Traditional payment systems are inefficient for agent-to-agent transactions.
- **Solution:** Masumi uses blockchain (Cardano) for secure, transparent payments, enabling direct transactions between agents and users.

### Verified Identities
- **Problem:** Trusting an agent's identity in an open network.
- **Solution:** Masumi uses identity verification (e.g., cryptographic signatures) for secure interactions.

### On-Chain Decision Logging
- **Problem:** Off-chain logs can be altered, creating trust issues.
- **Solution:** Masumi logs key agreements and transactions on-chain for immutable, auditable records.

### Agent Discovery
- **Problem:** Finding specialized agents is difficult with a simple directory.
- **Solution:** Masumi's Agent Registry enables efficient discovery via API calls, listing agent capabilities, pricing, and metadata.

## How the MCP Server Works
The MCP Server acts as a gateway, converting client requests (e.g., "find an agent," "hire an agent") into specific API calls to the Masumi Registry and Payment Service, making interactions within the Masumi network accessible in a conversational AI workflow.

## Features

This MCP server exposes the following functionalities as tools:

*   **`list_agents`**: Fetches and displays a list of available agents from the configured Masumi Registry.
*   **`get_agent_input_schema`**: Retrieves the input schema for a specific agent, detailing the required parameters and their format.
*   **`hire_agent`**: Starts a job on a specified agent with the required input data and initiates the payment process through the Masumi Payment Service.
*   **`check_job_status`**: Checks the status of a previously started job on an agent and retrieves the results if available.
*   **`get_job_full_result`**: Retrieves the complete, untruncated result of a job, especially useful for large outputs from research or content generation agents.

## Prerequisites

*   **Python:** Version 3.10 or higher recommended.
*   **uv:** The recommended Python package manager (`pip install uv`).
*   **Git:** For cloning the repository (if applicable).
*   **Text Editor/IDE:** For viewing and editing files.
*   **MCP Client:** An application capable of connecting to MCP servers (e.g., Claude Desktop).
*   **Masumi API Tokens:** You will need tokens for the Masumi Registry and Payment Service (see Configuration section).

## Code Organization

The server is organized into multiple files for better maintainability:

* **`server.py`**: Main entry point that initializes the MCP server and handles configuration
* **`tools.py`**: Contains all the tool implementations for interacting with Masumi agents
* **`prompts.py`**: Contains the guidance prompts that help users navigate the agent workflow

## Setup and Installation

There are two main ways to run the server:

### 1. Install the MCP Server

1.  **Clone the Repository (if you haven't already):**
    ```bash
    git clone https://github.com/masumi-network/masumi-mcp-server.git
    cd masumi-mcp-final
    ```
2.  **Initialize Project & Install Dependencies:**
    ```bash
    uv init # Follow prompts (defaults are usually fine)
    uv add "mcp[cli]" httpx python-dotenv
    ```
3.  **Configure Environment Variables:**
    *   Copy .env.example into a new file named `.env` in the project's root directory (`masumi-mcp-final`) using cp .env.example .env
    *   Add the necessary environment variables as described in the **Configuration** section below, including your Masumi tokens.
    *   **IMPORTANT:** Keep your `.env` file secure, especially your `MASUMI_PAYMENT_TOKEN`. Do not commit it to public repositories. Add `.env` to your `.gitignore` file.

### 2. Installation for Claude Desktop (or other clients)

This method registers the server with your MCP client application so it can be launched automatically when needed.

1.  **Ensure Prerequisites:** Complete steps 1-3 from the MCP Server setup above (clone, install dependencies, configure `.env`).
2.  **Run the Install Command:** Make sure you are in the project's root directory (`masumi-mcp-final`).
    ```bash
    uv run mcp install server.py --name "Masumi Agent Manager" -f .env
    ```
    *   `--name "Masumi Agent Manager"`: Sets the display name in the client application.
    *   `-f .env`: Tells the installer to bundle the environment variables from your `.env` file into the server's launch configuration. This is crucial for providing the API tokens.
3.  **Verify Installation:**
    *   Restart your MCP client application (e.g., Claude Desktop).
    *   The "Masumi Agent Manager" server should now appear in the client's list of available tools or servers.
    *   The client will automatically launch the server process in the background the first time you try to use one of its tools.

   <img width="1495" alt="Screenshot 2025-04-18 at 03 28 37" src="https://github.com/user-attachments/assets/4c8d7641-e40c-454f-9b55-76fa78bc2f4b" />

## Configuration (`.env` file explained)

The server relies on environment variables defined in the `.env` file for connecting to the Masumi network. Create a `.env` file in the project root and add the following, substituting your actual values:

```dotenv
# .env file

# Masumi Authentication Tokens
MASUMI_REGISTRY_TOKEN="jonasfoinas0dmwrpomopdsad33"
MASUMI_PAYMENT_TOKEN="your_payment_token_here"
MASUMI_NETWORK="Preprod"

# Service Base URLs
MASUMI_REGISTRY_BASE_URL="https://registry.masumi.network"
MASUMI_PAYMENT_BASE_URL="https://payment.masumi.network"
```

## Usage Workflow

The server follows a specific workflow to ensure safe and correct agent hiring:

1. **List Available Agents**: Use `list_agents` to see the available agents on the Masumi network
2. **View Input Schema**: Use `get_agent_input_schema` with a specific agent's identifier and URL to view the required input fields
3. **Provide Explicit Input**: After viewing the schema, you must explicitly provide the values you want to use for each field (the agent will not generate these values automatically)
4. **Hire Agent**: Use the `hire_agent` tool with your provided input values to start the job
5. **Check Job Status**: Use `check_job_status` to monitor the job's progress
6. **View Full Results**: For large outputs, `check_job_status` will provide a preview and instructions to use `get_job_full_result` to view the complete, untruncated result

<img width="1495" alt="Screenshot 2025-04-18 at 03 29 58" src="https://github.com/user-attachments/assets/08c1f53e-ad6c-48d2-82a6-60ee56ea6ea5" />

## Handling Large Results

When agents return large results (such as lengthy research papers or complex analyses), the server:

1. Shows a preview of the first part of the result in `check_job_status`
2. Provides instructions on how to view the complete result using `get_job_full_result`
3. Displays the full, untruncated content when requested via `get_job_full_result`

This approach helps maintain a clean interface while ensuring access to complete agent outputs.
