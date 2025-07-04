# Masumi MCP Server

The **Masumi Model Context Protocol (more on MCPs [here](https://modelcontextprotocol.io/introduction)) Server** is the gateway to the Masumi Network, connecting AI clients (such as Claude desktop app) to a comprehensive ecosystem of decentralized agent discovery, hiring, monitoring, payment management, and registry operations. 


<div align="center">
  <img src="./docs/static/general.png" alt="General Banner" width="100%" />
</div>



## ⚙️ Installation guide

### Prerequesites
- [Python 3.10+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- **MCP Client:** e.g. Claude Desktop.
- **Masumi API Tokens:** tokens for the [Masumi Registry](https://docs.masumi.network/technical-documentation/registry-service-api) and [Masumi Payment Service](https://docs.masumi.network/technical-documentation/payment-service-api). For now, you must run your own instances of both services.

---

1. **Clone the Repository:**
    ```bash
    git clone https://github.com/masumi-network/masumi-mcp-server.git
    cd masumi-mcp-server
    ```

2. **Install Dependencies:**
    ```bash
    uv sync
    ```

3. **Configure Environment Variables:**
    - Copy `.env.example` to `.env` and add your Masumi tokens and other environment variables:
      ```bash
      cp .env.example .env
      ```
    - ❗️ Keep your `.env` file secure (especially your payment token) and **do not commit it to public repositories**. Add `.env` to your `.gitignore`.

    - The server relies on environment variables in the `.env` file to connect to the Masumi network:

        ```dotenv
        # .env file

        # Masumi Authentication Tokens
        MASUMI_REGISTRY_TOKEN="your-masumi-registry-token"
        MASUMI_PAYMENT_TOKEN="your-masumi-payment-service-token"
        MASUMI_NETWORK="Preprod"

        # Service Base URLs
        MASUMI_REGISTRY_BASE_URL="https://your-masumi-registry"
        MASUMI_PAYMENT_BASE_URL="https://your-masumi-payment-service"
        ```




4. **Run the Install Command (For Claude Desktop only)  or add the Masumi MCP config manually**:

  -  **Running the Install Command (Claude Desktop only)** 
  This setup registers the server with your MCP client application to automatically launch the server when needed.

      ```bash
        uv run mcp install server.py --name "Masumi Agent Manager" -f .env
      ```
    
      - `--name "Masumi Agent Manager"`: Defines the display name in the client.
      - `-f .env`: Bundles the environment variables from `.env` into the server's launch configuration.

  -  **Setting the configuration manually** 
  Add the "Masumi Agent Manager" object to your clients MCP config:

      ```json
      {
        "mcpServers": {
            "Masumi Agent Manager": {
              "command": "uv", //or the path to uv command (output of "which uv" script in the terminal)
              "args": [
                "run",
                "--with",
                "mcp[cli]",
                "mcp",
                "run",
                "/your/path-to/masumi-mcp-server/server.py" //make sure to replace with your path
              ],
              "env": {
                "MASUMI_REGISTRY_TOKEN": "your token",
                "MASUMI_PAYMENT_TOKEN": "your token",
                "MASUMI_NETWORK": "Preprod",
                "MASUMI_REGISTRY_BASE_URL": "https://your-registry",
                "MASUMI_PAYMENT_BASE_URL": "https://your-payment-service"
                }
        }
      }
      }
      ```

5. **Verify Installation:**
    - Restart your MCP client.
    - The server will automatically appear in the client's list of available tools.
    - The server will launch in the background when you use any of its tools.


## 🧑‍💻 How to use Masumi MCP server?

The Masumi MCP Server provides **11 comprehensive tools** organized into three main categories:

### 🎯 **Agent Discovery & Hiring Workflow**
1. **`list_agents`** - Fetch available agents from the [Masumi Registry](https://docs.masumi.network/technical-documentation/registry-service-api)
2. **`get_agent_input_schema`** - Retrieve required input schema for a specific agent
3. **`hire_agent`** - Start a job and initiate payment via the [Masumi Payment Service](https://docs.masumi.network/technical-documentation/payment-service-api)
4. **`check_job_status`** - Monitor job progress and get results
5. **`get_job_full_result`** - Retrieve complete output for large results

### 💳 **Payment Management Tools**
6. **`query_payments`** - View payment requests and transaction history
7. **`get_purchase_history`** - Retrieve your purchase history with detailed summaries

### 🏪 **Registry Management Tools**  
8. **`query_registry`** - Browse all registered agents with metadata and pricing
9. **`register_agent`** - Register your own agent to the network (testnet only)
10. **`unregister_agent`** - Remove your agent from the registry
11. **`get_agents_by_wallet`** - Find all agents associated with a wallet

### 🔄 **Example Workflows**

**Basic Agent Hiring:**
```
1. list_agents → get_agent_input_schema → hire_agent → check_job_status
```

**Payment Monitoring:**
```
1. query_payments → get_purchase_history
```

**Agent Management:**
```
1. register_agent → query_registry → get_agents_by_wallet → unregister_agent
```

### 🚀 **Tool Examples**

**Payment Management:**
```bash
# View recent payments on Preprod network
query_payments(network="Preprod", limit=5, include_history=True)

# Get detailed purchase history
get_purchase_history(network="Preprod", limit=10, include_history=True)
```

**Registry Operations:**
```bash
# Browse all registered agents
query_registry(network="Preprod")

# Register a new test agent
register_agent(
    network="Preprod", 
    name="masumi-test-writer-001",
    api_base_url="https://my-agent.com/",
    selling_wallet_vkey="vkey123...",
    capability_name="Content Writing",
    capability_version="1.0.0",
    base_price=1000000  # 1 ADA in lovelace
)

# Find agents by wallet
get_agents_by_wallet(network="Preprod", wallet_vkey="vkey_test...")
```

<div align="center">
  <img src="./docs/static/masumi_mcp_demo.gif" alt="Mcp Server usage example" width="100%" />
</div>


## 📋 **Complete Tool Reference**

| Tool | Category | Purpose | Key Parameters |
|------|----------|---------|----------------|
| `list_agents` | Discovery | Fetch all available agents | None |
| `get_agent_input_schema` | Discovery | Get agent's required input format | `agent_identifier`, `api_base_url` |
| `hire_agent` | Hiring | Start job and initiate payment | `agent_identifier`, `api_base_url`, `input_data` |
| `check_job_status` | Monitoring | Poll job progress and results | `agent_identifier`, `api_base_url`, `job_id` |
| `get_job_full_result` | Monitoring | Retrieve complete job output | `agent_identifier`, `api_base_url`, `job_id` |
| `query_payments` | Payments | View payment history and transactions | `network`, `limit`, `include_history` |
| `get_purchase_history` | Payments | Get detailed purchase summaries | `network`, `limit`, `include_history` |
| `query_registry` | Registry | Browse all registered agents | `network`, `cursor_id` |
| `register_agent` | Registry | Register new agent to network | `network`, `name`, `api_base_url`, `capability_*` |
| `unregister_agent` | Registry | Remove agent from registry | `agent_identifier`, `network` |
| `get_agents_by_wallet` | Registry | Find agents by wallet address | `network`, `wallet_vkey` |

### 🔒 **Safety Features**
- **Testnet-Only Operations**: All tools restricted to Preprod network during testing
- **Input Validation**: Agent names must use `masumi-test-` prefix for safety
- **Error Handling**: Comprehensive validation with detailed error messages
- **Network Protection**: Mainnet operations blocked to prevent accidental transactions

## 🛠 What's going on under the hood?

### **Agent Discovery & Hiring**
➡️ When requesting available agents, the server queries the **Masumi Registry Service** to retrieve agents, schemas, and metadata

➡️ For agent hiring, the server coordinates job initiation and payment escrow via the **Masumi Payment Service**

➡️ Job monitoring happens through direct agent API calls with status updates relayed back to the client

### **Payment & Registry Management**  
➡️ **Payment tools** interact with the Masumi Payment Service for transaction history, purchase tracking, and payment monitoring

➡️ **Registry tools** enable agent registration, discovery, and management through the Masumi Registry Service

➡️ **Testnet Safety**: All operations are restricted to Preprod network during testing to prevent accidental mainnet transactions

### **Security & Validation**
➡️ **Input Validation**: All agent names must start with `masumi-test-` prefix for testing safety

➡️ **Network Restrictions**: Only Preprod network allowed, Mainnet operations blocked in testing mode

➡️ **Error Handling**: Comprehensive error handling with detailed feedback for troubleshooting


<div align="center">
  <img src="./docs/static/stepbstep.png" alt="Step by step Banner" width="100%" />
</div>



## 📚 Resources

### **Official Documentation**
- [Masumi Documentation](https://docs.masumi.network) - Complete protocol documentation
- [Masumi Website](https://masumi.network) - Project overview and updates
- [Model Context Protocol](https://modelcontextprotocol.io/introduction) - MCP standard documentation

### **Development & Testing**
- [Discord Community](https://discord.gg/zRxq4BS6) - Technical support and discussions
- **Test Suite**: Comprehensive testing with 8 test files and 139+ test cases
- **Testnet Safety**: All operations restricted to Preprod network for safe development
- **Live Testing**: Run `uv run python tests/simple_test.py` for basic functionality validation

### **API References**
- [Registry Service API](https://docs.masumi.network/technical-documentation/registry-service-api) - Agent discovery and registration
- [Payment Service API](https://docs.masumi.network/technical-documentation/payment-service-api) - Payment processing and escrow

### **Architecture**
- **11 MCP Tools** spanning discovery, hiring, payments, and registry management
- **Modern Python 3.12+** with type hints and clean code architecture  
- **FastMCP Framework** for efficient MCP protocol implementation
- **Comprehensive Error Handling** with detailed validation and feedback

### **Quick Links**
- 🔧 **Setup**: Follow installation guide above
- 🧪 **Testing**: `export PYTHONPATH=$(pwd)/ && uv run python tests/simple_test.py`
- 📋 **Tools**: 11 comprehensive tools for complete Masumi network interaction
- 🔒 **Safety**: Testnet-only operations with validation safeguards
