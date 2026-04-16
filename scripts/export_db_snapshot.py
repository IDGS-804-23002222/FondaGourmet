#!/usr/bin/env python3
"""Export a full DB snapshot (schema + data) when possible.

Preferred path: mysqldump (includes data, routines, events, triggers).
Fallback path: schema-only export if mysqldump is not available.
"""

from pathlib import Path
import shutil
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.engine.url import make_url

from app import create_app
from scripts.export_db_schema import run as export_schema_only


def _mysqldump_available():
    return shutil.which('mysqldump') is not None


def export_full_with_mysqldump(output_file):
    app = create_app()
    uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if not uri:
        raise RuntimeError('SQLALCHEMY_DATABASE_URI not configured')

    url = make_url(uri)
    if not (url.drivername.startswith('mysql') or url.drivername.startswith('mariadb')):
        raise RuntimeError('Full snapshot export only supports mysql/mariadb URIs')

    cmd = [
        'mysqldump',
        '--single-transaction',
        '--skip-lock-tables',
        '--routines',
        '--events',
        '--triggers',
        f'--host={url.host or "localhost"}',
        f'--port={url.port or 3306}',
        f'--user={url.username or "root"}',
    ]

    if url.password:
        cmd.append(f'--password={url.password}')

    cmd.append(url.database)

    with open(output_file, 'w', encoding='utf-8') as f:
        subprocess.run(cmd, check=True, stdout=f, stderr=subprocess.PIPE, text=True)


def run(output_path='scripts/fonda_snapshot.sql'):
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if _mysqldump_available():
        try:
            export_full_with_mysqldump(str(output_file))
            print(f'Full snapshot exported using mysqldump -> {output_file}')
            return
        except Exception as exc:
            print(f'mysqldump full export failed, fallback to schema-only export: {exc}')

    export_schema_only(str(output_file))
    print(f'Schema-only snapshot generated (mysqldump unavailable) -> {output_file}')


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'scripts/fonda_snapshot.sql'
    run(out)
