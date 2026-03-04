def generate_agent_spec(memo, version):

    company_name      = memo.get("company_name")
    business_hours    = memo.get("business_hours")
    services          = memo.get("services_supported")
    emergency_defs    = memo.get("emergency_definition")
    emergency_routing = memo.get("emergency_routing_rules")
    non_emergency     = memo.get("non_emergency_routing_rules")
    transfer_rules    = memo.get("call_transfer_rules")
    integration       = memo.get("integration_constraints")
    office_address    = memo.get("office_address")

    # Use fallback text if value is missing
    if not company_name:
        company_name = "the company"
    if not business_hours:
        business_hours = "not specified"
    if not office_address:
        office_address = "not specified"

    # Helper to convert a list into readable text
    def fmt(lst):
        if not lst:
            return "Not specified"
        result = ""
        for item in lst:
            result = result + "\n  - " + str(item)
        return result

    # Build the system prompt using extracted data
    system_prompt = (
        "You are a professional inbound call handling assistant for " + company_name + ".\n\n"
        "BUSINESS HOURS:\n" + str(business_hours) + "\n\n"
        "SERVICES HANDLED:\n" + fmt(services) + "\n\n"
        "EMERGENCY SITUATIONS:\n" + fmt(emergency_defs) + "\n\n"
        "EMERGENCY ROUTING RULES:\n" + fmt(emergency_routing) + "\n\n"
        "NON-EMERGENCY ROUTING RULES:\n" + fmt(non_emergency) + "\n\n"
        "CALL TRANSFER RULES:\n" + fmt(transfer_rules) + "\n\n"
        "IF TRANSFER FAILS:\n"
        "Apologize and say: I'm sorry, I was unable to connect you right now. "
        "Someone will call you back as soon as possible.\n\n"
        "INTEGRATION CONSTRAINTS:\n" + fmt(integration) + "\n\n"
        "RULES:\n"
        "- Never mention function calls or internal tools to the caller.\n"
        "- Only collect information needed for routing.\n"
        "- Always stay calm and professional.\n"
        "- If unsure whether something is an emergency, treat it as one.\n"
    )

    # Business hours call flow
    business_hours_flow = [
        "Greet the caller and identify yourself as assistant for " + company_name,
        "Ask the purpose of their call",
        "Collect the caller full name",
        "Collect the caller callback phone number",
        "Determine if the call is an emergency based on: " + fmt(emergency_defs),
        "If emergency follow emergency routing: " + fmt(emergency_routing),
        "If not emergency follow standard routing: " + fmt(non_emergency),
        "Attempt to transfer the call",
        "If transfer fails apologize and assure callback as soon as possible",
        "Ask if there is anything else you can help with",
        "Thank the caller and close the call"
    ]

    # After hours call flow
    after_hours_flow = [
        "Greet the caller and identify yourself as after hours assistant for " + company_name,
        "Ask the purpose of their call",
        "Confirm if the situation is an emergency based on: " + fmt(emergency_defs),
        "If emergency collect caller full name",
        "If emergency collect caller phone number",
        "If emergency collect caller address",
        "If emergency attempt transfer: " + fmt(emergency_routing),
        "If transfer fails apologize and assure immediate follow up",
        "If not emergency collect name and phone number",
        "If not emergency confirm callback during business hours: " + str(business_hours),
        "Ask if there is anything else you can help with",
        "Thank the caller and close the call"
    ]

    # Build the full agent spec
    if transfer_rules:
        transfer_protocol = fmt(transfer_rules)
    else:
        transfer_protocol = "Transfer to office staff during business hours. Transfer to emergency dispatch after hours."

    agent_spec = {
        "agent_name": company_name.replace(" ", "_") + "_Clara_Agent",
        "version": version,
        "voice_style": "professional",
        "system_prompt": system_prompt.strip(),
        "key_variables": {
            "company_name": company_name,
            "business_hours": business_hours,
            "office_address": office_address,
            "emergency_routing": emergency_routing,
            "services": services
        },
        "tool_invocation_placeholders": [
            "transfer_to_office_staff",
            "transfer_to_emergency_dispatch",
            "send_callback_request",
            "log_call_to_servicetrade"
        ],
        "call_transfer_protocol": transfer_protocol,
        "fallback_protocol": (
            "If transfer fails: apologize to the caller, "
            "collect name and number if not already done, "
            "assure them of a callback, and close the call politely."
        ),
        "business_hours_flow": business_hours_flow,
        "after_hours_flow": after_hours_flow
    }

    return agent_spec
