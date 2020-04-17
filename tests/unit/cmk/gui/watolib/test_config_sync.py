#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2019 tribe29 GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

import sys
import tarfile
# Explicitly check for Python 3 (which is understood by mypy)
if sys.version_info[0] >= 3:
    from pathlib import Path  # pylint: disable=import-error
else:
    from pathlib2 import Path

import pytest  # type: ignore[import]

import cmk.utils.paths

import cmk.gui.config as config
import cmk.gui.watolib.activate_changes as activate_changes
import cmk.gui.watolib.config_sync as config_sync


def _create_test_sync_config():
    """Create some config files to be synchronized"""
    conf_dir = Path(cmk.utils.paths.check_mk_config_dir, "wato")
    conf_dir.mkdir(parents=True, exist_ok=True)
    with conf_dir.joinpath("hosts.mk").open("w", encoding="utf-8") as f:
        f.write(u"all_hosts = []\n")

    gui_conf_dir = Path(cmk.utils.paths.default_config_dir) / "multisite.d" / "wato"
    gui_conf_dir.mkdir(parents=True, exist_ok=True)
    with gui_conf_dir.joinpath("global.mk").open("w", encoding="utf-8") as f:
        f.write(u"# 123\n")


@pytest.mark.parametrize(
    "edition_short,snapshot_manager_class",
    [
        ("cre", "CRESnapshotManager"),
        #("cme", "CMESnapshotManager"),
    ])
def test_generate_snapshot(edition_short, snapshot_manager_class, monkeypatch, tmp_path, with_user):
    user_id = with_user[0]
    _create_test_sync_config()

    # TODO: Make this better testable: Extract site snapshot setting calculation
    activation_manager = activate_changes.ActivateChangesManager()
    activation_manager._sites = ["unit", "unit_remote_1"]
    activation_manager._changes_by_site = {"unit": [], "unit_remote_1": []}
    activation_manager._activation_id = "123"
    monkeypatch.setattr(
        config, "sites", {
            "unit": {
                'alias': u'Der Master',
                'disable_wato': True,
                'disabled': False,
                'insecure': False,
                'multisiteurl': '',
                'persist': False,
                'replicate_ec': False,
                'replication': '',
                'timeout': 10,
                'user_login': True,
            },
            "unit_remote_1": {
                'alias': u'unit_remote_1',
                'disable_wato': True,
                'disabled': False,
                'insecure': False,
                'multisiteurl': 'http://localhost/unit_remote_1/check_mk/',
                'persist': False,
                'replicate_ec': True,
                'replication': 'slave',
                'secret': 'watosecret',
                'url_prefix': '/unit_remote_1/',
                'user_login': True,
            }
        })

    site_snapshot_settings = activation_manager._site_snapshot_settings()

    # Now create the snapshot
    work_dir = tmp_path / "activation"
    snapshot_manager = activate_changes.SnapshotManagerFactory.factory(
        str(work_dir), site_snapshot_settings)
    assert snapshot_manager.__class__.__name__ == snapshot_manager_class
    snapshot_manager.generate_snapshots()

    # And now check the resulting snapshot contents
    snapshot_settings = site_snapshot_settings["unit_remote_1"]
    assert Path(snapshot_settings.snapshot_path).exists()
    assert not Path(snapshot_settings.work_dir).exists()

    unpack_dir = tmp_path / "snapshot_unpack"
    with tarfile.open(snapshot_settings.snapshot_path, "r") as t:
        t.extractall(str(unpack_dir))

    assert sorted(f.name for f in unpack_dir.iterdir()) == sorted([
        "auth.secret.tar",
        "auth.serials.tar",
        "check_mk.tar",
        "dcd.tar",
        "diskspace.tar",
        "htpasswd.tar",
        "liveproxyd.tar",
        "mkeventd_mkp.tar",
        "mkeventd.tar",
        "mknotify.tar",
        "multisite.tar",
        "sitespecific.tar",
        "usersettings.tar",
    ])

    expected_files = {
        'mkeventd_mkp.tar': [],
        'multisite.tar': ["global.mk", "users.mk"],
        'usersettings.tar': [user_id],
        'mkeventd.tar': [],
        'check_mk.tar': ["hosts.mk", "contacts.mk"],
        'htpasswd.tar': ["htpasswd"],
        'liveproxyd.tar': [],
        'sitespecific.tar': ['sitespecific.mk'],
        'auth.secret.tar': [],
        'dcd.tar': [],
        'auth.serials.tar': ["auth.serials"],
        'mknotify.tar': [],
        'diskspace.tar': [],
    }

    # And now check the subtar contents
    for subtar in unpack_dir.iterdir():
        subtar_unpack_dir = unpack_dir / subtar.stem
        subtar_unpack_dir.mkdir(parents=True, exist_ok=True)

        with tarfile.open(str(subtar), "r") as s:
            s.extractall(str(subtar_unpack_dir))

        files = sorted(str(f.relative_to(subtar_unpack_dir)) for f in subtar_unpack_dir.iterdir())

        assert sorted(expected_files[subtar.name]) == files, \
            "Subtar %s has wrong files" % subtar.name


@pytest.mark.parametrize("master, slave, result", [
    pytest.param({"first": {
        "customer": "tribe"
    }}, {
        "first": {
            "customer": "tribe"
        },
        "second": {
            "customer": "tribe"
        }
    }, {"first": {
        "customer": "tribe"
    }},
                 id="Delete user from master"),
    pytest.param(
        {
            "cmkadmin": {
                "customer": None,
                "notification_rules": [{
                    "description": "adminevery"
                }]
            },
            "first": {
                "customer": "tribe",
                "notification_rules": []
            }
        }, {}, {
            "cmkadmin": {
                "customer": None,
                "notification_rules": [{
                    "description": "adminevery"
                }]
            },
            "first": {
                "customer": "tribe",
                "notification_rules": []
            }
        },
        id="New users"),
    pytest.param(
        {
            "cmkadmin": {
                "customer": None,
                "notification_rules": [{
                    "description": "all admins"
                }]
            },
            "first": {
                "customer": "tribe",
                "notification_rules": []
            }
        }, {
            "cmkadmin": {
                "customer": None,
                "notification_rules": [{
                    "description": "adminevery"
                }]
            },
            "first": {
                "customer": "tribe",
                "notification_rules": [{
                    "description": "Host on fire"
                }]
            }
        }, {
            "cmkadmin": {
                "customer": None,
                "notification_rules": [{
                    "description": "all admins"
                }]
            },
            "first": {
                "customer": "tribe",
                "notification_rules": [{
                    "description": "Host on fire"
                }]
            }
        },
        id="Update Global user notifications. Retain Customer user notifications"),
])
def test_update_contacts_dict(master, slave, result):
    assert config_sync._update_contacts_dict(master, slave) == result