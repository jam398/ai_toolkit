"""
Rubric management system for Artifact Critic.
Loads and manages versioned review rubrics.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class RubricCategory:
    """A single review category within a rubric."""
    id: str
    name: str
    weight: int
    criteria: List[str]


@dataclass
class Rubric:
    """A complete review rubric for an artifact type."""
    version: str
    rubric_id: str
    name: str
    description: str
    target_score: int
    max_score: int
    categories: List[RubricCategory]
    severity_mapping: Dict[str, List[str]]
    common_findings: List[Dict[str, Any]]
    
    def get_category(self, category_id: str) -> Optional[RubricCategory]:
        """Get a category by ID."""
        for cat in self.categories:
            if cat.id == category_id:
                return cat
        return None
    
    def get_total_weight(self) -> int:
        """Calculate total weight across all categories."""
        return sum(cat.weight for cat in self.categories)
    
    def format_for_prompt(self) -> str:
        """Format rubric as instructions for the AI critic."""
        lines = [
            f"# {self.name}",
            f"{self.description}",
            f"",
            f"Target Score: {self.target_score}/{self.max_score}",
            f"",
            f"## Evaluation Categories",
            f""
        ]
        
        for cat in self.categories:
            lines.append(f"### {cat.name} (Weight: {cat.weight}%)")
            lines.append("Criteria:")
            for criterion in cat.criteria:
                lines.append(f"  - {criterion}")
            lines.append("")
        
        lines.append("## Severity Guidelines")
        for severity, examples in self.severity_mapping.items():
            lines.append(f"**{severity.upper()}**: {', '.join(examples[:3])}")
        
        return "\n".join(lines)


class RubricManager:
    """Manages loading and caching of rubrics."""
    
    def __init__(self, rubrics_dir: str = "./rubrics"):
        self.rubrics_dir = Path(rubrics_dir)
        self._cache: Dict[str, Rubric] = {}
    
    def load_rubric(self, rubric_id: str) -> Rubric:
        """
        Load a rubric by ID.
        
        Args:
            rubric_id: Rubric identifier (e.g., 'resume_v1')
            
        Returns:
            Loaded Rubric object
            
        Raises:
            FileNotFoundError: If rubric file doesn't exist
            ValueError: If rubric YAML is invalid
        """
        # Check cache first
        if rubric_id in self._cache:
            return self._cache[rubric_id]
        
        # Load from file
        rubric_file = self.rubrics_dir / f"{rubric_id}.yaml"
        
        if not rubric_file.exists():
            raise FileNotFoundError(f"Rubric not found: {rubric_id}")
        
        try:
            with open(rubric_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Parse categories
            categories = []
            for cat_data in data.get('categories', []):
                categories.append(RubricCategory(
                    id=cat_data['id'],
                    name=cat_data['name'],
                    weight=cat_data['weight'],
                    criteria=cat_data['criteria']
                ))
            
            # Create rubric object
            rubric = Rubric(
                version=data['version'],
                rubric_id=data['rubric_id'],
                name=data['name'],
                description=data['description'],
                target_score=data['target_score'],
                max_score=data['max_score'],
                categories=categories,
                severity_mapping=data.get('severity_mapping', {}),
                common_findings=data.get('common_findings', [])
            )
            
            # Validate
            total_weight = rubric.get_total_weight()
            if total_weight != 100:
                raise ValueError(f"Rubric weights must sum to 100, got {total_weight}")
            
            # Cache and return
            self._cache[rubric_id] = rubric
            return rubric
            
        except Exception as e:
            raise ValueError(f"Failed to load rubric {rubric_id}: {e}")
    
    def list_available_rubrics(self) -> List[Dict[str, str]]:
        """List all available rubrics in the rubrics directory."""
        rubrics = []
        
        if not self.rubrics_dir.exists():
            return rubrics
        
        for rubric_file in self.rubrics_dir.glob("*.yaml"):
            try:
                rubric = self.load_rubric(rubric_file.stem)
                rubrics.append({
                    "id": rubric.rubric_id,
                    "name": rubric.name,
                    "description": rubric.description,
                    "version": rubric.version
                })
            except Exception:
                pass
        
        return rubrics
    
    def validate_rubric(self, rubric_id: str) -> Dict[str, Any]:
        """
        Validate a rubric file for correctness.
        
        Returns:
            Dict with 'valid' bool and 'errors' list
        """
        errors = []
        
        try:
            rubric = self.load_rubric(rubric_id)
            
            # Check weights sum to 100
            total_weight = rubric.get_total_weight()
            if total_weight != 100:
                errors.append(f"Weights sum to {total_weight}, not 100")
            
            # Check severity mapping
            required_severities = ['blocker', 'high', 'medium', 'low']
            for severity in required_severities:
                if severity not in rubric.severity_mapping:
                    errors.append(f"Missing severity level: {severity}")
            
            # Check categories have criteria
            for cat in rubric.categories:
                if not cat.criteria:
                    errors.append(f"Category '{cat.id}' has no criteria")
            
        except Exception as e:
            errors.append(f"Failed to load: {str(e)}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
