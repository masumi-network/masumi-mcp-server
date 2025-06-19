import os
import json
import uuid
import httpx
import random
import sys
from typing import Any, List, Tuple

from mcp.server.fastmcp import Context

# Import URLs from the main module
MASUMI_REGISTRY_URL = None
MASUMI_PAYMENT_URL = None

def set_urls(registry_url: str, payment_url: str):
    global MASUMI_REGISTRY_URL, MASUMI_PAYMENT_URL
    MASUMI_REGISTRY_URL = registry_url
    MASUMI_PAYMENT_URL = payment_url

# --- Helper functions ---

def split_large_content(content: str, max_size: int = 4000) -> List[str]:
    """
    Split large content into smaller chunks to avoid truncation.

    Args:
        content: The string content to split
        max_size: Maximum size for each chunk

    Returns:
        List of content chunks
    """
    if len(content) <= max_size:
        return [content]

    chunks = []
    current_pos = 0

    while current_pos < len(content):
        # Find a good breaking point (prefer line breaks)
        end_pos = current_pos + max_size
        if end_pos >= len(content):
            chunks.append(content[current_pos:])
            break

        # Look for a newline to break at
        break_pos = content.rfind('\n', current_pos, end_pos)
        if break_pos == -1 or break_pos <= current_pos:
            # No good newline, try to break at a space
            break_pos = content.rfind(' ', current_pos, end_pos)
            if break_pos == -1 or break_pos <= current_pos:
                # No good space, just break at max_size
                break_pos = end_pos

        chunks.append(content[current_pos:break_pos])
        current_pos = break_pos + 1

    return chunks

# --- MCP Tools (Actions) ---

async def list_agents(ctx: Context) -> str:
    """
    Lists available agents on the configured Masumi network from the registry.
    Returns a JSON string of agent entries, including 'agentIdentifier' and 'apiBaseUrl'.
    """
    m_ctx = ctx.request_context.lifespan_context
    client = m_ctx.http_client

    if not MASUMI_REGISTRY_URL:
        return "Error: MASUMI_REGISTRY_URL is not configured properly."

    if not m_ctx.registry_token:
        ctx.error("Masumi Registry Token is not configured.")
        return "Error: Masumi Registry Token is not configured."

    headers = {'accept': 'application/json', 'token': m_ctx.registry_token, 'Content-Type': 'application/json'}
    payload = {"limit": 50, "network": m_ctx.network}
    ctx.info(f"Fetching agents from registry (Tool: list_agents, Network: {m_ctx.network}, Limit: {payload['limit']})")

    try:
        response = await client.post(MASUMI_REGISTRY_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success":
            entries = data.get("data", {}).get("entries", [])
            ctx.info(f"Successfully fetched {len(entries)} agent(s).")
            return json.dumps(entries, indent=2)
        else:
            status_msg = f"Registry API did not return success status: {data.get('status')}"
            ctx.warn(status_msg)
            return f"Error: {status_msg}"

    except httpx.HTTPStatusError as e:
        error_text = e.response.text[:200]
        error_msg = f"HTTP error fetching agents: {e.response.status_code} - {error_text}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error fetching agents: {str(e)}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"

async def get_agent_input_schema(ctx: Context, agent_identifier: str, api_base_url: str) -> str:
    """
    Retrieves the required input schema for a specific Masumi agent using its URL.

    Args:
        agent_identifier: The unique identifier of the agent.
        api_base_url: The base URL for the agent's API (obtained from 'list_agents').

    Returns:
        A JSON string detailing the input schema, or an error message.
    """
    m_ctx = ctx.request_context.lifespan_context
    client = m_ctx.http_client
    ctx.info(f"Fetching input schema for agent: {agent_identifier} using URL: {api_base_url}")

    if not api_base_url:
         return f"Error: api_base_url must be provided for agent {agent_identifier}."

    if not api_base_url.endswith('/'):
        api_base_url += '/'

    schema_url = f"{api_base_url}input_schema"
    schema_headers = {'accept': 'application/json'}

    try:
        ctx.info(f"Calling agent input_schema endpoint: {schema_url}")
        schema_response = await client.get(schema_url, headers=schema_headers)
        schema_response.raise_for_status()
        schema_data = schema_response.json()

        schema_report = (
            f"--- Input Schema for Agent {agent_identifier} ---\n"
            f"{json.dumps(schema_data, indent=2)}"
        )
        ctx.info(f"Successfully fetched schema for agent {agent_identifier}.")
        return schema_report

    except httpx.HTTPStatusError as e:
        error_text = e.response.text[:200]
        if e.response.status_code == 404:
             error_msg = f"Input schema endpoint not found for agent {agent_identifier} at {schema_url}."
             ctx.warn(error_msg)
             return f"Error: {error_msg}"
        else:
             error_msg = f"HTTP error fetching input schema: {e.response.status_code} - {error_text}"
             ctx.error(error_msg)
             return f"Error: {error_msg}"
    except json.JSONDecodeError:
        error_msg = f"Agent {agent_identifier} returned invalid JSON for input schema from {schema_url}."
        ctx.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error fetching input schema for {agent_identifier}: {str(e)}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"

async def hire_agent(ctx: Context, agent_identifier: str, api_base_url: str, input_data: dict[str, Any]) -> str:
    """
    Hires a Masumi agent using its URL: starts a job and initiates payment.
    Use 'get_agent_input_schema' first to understand the required structure for 'input_data'.

    IMPORTANT: The input_data parameter should contain values explicitly provided by the user,
    not automatically generated by the assistant. Always confirm with the user what specific
    values they want to use after showing them the input schema.

    Args:
        agent_identifier: The unique identifier of the agent.
        api_base_url: The base URL for the agent's API (obtained from 'list_agents').
        input_data: A dictionary representing the input data required by the agent, matching the schema.
                    Example: {"text": "Write a story about a robot learning to paint"}

    Returns:
        A message indicating success (including Job ID) or failure details.
    """
    # WARNING TO ASSISTANT: DO NOT CALL THIS FUNCTION WITH AUTOMATICALLY GENERATED INPUT.
    # ALWAYS ASK THE USER TO EXPLICITLY PROVIDE THE VALUES THEY WANT TO USE.

    m_ctx = ctx.request_context.lifespan_context
    client = m_ctx.http_client

    if not MASUMI_PAYMENT_URL:
        return "Error: MASUMI_PAYMENT_URL is not configured properly."

    ctx.info(f"Initiating hiring process for agent: {agent_identifier} using URL: {api_base_url}")
    ctx.info(f"Received input_data: {input_data}")

    # --- Input Validation ---
    if not isinstance(input_data, dict) or not input_data:
        error_msg = "Error: The 'input_data' parameter must be a non-empty dictionary containing the agent's required inputs."
        ctx.error(error_msg + f" Received: {input_data}")
        return error_msg + " Please provide the required inputs based on the agent's schema (use get_agent_input_schema)."

    if not m_ctx.payment_token:
        return "Error: Masumi Payment Token is not configured. Cannot hire agent."
    if not api_base_url:
         return f"Error: api_base_url must be provided for agent {agent_identifier}."

    if not api_base_url.endswith('/'):
        api_base_url += '/'

    # --- Step 2: Call Agent /start_job ---
    start_job_url = f"{api_base_url}start_job"

    # Generate identifier in requested format
    random_suffix = "".join([str(random.randint(0, 9)) for _ in range(3)])
    identifier_from_purchaser = f"example_purchaser_{random_suffix}"
    ctx.info(f"Generated identifier_from_purchaser: {identifier_from_purchaser}")

    start_job_payload = {
        "identifier_from_purchaser": identifier_from_purchaser,
        "input_data": input_data
    }
    start_job_headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    job_id = None

    try:
        payload_to_send_str = json.dumps(start_job_payload)
        ctx.info(f"Payload to be sent to /start_job: {payload_to_send_str}")
    except Exception as dump_e:
        ctx.error(f"Could not serialize start_job_payload: {dump_e}")
        return f"Internal error: Could not serialize payload for agent {agent_identifier}."

    blockchain_identifier = None
    seller_vkey = None
    submit_time = None
    unlock_time = None
    ext_dispute_time = None
    input_hash = None
    agent_id_for_payment = None

    try:
        ctx.info(f"Calling start_job for {agent_identifier} at {start_job_url}")
        start_job_response = await client.post(start_job_url, headers=start_job_headers, json=start_job_payload)
        ctx.info(f"/start_job response status code: {start_job_response.status_code}")

        if start_job_response.status_code == 400:
             try:
                 error_detail = start_job_response.json()
                 ctx.error(f"Agent returned 400 Bad Request for /start_job. Detail: {json.dumps(error_detail)}")
             except json.JSONDecodeError:
                 ctx.error(f"Agent returned 400 Bad Request for /start_job. Response body not valid JSON: {start_job_response.text[:500]}")

        start_job_response.raise_for_status()

        start_job_data = start_job_response.json()
        ctx.info(f"/start_job successful response data: {json.dumps(start_job_data)}")

        job_id = start_job_data.get("job_id")
        blockchain_identifier = start_job_data.get("blockchainIdentifier")
        seller_vkey = start_job_data.get("sellerVKey")
        submit_time = start_job_data.get("submitResultTime")
        unlock_time = start_job_data.get("unlockTime")
        ext_dispute_time = start_job_data.get("externalDisputeUnlockTime")
        input_hash = start_job_data.get("input_hash")
        agent_id_for_payment = start_job_data.get("agentIdentifier")

        required_payment_fields = {
            "job_id": job_id, "blockchainIdentifier": blockchain_identifier, "sellerVkey": seller_vkey,
            "submitResultTime": submit_time, "unlockTime": unlock_time,
            "externalDisputeUnlockTime": ext_dispute_time, "input_hash": input_hash,
            "agentIdentifier (for payment)": agent_id_for_payment
        }
        missing_fields = [k for k, v in required_payment_fields.items() if v is None]
        if missing_fields:
             error_msg = f"Error: Missing required data from agent's /start_job response: {', '.join(missing_fields)}. Response: {json.dumps(start_job_data)}"
             ctx.error(error_msg)
             return error_msg

        ctx.info(f"Job started successfully for {agent_identifier}. Job ID: {job_id}. Proceeding to payment.")

    except httpx.HTTPStatusError as e:
        error_text = e.response.text
        error_msg = f"HTTP error calling /start_job for {agent_identifier}: {e.response.status_code} - Response Body: {error_text}"
        ctx.error(error_msg)
        try:
            detail = json.loads(error_text).get("detail", error_text)
            if isinstance(detail, list):
                 detail_str = "; ".join([f"{item.get('loc', ['Unknown location'])[1]}: {item.get('msg', 'Unknown error')}" for item in detail])
                 return f"Error from agent {agent_identifier}: {detail_str} (Status code: {e.response.status_code})"
            else:
                 if "Input_data or identifier_from_purchaser is missing" in str(detail):
                     return f"Error from agent {agent_identifier}: Input data or identifier is invalid/missing. Please ensure input matches schema and try again. (Status code: {e.response.status_code})"
                 else:
                     return f"Error from agent {agent_identifier}: {detail} (Status code: {e.response.status_code})"
        except json.JSONDecodeError:
            return f"Error from agent {agent_identifier}: {error_text} (Status code: {e.response.status_code})"

    except Exception as e:
        error_msg = f"Unexpected error during /start_job call for {agent_identifier}: {str(e)}"
        ctx.error(error_msg, exc_info=True)
        return f"Error: {error_msg}"

    # --- Step 3: Call Payment Service /purchase ---
    payment_headers = {'accept': 'application/json', 'token': m_ctx.payment_token, 'Content-Type': 'application/json'}
    payment_payload = {
          "identifierFromPurchaser": identifier_from_purchaser,
          "blockchainIdentifier": blockchain_identifier,
          "network": m_ctx.network,
          "sellerVkey": seller_vkey,
          "paymentType": "Web3CardanoV1",
          "submitResultTime": str(submit_time),
          "unlockTime": str(unlock_time),
          "externalDisputeUnlockTime": str(ext_dispute_time),
          "agentIdentifier": agent_id_for_payment,
          "inputHash": input_hash
    }

    try:
        ctx.info(f"Calling payment service ({MASUMI_PAYMENT_URL}) for job {job_id}")
        payment_response = await client.post(MASUMI_PAYMENT_URL, headers=payment_headers, json=payment_payload)
        ctx.info(f"/purchase response status code: {payment_response.status_code}")

        payment_response.raise_for_status()
        payment_data = payment_response.json()
        ctx.info(f"/purchase successful response data: {json.dumps(payment_data)}")

        if payment_data.get("status") == "success":
            next_action = payment_data.get("data", {}).get("NextAction", {}).get("requestedAction", "Unknown")
            payment_id = payment_data.get("data", {}).get("id", "N/A")
            success_msg = f"Successfully hired agent {agent_identifier}. Job ID: {job_id}. Payment initiated (ID: {payment_id}), Next Action: {next_action}."
            ctx.info(success_msg)
            return success_msg
        else:
            error_detail = json.dumps(payment_data)
            error_msg = f"Payment service returned status '{payment_data.get('status')}'. Details: {error_detail}"
            ctx.error(f"Payment initiation failed for job {job_id}: {error_msg}")
            return f"Error initiating payment for job {job_id}: {error_msg}"

    except httpx.HTTPStatusError as e:
        error_text = e.response.text
        error_msg = f"HTTP error calling payment service for job {job_id}: {e.response.status_code} - Response Body: {error_text}"
        ctx.error(error_msg)
        return f"Error: Job {job_id} was started on agent {agent_identifier}, but failed to initiate payment: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error calling payment service for job {job_id}: {str(e)}"
        ctx.error(error_msg, exc_info=True)
        return f"Error: Job {job_id} was started, but encountered an unexpected error initiating payment: {error_msg}"

async def get_job_full_result(ctx: Context, agent_identifier: str, api_base_url: str, job_id: str) -> str:
    """
    Retrieves only the result content from a completed job, without truncation.
    Use this after check_job_status shows a job is complete but the result was large.

    Args:
        agent_identifier: The unique identifier of the agent.
        api_base_url: The base URL for the agent's API (obtained from 'list_agents').
        job_id: The ID of the job to check (returned by hire_agent).

    Returns:
        The full result content from the job.
    """
    m_ctx = ctx.request_context.lifespan_context
    client = m_ctx.http_client

    if not api_base_url:
        return f"Error: api_base_url must be provided for agent {agent_identifier}."

    if not api_base_url.endswith('/'):
        api_base_url += '/'

    status_url = f"{api_base_url}status"
    status_headers = {'accept': 'application/json'}
    params = {'job_id': job_id}

    try:
        status_response = await client.get(status_url, headers=status_headers, params=params)
        status_response.raise_for_status()
        status_data = status_response.json()
        result = status_data.get("result", None)

        if result is None:
            return "No result available for this job."

        try:
            # Return the raw content directly if available
            if isinstance(result, dict) and result.get("raw"):
                return result.get("raw")
            elif isinstance(result, (dict, list)):
                return json.dumps(result, indent=2)
            else:
                return str(result)

        except Exception as e:
            ctx.warn(f"Could not format result for job {job_id}: {str(e)}")
            return "Error: Could not format the result content."

    except Exception as e:
        return f"Error retrieving job result: {str(e)}"

async def check_job_status(ctx: Context, agent_identifier: str, api_base_url: str, job_id: str) -> str:
    """
    Checks the status of a specific job running on a Masumi agent using its URL.

    Args:
        agent_identifier: The unique identifier of the agent.
        api_base_url: The base URL for the agent's API (obtained from 'list_agents').
        job_id: The ID of the job to check (returned by hire_agent).

    Returns:
        A string describing the job's current status and result (if available).
    """
    m_ctx = ctx.request_context.lifespan_context
    client = m_ctx.http_client
    ctx.info(f"Checking status for job {job_id} on agent {agent_identifier} using URL: {api_base_url}")

    if not api_base_url:
         return f"Error: api_base_url must be provided for agent {agent_identifier}."

    if not api_base_url.endswith('/'):
        api_base_url += '/'

    status_url = f"{api_base_url}status"
    status_headers = {'accept': 'application/json'}
    params = {'job_id': job_id}

    try:
        ctx.info(f"Calling agent status endpoint: {status_url} for job {job_id}")
        status_response = await client.get(status_url, headers=status_headers, params=params)
        status_response.raise_for_status()
        status_data = status_response.json()

        job_status = status_data.get("status", "Unknown")
        payment_status = status_data.get("payment_status", "N/A")
        result = status_data.get("result", None)

        # Format the basic status information
        status_info = (
            f"--- Job Status Report for {job_id} ---\n"
            f"Agent: {agent_identifier}\n"
            f"Status: {job_status}\n"
            f"Payment Status: {payment_status}\n"
        )

        # Handle the result separately
        if result is None:
            return f"{status_info}\nResult: Not available"

        try:
            # Check if we have a raw text result
            if isinstance(result, dict) and result.get("raw"):
                raw_text = result.get("raw")
                # Check if it's a large result
                if len(raw_text) > 3000:
                    # For large results, show a preview and instructions for full retrieval
                    preview = raw_text[:3000] + "..."
                    return (
                        f"{status_info}\n"
                        f"Result Preview (truncated - full result is {len(raw_text)} characters):\n\n"
                        f"{preview}\n\n"
                        f"To view the complete result, use the get_job_full_result tool:\n"
                        f"get_job_full_result(agent_identifier='{agent_identifier}', "
                        f"api_base_url='{api_base_url}', job_id='{job_id}')"
                    )
                else:
                    # Show full result for smaller content
                    return f"{status_info}\nResult:\n\n{raw_text}"
            elif isinstance(result, (dict, list)):
                # Convert JSON to pretty string
                json_text = json.dumps(result, indent=2)
                # Check if it's a large result
                if len(json_text) > 3000:
                    preview = json_text[:3000] + "..."
                    return (
                        f"{status_info}\n"
                        f"Result Preview (truncated - full JSON is {len(json_text)} characters):\n\n"
                        f"{preview}\n\n"
                        f"To view the complete result, use the get_job_full_result tool:\n"
                        f"get_job_full_result(agent_identifier='{agent_identifier}', "
                        f"api_base_url='{api_base_url}', job_id='{job_id}')"
                    )
                else:
                    return f"{status_info}\nResult (JSON):\n\n{json_text}"
            else:
                # Plain text result
                text_result = str(result)
                if len(text_result) > 3000:
                    preview = text_result[:3000] + "..."
                    return (
                        f"{status_info}\n"
                        f"Result Preview (truncated - full text is {len(text_result)} characters):\n\n"
                        f"{preview}\n\n"
                        f"To view the complete result, use the get_job_full_result tool:\n"
                        f"get_job_full_result(agent_identifier='{agent_identifier}', "
                        f"api_base_url='{api_base_url}', job_id='{job_id}')"
                    )
                else:
                    return f"{status_info}\nResult:\n\n{text_result}"

        except Exception as e:
            ctx.warn(f"Could not format result for job {job_id}: {str(e)}")
            return f"{status_info}\nResult: [Available but could not be formatted]"

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Error: Job {job_id} not found on agent {agent_identifier}."
        else:
            try:
                detail = json.loads(e.response.text).get("detail", e.response.text)
                return f"Error checking job status: {detail} (Status code: {e.response.status_code})"
            except json.JSONDecodeError:
                return f"Error checking job status: HTTP error {e.response.status_code}"

    except Exception as e:
        return f"Error: Unexpected error checking status for job {job_id}: {str(e)}"

async def query_payments(ctx: Context, network: str, limit: int = 10, cursor_id: str | None = None,
                        smart_contract_address: str | None = None, include_history: bool = False) -> str:
    """
    Query payment requests from the Masumi Payment Service.

    Args:
        network: The Cardano network ("Preprod" or "Mainnet"). For testing, only "Preprod" is allowed.
        limit: Number of results to return (1-100, default 10).
        cursor_id: Optional pagination cursor for retrieving next page of results.
        smart_contract_address: Optional smart contract address filter (max 250 chars).
        include_history: Whether to include transaction history (default False).

    Returns:
        JSON string containing payment request data with transaction details.
    """
    m_ctx = ctx.request_context.lifespan_context
    client = m_ctx.http_client

    # Parameter validation
    if not (1 <= limit <= 100):
        error_msg = f"Limit must be between 1 and 100, got: {limit}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"

    if smart_contract_address and len(smart_contract_address) > 250:
        error_msg = f"Smart contract address too long (max 250 chars), got: {len(smart_contract_address)}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"

    if not MASUMI_PAYMENT_URL:
        return "Error: MASUMI_PAYMENT_URL is not configured properly."

    if not m_ctx.payment_token:
        ctx.error("Masumi Payment Token is not configured.")
        return "Error: Masumi Payment Token is not configured."

    # Build the payment query URL (GET endpoint)
    payment_query_url = MASUMI_PAYMENT_URL.replace("/purchase/", "/payment/")

    headers = {
        'accept': 'application/json',
        'token': m_ctx.payment_token,
        'Content-Type': 'application/json'
    }

    # Build query parameters
    params = {
        "network": network,
        "limit": limit,
        "includeHistory": include_history
    }

    if cursor_id:
        params["cursorId"] = cursor_id

    if smart_contract_address:
        params["smartContractAddress"] = smart_contract_address

    ctx.info(f"Querying payments (Network: {network}, Limit: {limit}, Include History: {include_history})")

    try:
        response = await client.get(payment_query_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success":
            entries = data.get("data", {}).get("entries", [])
            ctx.info(f"Successfully queried {len(entries)} payment(s).")

            # Format response for better readability
            formatted_response = {
                "status": "success",
                "count": len(entries),
                "network": network,
                "payments": entries
            }

            if cursor_id:
                formatted_response["cursor_id"] = cursor_id

            return json.dumps(formatted_response, indent=2)
        else:
            status_msg = f"Payment API did not return success status: {data.get('status')}"
            ctx.warn(status_msg)
            return f"Error: {status_msg}"

    except httpx.HTTPStatusError as e:
        error_text = e.response.text[:200]
        error_msg = f"HTTP error querying payments: {e.response.status_code} - {error_text}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error querying payments: {str(e)}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"

async def get_purchase_history(ctx: Context, network: str, limit: int = 10, cursor_id: str | None = None,
                              smart_contract_address: str | None = None, include_history: bool = False) -> str:
    """
    Retrieve purchase history from the Masumi Payment Service.

    Args:
        network: The Cardano network ("Preprod" or "Mainnet"). For testing, only "Preprod" is allowed.
        limit: Number of results to return (1-100, default 10).
        cursor_id: Optional pagination cursor for retrieving next page of results.
        smart_contract_address: Optional smart contract address filter (max 250 chars).
        include_history: Whether to include full transaction history (default False).

    Returns:
        JSON string containing purchase request data with transaction details.
    """
    m_ctx = ctx.request_context.lifespan_context
    client = m_ctx.http_client

    # Parameter validation
    if not (1 <= limit <= 100):
        error_msg = f"Limit must be between 1 and 100, got: {limit}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"

    if smart_contract_address and len(smart_contract_address) > 250:
        error_msg = f"Smart contract address too long (max 250 chars), got: {len(smart_contract_address)}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"

    if not MASUMI_PAYMENT_URL:
        return "Error: MASUMI_PAYMENT_URL is not configured properly."

    if not m_ctx.payment_token:
        ctx.error("Masumi Payment Token is not configured.")
        return "Error: Masumi Payment Token is not configured."

    # Use the purchase endpoint (GET /api/v1/purchase)
    purchase_query_url = MASUMI_PAYMENT_URL

    headers = {
        'accept': 'application/json',
        'token': m_ctx.payment_token,
        'Content-Type': 'application/json'
    }

    # Build query parameters matching the API schema
    params = {
        "network": network,
        "limit": limit,
        "includeHistory": include_history
    }

    if cursor_id:
        params["cursorId"] = cursor_id

    if smart_contract_address:
        params["smartContractAddress"] = smart_contract_address

    ctx.info(f"Querying purchase history (Network: {network}, Limit: {limit}, Include History: {include_history})")

    try:
        response = await client.get(purchase_query_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success":
            entries = data.get("data", {}).get("entries", [])
            ctx.info(f"Successfully queried {len(entries)} purchase(s).")

            # Format response for better readability
            formatted_response = {
                "status": "success",
                "count": len(entries),
                "network": network,
                "purchases": entries
            }

            if cursor_id:
                formatted_response["cursor_id"] = cursor_id

            # Add summary information for each purchase
            if entries:
                summary = []
                for purchase in entries:
                    purchase_summary = {
                        "id": purchase.get("id", "N/A"),
                        "agent_identifier": purchase.get("agentIdentifier", "N/A"),
                        "amount": purchase.get("amount", "N/A"),
                        "status": purchase.get("status", "N/A"),
                        "created_at": purchase.get("createdAt", "N/A")
                    }
                    summary.append(purchase_summary)
                formatted_response["purchase_summary"] = summary

            return json.dumps(formatted_response, indent=2)
        else:
            status_msg = f"Purchase API did not return success status: {data.get('status')}"
            ctx.warn(status_msg)
            return f"Error: {status_msg}"

    except httpx.HTTPStatusError as e:
        error_text = e.response.text[:200]
        error_msg = f"HTTP error querying purchase history: {e.response.status_code} - {error_text}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error querying purchase history: {str(e)}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"

async def query_registry(ctx: Context, network: str, cursor_id: str | None = None,
                        smart_contract_address: str | None = None) -> str:
    """
    Query registry requests from the Masumi Registry Service.

    Args:
        network: The Cardano network ("Preprod" or "Mainnet"). For testing, only "Preprod" is allowed.
        cursor_id: Optional pagination cursor for retrieving next page of results.
        smart_contract_address: Optional smart contract address filter.

    Returns:
        JSON string containing registry request data with agent details, pricing, and metadata.
    """
    m_ctx = ctx.request_context.lifespan_context
    client = m_ctx.http_client

    if not MASUMI_REGISTRY_URL:
        return "Error: MASUMI_REGISTRY_URL is not configured properly."

    if not m_ctx.registry_token:
        ctx.error("Masumi Registry Token is not configured.")
        return "Error: Masumi Registry Token is not configured."

    headers = {
        'accept': 'application/json',
        'token': m_ctx.registry_token,
        'Content-Type': 'application/json'
    }

    # Build query parameters matching the API schema
    params = {
        "network": network
    }

    if cursor_id:
        params["cursorId"] = cursor_id

    if smart_contract_address:
        params["smartContractAddress"] = smart_contract_address

    ctx.info(f"Querying registry (Network: {network})")

    try:
        response = await client.get(MASUMI_REGISTRY_URL, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "success":
            entries = data.get("data", {}).get("entries", [])
            ctx.info(f"Successfully queried {len(entries)} registry entr(ies).")

            # Format response for better readability
            formatted_response = {
                "status": "success",
                "count": len(entries),
                "network": network,
                "registry_entries": entries
            }

            if cursor_id:
                formatted_response["cursor_id"] = cursor_id

            # Add summary information for each agent
            if entries:
                summary = []
                for entry in entries:
                    agent_summary = {
                        "agent_identifier": entry.get("agentIdentifier", "N/A"),
                        "name": entry.get("name", "N/A"),
                        "api_base_url": entry.get("apiBaseUrl", "N/A"),
                        "capability": entry.get("Capability", {}).get("name", "N/A"),
                        "base_price": entry.get("AgentPricing", {}).get("basePrice", "N/A"),
                        "status": entry.get("status", "N/A")
                    }
                    summary.append(agent_summary)
                formatted_response["agent_summary"] = summary

            return json.dumps(formatted_response, indent=2)
        else:
            status_msg = f"Registry API did not return success status: {data.get('status')}"
            ctx.warn(status_msg)
            return f"Error: {status_msg}"

    except httpx.HTTPStatusError as e:
        error_text = e.response.text[:200]
        error_msg = f"HTTP error querying registry: {e.response.status_code} - {error_text}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error querying registry: {str(e)}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"

async def register_agent(ctx: Context, network: str, name: str, api_base_url: str, selling_wallet_vkey: str,
                        capability_name: str, capability_version: str, base_price: int, 
                        tags: list[str] | None = None, description: str | None = None, 
                        author: str | None = None, legal_info: str | None = None) -> str:
    """
    Register a new agent in the Masumi Registry Service.
    
    Args:
        network: The Cardano network ("Preprod" or "Mainnet"). For testing, only "Preprod" is allowed.
        name: The agent name (required).
        api_base_url: The base URL for the agent's API (required).
        selling_wallet_vkey: The verification key of the selling wallet (required).
        capability_name: The name of the agent's capability (required).
        capability_version: The version of the agent's capability (required).
        base_price: The base price in lovelace (required).
        tags: Optional list of tags for categorization.
        description: Optional description of the agent.
        author: Optional author information.
        legal_info: Optional legal information.
        
    Returns:
        JSON string containing registration confirmation or error details.
    """
    m_ctx = ctx.request_context.lifespan_context
    client = m_ctx.http_client
    
    # Testnet safety validation
    try:
        validate_testnet_safety(network)
    except ValueError as e:
        ctx.error(f"Testnet safety check failed: {str(e)}")
        return f"Error: {str(e)}"
    
    # Agent identifier validation (ensure it's a test agent)
    if not name.startswith("masumi-test-"):
        try:
            validate_test_data_only(name)
        except ValueError as e:
            ctx.error(f"Agent name validation failed: {str(e)}")
            return f"Error: {str(e)} Agent name must start with 'masumi-test-' for testing."
    
    # Parameter validation
    if not name or len(name.strip()) == 0:
        error_msg = "Agent name cannot be empty"
        ctx.error(error_msg)
        return f"Error: {error_msg}"
    
    if not api_base_url or not api_base_url.startswith(("http://", "https://")):
        error_msg = "Invalid API base URL - must start with http:// or https://"
        ctx.error(error_msg)
        return f"Error: {error_msg}"
    
    if not selling_wallet_vkey or len(selling_wallet_vkey.strip()) == 0:
        error_msg = "Selling wallet verification key cannot be empty"
        ctx.error(error_msg)
        return f"Error: {error_msg}"
    
    if base_price < 0:
        error_msg = f"Base price must be non-negative, got: {base_price}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"
    
    if not MASUMI_REGISTRY_URL:
        return "Error: MASUMI_REGISTRY_URL is not configured properly."
    
    if not m_ctx.registry_token:
        ctx.error("Masumi Registry Token is not configured.")
        return "Error: Masumi Registry Token is not configured."
    
    headers = {
        'accept': 'application/json', 
        'token': m_ctx.registry_token,
        'Content-Type': 'application/json'
    }
    
    # Build registration payload matching the API schema
    registration_payload = {
        "network": network,
        "name": name.strip(),
        "apiBaseUrl": api_base_url.strip(),
        "sellingWalletVkey": selling_wallet_vkey.strip(),
        "Tags": tags if tags else [],
        "Capability": {
            "name": capability_name.strip(),
            "version": capability_version.strip()
        },
        "AgentPricing": {
            "basePrice": base_price,
            "currency": "ADA"
        }
    }
    
    # Add optional fields if provided
    if description:
        registration_payload["description"] = description.strip()
    
    if author:
        registration_payload["author"] = author.strip()
    
    if legal_info:
        registration_payload["legalInfo"] = legal_info.strip()
    
    ctx.info(f"Registering agent '{name}' on network {network}")
    
    try:
        response = await client.post(MASUMI_REGISTRY_URL, headers=headers, json=registration_payload)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            registration_data = data.get("data", {})
            ctx.info(f"Successfully registered agent '{name}'.")
            
            # Format response for better readability
            formatted_response = {
                "status": "success",
                "message": f"Agent '{name}' registered successfully",
                "network": network,
                "agent_details": {
                    "name": name,
                    "api_base_url": api_base_url,
                    "capability": f"{capability_name} v{capability_version}",
                    "base_price": f"{base_price} lovelace",
                    "tags": tags if tags else []
                },
                "registration_data": registration_data
            }
            
            return json.dumps(formatted_response, indent=2)
        else:
            status_msg = f"Registry API did not return success status: {data.get('status')}"
            ctx.warn(status_msg)
            return f"Error: {status_msg}"
    
    except httpx.HTTPStatusError as e:
        error_text = e.response.text[:500]
        error_msg = f"HTTP error registering agent: {e.response.status_code} - {error_text}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error registering agent: {str(e)}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"

async def unregister_agent(ctx: Context, agent_identifier: str, network: str, 
                          smart_contract_address: str | None = None) -> str:
    """
    Unregister an agent from the Masumi Registry Service.
    
    Args:
        agent_identifier: The unique identifier of the agent to unregister.
        network: The Cardano network ("Preprod" or "Mainnet"). For testing, only "Preprod" is allowed.
        smart_contract_address: Optional smart contract address.
        
    Returns:
        JSON string containing unregistration confirmation or error details.
    """
    m_ctx = ctx.request_context.lifespan_context
    client = m_ctx.http_client
    
    # Testnet safety validation
    try:
        validate_testnet_safety(network)
    except ValueError as e:
        ctx.error(f"Testnet safety check failed: {str(e)}")
        return f"Error: {str(e)}"
    
    # Agent identifier validation (ensure it's a test agent)
    try:
        validate_test_data_only(agent_identifier)
    except ValueError as e:
        ctx.error(f"Agent identifier validation failed: {str(e)}")
        return f"Error: {str(e)}"
    
    # Parameter validation
    if not agent_identifier or len(agent_identifier.strip()) == 0:
        error_msg = "Agent identifier cannot be empty"
        ctx.error(error_msg)
        return f"Error: {error_msg}"
    
    if not MASUMI_REGISTRY_URL:
        return "Error: MASUMI_REGISTRY_URL is not configured properly."
    
    if not m_ctx.registry_token:
        ctx.error("Masumi Registry Token is not configured.")
        return "Error: Masumi Registry Token is not configured."
    
    headers = {
        'accept': 'application/json', 
        'token': m_ctx.registry_token,
        'Content-Type': 'application/json'
    }
    
    # Build unregistration payload matching the API schema
    unregistration_payload = {
        "agentIdentifier": agent_identifier.strip(),
        "network": network
    }
    
    if smart_contract_address:
        unregistration_payload["smartContractAddress"] = smart_contract_address.strip()
    
    ctx.info(f"Unregistering agent '{agent_identifier}' from network {network}")
    
    try:
        response = await client.delete(MASUMI_REGISTRY_URL, headers=headers, json=unregistration_payload)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            unregistration_data = data.get("data", {})
            ctx.info(f"Successfully unregistered agent '{agent_identifier}'.")
            
            # Format response for better readability
            formatted_response = {
                "status": "success",
                "message": f"Agent '{agent_identifier}' unregistered successfully",
                "network": network,
                "agent_identifier": agent_identifier,
                "unregistration_data": unregistration_data
            }
            
            return json.dumps(formatted_response, indent=2)
        else:
            status_msg = f"Registry API did not return success status: {data.get('status')}"
            ctx.warn(status_msg)
            return f"Error: {status_msg}"
    
    except httpx.HTTPStatusError as e:
        error_text = e.response.text[:500]
        if e.response.status_code == 404:
            error_msg = f"Agent '{agent_identifier}' not found in registry"
            ctx.warn(error_msg)
            return f"Error: {error_msg}"
        else:
            error_msg = f"HTTP error unregistering agent: {e.response.status_code} - {error_text}"
            ctx.error(error_msg)
            return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error unregistering agent: {str(e)}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"

async def get_agents_by_wallet(ctx: Context, network: str, wallet_vkey: str) -> str:
    """
    Query agents by wallet verification key from the Masumi Registry Service.
    
    Args:
        network: The Cardano network ("Preprod" or "Mainnet"). For testing, only "Preprod" is allowed.
        wallet_vkey: The wallet verification key to search for.
        
    Returns:
        JSON string containing agents associated with the wallet.
    """
    m_ctx = ctx.request_context.lifespan_context
    client = m_ctx.http_client
    
    # Testnet safety validation
    try:
        validate_testnet_safety(network)
    except ValueError as e:
        ctx.error(f"Testnet safety check failed: {str(e)}")
        return f"Error: {str(e)}"
    
    # Parameter validation
    if not wallet_vkey or len(wallet_vkey.strip()) == 0:
        error_msg = "Wallet verification key cannot be empty"
        ctx.error(error_msg)
        return f"Error: {error_msg}"
    
    if not MASUMI_REGISTRY_URL:
        return "Error: MASUMI_REGISTRY_URL is not configured properly."
    
    if not m_ctx.registry_token:
        ctx.error("Masumi Registry Token is not configured.")
        return "Error: Masumi Registry Token is not configured."
    
    # Build wallet query URL (assuming /wallet endpoint exists)
    wallet_query_url = MASUMI_REGISTRY_URL.replace("/registry-entry/", "/registry/wallet/")
    
    headers = {
        'accept': 'application/json', 
        'token': m_ctx.registry_token,
        'Content-Type': 'application/json'
    }
    
    # Build query parameters
    params = {
        "network": network,
        "walletVkey": wallet_vkey.strip()
    }
    
    ctx.info(f"Querying agents by wallet (Network: {network}, Wallet: {wallet_vkey[:20]}...)")
    
    try:
        response = await client.get(wallet_query_url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("status") == "success":
            agents = data.get("data", {}).get("agents", [])
            ctx.info(f"Successfully found {len(agents)} agent(s) for wallet.")
            
            # Format response for better readability
            formatted_response = {
                "status": "success",
                "count": len(agents),
                "network": network,
                "wallet_vkey": wallet_vkey,
                "agents": agents
            }
            
            # Add summary information for each agent
            if agents:
                summary = []
                for agent in agents:
                    agent_summary = {
                        "agent_identifier": agent.get("agentIdentifier", "N/A"),
                        "name": agent.get("name", "N/A"),
                        "api_base_url": agent.get("apiBaseUrl", "N/A"),
                        "capability": agent.get("Capability", {}).get("name", "N/A"),
                        "status": agent.get("status", "N/A")
                    }
                    summary.append(agent_summary)
                formatted_response["agent_summary"] = summary
            
            return json.dumps(formatted_response, indent=2)
        else:
            status_msg = f"Registry API did not return success status: {data.get('status')}"
            ctx.warn(status_msg)
            return f"Error: {status_msg}"
    
    except httpx.HTTPStatusError as e:
        error_text = e.response.text[:200]
        if e.response.status_code == 404:
            # No agents found for this wallet - this is valid
            formatted_response = {
                "status": "success",
                "count": 0,
                "network": network,
                "wallet_vkey": wallet_vkey,
                "agents": [],
                "message": "No agents found for this wallet"
            }
            return json.dumps(formatted_response, indent=2)
        else:
            error_msg = f"HTTP error querying agents by wallet: {e.response.status_code} - {error_text}"
            ctx.error(error_msg)
            return f"Error: {error_msg}"
    except Exception as e:
        error_msg = f"Unexpected error querying agents by wallet: {str(e)}"
        ctx.error(error_msg)
        return f"Error: {error_msg}"
