"""
Populate the library with Android development knowledge.
This pre-seeds the library with key information about Android Studio and Android development.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from library_agent.library_store import LibraryStore, LibraryEntry
from config import Config

def populate_android_knowledge():
    """Add comprehensive Android development knowledge to the library."""
    print("Populating library with Android development knowledge...\n")
    
    library = LibraryStore()
    
    # Android Studio entry
    android_studio = LibraryEntry(
        title="Android Studio - Official IDE for Android Development",
        url="https://developer.android.com/studio",
        publisher="Google Android Developers",
        date_published="2024",
        topic_tags=["android", "development", "tools", "documentation"],
        summary="""
• Android Studio is the official Integrated Development Environment (IDE) for Android app development
• Based on IntelliJ IDEA from JetBrains, customized for Android development
• Provides comprehensive tools for building Android apps for phones, tablets, Wear OS, TV, and Auto
• Includes visual layout editor, code editor with intelligent code completion, and extensive testing tools
• Free and open-source, available for Windows, macOS, and Linux
• Current stable version is Android Studio Hedgehog (2023.1.1) as of 2024
• Supports Kotlin, Java, and C++ programming languages
• Integrates with Android SDK, emulator, and Gradle build system
        """.strip(),
        key_facts=[
            "Android Studio is built on IntelliJ IDEA and is the official IDE recommended by Google for Android development (https://developer.android.com/studio)",
            "Key features include Layout Editor for drag-and-drop UI design, APK Analyzer, fast emulator, and real-time profilers (https://developer.android.com/studio/features)",
            "Supports Kotlin as the preferred language, with full Java and C++ support via NDK (https://developer.android.com/kotlin)",
            "Includes Android Emulator for testing apps without physical devices (https://developer.android.com/studio/run/emulator)",
            "Gradle is the build automation system used by Android Studio (https://developer.android.com/studio/build)",
            "Version control integration with Git, SVN, and other systems built-in (https://developer.android.com/studio/intro)",
            "Real-time layout preview shows UI changes instantly without rebuilding (https://developer.android.com/studio/write/layout-editor)",
        ],
        credibility_notes="Official Android Developer documentation from Google - the authoritative source for Android development tools and practices",
        freshness_ttl_days=60,
    )
    
    # Android OS entry
    android_os = LibraryEntry(
        title="Android Operating System - Architecture and Overview",
        url="https://developer.android.com/guide/platform",
        publisher="Google Android Developers",
        date_published="2024",
        topic_tags=["android", "operating-system", "mobile", "documentation"],
        summary="""
• Android is a Linux-based mobile operating system developed by Google
• Powers billions of devices including smartphones, tablets, watches, TVs, and cars
• Open-source core (Android Open Source Project - AOSP) with proprietary Google services
• Latest version is Android 14 (API level 34), released in 2023
• Architecture includes Linux kernel, HAL, native libraries, Android Runtime (ART), and application framework
• Uses APK (Android Package) or AAB (Android App Bundle) format for app distribution
• Supports multiple CPU architectures: ARM, ARM64, x86, and x86-64
• Apps run in isolated sandbox environments for security
        """.strip(),
        key_facts=[
            "Android is built on the Linux kernel, providing core system services like security, memory management, and networking (https://developer.android.com/guide/platform)",
            "Android Runtime (ART) compiles app bytecode into native code for better performance (https://source.android.com/docs/core/runtime)",
            "Each app runs in its own security sandbox with unique Linux user ID for isolation (https://developer.android.com/guide/platform#security-features)",
            "Android 14 (API level 34) is the latest major version as of 2024, with features like improved privacy controls and performance (https://developer.android.com/about/versions/14)",
            "Material Design is Google's design language for Android applications (https://material.io/design)",
            "Play Store requires apps to be in AAB format for new submissions since 2021 (https://developer.android.com/guide/app-bundle)",
            "Android SDK provides APIs and tools for app development across all Android versions (https://developer.android.com/studio/releases/platforms)",
        ],
        credibility_notes="Official Android Platform documentation from Google - authoritative source for Android OS information",
        freshness_ttl_days=60,
    )
    
    # Building Android Apps entry
    android_app_dev = LibraryEntry(
        title="Building Android Apps - Complete Development Guide",
        url="https://developer.android.com/training/basics/firstapp",
        publisher="Google Android Developers",
        date_published="2024",
        topic_tags=["android", "development", "tutorial", "programming"],
        summary="""
• Android apps are primarily written in Kotlin (preferred) or Java
• Core components: Activities (screens), Services (background tasks), Broadcast Receivers, Content Providers
• UI built with XML layouts or Jetpack Compose (modern declarative UI)
• Manifest file declares app components, permissions, and requirements
• Gradle handles build configuration, dependencies, and variants
• Testing includes local unit tests, instrumented tests, and UI tests
• Publishing through Google Play Store or other distribution channels
• Modern development uses Android Jetpack libraries for best practices
        """.strip(),
        key_facts=[
            "Kotlin is Google's preferred language for Android development since 2019, offering null safety and concise syntax (https://developer.android.com/kotlin/first)",
            "Four main app components: Activities, Services, Broadcast Receivers, and Content Providers (https://developer.android.com/guide/components/fundamentals)",
            "Jetpack Compose is the modern UI toolkit for building native Android UIs declaratively (https://developer.android.com/jetpack/compose)",
            "AndroidManifest.xml declares all app components and required permissions (https://developer.android.com/guide/topics/manifest/manifest-intro)",
            "Gradle build system allows multiple build variants (debug, release) and product flavors (https://developer.android.com/studio/build)",
            "Activity lifecycle methods (onCreate, onStart, onResume, etc.) must be properly handled (https://developer.android.com/guide/components/activities/activity-lifecycle)",
            "Material Design Components library provides pre-built UI components following Material Design (https://material.io/develop/android)",
            "ViewModel and LiveData from Jetpack Architecture Components help manage UI data lifecycle-aware (https://developer.android.com/topic/libraries/architecture/viewmodel)",
            "Room Persistence Library provides abstraction over SQLite database (https://developer.android.com/training/data-storage/room)",
            "Minimum SDK version determines oldest Android version supported, while target SDK ensures compatibility with latest features (https://developer.android.com/distribute/best-practices/develop/target-sdk)",
        ],
        credibility_notes="Official Android Development training materials from Google - comprehensive and regularly updated guide for building Android apps",
        freshness_ttl_days=30,
    )
    
    # Kotlin for Android entry
    kotlin_android = LibraryEntry(
        title="Kotlin for Android Development",
        url="https://kotlinlang.org/docs/android-overview.html",
        publisher="JetBrains / Kotlin Foundation",
        date_published="2024",
        topic_tags=["kotlin", "android", "programming", "documentation"],
        summary="""
• Kotlin is a modern, statically-typed programming language officially supported for Android
• Announced as preferred language for Android at Google I/O 2019
• 100% interoperable with Java - can use Java libraries and frameworks
• Reduces boilerplate code by 20-40% compared to Java
• Null safety built into type system prevents NullPointerExceptions
• Coroutines provide lightweight concurrency for async operations
• Extension functions allow adding functionality to existing classes
• Data classes automatically generate equals, hashCode, toString, copy methods
        """.strip(),
        key_facts=[
            "Over 70% of top 1000 Android apps use Kotlin according to Google (https://developer.android.com/kotlin)",
            "Kotlin's null safety prevents the #1 cause of Android crashes - NullPointerExceptions (https://kotlinlang.org/docs/null-safety.html)",
            "Coroutines in Kotlin simplify async programming compared to callbacks or RxJava (https://kotlinlang.org/docs/coroutines-overview.html)",
            "Kotlin Multiplatform allows sharing code between Android and iOS (https://kotlinlang.org/docs/multiplatform-mobile-getting-started.html)",
            "Android Studio provides excellent Kotlin support with code completion, refactoring, and debugging (https://developer.android.com/kotlin/add-kotlin)",
            "Kotlin is fully interoperable with Java, allowing gradual migration of existing codebases (https://kotlinlang.org/docs/java-interop.html)",
        ],
        credibility_notes="Official Kotlin documentation from JetBrains (language creators) and Google (Android platform owner)",
        freshness_ttl_days=60,
    )
    
    # Add all entries to library
    entries = [android_studio, android_os, android_app_dev, kotlin_android]
    
    for entry in entries:
        result = library.add_entry(entry, update_if_exists=True)
        print(f"✅ {result['action'].upper()}: {entry.title}")
    
    # Show stats
    print("\n" + "=" * 80)
    stats = library.get_stats()
    print(f"Library now contains {stats['total_entries']} entries")
    print(f"Topics: {', '.join(sorted(stats['topics'].keys()))}")
    print("=" * 80)

if __name__ == "__main__":
    populate_android_knowledge()
