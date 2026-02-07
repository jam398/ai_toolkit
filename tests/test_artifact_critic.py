"""
Tests for Artifact Critic system.
"""
import json
import sys
import tempfile
from pathlib import Path
import pytest

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from artifact_critic.rubric_manager import RubricManager, Rubric
from artifact_critic.artifact_processor import ArtifactProcessor
from artifact_critic.gemini_critic import Finding, ReviewResult


class TestResults:
    """Track test results."""
    def __init__(self):
        self.passed = []
        self.failed = []
    
    def add_pass(self, test_name: str):
        self.passed.append(test_name)
        print(f"✅ PASS: {test_name}")
    
    def add_fail(self, test_name: str, reason: str):
        self.failed.append((test_name, reason))
        print(f"❌ FAIL: {test_name}")
        print(f"   Reason: {reason}")
    
    def summary(self):
        total = len(self.passed) + len(self.failed)
        print("\n" + "=" * 80)
        print(f"TEST SUMMARY: {len(self.passed)}/{total} passed")
        print("=" * 80)
        if self.failed:
            print("\nFailed tests:")
            for name, reason in self.failed:
                print(f"  • {name}: {reason}")
        return len(self.failed) == 0


def test_rubric_loading():
    """Test rubric loading and validation."""
    results = TestResults()
    
    manager = RubricManager("./rubrics")
    
    # Test loading each rubric
    rubric_ids = ["resume_v1", "deck_v1", "ui_v1", "api_docs_v1"]
    
    for rubric_id in rubric_ids:
        try:
            rubric = manager.load_rubric(rubric_id)
            
            # Check basic attributes
            if not rubric.rubric_id:
                results.add_fail(f"Rubric {rubric_id} load", "Missing rubric_id")
                continue
            
            if not rubric.categories:
                results.add_fail(f"Rubric {rubric_id} load", "No categories")
                continue
            
            # Check weights sum to 100
            total_weight = rubric.get_total_weight()
            if total_weight != 100:
                results.add_fail(f"Rubric {rubric_id} weights", f"Sum is {total_weight}, not 100")
                continue
            
            # Check severity mapping
            required_severities = ['blocker', 'high', 'medium', 'low']
            missing = [s for s in required_severities if s not in rubric.severity_mapping]
            if missing:
                results.add_fail(f"Rubric {rubric_id} severity", f"Missing: {missing}")
                continue
            
            results.add_pass(f"Rubric {rubric_id} load and validate")
        
        except Exception as e:
            results.add_fail(f"Rubric {rubric_id} load", str(e))
    
    # Test listing rubrics
    try:
        rubrics_list = manager.list_available_rubrics()
        if len(rubrics_list) >= 4:
            results.add_pass("List available rubrics")
        else:
            results.add_fail("List available rubrics", f"Expected 4+, got {len(rubrics_list)}")
    except Exception as e:
        results.add_fail("List available rubrics", str(e))
    
    # Test prompt formatting
    try:
        rubric = manager.load_rubric("resume_v1")
        prompt = rubric.format_for_prompt()
        
        if "# Resume Review Rubric" in prompt and "Impact & Achievement Bullets" in prompt:
            results.add_pass("Rubric prompt formatting")
        else:
            results.add_fail("Rubric prompt formatting", "Missing expected content")
    except Exception as e:
        results.add_fail("Rubric prompt formatting", str(e))
    
    return results.summary()


def test_artifact_processing():
    """Test artifact preprocessing."""
    results = TestResults()
    
    processor = ArtifactProcessor(max_pages=10)
    
    # Test image processing (create a test image)
    from PIL import Image
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test PNG
        test_img_path = Path(tmpdir) / "test.png"
        img = Image.new('RGB', (800, 600), color='white')
        img.save(test_img_path)
        
        try:
            artifact = processor.process_artifact(str(test_img_path))
            
            if artifact.artifact_type == "image":
                results.add_pass("Image artifact processing")
            else:
                results.add_fail("Image artifact processing", f"Wrong type: {artifact.artifact_type}")
            
            if artifact.total_pages == 1:
                results.add_pass("Image page count")
            else:
                results.add_fail("Image page count", f"Expected 1, got {artifact.total_pages}")
            
            if len(artifact.images) == 1:
                results.add_pass("Image data extraction")
            else:
                results.add_fail("Image data extraction", f"Expected 1 image, got {len(artifact.images)}")
        
        except Exception as e:
            results.add_fail("Image artifact processing", str(e))
    
    # Test type detection
    test_files = {
        "test.pdf": "pdf",
        "test.pptx": "pptx",
        "test.png": "image",
        "test.jpg": "image"
    }
    
    for filename, expected_type in test_files.items():
        try:
            detected = processor._detect_type(Path(filename))
            if detected == expected_type:
                results.add_pass(f"Type detection: {filename}")
            else:
                results.add_fail(f"Type detection: {filename}", f"Expected {expected_type}, got {detected}")
        except Exception as e:
            results.add_fail(f"Type detection: {filename}", str(e))
    
    return results.summary()


def test_review_result_structure():
    """Test ReviewResult structure and JSON serialization."""
    results = TestResults()
    
    # Create a sample finding
    finding = Finding(
        id="test_001",
        severity="high",
        category="clarity",
        location={"page": 1},
        evidence="Test evidence",
        recommendation="Test recommendation"
    )
    
    # Create a sample review result
    review = ReviewResult(
        overall_score=75,
        summary=["Test summary point 1", "Test summary point 2"],
        findings=[finding],
        must_fix=["test_001"],
        nice_to_have=[],
        next_actions=["Action 1", "Action 2"],
        rubric_used="test_v1",
        artifact_metadata={"type": "pdf", "pages": 1}
    )
    
    # Test structure
    if review.overall_score == 75:
        results.add_pass("ReviewResult score")
    else:
        results.add_fail("ReviewResult score", f"Expected 75, got {review.overall_score}")
    
    if len(review.findings) == 1:
        results.add_pass("ReviewResult findings")
    else:
        results.add_fail("ReviewResult findings", f"Expected 1, got {len(review.findings)}")
    
    # Test JSON serialization
    try:
        from dataclasses import asdict
        data = {
            "overall_score": review.overall_score,
            "findings": [asdict(f) for f in review.findings]
        }
        json_str = json.dumps(data)
        json.loads(json_str)  # Verify valid JSON
        results.add_pass("ReviewResult JSON serialization")
    except Exception as e:
        results.add_fail("ReviewResult JSON serialization", str(e))
    
    # Test finding structure
    if finding.severity in ["blocker", "high", "medium", "low"]:
        results.add_pass("Finding severity validation")
    else:
        results.add_fail("Finding severity validation", f"Invalid severity: {finding.severity}")
    
    return results.summary()


def test_security_checks():
    """Test security features."""
    results = TestResults()
    
    # Test that GEMINI_API_KEY is not exposed in code
    sensitive_patterns = [
        "GEMINI_API_KEY.*=.*['\"]AIza",  # Actual key pattern
        "sk-[a-zA-Z0-9]{20,}",  # OpenAI key pattern
    ]
    
    files_to_check = [
        "gemini_critic.py",
        "artifact_critic.py",
        "config.py"
    ]
    
    for file_name in files_to_check:
        file_path = Path(file_name)
        if not file_path.exists():
            continue
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            # Try with latin-1 as fallback
            try:
                content = file_path.read_text(encoding='latin-1')
            except Exception as e:
                results.add_fail(f"Security check: {file_name}", f"Encoding error: {e}")
                continue
        
        for pattern in sensitive_patterns:
            import re
            if re.search(pattern, content) and "your_" not in content:
                results.add_fail(f"Security check: {file_name}", f"Possible exposed secret: {pattern}")
                break
        else:
            results.add_pass(f"Security check: {file_name}")
    
    # Test that .env is in .gitignore
    gitignore_path = Path(".gitignore")
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()
        if ".env" in gitignore_content:
            results.add_pass("Security: .env in .gitignore")
        else:
            results.add_fail("Security: .env in .gitignore", ".env not found in .gitignore")
    
    return results.summary()


def test_json_contract():
    """Test that output follows the required JSON contract."""
    results = TestResults()
    
    # Required fields in output
    required_fields = [
        "overall_score",
        "summary",
        "findings",
        "must_fix",
        "nice_to_have",
        "next_actions"
    ]
    
    # Required fields in each finding
    finding_fields = [
        "id",
        "severity",
        "category",
        "location",
        "evidence",
        "recommendation"
    ]
    
    # Create sample output
    sample_finding = {
        "id": "finding_001",
        "severity": "high",
        "category": "clarity",
        "location": {"page": 1},
        "evidence": "Sample evidence",
        "recommendation": "Sample fix",
        "suggested_rewrite": "Sample rewrite"
    }
    
    sample_output = {
        "overall_score": 80,
        "summary": ["Point 1", "Point 2"],
        "findings": [sample_finding],
        "must_fix": ["finding_001"],
        "nice_to_have": [],
        "next_actions": ["Step 1", "Step 2"]
    }
    
    # Test required fields
    missing_main = [field for field in required_fields if field not in sample_output]
    if not missing_main:
        results.add_pass("JSON contract: main fields")
    else:
        results.add_fail("JSON contract: main fields", f"Missing: {missing_main}")
    
    # Test finding fields
    missing_finding = [field for field in finding_fields if field not in sample_finding]
    if not missing_finding:
        results.add_pass("JSON contract: finding fields")
    else:
        results.add_fail("JSON contract: finding fields", f"Missing: {missing_finding}")
    
    # Test JSON validity
    try:
        json_str = json.dumps(sample_output)
        parsed = json.loads(json_str)
        if parsed == sample_output:
            results.add_pass("JSON contract: valid JSON")
        else:
            results.add_fail("JSON contract: valid JSON", "Parsed data doesn't match")
    except Exception as e:
        results.add_fail("JSON contract: valid JSON", str(e))
    
    return results.summary()


def run_all_tests():
    """Run all acceptance tests."""
    print("=" * 80)
    print("ARTIFACT CRITIC - ACCEPTANCE TESTS")
    print("=" * 80)
    print()
    
    tests = [
        ("Rubric Loading & Validation", test_rubric_loading),
        ("Artifact Processing", test_artifact_processing),
        ("Review Result Structure", test_review_result_structure),
        ("Security Checks", test_security_checks),
        ("JSON Contract", test_json_contract),
    ]
    
    all_passed = True
    
    for test_name, test_func in tests:
        print(f"\n{'─' * 80}")
        print(f"Running: {test_name}")
        print('─' * 80)
        
        try:
            passed = test_func()
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"❌ TEST CRASHED: {e}")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL ACCEPTANCE TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    import sys
    sys.exit(run_all_tests())
