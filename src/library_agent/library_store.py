"""
Library storage backend with vector search and metadata management.
Implements deduplication, freshness tracking, and CRUD operations.
"""
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse

# Try to import ChromaDB, fall back to simple implementation if not available
try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except (ImportError, Exception) as e:
    CHROMADB_AVAILABLE = False
    print(f"Warning: ChromaDB not available ({e}). Using simple fallback storage.")


class LibraryEntry:
    """Schema for a library entry with all required fields."""
    
    def __init__(
        self,
        title: str,
        url: str,
        publisher: str,
        summary: str,
        key_facts: List[str],
        topic_tags: List[str],
        date_published: Optional[str] = None,
        date_accessed: Optional[str] = None,
        credibility_notes: str = "",
        freshness_ttl_days: int = 30,
        entry_id: Optional[str] = None,
    ):
        self.title = title
        self.url = url
        self.publisher = publisher
        self.summary = summary
        self.key_facts = key_facts
        self.topic_tags = topic_tags
        self.date_published = date_published
        self.date_accessed = date_accessed or datetime.now().isoformat()
        self.credibility_notes = credibility_notes
        self.freshness_ttl_days = freshness_ttl_days
        self.entry_id = entry_id or self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate unique ID based on normalized URL."""
        normalized_url = self._normalize_url(self.url)
        return hashlib.sha256(normalized_url.encode()).hexdigest()[:16]
    
    @staticmethod
    def _normalize_url(url: str) -> str:
        """Normalize URL for deduplication."""
        parsed = urlparse(url.lower().strip())
        # Remove www., trailing slashes, and fragments
        domain = parsed.netloc.replace('www.', '')
        path = parsed.path.rstrip('/')
        return f"{parsed.scheme}://{domain}{path}"
    
    def is_stale(self) -> bool:
        """Check if entry is older than its TTL."""
        if not self.date_accessed:
            return True
        
        accessed = datetime.fromisoformat(self.date_accessed)
        age_days = (datetime.now() - accessed).days
        return age_days > self.freshness_ttl_days
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "entry_id": self.entry_id,
            "title": self.title,
            "url": self.url,
            "publisher": self.publisher,
            "date_published": self.date_published,
            "date_accessed": self.date_accessed,
            "topic_tags": self.topic_tags,
            "summary": self.summary,
            "key_facts": self.key_facts,
            "credibility_notes": self.credibility_notes,
            "freshness_ttl_days": self.freshness_ttl_days,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LibraryEntry":
        """Create entry from dictionary."""
        return cls(**data)
    
    def get_full_text(self) -> str:
        """Get full text for vector embedding."""
        facts_text = "\n".join(self.key_facts)
        tags_text = ", ".join(self.topic_tags)
        return f"""Title: {self.title}
Publisher: {self.publisher}
Topics: {tags_text}

Summary:
{self.summary}

Key Facts:
{facts_text}

Credibility: {self.credibility_notes}"""


class LibraryStore:
    """Vector-based library with metadata tracking and deduplication."""
    
    def __init__(self, persist_directory: str = "./library_data"):
        """Initialize the library store."""
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        if CHROMADB_AVAILABLE:
            # Initialize ChromaDB for vector search
            self.client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="library_entries",
                metadata={"hnsw:space": "cosine"}
            )
            self.use_simple_storage = False
        else:
            # Use simple JSON-based storage as fallback
            self.simple_storage_path = self.persist_directory / "entries.json"
            self._load_simple_storage()
            self.use_simple_storage = True
    
    def _load_simple_storage(self):
        """Load entries from simple JSON storage."""
        if self.simple_storage_path.exists():
            try:
                with open(self.simple_storage_path, 'r', encoding='utf-8') as f:
                    self.simple_entries = json.load(f)
            except:
                self.simple_entries = {}
        else:
            self.simple_entries = {}
    
    def _save_simple_storage(self):
        """Save entries to simple JSON storage."""
        with open(self.simple_storage_path, 'w', encoding='utf-8') as f:
            json.dump(self.simple_entries, f, indent=2, ensure_ascii=False)
    
    def add_entry(self, entry: LibraryEntry, update_if_exists: bool = True) -> Dict[str, Any]:
        """
        Add or update a library entry with deduplication.
        
        Returns:
            Dict with 'action' (added/updated/skipped) and 'entry_id'
        """
        # Check if entry already exists
        existing = self._get_by_id(entry.entry_id)
        
        if existing:
            if update_if_exists:
                # Update the existing entry
                entry.date_accessed = datetime.now().isoformat()
                self._update_entry(entry)
                return {"action": "updated", "entry_id": entry.entry_id, "reason": "existing entry refreshed"}
            else:
                return {"action": "skipped", "entry_id": entry.entry_id, "reason": "entry already exists"}
        
        # Add new entry
        if self.use_simple_storage:
            self.simple_entries[entry.entry_id] = entry.to_dict()
            self._save_simple_storage()
        else:
            self.collection.add(
                ids=[entry.entry_id],
                documents=[entry.get_full_text()],
                metadatas=[entry.to_dict()]
            )
        
        return {"action": "added", "entry_id": entry.entry_id, "reason": "new entry created"}
    
    def _get_by_id(self, entry_id: str) -> Optional[LibraryEntry]:
        """Retrieve entry by ID."""
        try:
            if self.use_simple_storage:
                if entry_id in self.simple_entries:
                    return LibraryEntry.from_dict(self.simple_entries[entry_id])
            else:
                results = self.collection.get(ids=[entry_id])
                if results['ids']:
                    metadata = results['metadatas'][0]
                    return LibraryEntry.from_dict(metadata)
        except Exception:
            pass
        return None
    
    def _update_entry(self, entry: LibraryEntry):
        """Update an existing entry."""
        if self.use_simple_storage:
            self.simple_entries[entry.entry_id] = entry.to_dict()
            self._save_simple_storage()
        else:
            self.collection.update(
                ids=[entry.entry_id],
                documents=[entry.get_full_text()],
                metadatas=[entry.to_dict()]
            )
    
    def search(self, query: str, limit: int = 5, filter_stale: bool = False) -> List[Dict[str, Any]]:
        """
        Search library entries by semantic similarity.
        
        Returns:
            List of dicts with 'entry', 'score', and 'is_stale' keys
        """
        if self.use_simple_storage:
            # Simple keyword-based search for fallback
            entries = []
            query_lower = query.lower()
            
            for entry_data in self.simple_entries.values():
                entry = LibraryEntry.from_dict(entry_data)
                
                # Simple relevance scoring based on keyword matching
                full_text = entry.get_full_text().lower()
                query_words = query_lower.split()
                matches = sum(1 for word in query_words if word in full_text)
                score = matches / max(len(query_words), 1) if query_words else 0
                
                is_stale = entry.is_stale()
                
                if filter_stale and is_stale:
                    continue
                
                if score > 0:
                    entries.append({
                        "entry": entry,
                        "score": score,
                        "is_stale": is_stale
                    })
            
            # Sort by score and limit
            entries.sort(key=lambda x: x["score"], reverse=True)
            return entries[:limit]
        else:
            # ChromaDB vector search
            if self.collection.count() == 0:
                return []
            
            results = self.collection.query(
                query_texts=[query],
                n_results=min(limit, self.collection.count())
            )
            
            entries = []
            if results['ids'] and results['ids'][0]:
                for i, entry_id in enumerate(results['ids'][0]):
                    metadata = results['metadatas'][0][i]
                    entry = LibraryEntry.from_dict(metadata)
                    
                    is_stale = entry.is_stale()
                    
                    # Skip stale entries if filter requested
                    if filter_stale and is_stale:
                        continue
                    
                    entries.append({
                        "entry": entry,
                        "score": 1 - results['distances'][0][i],  # Convert distance to similarity
                        "is_stale": is_stale
                    })
            
            return entries
    
    def get_stale_entries(self, query: str, limit: int = 5) -> List[LibraryEntry]:
        """Get stale entries that match the query."""
        all_results = self.search(query, limit=limit * 2, filter_stale=False)
        return [r["entry"] for r in all_results if r["is_stale"]]
    
    def get_all_entries(self) -> List[LibraryEntry]:
        """Get all library entries."""
        if self.use_simple_storage:
            return [LibraryEntry.from_dict(data) for data in self.simple_entries.values()]
        else:
            if self.collection.count() == 0:
                return []
            
            results = self.collection.get()
            entries = []
            
            if results['ids']:
                for metadata in results['metadatas']:
                    entries.append(LibraryEntry.from_dict(metadata))
            
            return entries
    
    def delete_entry(self, entry_id: str) -> bool:
        """Delete an entry by ID."""
        try:
            if self.use_simple_storage:
                if entry_id in self.simple_entries:
                    del self.simple_entries[entry_id]
                    self._save_simple_storage()
                    return True
                return False
            else:
                self.collection.delete(ids=[entry_id])
                return True
        except Exception:
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get library statistics."""
        entries = self.get_all_entries()
        
        if not entries:
            return {
                "total_entries": 0,
                "fresh_entries": 0,
                "stale_entries": 0,
                "topics": {},
            }
        
        stale_count = sum(1 for e in entries if e.is_stale())
        
        # Count by topic
        topic_counts = {}
        for entry in entries:
            for topic in entry.topic_tags:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        return {
            "total_entries": len(entries),
            "fresh_entries": len(entries) - stale_count,
            "stale_entries": stale_count,
            "topics": topic_counts,
        }
