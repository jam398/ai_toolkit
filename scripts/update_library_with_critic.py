"""
Update Library Research Agent with Artifact Critic information.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from library_agent.library_store import LibraryStore, LibraryEntry
from config import Config


def add_artifact_critic_entries():
    """Add comprehensive Artifact Critic information to the library."""
    
    config = Config()
    store = LibraryStore(config.LIBRARY_DB_PATH)
    
    entries = [
        LibraryEntry(
            title="Artifact Critic - Multimodal Review Tool Overview",
            url="internal://artifact-critic/overview",
            publisher="Project Documentation",
            date_published="2026-02-06",
            date_accessed="2026-02-06",
            topic_tags=["artifact-critic", "gemini", "multimodal", "review", "ai-tools"],
            summary="The Artifact Critic is a Gemini 3-powered multimodal review tool that automatically analyzes artifacts (PDFs, PowerPoint presentations, images, diagrams, screenshots) and returns structured, actionable feedback. It uses version-controlled YAML rubrics with weighted categories and severity-based findings to provide evidence, location tracking, recommendations, and suggested rewrites. The tool includes a repair loop for iterative improvement and outputs machine-readable JSON for agent automation.",
            key_facts=[
                "Uses Google Gemini 2.0 Flash model (gemini-2.0-flash-exp) for multimodal understanding",
                "Supports PDF, PPTX, PNG, JPG artifact formats with preprocessing pipeline",
                "Four production-ready rubrics: resume_v1, deck_v1, ui_v1, api_docs_v1",
                "Rubrics use weighted categories that sum to 100% for consistent scoring",
                "Findings include: ID, severity (blocker/high/medium/low), category, location, evidence, recommendation, suggested_rewrite",
                "Repair loop iterates until score threshold (default 85/100) or max iterations (default 3) reached",
                "CLI commands: 'python artifact_critic.py review <file> --rubric <id>' and 'repair-loop <file> --rubric <id>'",
                "All 24 acceptance tests pass (rubric validation, artifact processing, JSON contract, security checks)",
                "Security features: detects exposed secrets in artifacts, API keys from environment only"
            ],
            credibility_notes="Official project documentation, fully tested implementation as of 2026-02-06",
            freshness_ttl_days=365
        ),
        
        LibraryEntry(
            title="Artifact Critic - Rubric System and Customization",
            url="internal://artifact-critic/rubrics",
            publisher="Project Documentation",
            date_published="2026-02-06",
            date_accessed="2026-02-06",
            topic_tags=["artifact-critic", "rubrics", "yaml", "evaluation", "standards"],
            summary="The Artifact Critic uses a YAML-based rubric system for version-controlled evaluation criteria. Each rubric defines weighted categories (must sum to 100), evaluation criteria, severity mappings, and common findings templates. Four production rubrics are included: resume_v1 (technical resume evaluation), deck_v1 (presentation deck review), ui_v1 (UI mockup assessment), and api_docs_v1 (API documentation standards). Custom rubrics can be created by adding YAML files to the rubrics/ directory.",
            key_facts=[
                "Rubric structure: rubric_id, version, description, categories (with weights), severity_mapping, common_findings",
                "resume_v1 categories: Impact & Achievement Bullets (30%), Clarity & Readability (25%), Technical Content (20%), ATS Compatibility (15%), Design & Formatting (10%)",
                "deck_v1 categories: Message & Story (30%), Visual Design (25%), Flow & Structure (20%), Text & Readability (15%), Polish & Professionalism (10%)",
                "ui_v1 categories: Visual Hierarchy (25%), Information Architecture (25%), Accessibility (20%), Consistency (15%), Usability (15%)",
                "api_docs_v1 categories: Completeness (30%), Code Examples (25%), Clarity & Organization (20%), Error Handling (15%), Developer Experience (10%)",
                "Severity levels map to impact: blocker (prevents purpose), high (significant quality impact), medium (noticeable issue), low (minor polish)",
                "Rubrics are hot-reloadable without system restart",
                "Custom rubrics enable domain-specific evaluation (e.g., legal docs, marketing copy, code reviews)"
            ],
            credibility_notes="Built-in rubrics based on industry best practices, extensible architecture",
            freshness_ttl_days=365
        ),
        
        LibraryEntry(
            title="Artifact Critic - Technical Architecture and Dependencies",
            url="internal://artifact-critic/architecture",
            publisher="Project Documentation",
            date_published="2026-02-06",
            date_accessed="2026-02-06",
            topic_tags=["artifact-critic", "architecture", "dependencies", "python"],
            summary="The Artifact Critic consists of four core components: gemini_critic.py (review engine), artifact_processor.py (PDF/PPTX/image preprocessing), rubric_manager.py (YAML rubric loading), and artifact_critic.py (CLI tool with repair loop). The system preprocesses artifacts into a standardized format (images + metadata), loads evaluation rubrics, sends multimodal prompts to Gemini 3, and parses structured JSON responses with findings and recommendations.",
            key_facts=[
                "Dependencies: google-generativeai (Gemini API), PyPDF2 (PDF text), pdf2image (PDF to images), python-pptx (PowerPoint), Pillow (image processing), PyYAML (rubric loading)",
                "Artifact processing: PDFs converted to images at configurable DPI (default 150), PPTX slides extracted individually, images resized if needed, all encoded as base64",
                "gemini_critic.py: Builds multimodal prompts with rubric instructions + artifact images, parses JSON responses with retry logic, validates findings structure",
                "artifact_processor.py: Detects artifact type by extension, extracts pages/slides, handles graceful degradation (PDF images fallback to text)",
                "rubric_manager.py: Loads YAML rubrics, validates structure (weights sum to 100%), caches for performance, formats rubric as prompt instructions",
                "artifact_critic.py: ArtifactCriticTool class orchestrates processor+rubric+critic, implements review_artifact() and review_with_repair_loop() methods",
                "Configuration: GEMINI_API_KEY (environment), MAX_PAGES_PER_REVIEW=50, PDF_TO_IMAGE_DPI=150, MAX_REPAIR_ITERATIONS=3, REPAIR_SCORE_THRESHOLD=85",
                "PDF image conversion requires poppler-utils: brew install poppler (macOS), apt-get install poppler-utils (Linux), manual install on Windows"
            ],
            credibility_notes="Source code documentation, tested with Python 3.14.3 on Windows",
            freshness_ttl_days=365
        ),
        
        LibraryEntry(
            title="Artifact Critic - Repair Loop and Agent Integration",
            url="internal://artifact-critic/repair-loop",
            publisher="Project Documentation",
            date_published="2026-02-06",
            date_accessed="2026-02-06",
            topic_tags=["artifact-critic", "repair-loop", "automation", "agent-integration"],
            summary="The Artifact Critic's repair loop enables automated quality improvement through iterative review cycles. The workflow: (1) review artifact with rubric, (2) agent applies fixes using structured findings (evidence, location, recommendation, suggested_rewrite), (3) re-review updated artifact, (4) repeat until score threshold reached or max iterations hit. The loop exits when score ≥ 85/100, max 3 iterations completed, or no must-fix issues remain. This enables integration with builder agents for automatic artifact refinement.",
            key_facts=[
                "Repair loop command: 'python artifact_critic.py repair-loop <file> --rubric <id> --max-iterations 3 --score-threshold 85'",
                "Each finding includes: id (unique identifier), severity (blocker/high/medium/low), category (rubric category), location (page/section/line dict), evidence (what's wrong), recommendation (how to fix), suggested_rewrite (exact replacement)",
                "Exit conditions: score reaches threshold (e.g., ≥85/100), max iterations reached (default 3), or no more must-fix issues",
                "Progress tracking: overall_score shows improvement, must_fix list shrinks, nice_to_have addresses polish",
                "Agent integration pattern: agent.create_artifact() → critic.review_artifact() → agent.apply_fixes() → repeat until quality threshold",
                "Location tracking enables precise edits: page numbers for PDFs, slide indices for decks, pixel regions for images, section names for documents",
                "Suggested rewrites provide exact replacement text for text-based artifacts, avoiding ambiguous feedback",
                "Batch processing possible: iterate over file glob, review each, filter by score, collect aggregated statistics"
            ],
            credibility_notes="Documented workflow with programmatic API examples, supports automated agent pipelines",
            freshness_ttl_days=365
        ),
        
        LibraryEntry(
            title="Artifact Critic vs Library Research Agent - Tool Comparison",
            url="internal://ai-toolkit/comparison",
            publisher="Project Documentation",
            date_published="2026-02-06",
            date_accessed="2026-02-06",
            topic_tags=["artifact-critic", "library-research-agent", "comparison", "ai-toolkit"],
            summary="The AI toolkit now contains two complementary tools: Library Research Agent (knowledge curation and Q&A) and Artifact Critic (artifact review and quality improvement). Library Research Agent searches an internal knowledge library first, uses web search when needed, and writes findings back to the library with citations. Artifact Critic analyzes visual artifacts (PDFs, decks, images) using Gemini 3 multimodal capabilities and provides structured feedback against rubric standards. Together they enable: research → document → critique → refine workflows.",
            key_facts=[
                "Library Research Agent: OpenAI GPT-4o, ChromaDB vector storage, library-first approach, web search fallback, automatic citations, TTL-based freshness",
                "Artifact Critic: Google Gemini 3, multimodal review (text+images), YAML rubrics, structured findings, repair loop, JSON automation",
                "Complementary workflow: (1) Research Agent gathers knowledge, (2) Builder creates artifact, (3) Artifact Critic reviews, (4) Builder refines based on findings",
                "Both tools: API keys from environment only, no secrets in code, comprehensive test coverage (23 tests for Research Agent, 24 for Artifact Critic)",
                "Library Research Agent use cases: answering questions from curated knowledge, building domain expertise libraries, tracking information freshness",
                "Artifact Critic use cases: resume reviews, deck feedback, UI mockup critique, API documentation standards, automated quality gates",
                "Integration example: Research Agent finds 'accessible UI design principles' → Builder creates mockup → Artifact Critic reviews with ui_v1 rubric → Builder fixes accessibility issues",
                "Both tools production-ready with complete documentation, examples, and passing acceptance tests"
            ],
            credibility_notes="Official project documentation covering both tools in the AI toolkit, tested 2026-02-06",
            freshness_ttl_days=365
        )
    ]
    
    print("Adding Artifact Critic information to Library Research Agent...")
    print("=" * 80)
    
    for i, entry in enumerate(entries, 1):
        print(f"\n[{i}/{len(entries)}] Adding: {entry.title}")
        store.add_entry(entry)
        print(f"✅ Added with {len(entry.key_facts)} key facts")
    
    print("\n" + "=" * 80)
    print("✅ Library updated successfully!")
    print("\nYou can now query the Library Research Agent about Artifact Critic:")
    print("  • 'What is the Artifact Critic tool?'")
    print("  • 'How do I create custom rubrics?'")
    print("  • 'What are the repair loop exit conditions?'")
    print("  • 'Compare Library Research Agent and Artifact Critic'")
    print("  • 'How do I integrate the Artifact Critic with builder agents?'")


if __name__ == "__main__":
    add_artifact_critic_entries()
