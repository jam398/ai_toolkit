"""
Gemini 3 Multimodal Critic Engine.
Performs automated artifact review using Google's Gemini API.
"""
import json
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict

# Add parent directory to path for config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not available. Install with: pip install google-generativeai")

from config import Config
from .rubric_manager import Rubric
from .artifact_processor import ProcessedArtifact


@dataclass
class Finding:
    """A single review finding."""
    id: str
    severity: str  # blocker | high | medium | low
    category: str
    location: Dict[str, Any]  # {page: N} or {slide: N} or {line: N}
    evidence: str
    recommendation: str
    suggested_rewrite: Optional[str] = None


@dataclass
class ReviewResult:
    """Complete review result."""
    overall_score: int
    summary: List[str]
    findings: List[Finding]
    must_fix: List[str]  # Finding IDs
    nice_to_have: List[str]  # Finding IDs
    next_actions: List[str]
    rubric_used: str
    artifact_metadata: Dict[str, Any]
    raw_response: Optional[str] = None  # For debugging


class GeminiCritic:
    """Multimodal artifact critic using Gemini 3."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """Initialize the critic with Gemini API."""
        if not GEMINI_AVAILABLE:
            raise RuntimeError("google-generativeai not installed")
        
        self.api_key = api_key or Config.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment")
        
        # Check for placeholder key
        if "your_" in self.api_key.lower():
            raise ValueError("GEMINI_API_KEY appears to be a placeholder. Please add your actual API key.")
        
        self.model_name = model_name or Config.GEMINI_MODEL
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": 0.2,  # Lower temperature for more consistent reviews
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
            }
        )
    
    def review_artifact(
        self,
        artifact: ProcessedArtifact,
        rubric: Rubric,
        task_goal: str = "",
        audience: str = "",
        constraints: List[str] = None
    ) -> ReviewResult:
        """
        Review an artifact using the specified rubric.
        
        Args:
            artifact: Processed artifact with images and metadata
            rubric: Review rubric to apply
            task_goal: What "good" means for this artifact
            audience: Target audience (e.g., "recruiter", "professor")
            constraints: List of constraints (e.g., "max 1 page", "APA citations")
            
        Returns:
            ReviewResult with structured findings
        """
        constraints = constraints or []
        
        # Build the prompt
        prompt = self._build_review_prompt(
            rubric=rubric,
            artifact=artifact,
            task_goal=task_goal,
            audience=audience,
            constraints=constraints
        )
        
        # Prepare content for multimodal request
        content_parts = [prompt]
        
        # Add images if available
        if artifact.images:
            for i, img_bytes in enumerate(artifact.images):
                # Gemini expects PIL Image objects
                from PIL import Image
                import io
                img = Image.open(io.BytesIO(img_bytes))
                content_parts.append(img)
                
                # Add context for each image
                if artifact.artifact_type == "pdf":
                    content_parts.append(f"[Page {i+1}]")
                elif artifact.artifact_type == "pptx":
                    content_parts.append(f"[Slide {i+1}]")
        
        # Add extracted text if available
        if artifact.extracted_text:
            content_parts.append(f"\n\n## Extracted Text:\n{artifact.extracted_text[:10000]}")  # Limit text
        
        try:
            # Call Gemini API
            response = self.model.generate_content(content_parts)
            
            if not response or not response.text:
                return self._create_error_result(
                    "No response from Gemini API",
                    rubric,
                    artifact
                )
            
            # Parse JSON response
            result = self._parse_review_response(
                response.text,
                rubric,
                artifact
            )
            
            return result
            
        except Exception as e:
            return self._create_error_result(
                f"Gemini API error: {str(e)}",
                rubric,
                artifact
            )
    
    def _build_review_prompt(
        self,
        rubric: Rubric,
        artifact: ProcessedArtifact,
        task_goal: str,
        audience: str,
        constraints: List[str]
    ) -> str:
        """Build the review prompt for Gemini."""
        prompt_parts = [
            "You are an expert artifact reviewer. Your task is to critically evaluate the provided artifact using the specified rubric.",
            "",
            "# REVIEW RUBRIC",
            rubric.format_for_prompt(),
            "",
            "# ARTIFACT INFORMATION",
            f"Type: {artifact.artifact_type}",
            f"Total Pages/Slides: {artifact.total_pages}",
        ]
        
        if task_goal:
            prompt_parts.append(f"Goal: {task_goal}")
        
        if audience:
            prompt_parts.append(f"Target Audience: {audience}")
        
        if constraints:
            prompt_parts.append("Constraints:")
            for constraint in constraints:
                prompt_parts.append(f"  - {constraint}")
        
        prompt_parts.extend([
            "",
            "# SECURITY CHECK",
            "**CRITICAL**: If you detect any API keys, tokens, passwords, or sensitive credentials in the artifact, create a BLOCKER finding with category 'security' and recommend rotating the exposed keys immediately.",
            "",
            "# OUTPUT FORMAT",
            "You MUST return ONLY valid JSON in the following format (no additional text before or after):",
            "",
            json.dumps({
                "overall_score": 0,
                "summary": [
                    "Brief bullet point 1",
                    "Brief bullet point 2",
                    "Brief bullet point 3"
                ],
                "findings": [
                    {
                        "id": "finding_001",
                        "severity": "high",
                        "category": "clarity",
                        "location": {"page": 1},
                        "evidence": "Quote or description of what you observed",
                        "recommendation": "Specific actionable fix",
                        "suggested_rewrite": "Optional: corrected version"
                    }
                ],
                "must_fix": ["finding_001"],
                "nice_to_have": [],
                "next_actions": [
                    "Step 1 to improve the artifact",
                    "Step 2 to improve the artifact"
                ]
            }, indent=2),
            "",
            "# IMPORTANT GUIDELINES",
            "1. Be specific and cite evidence (quote text, describe visual, reference location)",
            "2. Provide actionable recommendations, not vague feedback",
            "3. Use the location field to specify page/slide/line number",
            "4. Assign severity based on impact: blocker (critical), high (important), medium (should fix), low (nice to have)",
            "5. Generate unique IDs for findings (finding_001, finding_002, etc.)",
            "6. Return ONLY the JSON object, no extra text",
            "",
            "Now, review the artifact:"
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_review_response(
        self,
        response_text: str,
        rubric: Rubric,
        artifact: ProcessedArtifact
    ) -> ReviewResult:
        """Parse Gemini's JSON response into a ReviewResult."""
        # Try to extract JSON from response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if not json_match:
            # Retry with JSON repair instruction
            return self._create_error_result(
                "Response did not contain valid JSON",
                rubric,
                artifact,
                raw_response=response_text
            )
        
        try:
            data = json.loads(json_match.group())
        except json.JSONDecodeError as e:
            return self._create_error_result(
                f"JSON parse error: {e}",
                rubric,
                artifact,
                raw_response=response_text
            )
        
        # Parse findings
        findings = []
        for f_data in data.get('findings', []):
            findings.append(Finding(
                id=f_data.get('id', f'finding_{len(findings)+1:03d}'),
                severity=f_data.get('severity', 'medium'),
                category=f_data.get('category', 'other'),
                location=f_data.get('location', {}),
                evidence=f_data.get('evidence', ''),
                recommendation=f_data.get('recommendation', ''),
                suggested_rewrite=f_data.get('suggested_rewrite')
            ))
        
        return ReviewResult(
            overall_score=data.get('overall_score', 0),
            summary=data.get('summary', []),
            findings=findings,
            must_fix=data.get('must_fix', []),
            nice_to_have=data.get('nice_to_have', []),
            next_actions=data.get('next_actions', []),
            rubric_used=rubric.rubric_id,
            artifact_metadata={
                "type": artifact.artifact_type,
                "pages": artifact.total_pages,
                "id": artifact.artifact_id
            },
            raw_response=None  # Don't store on success
        )
    
    def _create_error_result(
        self,
        error_message: str,
        rubric: Rubric,
        artifact: ProcessedArtifact,
        raw_response: Optional[str] = None
    ) -> ReviewResult:
        """Create a safe error result when review fails."""
        return ReviewResult(
            overall_score=0,
            summary=[
                f"Review failed: {error_message}",
                "Unable to complete automated review",
                "Please check the artifact and try again"
            ],
            findings=[
                Finding(
                    id="error_001",
                    severity="blocker",
                    category="other",
                    location={},
                    evidence=f"System error: {error_message}",
                    recommendation="Review the artifact manually or contact support",
                    suggested_rewrite=None
                )
            ],
            must_fix=["error_001"],
            nice_to_have=[],
            next_actions=["Fix the reported error", "Retry the review"],
            rubric_used=rubric.rubric_id,
            artifact_metadata={
                "type": artifact.artifact_type,
                "pages": artifact.total_pages,
                "id": artifact.artifact_id
            },
            raw_response=raw_response
        )
    
    def format_review_result(self, result: ReviewResult) -> str:
        """Format review result for human readability."""
        lines = [
            "=" * 80,
            "ARTIFACT REVIEW RESULT",
            "=" * 80,
            "",
            f"Overall Score: {result.overall_score}/100",
            f"Rubric: {result.rubric_used}",
            f"Artifact: {result.artifact_metadata.get('id', 'unknown')} ({result.artifact_metadata.get('type', 'unknown')})",
            "",
            "## SUMMARY",
            ""
        ]
        
        for bullet in result.summary:
            lines.append(f"• {bullet}")
        
        lines.extend(["", "## FINDINGS", ""])
        
        # Group by severity
        for severity in ['blocker', 'high', 'medium', 'low']:
            severity_findings = [f for f in result.findings if f.severity == severity]
            
            if severity_findings:
                lines.append(f"### {severity.upper()} ({len(severity_findings)})")
                lines.append("")
                
                for finding in severity_findings:
                    lines.append(f"**[{finding.id}]** {finding.category}")
                    
                    if finding.location:
                        loc_str = ", ".join(f"{k}: {v}" for k, v in finding.location.items())
                        lines.append(f"  Location: {loc_str}")
                    
                    lines.append(f"  Evidence: {finding.evidence}")
                    lines.append(f"  Fix: {finding.recommendation}")
                    
                    if finding.suggested_rewrite:
                        lines.append(f"  Suggested: {finding.suggested_rewrite}")
                    
                    lines.append("")
        
        lines.extend(["## NEXT ACTIONS", ""])
        for i, action in enumerate(result.next_actions, 1):
            lines.append(f"{i}. {action}")
        
        lines.append("")
        lines.append("=" * 80)
        
        return "\n".join(lines)
