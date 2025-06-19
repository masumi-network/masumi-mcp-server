from typing import Optional

# --- MCP Prompts (User Guidance) ---

def prompt_list_agents() -> str:
    """Provides guidance on how to list available Masumi agents."""
    return (
        "To see available Masumi agents, use the `list_agents` tool. "
        "Note the `agentIdentifier` and `apiBaseUrl` for desired agents, needed for other tools."
    )

def prompt_get_agent_input_schema(agent_identifier: Optional[str] = None) -> str:
    """Provides guidance on how to retrieve the input schema for a Masumi agent."""
    base_message = (
        "After using `list_agents`, use `get_agent_input_schema` to see required inputs. "
        "Provide `agent_identifier` and `api_base_url`.\n\n"
        "I'll show you the required input schema. You'll need to provide the specific input values "
        "based on this schema before proceeding to hire the agent.\n\n"
        "Example: `get_agent_input_schema(agent_identifier='ID', api_base_url='URL')`"
    )
    if agent_identifier:
        return (
             f"To see required inputs for agent `{agent_identifier}`, use `get_agent_input_schema`. "
             f"Also provide its `api_base_url`.\n\n"
             f"After viewing the schema, you'll need to explicitly provide the input values you want to use.\n\n"
             f"Example: `get_agent_input_schema(agent_identifier='{agent_identifier}', api_base_url='URL')`"
         )
    else:
         return base_message

def prompt_hire_agent(agent_identifier: Optional[str] = None) -> str:
    """Provides guidance on how to hire a Masumi agent (start a job and payment)."""
    general_guidance = (
        "To hire an agent, use the `hire_agent` tool. Provide:\n"
        "1. `agent_identifier` (from `list_agents`).\n"
        "2. `api_base_url` (from `list_agents`).\n"
        "3. `input_data`: A dictionary with inputs matching the agent's schema.\n\n"
        "IMPORTANT: You must explicitly provide the input values you want to use. "
        "After viewing the input schema with `get_agent_input_schema`, tell me what specific values "
        "you want to provide for each required field.\n\n"
        "Workflow: \n"
        "1. `list_agents` to see available agents\n"
        "2. `get_agent_input_schema` to see required input fields\n"
        "3. Tell me what values to use for each required field\n"
        "4. `hire_agent` with your provided values\n\n"
        'Example: `hire_agent(agent_identifier=\'ID\', api_base_url=\'URL\', input_data={"text": "Research topic..."})`'
    )
    if agent_identifier:
        return (
            f"To hire agent `{agent_identifier}`:\n"
            f"1. First check the required inputs with `get_agent_input_schema`\n"
            f"2. After seeing the schema, tell me exactly what values you want to use for each required field\n"
            f"3. I'll then use `hire_agent` with your specific inputs\n\n"
            f"IMPORTANT: I won't proceed with hiring until you explicitly provide the input values. "
            f"Please review the schema and tell me what specific values to use.\n\n"
            f'Example: `hire_agent(agent_identifier=\'{agent_identifier}\', api_base_url=\'URL\', input_data={{"param": "your-specific-value"}})`'
        )
    else:
        return general_guidance

def prompt_check_job_status(job_id: Optional[str] = None) -> str:
    """Provides guidance on how to check the status of a Masumi job."""
    general_guidance = (
        "To check job status, use `check_job_status`. Provide:\n"
        "1. `agent_identifier`.\n"
        "2. `api_base_url`.\n"
        "3. `job_id` (from `hire_agent`).\n\n"
        "Example: `check_job_status(agent_identifier='ID', api_base_url='URL', job_id='JOB_ID')`"
    )
    if job_id:
         return (
             f"To check status for job `{job_id}`, use `check_job_status`. "
             f"Provide `agent_identifier` and `api_base_url` too.\n\n"
             f"Example: `check_job_status(agent_identifier='ID', api_base_url='URL', job_id='{job_id}')`"
         )
    else:
         return general_guidance
         
def prompt_get_job_full_result(job_id: Optional[str] = None) -> str:
    """Provides guidance on how to retrieve the full result of a job."""
    general_guidance = (
        "To retrieve the complete result of a job without truncation, use `get_job_full_result`. "
        "This is useful when the result is large and was truncated in `check_job_status`. Provide:\n"
        "1. `agent_identifier`\n"
        "2. `api_base_url`\n"
        "3. `job_id` (from `hire_agent`)\n\n"
        "Example: `get_job_full_result(agent_identifier='ID', api_base_url='URL', job_id='JOB_ID')`"
    )
    if job_id:
        return (
            f"To retrieve the complete result for job `{job_id}`, use `get_job_full_result`. "
            f"Provide `agent_identifier` and `api_base_url` too.\n\n"
            f"Example: `get_job_full_result(agent_identifier='ID', api_base_url='URL', job_id='{job_id}')`"
        )
    else:
        return general_guidance

def prompt_query_payments() -> str:
    """Provides guidance on how to query payment requests from the Masumi Payment Service."""
    return (
        "To query payment requests, use the `query_payments` tool. This allows you to view payment history "
        "and transaction details from the Masumi Payment Service.\n\n"
        "Required parameters:\n"
        "- `network`: Must be 'Preprod' for testing (Mainnet blocked in testing mode)\n\n"
        "Optional parameters:\n"
        "- `limit`: Number of results (1-100, default 10)\n"
        "- `cursor_id`: For pagination to get next page of results\n"
        "- `smart_contract_address`: Filter by specific contract address\n"
        "- `include_history`: Include full transaction history (default False)\n\n"
        "Example: `query_payments(network='Preprod', limit=5, include_history=True)`\n\n"
        "⚠️ TESTNET SAFETY: Only 'Preprod' network is allowed during testing to prevent mainnet operations."
    )

def prompt_get_purchase_history() -> str:
    """Provides guidance on how to retrieve purchase history from the Masumi Payment Service."""
    return (
        "To retrieve your purchase history, use the `get_purchase_history` tool. This allows you to view "
        "all your past purchases and their current status.\n\n"
        "Required parameters:\n"
        "- `network`: Must be 'Preprod' for testing (Mainnet blocked in testing mode)\n\n"
        "Optional parameters:\n"
        "- `limit`: Number of results (1-100, default 10)\n"
        "- `cursor_id`: For pagination to get next page of results\n"
        "- `smart_contract_address`: Filter by specific contract address\n"
        "- `include_history`: Include full transaction history (default False)\n\n"
        "Example: `get_purchase_history(network='Preprod', limit=20, include_history=True)`\n\n"
        "The response includes:\n"
        "- Purchase details (ID, agent, amount, status)\n"
        "- Transaction information\n"
        "- Purchase summary for quick overview\n\n"
        "⚠️ TESTNET SAFETY: Only 'Preprod' network is allowed during testing to prevent mainnet operations."
    )

def prompt_query_registry() -> str:
    """Provides guidance on how to query the Masumi Registry Service."""
    return (
        "To query the agent registry, use the `query_registry` tool. This allows you to browse "
        "all registered agents on the Masumi network with their details and pricing.\n\n"
        "Required parameters:\n"
        "- `network`: Must be 'Preprod' for testing (Mainnet blocked in testing mode)\n\n"
        "Optional parameters:\n"
        "- `cursor_id`: For pagination to get next page of results\n"
        "- `smart_contract_address`: Filter by specific contract address\n\n"
        "Example: `query_registry(network='Preprod', cursor_id='some-cursor-id')`\n\n"
        "The response includes:\n"
        "- Complete agent registry entries with metadata\n"
        "- Agent capabilities and pricing information\n"
        "- API endpoints and contact details\n"
        "- Agent summary for quick overview\n\n"
        "⚠️ TESTNET SAFETY: Only 'Preprod' network is allowed during testing to prevent mainnet operations."
    )

def prompt_register_agent() -> str:
    """Provides guidance on how to register a new agent in the Masumi Registry."""
    return (
        "To register a new agent, use the `register_agent` tool. This allows you to onboard "
        "your agent to the Masumi network for others to discover and use.\n\n"
        "Required parameters:\n"
        "- `network`: Must be 'Preprod' for testing (Mainnet blocked in testing mode)\n"
        "- `name`: Agent name (must start with 'masumi-test-' for testing)\n"
        "- `api_base_url`: Your agent's API endpoint (http:// or https://)\n"
        "- `selling_wallet_vkey`: Your wallet verification key for payments\n"
        "- `capability_name`: What your agent does (e.g., 'Content Writing')\n"
        "- `capability_version`: Version of your capability (e.g., '1.0.0')\n"
        "- `base_price`: Price in lovelace (e.g., 1000000 for 1 ADA)\n\n"
        "Optional parameters:\n"
        "- `tags`: List of tags for categorization\n"
        "- `description`: Detailed description of your agent\n"
        "- `author`: Author information\n"
        "- `legal_info`: Legal information\n\n"
        "Example: `register_agent(network='Preprod', name='masumi-test-writer-001', "
        "api_base_url='https://my-agent.com/', selling_wallet_vkey='vkey123...', "
        "capability_name='Content Writing', capability_version='1.0.0', base_price=1000000)`\n\n"
        "⚠️ TESTNET SAFETY: Only test agents with 'masumi-test-' prefix allowed during testing."
    )

def prompt_unregister_agent() -> str:
    """Provides guidance on how to unregister an agent from the Masumi Registry."""
    return (
        "To unregister an agent, use the `unregister_agent` tool. This removes your agent "
        "from the Masumi network registry.\n\n"
        "Required parameters:\n"
        "- `agent_identifier`: The unique identifier of your agent (must start with 'masumi-test-')\n"
        "- `network`: Must be 'Preprod' for testing (Mainnet blocked in testing mode)\n\n"
        "Optional parameters:\n"
        "- `smart_contract_address`: Smart contract address if applicable\n\n"
        "Example: `unregister_agent(agent_identifier='masumi-test-writer-001', network='Preprod')`\n\n"
        "⚠️ TESTNET SAFETY: Only test agents with 'masumi-test-' prefix can be unregistered during testing."
    )

def prompt_get_agents_by_wallet() -> str:
    """Provides guidance on how to query agents by wallet verification key."""
    return (
        "To find agents associated with a specific wallet, use the `get_agents_by_wallet` tool. "
        "This helps you see all agents registered under a particular wallet.\n\n"
        "Required parameters:\n"
        "- `network`: Must be 'Preprod' for testing (Mainnet blocked in testing mode)\n"
        "- `wallet_vkey`: The wallet verification key to search for\n\n"
        "Example: `get_agents_by_wallet(network='Preprod', wallet_vkey='vkey_test_writer_123...')`\n\n"
        "The response includes:\n"
        "- Complete list of agents for the wallet\n"
        "- Agent details and capabilities\n"
        "- Registration status and metadata\n"
        "- Agent summary for quick overview\n\n"
        "⚠️ TESTNET SAFETY: Only 'Preprod' network is allowed during testing to prevent mainnet operations."
    )