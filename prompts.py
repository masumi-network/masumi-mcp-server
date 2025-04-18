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