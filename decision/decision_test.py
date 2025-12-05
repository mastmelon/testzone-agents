import json
import yaml
import asyncio

from decision.decision import Decision
from mcp_servers.multiMCP import MultiMCP


async def test_decision():
    with open("config/mcp_server_config.yaml", 'r') as f:
        mcp_server_config = yaml.safe_load(f)
        mcp_servers_config_dict = mcp_server_config.get("mcp_servers", [])

    multi_mcp = MultiMCP(mcp_server_configs=mcp_servers_config_dict)
    await multi_mcp.initialize()

    decision = Decision(decision_prompt_path="prompts/decision_prompt.txt", multi_mcp=multi_mcp)
    result = decision.run(
        decision_input={
            "plan_mode": "initial",
            "planning_strategy": "conservative",
            "original_query": "Find number of BHK variants available in DLF Camelia from local sources.",
            "perception": {
                "entities": ["DLF Camelia", "BHK variants", "local sources"],
                "result_requirement": "Numerical count of distinct BHK configurations...",
                "original_goal_achieved": False,
                "reasoning": "The user wants...",
                "local_goal_achieved": False,
                "local_reasoning": "This is just perception, no data retrieved yet."
            }
        }
    )
    print(json.dumps(result, indent=2))
    print(result)


if __name__ == "__main__":
    asyncio.run(test_decision())
