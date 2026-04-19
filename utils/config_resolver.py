def resolve_config(config):
    base = config.get("base_profile", {})
    ui = config.get("ui_params", {})

    resolved = {}

    for key in set(base.keys()).union(ui.keys()):
        if ui.get(key) is not None:
            resolved[key] = ui[key]
        else:
            resolved[key] = base.get(key)

    resolved["channel_name"] = config.get("channel_name")
    resolved["limits"] = config.get("limits")

    return resolved