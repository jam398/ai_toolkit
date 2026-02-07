"""
Artifact Critic - Main CLI tool.
Automated multimodal artifact review using Gemini 3.
"""
import sys
import argparse
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add parent directory to path for config
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import Config
from .rubric_manager import RubricManager
from .artifact_processor import ArtifactProcessor
from .gemini_critic import GeminiCritic, ReviewResult


class ArtifactCriticTool:
    """Main tool for artifact review."""
    
    def __init__(self):
        self.rubric_manager = RubricManager()
        self.processor = ArtifactProcessor(
            temp_dir=Config.ARTIFACT_TEMP_DIR,
            max_pages=Config.MAX_PAGES_PER_REVIEW
        )
        self.critic = None  # Will be initialized when needed
    
    def _init_critic(self):
        """Initialize Gemini critic (lazy loading)."""
        if self.critic is None:
            try:
                self.critic = GeminiCritic()
            except Exception as e:
                print(f"Error initializing Gemini critic: {e}")
                sys.exit(1)
    
    def review_artifact(
        self,
        file_path: str,
        rubric_id: str,
        task_goal: str = "",
        audience: str = "",
        constraints: List[str] = None,
        high_detail: bool = False,
        output_file: Optional[str] = None
    ) -> ReviewResult:
        """
        Review an artifact and return structured feedback.
        
        Args:
            file_path: Path to artifact file
            rubric_id: Rubric to use (e.g., 'resume_v1')
            task_goal: What "good" means for this artifact
            audience: Target audience
            constraints: List of constraints
            high_detail: Use high resolution mode
            output_file: Optional file to save JSON results
            
        Returns:
            ReviewResult object
        """
        print(f"Loading artifact: {file_path}")
        
        # Process artifact
        try:
            artifact = self.processor.process_artifact(
                file_path,
                high_detail=high_detail
            )
            print(f"✓ Processed {artifact.total_pages} pages/slides")
        except Exception as e:
            print(f"✗ Failed to process artifact: {e}")
            sys.exit(1)
        
        # Load rubric
        print(f"Loading rubric: {rubric_id}")
        try:
            rubric = self.rubric_manager.load_rubric(rubric_id)
            print(f"✓ Loaded rubric: {rubric.name}")
        except Exception as e:
            print(f"✗ Failed to load rubric: {e}")
            sys.exit(1)
        
        # Initialize critic
        self._init_critic()
        
        # Perform review
        print("\n⏳ Reviewing artifact with Gemini...")
        try:
            result = self.critic.review_artifact(
                artifact=artifact,
                rubric=rubric,
                task_goal=task_goal,
                audience=audience,
                constraints=constraints or []
            )
            print("✓ Review complete\n")
        except Exception as e:
            print(f"✗ Review failed: {e}")
            sys.exit(1)
        
        # Display results
        print(self.critic.format_review_result(result))
        
        # Save to file if requested
        if output_file:
            self._save_result(result, output_file)
        
        return result
    
    def review_with_repair_loop(
        self,
        file_path: str,
        rubric_id: str,
        max_iterations: int = None,
        score_threshold: int = None,
        **kwargs
    ) -> List[ReviewResult]:
        """
        Review artifact with repair loop.
        
        Note: Actual repair requires integration with builder agents.
        This shows the review iteration pattern.
        
        Args:
            file_path: Path to artifact
            rubric_id: Rubric to use
            max_iterations: Maximum repair iterations
            score_threshold: Target score to reach
            **kwargs: Additional review parameters
            
        Returns:
            List of ReviewResult objects (one per iteration)
        """
        max_iterations = max_iterations or Config.MAX_REPAIR_ITERATIONS
        score_threshold = score_threshold or Config.REPAIR_SCORE_THRESHOLD
        
        results = []
        current_file = file_path
        
        print("=" * 80)
        print("REPAIR LOOP MODE")
        print("=" * 80)
        print(f"Max iterations: {max_iterations}")
        print(f"Score threshold: {score_threshold}")
        print()
        
        for iteration in range(1, max_iterations + 1):
            print(f"\n{'=' * 80}")
            print(f"ITERATION {iteration}")
            print('=' * 80)
            
            # Review current version
            result = self.review_artifact(
                file_path=current_file,
                rubric_id=rubric_id,
                **kwargs
            )
            
            results.append(result)
            
            # Check if we should continue
            blockers = [f for f in result.findings if f.severity == 'blocker']
            high_priority = [f for f in result.findings if f.severity == 'high']
            
            print(f"\nIteration {iteration} Summary:")
            print(f"  Score: {result.overall_score}/{result.artifact_metadata.get('max_score', 100)}")
            print(f"  Blockers: {len(blockers)}")
            print(f"  High: {len(high_priority)}")
            
            # Stop conditions
            if result.overall_score >= score_threshold and len(blockers) == 0:
                print(f"\n✓ Target score reached ({result.overall_score} >= {score_threshold}) with no blockers!")
                break
            
            if len(blockers) == 0 and len(high_priority) == 0:
                print(f"\n✓ No critical issues remaining!")
                break
            
            if iteration < max_iterations:
                print(f"\n→ Issues remain. Would apply fixes and continue to iteration {iteration + 1}")
                print("   (Note: Actual repair requires builder agent integration)")
                # In production: apply fixes, generate new version, continue loop
                # For now, we just demonstrate the pattern
                break
            else:
                print(f"\n⚠ Max iterations ({max_iterations}) reached")
        
        return results
    
    def list_rubrics(self):
        """List all available rubrics."""
        rubrics = self.rubric_manager.list_available_rubrics()
        
        print("\n" + "=" * 80)
        print("AVAILABLE RUBRICS")
        print("=" * 80)
        
        if not rubrics:
            print("No rubrics found in rubrics/ directory")
            return
        
        for rubric in rubrics:
            print(f"\n• {rubric['id']}")
            print(f"  Name: {rubric['name']}")
            print(f"  Description: {rubric['description']}")
            print(f"  Version: {rubric['version']}")
    
    def _save_result(self, result: ReviewResult, output_file: str):
        """Save review result to JSON file."""
        import json
        from dataclasses import asdict
        
        output_path = Path(output_file)
        
        try:
            # Convert to dict
            data = {
                "overall_score": result.overall_score,
                "summary": result.summary,
                "findings": [asdict(f) for f in result.findings],
                "must_fix": result.must_fix,
                "nice_to_have": result.nice_to_have,
                "next_actions": result.next_actions,
                "rubric_used": result.rubric_used,
                "artifact_metadata": result.artifact_metadata
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"\n✓ Results saved to: {output_file}")
            
        except Exception as e:
            print(f"\n⚠ Failed to save results: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Artifact Critic - Automated multimodal review using Gemini 3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Review a resume
  python artifact_critic.py resume.pdf --rubric resume_v1
  
  # Review a slide deck with context
  python artifact_critic.py slides.pdf --rubric deck_v1 --goal "Pitch investors" --audience "VCs"
  
  # Review with repair loop
  python artifact_critic.py doc.pdf --rubric api_docs_v1 --repair-loop
  
  # List available rubrics
  python artifact_critic.py --list-rubrics
  
  # High detail mode for text-heavy artifacts
  python artifact_critic.py dense_doc.pdf --rubric resume_v1 --high-detail

Security:
  API keys must be in .env file. Never commit .env to version control.
        """
    )
    
    parser.add_argument(
        'artifact',
        nargs='?',
        help='Path to artifact file (PDF, PPTX, or image)'
    )
    
    parser.add_argument(
        '--rubric',
        type=str,
        help='Rubric ID to use (e.g., resume_v1, deck_v1, ui_v1)'
    )
    
    parser.add_argument(
        '--goal',
        type=str,
        default='',
        help='Task goal: what "good" means for this artifact'
    )
    
    parser.add_argument(
        '--audience',
        type=str,
        default='',
        help='Target audience (e.g., recruiter, professor, end users)'
    )
    
    parser.add_argument(
        '--constraints',
        type=str,
        nargs='+',
        help='Constraints (e.g., "max 1 page" "APA citations")'
    )
    
    parser.add_argument(
        '--high-detail',
        action='store_true',
        help='Use high resolution mode for text-heavy artifacts'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file for JSON results'
    )
    
    parser.add_argument(
        '--repair-loop',
        action='store_true',
        help='Enable repair loop (iterative review and fix)'
    )
    
    parser.add_argument(
        '--max-iterations',
        type=int,
        help=f'Max repair iterations (default: {Config.MAX_REPAIR_ITERATIONS})'
    )
    
    parser.add_argument(
        '--score-threshold',
        type=int,
        help=f'Target score for repair loop (default: {Config.REPAIR_SCORE_THRESHOLD})'
    )
    
    parser.add_argument(
        '--list-rubrics',
        action='store_true',
        help='List all available rubrics'
    )
    
    args = parser.parse_args()
    
    tool = ArtifactCriticTool()
    
    # Handle list rubrics
    if args.list_rubrics:
        tool.list_rubrics()
        return 0
    
    # Validate required arguments
    if not args.artifact:
        parser.error("artifact positional argument is required (use --list-rubrics to see available rubrics)")
    
    if not args.rubric:
        parser.error("--rubric is required")
    
    # Run review
    try:
        if args.repair_loop:
            tool.review_with_repair_loop(
                file_path=args.artifact,
                rubric_id=args.rubric,
                task_goal=args.goal,
                audience=args.audience,
                constraints=args.constraints,
                high_detail=args.high_detail,
                output_file=args.output,
                max_iterations=args.max_iterations,
                score_threshold=args.score_threshold
            )
        else:
            tool.review_artifact(
                file_path=args.artifact,
                rubric_id=args.rubric,
                task_goal=args.goal,
                audience=args.audience,
                constraints=args.constraints,
                high_detail=args.high_detail,
                output_file=args.output
            )
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
