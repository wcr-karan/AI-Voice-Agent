"""
Pydantic models for Retell AI webhook event payloads.
"""

from pydantic import BaseModel, Field
from typing import Optional


class CallAnalysis(BaseModel):
    """Post-call analysis data from Retell."""
    call_summary: str = Field(default="", description="AI-generated call summary")
    user_sentiment: str = Field(default="", description="Detected caller sentiment")
    custom_analysis_data: dict = Field(default_factory=dict, description="Custom analysis fields")


class CallObject(BaseModel):
    """
    The call object included in webhook payloads.
    Contains all metadata about the call.
    """
    call_id: str = Field(..., description="Unique call identifier")
    call_type: str = Field(default="phone_call", description="Call type: phone_call | web_call")
    from_number: str = Field(default="", description="Caller phone number")
    to_number: str = Field(default="", description="Receiving phone number")
    direction: str = Field(default="inbound", description="Call direction: inbound | outbound")
    agent_id: str = Field(default="", description="Retell agent ID")
    start_timestamp: Optional[int] = Field(default=None, description="Call start time (epoch ms)")
    end_timestamp: Optional[int] = Field(default=None, description="Call end time (epoch ms)")
    duration_ms: Optional[int] = Field(default=None, description="Call duration in milliseconds")
    status: str = Field(default="", description="Call status")
    disconnection_reason: str = Field(default="", description="Why the call ended")

    # Dynamic variables extracted during conversation
    retell_llm_dynamic_variables: dict = Field(
        default_factory=dict,
        description="Variables extracted by the conversation flow (name, email, etc.)"
    )

    # Post-call analysis (only present in call_analyzed events)
    call_analysis: Optional[CallAnalysis] = Field(default=None, description="Post-call analysis data")

    # Additional metadata
    metadata: dict = Field(default_factory=dict, description="Custom metadata attached to the call")

    @property
    def duration_seconds(self) -> int:
        """Call duration in seconds."""
        if self.duration_ms:
            return self.duration_ms // 1000
        if self.start_timestamp and self.end_timestamp:
            return (self.end_timestamp - self.start_timestamp) // 1000
        return 0


class WebhookEvent(BaseModel):
    """
    Top-level webhook event payload from Retell AI.

    Retell sends POST requests with this structure for events:
    - call_started
    - call_ended
    - call_analyzed
    """
    event: str = Field(..., description="Event type: call_started | call_ended | call_analyzed")
    call: CallObject = Field(..., description="Call data object")
