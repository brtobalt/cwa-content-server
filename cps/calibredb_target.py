# -*- coding: utf-8 -*-
# Calibre-Web Automated - fork of Calibre-Web
# Copyright (C) 2018-2026 Calibre-Web contributors
# Copyright (C) 2024-2026 Calibre-Web Automated contributors
# SPDX-License-Identifier: GPL-3.0-or-later
# See CONTRIBUTORS for full list of authors.

import os
import sqlite3


def _is_truthy(value):
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def is_content_server_enabled(config_obj=None):
    if _is_truthy(os.environ.get("DISABLE_CALIBRE_CONTENT_SERVER", "false")):
        return False
    if config_obj is None:
        app_db = os.environ.get("CWA_APP_DB_PATH", "/config/app.db")
        if not os.path.isfile(app_db):
            return True
        try:
            with sqlite3.connect(app_db) as conn:
                row = conn.execute(
                    "SELECT COALESCE(config_calibre_content_server_enabled, 1) FROM settings LIMIT 1"
                ).fetchone()
            if row:
                return bool(row[0])
        except sqlite3.Error:
            return True
        return True
    return bool(getattr(config_obj, "config_calibre_content_server_enabled", True))


def get_content_server_port():
    port = os.environ.get("CALIBRE_CONTENT_SERVER_PORT", "8080").strip()
    if not port.isdigit():
        return "8080"
    port_number = int(port)
    if port_number < 1 or port_number > 65535:
        return "8080"
    return str(port_number)


def get_content_server_library_id(library_path=None):
    configured_id = os.environ.get("CALIBRE_CONTENT_SERVER_LIBRARY_ID", "").strip()
    if configured_id:
        return configured_id
    library_path = library_path or os.environ.get("CALIBRE_CONTENT_SERVER_LIBRARY", "/calibre-library")
    return os.path.basename(os.path.normpath(library_path)) or "calibre-library"


def get_content_server_library_url(library_path=None):
    return "http://127.0.0.1:{}/#{}".format(
        get_content_server_port(),
        get_content_server_library_id(library_path),
    )


def get_calibredb_library_target(config_obj=None, library_path=None):
    if is_content_server_enabled(config_obj):
        server_library = os.environ.get("CALIBRE_CONTENT_SERVER_LIBRARY", "").strip()
        return get_content_server_library_url(server_library or library_path)
    if config_obj is not None and hasattr(config_obj, "get_book_path"):
        return config_obj.get_book_path()
    return library_path


def get_calibredb_library_args(config_obj=None, library_path=None):
    return ["--with-library", get_calibredb_library_target(config_obj, library_path)]
