#!/usr/bin/env python3
"""
AIMU GitHub-based Update Server
Lightweight API that reads from GitHub Releases
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import requests
from packaging import version
from datetime import datetime
import sqlite3
from pathlib import Path

app = Flask(__name__)
CORS(app)

# Configuration
GITHUB_OWNER = os.getenv('GITHUB_OWNER', 'Tayeb2323')
GITHUB_REPO = os.getenv('GITHUB_REPO', 'AIMU-releases')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', '')  # Optional: for private repos or higher rate limits
DATABASE_PATH = "update_logs.db"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the update logs database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS update_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_version TEXT NOT NULL,
            client_id TEXT,
            action TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT,
            user_agent TEXT,
            platform TEXT
        )
    ''')

    conn.commit()
    conn.close()

def get_github_releases():
    """Fetch releases from GitHub API"""
    try:
        headers = {}
        if GITHUB_TOKEN:
            headers['Authorization'] = f'token {GITHUB_TOKEN}'

        url = f'https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases'
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"GitHub API error: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error fetching GitHub releases: {e}")
        return []

def get_latest_release():
    """Get the latest stable release from GitHub"""
    releases = get_github_releases()

    # Filter out pre-releases and drafts
    stable_releases = [r for r in releases if not r.get('prerelease', False) and not r.get('draft', False)]

    if not stable_releases:
        return None

    # Sort by published date (newest first)
    stable_releases.sort(key=lambda x: x.get('published_at', ''), reverse=True)

    return stable_releases[0]

def find_windows_asset(release):
    """Find the Windows executable asset in a release"""
    assets = release.get('assets', [])

    # Look for .zip or .exe files
    for asset in assets:
        name = asset['name'].lower()
        if name.endswith('.zip') or name.endswith('.exe'):
            return asset

    return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'AIMU GitHub Update Server',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat(),
        'github_repo': f'{GITHUB_OWNER}/{GITHUB_REPO}'
    })

@app.route('/api/updates/check', methods=['GET'])
def check_for_updates():
    """Check for available updates from GitHub Releases"""
    try:
        current_version = request.args.get('version', '1.0.0')
        platform = request.args.get('platform', 'windows')
        client_id = request.args.get('client_id', 'unknown')

        # Log the check
        log_update_action(client_id, current_version, 'check_update',
                         request.remote_addr, request.headers.get('User-Agent'), platform)

        # Get latest release from GitHub
        latest_release = get_latest_release()

        if not latest_release:
            return jsonify({
                'update_available': False,
                'message': 'No releases available',
                'current_version': current_version
            })

        # Parse version from tag (remove 'v' prefix if present)
        latest_version = latest_release['tag_name'].lstrip('v')

        # Compare versions
        try:
            update_available = version.parse(latest_version) > version.parse(current_version)
        except:
            # If version parsing fails, assume no update
            update_available = False

        # Find Windows asset
        asset = find_windows_asset(latest_release)

        if not asset and update_available:
            return jsonify({
                'update_available': False,
                'message': 'Update available but no Windows asset found',
                'latest_version': latest_version,
                'current_version': current_version
            })

        response = {
            'update_available': update_available,
            'latest_version': latest_version,
            'current_version': current_version,
            'release_date': latest_release.get('published_at', ''),
            'release_notes': latest_release.get('body', 'No release notes available'),
            'is_supported': True,  # Can add version support logic later
            'min_supported_version': '1.0.0'
        }

        if asset:
            response['download_url'] = asset['browser_download_url']
            response['file_size'] = asset['size']
            response['file_name'] = asset['name']

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error checking for updates: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/updates/latest', methods=['GET'])
def get_latest():
    """Get information about the latest release"""
    try:
        latest_release = get_latest_release()

        if not latest_release:
            return jsonify({'error': 'No releases available'}), 404

        latest_version = latest_release['tag_name'].lstrip('v')
        asset = find_windows_asset(latest_release)

        response = {
            'version': latest_version,
            'release_date': latest_release.get('published_at', ''),
            'release_notes': latest_release.get('body', 'No release notes available'),
            'html_url': latest_release.get('html_url', '')
        }

        if asset:
            response['download_url'] = asset['browser_download_url']
            response['file_size'] = asset['size']
            response['file_name'] = asset['name']

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error getting latest release: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/updates/versions', methods=['GET'])
def list_versions():
    """List all available versions from GitHub"""
    try:
        releases = get_github_releases()

        versions = []
        for release in releases:
            if release.get('draft', False):
                continue

            asset = find_windows_asset(release)

            versions.append({
                'version': release['tag_name'].lstrip('v'),
                'release_date': release.get('published_at', ''),
                'prerelease': release.get('prerelease', False),
                'has_asset': asset is not None,
                'html_url': release.get('html_url', '')
            })

        return jsonify({'versions': versions})

    except Exception as e:
        logger.error(f"Error listing versions: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/updates/install', methods=['POST'])
def report_installation():
    """Report successful installation"""
    try:
        data = request.get_json()
        client_id = data.get('client_id', 'unknown')
        version = data.get('version', 'unknown')
        platform = data.get('platform', 'unknown')

        # Log the installation
        log_update_action(client_id, version, 'install_update',
                         request.remote_addr, request.headers.get('User-Agent'), platform)

        return jsonify({'status': 'success'})

    except Exception as e:
        logger.error(f"Error reporting installation: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/updates/rollback', methods=['POST'])
def report_rollback():
    """Report rollback to previous version"""
    try:
        data = request.get_json()
        client_id = data.get('client_id', 'unknown')
        version = data.get('version', 'unknown')
        reason = data.get('reason', 'unknown')
        platform = data.get('platform', 'unknown')

        # Log the rollback
        log_update_action(client_id, version, f'rollback_update: {reason}',
                         request.remote_addr, request.headers.get('User-Agent'), platform)

        return jsonify({'status': 'success'})

    except Exception as e:
        logger.error(f"Error reporting rollback: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/updates/stats', methods=['GET'])
def get_stats():
    """Get update statistics (admin endpoint)"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Total checks
        cursor.execute("SELECT COUNT(*) FROM update_logs WHERE action = 'check_update'")
        total_checks = cursor.fetchone()[0]

        # Total installations
        cursor.execute("SELECT COUNT(*) FROM update_logs WHERE action = 'install_update'")
        total_installs = cursor.fetchone()[0]

        # Unique clients
        cursor.execute("SELECT COUNT(DISTINCT client_id) FROM update_logs")
        unique_clients = cursor.fetchone()[0]

        # Version distribution
        cursor.execute("""
            SELECT client_version, COUNT(*) as count
            FROM update_logs
            WHERE action = 'check_update'
            GROUP BY client_version
            ORDER BY count DESC
            LIMIT 10
        """)
        version_dist = [{'version': row[0], 'count': row[1]} for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'total_checks': total_checks,
            'total_installations': total_installs,
            'unique_clients': unique_clients,
            'version_distribution': version_dist
        })

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': 'Internal server error'}), 500

def log_update_action(client_id: str, version: str, action: str,
                     ip_address: str, user_agent: str, platform: str = 'unknown'):
    """Log update actions for analytics"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO update_logs (client_version, client_id, action, ip_address, user_agent, platform)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (version, client_id, action, ip_address, user_agent, platform))

        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error logging action: {e}")

if __name__ == '__main__':
    # Initialize database
    init_database()

    # Get port from environment (Render provides this)
    port = int(os.getenv('PORT', 5000))

    # Run the server
    app.run(host='0.0.0.0', port=port, debug=False)
