#!/usr/bin/env python3
"""Export current DB schema to SQL file.

Prefers mysqldump if available; falls back to SHOW CREATE TABLE via SQLAlchemy.
"""

from pathlib import Path
import shutil
import subprocess
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import text
from sqlalchemy.engine.url import make_url

from app import create_app
from models import db


def _mysqldump_available():
    return shutil.which('mysqldump') is not None


def export_with_mysqldump(output_file):
    app = create_app()
    uri = app.config.get('SQLALCHEMY_DATABASE_URI')
    if not uri:
        raise RuntimeError('SQLALCHEMY_DATABASE_URI not configured')

    url = make_url(uri)
    if not (url.drivername.startswith('mysql') or url.drivername.startswith('mariadb')):
        raise RuntimeError('mysqldump export only supports mysql/mariadb URIs')

    cmd = [
        'mysqldump',
        '--no-data',
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


def export_with_show_create(output_file):
    app = create_app()
    with app.app_context():
        tables = db.session.execute(text('SHOW TABLES')).scalars().all()
        lines = [
            '-- Schema export generated via SHOW CREATE TABLE',
            f'-- Total tables: {len(tables)}',
            '',
            'SET FOREIGN_KEY_CHECKS=0;',
            '',
        ]

        for table in tables:
            row = db.session.execute(text(f'SHOW CREATE TABLE `{table}`')).first()
            if not row:
                continue
            create_stmt = row[1]
            lines.append(f'-- Table: {table}')
            lines.append(f'DROP TABLE IF EXISTS `{table}`;')
            lines.append(f'{create_stmt};')
            lines.append('')

        lines.append('SET FOREIGN_KEY_CHECKS=1;')
        Path(output_file).write_text('\n'.join(lines), encoding='utf-8')


def run(output_path='scripts/fonda_schema_export.sql'):
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if _mysqldump_available():
        try:
            export_with_mysqldump(str(output_file))
            print(f'Schema exported using mysqldump -> {output_file}')
            return
        except Exception as exc:
            print(f'mysqldump failed, fallback to SHOW CREATE TABLE: {exc}')

    export_with_show_create(str(output_file))
    print(f'Schema exported using SQL fallback -> {output_file}')


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else 'scripts/fonda_schema_export.sql'
    run(out)
