import pytest  # type: ignore

# Triggers plugin loading of plugins.wato which registers all the plugins
import cmk.gui.wato  # pylint: disable=unused-import

from cmk.gui.exceptions import MKGeneralException
import cmk.gui.watolib.rulesets as rulesets
import cmk.gui.watolib.hosts_and_folders as hosts_and_folders


def _rule(ruleset_name):
    ruleset = rulesets.Ruleset(ruleset_name)
    return rulesets.Rule(hosts_and_folders.Folder.root_folder(), ruleset)


@pytest.mark.parametrize(
    "ruleset_name,default_value",
    [
        # non-binary host ruleset
        ("inventory_processes_rules", None),
        # binary host ruleset
        ("only_hosts", True),
        # non-binary service ruleset
        ("checkgroup_parameters:local", None),
        # binary service ruleset
        ("clustered_services", True),
    ])
def test_rule_initialize(register_builtin_html, ruleset_name, default_value):
    rule = _rule(ruleset_name)
    assert rule.tag_specs == []
    assert rule.host_list == []
    assert rule.item_list is None
    assert rule.rule_options == {}
    assert rule.value == default_value


def test_rule_from_config_unhandled_format():
    rule = _rule("inventory_processes_rules")
    with pytest.raises(MKGeneralException, match="Invalid rule"):
        rule.from_config([])

    with pytest.raises(MKGeneralException, match="Invalid rule"):
        rule.from_config((None,))


@pytest.mark.parametrize(
    "rule_options",
    [
        {
            "disabled": True
        },
        None,
    ],
)
@pytest.mark.parametrize(
    "ruleset_name,rule_spec,expected_attributes",
    [
        # non-binary host ruleset
        (
            "inventory_processes_rules",
            ("VAL", ["HOSTLIST"]),
            {
                "value": "VAL",
                "item_list": None,
                "host_list": ["HOSTLIST"],
                "tag_specs": [],
            },
        ),
        (
            "inventory_processes_rules",
            ("VAL", ["tag", "specs"], ["HOSTLIST"]),
            {
                "value": "VAL",
                "item_list": None,
                "host_list": ["HOSTLIST"],
                "tag_specs": ["tag", "specs"],
            },
        ),
        # binary host ruleset
        ("only_hosts", (["HOSTLIST"],), {
            "value": True,
            "item_list": None,
            "host_list": ["HOSTLIST"],
            "tag_specs": [],
        }),
        ("only_hosts", (
            rulesets.NEGATE,
            ["HOSTLIST"],
        ), {
            "value": False,
            "item_list": None,
            "host_list": ["HOSTLIST"],
            "tag_specs": [],
        }),
        # non-binary service ruleset
        ("checkgroup_parameters:local", ("VAL", ["HOSTLIST"], ["SVC", "LIST"]), {
            "value": "VAL",
            "item_list": ["SVC", "LIST"],
            "host_list": ["HOSTLIST"],
            "tag_specs": [],
        }),
        # binary service ruleset
        ("clustered_services", (["HOSTLIST"], ["SVC", "LIST"]), {
            "value": True,
            "item_list": ["SVC", "LIST"],
            "host_list": ["HOSTLIST"],
            "tag_specs": [],
        }),
        ("clustered_services", (rulesets.NEGATE, ["HOSTLIST"], ["SVC", "LIST"]), {
            "value": False,
            "item_list": ["SVC", "LIST"],
            "host_list": ["HOSTLIST"],
            "tag_specs": [],
        }),
    ])
def test_rule_from_config_tuple(ruleset_name, rule_spec, expected_attributes, rule_options):
    if rule_options is not None:
        rule_spec = rule_spec + (rule_options,)

    rule = _rule(ruleset_name)
    rule.from_config(rule_spec)

    for key, val in expected_attributes.items():
        assert getattr(rule, key) == val

    if rule_options is not None:
        assert rule.rule_options == rule_options
    else:
        assert rule.rule_options == {}


@pytest.mark.parametrize(
    "rule_options",
    [
        {
            "disabled": True
        },
        None,
    ],
)
@pytest.mark.parametrize(
    "ruleset_name,rule_spec,expected_attributes",
    [
        # non-binary host ruleset
        (
            "inventory_processes_rules",
            {
                "value": "VAL",
                "conditions": {
                    "host_specs": ["HOSTLIST"],
                },
            },
            {
                "value": "VAL",
                "item_list": None,
                "host_list": ["HOSTLIST"],
                "tag_specs": [],
            },
        ),
        (
            "inventory_processes_rules",
            {
                "value": "VAL",
                "conditions": {
                    "host_tags": ["tag", "specs"],
                    "host_specs": ["HOSTLIST"],
                },
            },
            {
                "value": "VAL",
                "item_list": None,
                "host_list": ["HOSTLIST"],
                "tag_specs": ["tag", "specs"],
            },
        ),
        # binary host ruleset
        ("only_hosts", {
            "conditions": {
                "host_specs": ["HOSTLIST"],
            },
        }, {
            "value": True,
            "item_list": None,
            "host_list": ["HOSTLIST"],
            "tag_specs": [],
        }),
        ("only_hosts", {
            "negate": True,
            "conditions": {
                "host_specs": ["HOSTLIST"],
            },
        }, {
            "value": False,
            "item_list": None,
            "host_list": ["HOSTLIST"],
            "tag_specs": [],
        }),
        # non-binary service ruleset
        ("checkgroup_parameters:local", {
            "value": "VAL",
            "conditions": {
                "host_specs": ["HOSTLIST"],
                "service_specs": ["SVC", "LIST"],
            },
        }, {
            "value": "VAL",
            "item_list": ["SVC", "LIST"],
            "host_list": ["HOSTLIST"],
            "tag_specs": [],
        }),
        # binary service ruleset
        ("clustered_services", {
            "conditions": {
                "host_specs": ["HOSTLIST"],
                "service_specs": ["SVC", "LIST"],
            },
        }, {
            "value": True,
            "item_list": ["SVC", "LIST"],
            "host_list": ["HOSTLIST"],
            "tag_specs": [],
        }),
        ("clustered_services", {
            "negate": True,
            "conditions": {
                "host_specs": ["HOSTLIST"],
                "service_specs": ["SVC", "LIST"],
            },
        }, {
            "value": False,
            "item_list": ["SVC", "LIST"],
            "host_list": ["HOSTLIST"],
            "tag_specs": [],
        }),
    ])
def test_rule_from_config_dict(ruleset_name, rule_spec, expected_attributes, rule_options):
    rule_spec = rule_spec.copy()
    if rule_options is not None:
        rule_spec["options"] = rule_options

    rule = _rule(ruleset_name)
    rule.from_config(rule_spec)

    for key, val in expected_attributes.items():
        assert getattr(rule, key) == val

    if rule_options is not None:
        assert rule.rule_options == rule_options
    else:
        assert rule.rule_options == {}

    # test for synchronous to_dict on the way
    assert rule.to_dict_config() == rule_spec


def test_rule_clone():
    rule = _rule("clustered_services")
    rule.from_config({
        "negate": True,
        "conditions": {
            "host_specs": ["HOSTLIST"],
            "service_specs": ["SVC", "LIST"],
        },
    })

    cloned_rule = rule.clone()

    assert rule.to_dict_config() == cloned_rule.to_dict_config()
    assert rule.folder == cloned_rule.folder
    assert rule.ruleset == cloned_rule.ruleset
