"""
Media Store - Storage for image, video, and audio analyses.

Separate from the library to keep media analyses organized independently.
"""
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class MediaAnalysis:
    """Represents a single media analysis entry."""
    
    analysis_id: str
    media_type: str  # "image", "video", "audio"
    filename: str
    filepath: str
    analysis_text: str
    analyzed_by: str  # Model name (e.g., "gemini-2.0-flash")
    date_analyzed: str
    file_size: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    
    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)


class MediaStore:
    """Storage manager for media analyses."""
    
    def __init__(self, storage_path: str = "./media_data"):
        """
        Initialize the media store.
        
        Args:
            storage_path: Directory for media storage
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.analyses_file = self.storage_path / "analyses.json"
        
        # Create empty file if it doesn't exist
        if not self.analyses_file.exists():
            self._save_data({})
    
    def _load_data(self) -> Dict[str, Dict]:
        """Load all analyses from storage."""
        try:
            with open(self.analyses_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def _save_data(self, data: Dict[str, Dict]):
        """Save all analyses to storage."""
        with open(self.analyses_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_analysis(self, analysis: MediaAnalysis) -> bool:
        """
        Add a new media analysis.
        
        Args:
            analysis: MediaAnalysis object
            
        Returns:
            True if successful
        """
        data = self._load_data()
        data[analysis.analysis_id] = analysis.to_dict()
        self._save_data(data)
        return True
    
    def get_analysis(self, analysis_id: str) -> Optional[MediaAnalysis]:
        """
        Get a specific analysis by ID.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            MediaAnalysis object or None
        """
        data = self._load_data()
        if analysis_id in data:
            return MediaAnalysis(**data[analysis_id])
        return None
    
    def search_by_filename(self, filename: str) -> List[MediaAnalysis]:
        """
        Search analyses by filename.
        
        Args:
            filename: Filename to search for
            
        Returns:
            List of matching MediaAnalysis objects
        """
        data = self._load_data()
        results = []
        
        for analysis_data in data.values():
            if filename.lower() in analysis_data['filename'].lower():
                results.append(MediaAnalysis(**analysis_data))
        
        return results
    
    def search_by_type(self, media_type: str) -> List[MediaAnalysis]:
        """
        Search analyses by media type.
        
        Args:
            media_type: Type of media ("image", "video", "audio")
            
        Returns:
            List of matching MediaAnalysis objects
        """
        data = self._load_data()
        results = []
        
        for analysis_data in data.values():
            if analysis_data['media_type'] == media_type:
                results.append(MediaAnalysis(**analysis_data))
        
        return results
    
    def get_all_analyses(self) -> List[MediaAnalysis]:
        """
        Get all analyses.
        
        Returns:
            List of all MediaAnalysis objects
        """
        data = self._load_data()
        return [MediaAnalysis(**analysis_data) for analysis_data in data.values()]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about stored analyses.
        
        Returns:
            Dictionary with statistics
        """
        data = self._load_data()
        analyses = list(data.values())
        
        stats = {
            'total_analyses': len(analyses),
            'by_type': {},
            'recent_analyses': []
        }
        
        # Count by type
        for analysis in analyses:
            media_type = analysis.get('media_type', 'unknown')
            stats['by_type'][media_type] = stats['by_type'].get(media_type, 0) + 1
        
        # Get 5 most recent
        sorted_analyses = sorted(
            analyses,
            key=lambda x: x.get('date_analyzed', ''),
            reverse=True
        )
        stats['recent_analyses'] = [
            {
                'filename': a['filename'],
                'media_type': a['media_type'],
                'date': a['date_analyzed']
            }
            for a in sorted_analyses[:5]
        ]
        
        return stats
    
    def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete an analysis.
        
        Args:
            analysis_id: Analysis ID to delete
            
        Returns:
            True if successful
        """
        data = self._load_data()
        if analysis_id in data:
            del data[analysis_id]
            self._save_data(data)
            return True
        return False
