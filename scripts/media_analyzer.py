"""
Media Analyzer - Analyze local images/videos with Gemini.

This tool:
1. Takes user-provided images or videos
2. Uses Gemini to analyze and provide feedback
3. Saves analysis to library for future reference
"""
import sys
import os
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import glob

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import Config
from artifact_critic.gemini_critic import GeminiCritic
from media_store import MediaStore, MediaAnalysis

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not available")


class MediaAnalyzer:
    """Analyze images and videos with Gemini."""
    
    def __init__(self):
        self.config = Config()
        self.config.validate()
        
        if GEMINI_AVAILABLE:
            genai.configure(api_key=self.config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(self.config.GEMINI_MODEL)
        
        # Use separate media storage instead of library
        self.media_store = MediaStore("./media_data")
    
    def find_local_images(self, directory: str = None) -> List[Path]:
        """
        Find image files in a directory.
        
        Args:
            directory: Directory to search (default: current directory)
            
        Returns:
            List of image file paths
        """
        if directory is None:
            directory = "."
        
        search_dir = Path(directory)
        if not search_dir.exists():
            print(f"✗ Directory not found: {directory}")
            return []
        
        # Supported image formats
        patterns = ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.bmp", "*.webp"]
        
        images = []
        for pattern in patterns:
            images.extend(search_dir.glob(pattern))
            images.extend(search_dir.glob(pattern.upper()))
        
        return sorted(images)
    
    def analyze_image(self, image_path: Path, context: str = "") -> Dict[str, Any]:
        """
        Analyze an image with Gemini.
        
        Args:
            image_path: Path to image file
            context: Optional context about the image
            
        Returns:
            Analysis results dict
        """
        if not GEMINI_AVAILABLE:
            return {"error": "Gemini API not available"}
        
        try:
            # Load image
            from PIL import Image
            img = Image.open(image_path)
            
            # Create analysis prompt
            prompt = f"""Analyze this image in detail. Provide:

1. **Description**: What do you see in the image?
2. **Technical Quality**: Composition, lighting, colors, focus
3. **Mood/Atmosphere**: What feeling does it convey?
4. **Interesting Elements**: Noteworthy details or patterns
5. **Potential Uses**: Where could this image be used effectively?
6. **Accessibility**: How would you describe this to someone who can't see it?

{f'Context: {context}' if context else ''}

Provide thoughtful, specific observations."""

            # Get analysis from Gemini
            response = self.model.generate_content([prompt, img])
            
            return {
                "timestamp": datetime.now().isoformat(),
                "image_path": str(image_path),
                "analysis": response.text,
                "context": context,
                "success": True
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def analyze_images(self, image_paths: List[Path], save_to_library: bool = True):
        """
        Main workflow: analyze provided images.
        
        Args:
            image_paths: List of paths to image files
            save_to_library: Whether to save analyses to library
        """
        print("\n" + "=" * 80)
        print(f"MEDIA ANALYZER - Analyzing {len(image_paths)} image(s)")
        print("=" * 80)
        
        results = []
        
        # Process each image
        for i, filepath in enumerate(image_paths, 1):
            print(f"\n{'─' * 80}")
            print(f"IMAGE {i}/{len(image_paths)}: {filepath.name}")
            print('─' * 80)
            
            # Analyze with Gemini
            print("🤖 Analyzing with Gemini...")
            analysis = self.analyze_image(filepath, context=f"Local file: {filepath.name}")
            
            if analysis.get("success"):
                print("\n" + "=" * 80)
                print("📊 GEMINI ANALYSIS")
                print("=" * 80)
                print(analysis["analysis"])
                print("=" * 80)
                
                results.append({
                    "filepath": str(filepath),
                    "filename": filepath.name,
                    "analysis": analysis
                })
                
                # Save to media storage
                if save_to_library:
                    self._save_to_media_store(filepath, analysis)
            
            else:
                print(f"✗ Analysis failed: {analysis.get('error')}")
        
        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"Images processed: {len(image_paths)}")
        print(f"Successfully analyzed: {len(results)}")
        
        if results and save_to_library:
            print("Analyses saved to media storage for future queries")
        
        return results
    
    def _save_to_media_store(self, filepath: Path, analysis: Dict):
        """Save analysis to media storage."""
        try:
            # Generate unique ID
            import hashlib
            unique_str = f"{filepath.absolute()}{datetime.now().isoformat()}"
            analysis_id = hashlib.md5(unique_str.encode()).hexdigest()[:16]
            
            # Determine media type from extension
            ext = filepath.suffix.lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
                media_type = 'image'
            elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                media_type = 'video'
            elif ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
                media_type = 'audio'
            else:
                media_type = 'unknown'
            
            # Get file size
            file_size = filepath.stat().st_size if filepath.exists() else None
            
            media_analysis = MediaAnalysis(
                analysis_id=analysis_id,
                media_type=media_type,
                filename=filepath.name,
                filepath=str(filepath.absolute()),
                analysis_text=analysis["analysis"],
                analyzed_by=self.config.GEMINI_MODEL,
                date_analyzed=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                file_size=file_size,
                metadata={'status': 'success'},
                tags=[media_type, 'gemini', 'ai-analysis']
            )
            
            self.media_store.add_analysis(media_analysis)
            print("  ✓ Saved to media storage")
        
        except Exception as e:
            print(f"  ⚠ Failed to save to media storage: {e}")
    
    def interactive_mode(self):
        """Interactive mode - analyzes user-provided images."""
        print("\n" + "🖼️ " * 40)
        print("MEDIA ANALYZER - INTERACTIVE MODE")
        print("🖼️ " * 40)
        
        print("\nOptions:")
        print("  1. Analyze a single image file")
        print("  2. Analyze all images in a directory")
        print("  3. Analyze multiple specific files")
        print("  Type 'quit' to exit\n")
        
        while True:
            try:
                choice = input("Choose option (1-3): ").strip()
                
                if choice.lower() == 'quit':
                    print("\n👋 Goodbye!")
                    break
                
                image_paths = []
                
                if choice == '1':
                    # Single file
                    filepath = input("Enter image path: ").strip().strip('"')
                    path = Path(filepath)
                    if path.exists() and path.is_file():
                        image_paths = [path]
                    else:
                        print("✗ File not found")
                        continue
                
                elif choice == '2':
                    # Directory
                    directory = input("Enter directory path (or '.' for current): ").strip().strip('"')
                    if not directory:
                        directory = "."
                    
                    images = self.find_local_images(directory)
                    if images:
                        print(f"\nFound {len(images)} images:")
                        for i, img in enumerate(images[:10], 1):  # Show first 10
                            print(f"  {i}. {img.name}")
                        if len(images) > 10:
                            print(f"  ... and {len(images) - 10} more")
                        
                        confirm = input(f"\nAnalyze all {len(images)} images? (y/n): ").strip().lower()
                        if confirm == 'y':
                            image_paths = images
                    else:
                        print("✗ No images found in directory")
                        continue
                
                elif choice == '3':
                    # Multiple files
                    print("Enter image paths (one per line, empty line to finish):")
                    while True:
                        filepath = input("> ").strip().strip('"')
                        if not filepath:
                            break
                        path = Path(filepath)
                        if path.exists() and path.is_file():
                            image_paths.append(path)
                        else:
                            print(f"  ⚠ Skipped (not found): {filepath}")
                    
                    if not image_paths:
                        print("✗ No valid images provided")
                        continue
                
                else:
                    print("✗ Invalid option")
                    continue
                
                if image_paths:
                    # Run analysis
                    save = input("\nSave analyses to library? (y/n, default: y): ").strip().lower()
                    save_to_lib = save != 'n'
                    
                    self.analyze_images(image_paths, save_to_library=save_to_lib)
                
                print("\n" + "─" * 80)
                input("Press Enter to continue...")
                print()
            
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n✗ Error: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Media Analyzer - Analyze images with Gemini",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python media_analyzer.py
  
  # Analyze a single image
  python media_analyzer.py --file image.jpg
  
  # Analyze all images in a directory
  python media_analyzer.py --directory ./photos
  
  # Analyze multiple images
  python media_analyzer.py --file img1.jpg --file img2.png --file img3.jpg
  
  # Don't save to library
  python media_analyzer.py --file image.jpg --no-save

Features:
  • Uses Gemini 3 for detailed multimodal analysis
  • Analyzes composition, quality, mood, and purpose
  • Saves analyses to library for future reference
  • Supports JPG, PNG, GIF, BMP, WEBP formats
        """
    )
    
    parser.add_argument(
        '--file',
        type=str,
        action='append',
        help='Path to image file (can be used multiple times)'
    )
    
    parser.add_argument(
        '--directory',
        type=str,
        help='Directory containing images to analyze'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Don\'t save analyses to library'
    )
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = MediaAnalyzer()
    
    # Gather image paths
    image_paths = []
    
    if args.file:
        # Individual files
        for filepath in args.file:
            path = Path(filepath)
            if path.exists() and path.is_file():
                image_paths.append(path)
            else:
                print(f"⚠ File not found: {filepath}")
    
    if args.directory:
        # Directory scan
        dir_images = analyzer.find_local_images(args.directory)
        image_paths.extend(dir_images)
    
    if image_paths:
        # Direct analysis
        analyzer.analyze_images(
            image_paths=image_paths,
            save_to_library=not args.no_save
        )
    else:
        # Interactive mode (default)
        analyzer.interactive_mode()


if __name__ == "__main__":
    main()
