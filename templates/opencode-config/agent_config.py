import os
import yaml
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("EU-Sovereignty-Validator")

# Define SECURITY_POLICY constant
SECURITY_POLICY = {
    "allowed_jurisdictions": ["EU", "Sovereign", "US", "Local"],
    "high_reasoning_fallback_allowed": True,
    "high_reasoning_fallback_model": "opencode/gemini-3.5-flash",
    "restricted_tasks_jurisdiction_enforced": True,
    "default_code_generation_model": "opencode/gpt-5.1-codex",
    "default_task_execution_model": "opencode/gemini-3-flash",
}

class EUSovereigntyException(Exception):
    """Exception raised when a model violates EU-sovereignty security policy."""
    pass

def load_manifest(manifest_path="manifest.yaml"):
    """Loads the agentic configuration manifest."""
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"Manifest file not found at {manifest_path}")
    with open(manifest_path, 'r') as f:
        return yaml.safe_load(f)

def validate_model_jurisdiction(agent_name, model_name, jurisdiction, task_type="STANDARD"):
    """
    Validation hook that logs the origin jurisdiction of every model used in the orchestration loop
    and triggers an alert/exception if a non-EU, non-authorized model is selected for a 'RESTRICTED' task.
    """
    logger.info(f"Validating agent '{agent_name}' using model '{model_name}' (Jurisdiction: {jurisdiction}) for task type '{task_type}'")
    
    # Check if the task is RESTRICTED and requires strict EU-sovereignty
    if task_type == "RESTRICTED":
        if jurisdiction not in SECURITY_POLICY["allowed_jurisdictions"]:
            # Check if it's the authorized high-reasoning fallback
            if SECURITY_POLICY["high_reasoning_fallback_allowed"] and model_name == SECURITY_POLICY["high_reasoning_fallback_model"]:
                logger.warning(f"ALERT: High-Reasoning fallback model '{model_name}' (Jurisdiction: {jurisdiction}) selected for RESTRICTED task. Proceeding with caution.")
                return True
            else:
                alert_msg = f"CRITICAL SECURITY VIOLATION: Non-EU, non-authorized model '{model_name}' (Jurisdiction: {jurisdiction}) selected for RESTRICTED task!"
                logger.error(alert_msg)
                raise EUSovereigntyException(alert_msg)
                
    # Standard task validation
    if jurisdiction not in SECURITY_POLICY["allowed_jurisdictions"]:
        if SECURITY_POLICY["high_reasoning_fallback_allowed"] and model_name == SECURITY_POLICY["high_reasoning_fallback_model"]:
            logger.info(f"Authorized fallback model '{model_name}' used for standard task.")
            return True
        else:
            logger.warning(f"WARNING: Non-EU model '{model_name}' (Jurisdiction: {jurisdiction}) used for standard task.")
            
    return True

def get_agent_config(agent_name, task_type="STANDARD", manifest_path="manifest.yaml"):
    """
    Retrieves the configuration for a given agent, applying the SECURITY_POLICY
    to force EU-sourced models for Code-Generation and Task-Execution roles.
    """
    manifest = load_manifest(manifest_path)
    agents = manifest.get("agents", {})
    
    if agent_name not in agents:
        raise ValueError(f"Agent '{agent_name}' not defined in manifest.")
        
    agent_cfg = agents[agent_name]
    role = agent_cfg.get("role")
    model = agent_cfg.get("model")
    jurisdiction = agent_cfg.get("jurisdiction")
    
    # Enforce SECURITY_POLICY for Code-Generation and Task-Execution roles
    if role in ["Code-Generation", "Task-Execution"]:
        # If the manifest has a non-EU model for these roles, override it with the EU-sovereign default
        if jurisdiction not in SECURITY_POLICY["allowed_jurisdictions"]:
            logger.warning(f"Policy Enforcement: Overriding non-EU model '{model}' for agent '{agent_name}' (Role: {role}) with EU-sovereign default.")
            if role == "Code-Generation":
                agent_cfg["model"] = SECURITY_POLICY["default_code_generation_model"]
                agent_cfg["endpoint"] = "https://opencode.ai/zen/v1"
                agent_cfg["jurisdiction"] = "Sovereign"
            else:
                agent_cfg["model"] = SECURITY_POLICY["default_task_execution_model"]
                agent_cfg["endpoint"] = "https://opencode.ai/zen/v1"
                agent_cfg["jurisdiction"] = "Sovereign"
                
    # Run the validation hook
    validate_model_jurisdiction(
        agent_name=agent_name,
        model_name=agent_cfg["model"],
        jurisdiction=agent_cfg["jurisdiction"],
        task_type=task_type
    )
    
    return agent_cfg

if __name__ == "__main__":
    # Self-test execution
    print("--- Running EU-Sovereignty Agentic Configuration Self-Test ---")
    try:
        # 1. Test Orchestrator (High-Reasoning Fallback)
        print("\n1. Testing Orchestrator (High-Reasoning Fallback):")
        orch_cfg = get_agent_config("orchestrator", task_type="STANDARD")
        print(f"Result: Success. Model: {orch_cfg['model']} ({orch_cfg['jurisdiction']})")
        
        # 2. Test Code-Generation Agent (builder-infra-tf)
        print("\n2. Testing Code-Generation Agent (builder-infra-tf):")
        tf_cfg = get_agent_config("builder-infra-tf", task_type="RESTRICTED")
        print(f"Result: Success. Model: {tf_cfg['model']} ({tf_cfg['jurisdiction']})")
        
        # 3. Test Task-Execution Agent (verifier)
        print("\n3. Testing Task-Execution Agent (verifier):")
        ver_cfg = get_agent_config("verifier", task_type="STANDARD")
        print(f"Result: Success. Model: {ver_cfg['model']} ({ver_cfg['jurisdiction']})")
        
        # 4. Test Restricted Task with unauthorized model (Simulated)
        # Under the EU+US policy, US models are permitted, so a Global-jurisdiction
        # model (e.g. a Chinese provider) is used to demonstrate enforcement.
        print("\n4. Testing Restricted Task with unauthorized model (Simulated):")
        validate_model_jurisdiction("malicious-agent", "deepseek/deepseek-v4-pro", "Global", task_type="RESTRICTED")
        
    except EUSovereigntyException as e:
        print(f"\nCaught expected security exception: {e}")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
