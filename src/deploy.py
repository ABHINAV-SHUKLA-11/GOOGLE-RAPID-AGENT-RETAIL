from google.cloud import aiplatform
import yaml
import os

class AgentBuilderDeployer:
    """Deploy agent to Google Cloud Agent Builder"""
    
    def __init__(self, project_id: str, location: str = "us-central1"):
        self.project_id = project_id
        self.location = location
        # Initialize Google Cloud AI Platform
        aiplatform.init(project=project_id, location=location)
    
    def deploy_agent(self, config_file: str) -> str:
        """Deploy agent configuration to Google Cloud"""
        
        # 1. Load configuration from YAML
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        # 2. Setup Agent object
        agent = aiplatform.Agent(
            display_name=config["displayName"],
            description=config["description"]
        )
        
        # 3. Configure system prompt
        agent.system_prompt = config["agentBehavior"]["systemPrompt"]
        
        # 4. Deploy the agent
        print(f"🚀 Deploying agent: {config['displayName']}...")
        deployed_agent = agent.deploy()
        
        print(f"✅ Agent deployed successfully: {deployed_agent.resource_name}")
        return deployed_agent.resource_name

# Execution Block
if __name__ == "__main__":
    # Ensure environment variables are set
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        print("❌ Error: GCP_PROJECT_ID environment variable not set.")
    else:
        deployer = AgentBuilderDeployer(project_id=project_id)
        # Deploy using the config file in the same src directory
        agent_path = deployer.deploy_agent("src/agent_builder_config.yaml")