"""
Artifact Critic - Example Usage

This demonstrates how to use the Artifact Critic tool programmatically.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from artifact_critic import ArtifactCriticTool
from config import Config


def example_1_simple_review():
    """Example 1: Simple artifact review."""
    print("=" * 80)
    print("EXAMPLE 1: Simple Artifact Review")
    print("=" * 80)
    
    try:
        # Initialize the tool
        config = Config()
        config.validate()
        
        tool = ArtifactCriticTool()
        
        # Review a sample artifact
        artifact_path = Path(__file__).parent / "artifacts" / "sample_resume.txt"
        
        print(f"\nReviewing: {artifact_path.name}")
        print(f"Rubric: resume_v1")
        
        result = tool.review_artifact(
            file_path=str(artifact_path),
            rubric_id="resume_v1",
            task_goal="Software engineer role at a tech company",
            audience="Technical recruiters and hiring managers",
            constraints="One page only"
        )
        
        print("\n" + "─" * 80)
        print("RESULTS")
        print("─" * 80)
        print(f"Overall Score: {result.overall_score}/100")
        
        print("\nSummary:")
        for i, point in enumerate(result.summary, 1):
            print(f"  {i}. {point}")
        
        print(f"\nFindings: {len(result.findings)} total")
        print(f"  • Must fix: {len(result.must_fix)}")
        print(f"  • Nice to have: {len(result.nice_to_have)}")
        
        # Show top 3 findings
        print("\nTop Issues:")
        for finding in result.findings[:3]:
            print(f"  [{finding.severity.upper()}] {finding.category}")
            print(f"  └─ {finding.evidence[:80]}...")
        
        print("\nNext Actions:")
        for i, action in enumerate(result.next_actions, 1):
            print(f"  {i}. {action}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def example_2_list_rubrics():
    """Example 2: List available rubrics."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: List Available Rubrics")
    print("=" * 80)
    
    try:
        tool = ArtifactCriticTool()
        
        rubrics = tool.list_rubrics()
        
        print(f"\nFound {len(rubrics)} rubrics:\n")
        
        for rubric_info in rubrics:
            print(f"• {rubric_info['id']}")
            print(f"  Version: {rubric_info['version']}")
            print(f"  Description: {rubric_info['description']}")
            print(f"  Categories: {', '.join(rubric_info['categories'])}")
            print()
    
    except Exception as e:
        print(f"❌ Error: {e}")


def example_3_repair_loop():
    """Example 3: Review with repair loop (simulation)."""
    print("=" * 80)
    print("EXAMPLE 3: Repair Loop Workflow (Conceptual)")
    print("=" * 80)
    
    print("""
The repair loop workflow:

1. Review artifact with chosen rubric
2. Get structured findings with:
   - Evidence (what's wrong)
   - Location (where it is)
   - Recommendation (how to fix)
   - Suggested rewrite (exact replacement)

3. Agent uses findings to update artifact
   - For text: Apply rewrites directly
   - For images: Generate improvement instructions
   - For slides: Update specific slides

4. Re-review updated artifact
5. Repeat until:
   - Score reaches threshold (e.g., 85/100)
   - Max iterations reached (e.g., 3)
   - No more must-fix issues

Benefits:
✓ Automated quality improvement
✓ Consistent with rubric standards
✓ Actionable, specific feedback
✓ Measurable progress (score)
    """)


def example_4_custom_rubric():
    """Example 4: Understanding rubric customization."""
    print("=" * 80)
    print("EXAMPLE 4: Custom Rubric Structure")
    print("=" * 80)
    
    print("""
To create a custom rubric, add a YAML file to rubrics/:

rubric_id: "my_rubric_v1"
version: "1.0"
description: "Reviews for X artifacts"

categories:
  - name: "Clarity"
    weight: 40  # Out of 100
    criteria:
      - "Information is organized logically"
      - "Technical terms are explained"
  
  - name: "Completeness"
    weight: 35
    criteria:
      - "All required sections present"
      - "No missing context"
  
  - name: "Design"
    weight: 25
    criteria:
      - "Visual hierarchy is clear"
      - "Formatting is consistent"

severity_mapping:
  blocker: "Prevents artifact from serving its purpose"
  high: "Significantly impacts quality"
  medium: "Noticeable but not critical"
  low: "Minor polish issue"

common_findings:
  - id: "missing_context"
    severity: "high"
    category: "Completeness"
    evidence_pattern: "Section X lacks background"
    recommendation: "Add context explaining..."

Then use: tool.review_artifact(..., rubric_id="my_rubric_v1")
    """)


def main():
    """Run all examples."""
    print("\n")
    print("█" * 80)
    print("ARTIFACT CRITIC - DEMONSTRATION")
    print("█" * 80)
    
    example_2_list_rubrics()
    
    print("\n")
    input("Press Enter to continue to Example 1 (artifact review)...")
    
    example_1_simple_review()
    
    print("\n")
    input("Press Enter to continue to Example 3 (repair loop)...")
    
    example_3_repair_loop()
    
    print("\n")
    input("Press Enter to continue to Example 4 (custom rubrics)...")
    
    example_4_custom_rubric()
    
    print("\n" + "█" * 80)
    print("DEMONSTRATION COMPLETE")
    print("█" * 80)
    print("\nNext steps:")
    print("  1. Run: python artifact_critic.py review <file> --rubric <id>")
    print("  2. Try: python artifact_critic.py repair-loop <file> --rubric <id>")
    print("  3. Create your own rubric in rubrics/")


if __name__ == "__main__":
    main()
