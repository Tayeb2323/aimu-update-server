#!/usr/bin/env python3
"""
Helper script to create GitHub releases for AIMU
Requires: pip install PyGithub
"""

import argparse
import sys
from pathlib import Path
from github import Github
import os

def create_release(version, file_path, token, repo_name, release_notes=""):
    """
    Create a GitHub release and upload asset

    Args:
        version: Version string (e.g., "1.0.0")
        file_path: Path to the file to upload
        token: GitHub personal access token
        repo_name: Repository name (e.g., "Tayeb2323/AIMU")
        release_notes: Release notes (markdown)
    """
    try:
        # Initialize GitHub client
        g = Github(token)
        repo = g.get_repo(repo_name)

        # Ensure version has 'v' prefix for tag
        tag_name = f"v{version}" if not version.startswith('v') else version

        # Check if file exists
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"❌ Error: File not found: {file_path}")
            return False

        print(f"📦 Creating release {tag_name}...")
        print(f"   Repository: {repo_name}")
        print(f"   File: {file_path.name} ({file_path.stat().st_size / (1024*1024):.1f} MB)")

        # Create release
        release = repo.create_git_release(
            tag=tag_name,
            name=f"AIMU {tag_name}",
            message=release_notes or f"Release {tag_name}",
            draft=False,
            prerelease=False
        )

        print(f"✅ Release created: {release.html_url}")

        # Upload asset
        print(f"📤 Uploading {file_path.name}...")
        asset = release.upload_asset(
            str(file_path),
            label=file_path.name,
            content_type="application/zip" if file_path.suffix == '.zip' else "application/octet-stream"
        )

        print(f"✅ Asset uploaded: {asset.browser_download_url}")
        print(f"\n🎉 Release complete!")
        print(f"   Release URL: {release.html_url}")
        print(f"   Download URL: {asset.browser_download_url}")

        return True

    except Exception as e:
        print(f"❌ Error creating release: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Create a GitHub release for AIMU',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create release with file
  python create_github_release.py --version 1.0.0 --file dist/AIMU_v1.0.0.zip

  # With release notes
  python create_github_release.py --version 1.0.0 --file dist/AIMU_v1.0.0.zip --notes "Bug fixes"

  # Custom repository
  python create_github_release.py --version 1.0.0 --file dist/AIMU_v1.0.0.zip --repo "YourUser/YourRepo"

Environment Variables:
  GITHUB_TOKEN: GitHub personal access token (required)
  GITHUB_REPO: Default repository (default: Tayeb2323/AIMU)
        """
    )

    parser.add_argument('--version', '-v', required=True,
                       help='Version number (e.g., 1.0.0)')
    parser.add_argument('--file', '-f', required=True,
                       help='Path to file to upload (.zip or .exe)')
    parser.add_argument('--notes', '-n', default='',
                       help='Release notes (markdown supported)')
    parser.add_argument('--repo', '-r',
                       default=os.getenv('GITHUB_REPO', 'Tayeb2323/AIMU'),
                       help='Repository name (owner/repo)')
    parser.add_argument('--token', '-t',
                       default=os.getenv('GITHUB_TOKEN'),
                       help='GitHub personal access token')

    args = parser.parse_args()

    # Validate token
    if not args.token:
        print("❌ Error: GitHub token required")
        print("\nSet GITHUB_TOKEN environment variable or use --token flag")
        print("\nTo create a token:")
        print("1. Go to: https://github.com/settings/tokens")
        print("2. Generate new token (classic)")
        print("3. Select 'repo' scope")
        print("4. Copy the token")
        print("\nThen:")
        print("  export GITHUB_TOKEN=your_token_here")
        print("  # or")
        print("  python create_github_release.py --token your_token_here ...")
        sys.exit(1)

    # Create release
    success = create_release(
        version=args.version,
        file_path=args.file,
        token=args.token,
        repo_name=args.repo,
        release_notes=args.notes
    )

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
