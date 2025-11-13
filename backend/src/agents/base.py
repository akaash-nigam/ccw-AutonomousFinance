"""Base agent class for autonomous financial operations."""
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable
from uuid import uuid4

import structlog
from anthropic import Anthropic
from pydantic import BaseModel, Field

from src.core.config import settings

logger = structlog.get_logger()


class AgentContext(BaseModel):
    """Context for agent execution."""

    agent_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_name: str
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    user_id: str | None = None
    entity_id: str | None = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReasoningStep(BaseModel):
    """A single step in the agent's reasoning chain."""

    step_number: int
    action: str
    observation: str
    reasoning: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentDecision(BaseModel):
    """Final decision made by the agent."""

    decision: str
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_chain: list[ReasoningStep]
    supporting_data: dict[str, Any] = Field(default_factory=dict)
    suggested_action: str | None = None
    requires_approval: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Tool(BaseModel):
    """Tool that can be used by the agent."""

    name: str
    description: str
    parameters: dict[str, Any]
    function: Callable


class BaseAgent(ABC):
    """
    Base class for all AI agents in the Autonomous Finance system.

    Agents are autonomous entities that:
    - Reason through complex financial scenarios
    - Use tools to interact with external systems (ERP, databases, APIs)
    - Maintain context across multi-step workflows
    - Generate audit-grade reasoning chains for every decision
    """

    def __init__(self, name: str, description: str) -> None:
        """
        Initialize the agent.

        Args:
            name: Agent name (e.g., "P2P Agent", "Reconciliation Agent")
            description: Agent's purpose and capabilities
        """
        self.name = name
        self.description = description
        self.tools: dict[str, Tool] = {}
        self.client = Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model
        self.logger = logger.bind(agent=name)

    def register_tool(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        function: Callable,
    ) -> None:
        """
        Register a tool that the agent can use.

        Args:
            name: Tool name
            description: What the tool does
            parameters: Tool parameter schema (JSON schema format)
            function: Callable function to execute the tool
        """
        self.tools[name] = Tool(
            name=name,
            description=description,
            parameters=parameters,
            function=function,
        )
        self.logger.info("tool_registered", tool_name=name)

    def _format_tools_for_claude(self) -> list[dict[str, Any]]:
        """Format tools for Claude's function calling API."""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.parameters,
            }
            for tool in self.tools.values()
        ]

    async def _execute_tool(self, tool_name: str, tool_input: dict[str, Any]) -> Any:
        """
        Execute a tool and return the result.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool not found
        """
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")

        tool = self.tools[tool_name]
        self.logger.info("executing_tool", tool_name=tool_name, input=tool_input)

        try:
            result = await tool.function(**tool_input)
            self.logger.info("tool_executed_successfully", tool_name=tool_name)
            return result
        except Exception as e:
            self.logger.error("tool_execution_failed", tool_name=tool_name, error=str(e))
            raise

    async def reason(
        self,
        task: str,
        context: AgentContext,
        max_steps: int = 10,
    ) -> AgentDecision:
        """
        Execute reasoning loop with tool use.

        The agent will:
        1. Analyze the task
        2. Plan multi-step approach
        3. Use tools to gather information
        4. Make a final decision with confidence score
        5. Generate audit trail with reasoning chain

        Args:
            task: The task to accomplish (e.g., "Match this invoice to a PO")
            context: Execution context (session, user, entity, metadata)
            max_steps: Maximum reasoning steps before forcing a decision

        Returns:
            AgentDecision with reasoning chain and suggested action
        """
        self.logger.info("starting_reasoning", task=task, context=context.model_dump())

        reasoning_chain: list[ReasoningStep] = []
        messages = [
            {
                "role": "user",
                "content": self._build_system_prompt(task, context),
            }
        ]

        for step in range(1, max_steps + 1):
            self.logger.debug("reasoning_step", step=step)

            # Call Claude with tool use
            response = self.client.messages.create(
                model=self.model,
                max_tokens=settings.anthropic_max_tokens,
                temperature=settings.anthropic_temperature,
                tools=self._format_tools_for_claude() if self.tools else None,
                messages=messages,
            )

            # Process response
            if response.stop_reason == "end_turn":
                # Agent finished reasoning
                final_text = self._extract_text_from_response(response)
                reasoning_chain.append(
                    ReasoningStep(
                        step_number=step,
                        action="final_decision",
                        observation=final_text,
                        reasoning="Agent reached final decision",
                    )
                )
                break

            elif response.stop_reason == "tool_use":
                # Agent wants to use tools
                tool_uses = [block for block in response.content if block.type == "tool_use"]

                for tool_use in tool_uses:
                    tool_name = tool_use.name
                    tool_input = tool_use.input

                    # Execute tool
                    tool_result = await self._execute_tool(tool_name, tool_input)

                    # Record reasoning step
                    reasoning_chain.append(
                        ReasoningStep(
                            step_number=step,
                            action=f"use_tool:{tool_name}",
                            observation=json.dumps(tool_result, default=str),
                            reasoning=f"Using {tool_name} to gather information",
                        )
                    )

                    # Add tool result to conversation
                    messages.append({"role": "assistant", "content": response.content})
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_use.id,
                                    "content": json.dumps(tool_result, default=str),
                                }
                            ],
                        }
                    )

            else:
                # Unexpected stop reason
                self.logger.warning("unexpected_stop_reason", stop_reason=response.stop_reason)
                break

        # Parse final decision from reasoning chain
        decision = await self._extract_decision(reasoning_chain, context)

        self.logger.info(
            "reasoning_completed",
            decision=decision.decision,
            confidence=decision.confidence,
            steps=len(reasoning_chain),
        )

        return decision

    def _build_system_prompt(self, task: str, context: AgentContext) -> str:
        """
        Build system prompt with task and context.

        Args:
            task: The task to accomplish
            context: Execution context

        Returns:
            Formatted system prompt
        """
        return f"""You are {self.name}, an AI agent for autonomous financial operations.

**Your Role**: {self.description}

**Task**: {task}

**Context**:
- Session ID: {context.session_id}
- Entity ID: {context.entity_id}
- User ID: {context.user_id}
- Metadata: {json.dumps(context.metadata, indent=2)}

**Instructions**:
1. Analyze the task carefully
2. Use available tools to gather information
3. Reason through the problem step-by-step
4. Make a final decision with confidence score (0.0 to 1.0)
5. Provide clear reasoning for every step
6. If confidence < 0.7, suggest escalation to human review

**Available Tools**: {', '.join(self.tools.keys()) if self.tools else 'None'}

Think carefully and provide audit-grade reasoning for compliance.
"""

    def _extract_text_from_response(self, response: Any) -> str:
        """Extract text content from Claude response."""
        text_blocks = [block.text for block in response.content if hasattr(block, "text")]
        return "\n".join(text_blocks)

    @abstractmethod
    async def _extract_decision(
        self,
        reasoning_chain: list[ReasoningStep],
        context: AgentContext,
    ) -> AgentDecision:
        """
        Extract final decision from reasoning chain.

        This method must be implemented by each agent subclass to parse
        the reasoning chain and create a structured decision.

        Args:
            reasoning_chain: List of reasoning steps
            context: Execution context

        Returns:
            AgentDecision with decision, confidence, and suggested action
        """
        pass

    @abstractmethod
    async def execute(self, task: str, context: AgentContext) -> AgentDecision:
        """
        Execute the agent's primary task.

        This is the main entry point for the agent. Each agent subclass
        must implement this method to define its specific behavior.

        Args:
            task: The task to accomplish
            context: Execution context

        Returns:
            AgentDecision with final decision and reasoning
        """
        pass
