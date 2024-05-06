from modules import shared, scripts


def grid_reference():
    for data in scripts.scripts_data:
        if data.script_class.__module__ in (
            "scripts.xyz_grid",
            "xyz_grid.py",
        ) and hasattr(data, "module"):
            return data.module

    raise SystemError("Could not find X/Y/Z Plot...")


def xyz_support(cache: dict):
    xyz_grid = grid_reference()

    def apply_field(field):
        def _(p, x, xs):
            cache.update({field: x})

        return _

    def choices_bool():
        return ["False", "True"]

    extra_axis_options = [
        xyz_grid.AxisOption(
            "[Diff. CG] Enable", str, apply_field("enableG"), choices=choices_bool
        ),
        xyz_grid.AxisOption("[Diff. CG] ReCenter", float, apply_field("rc_str")),
        xyz_grid.AxisOption(
            "[Diff. CG] Normalization",
            str,
            apply_field("enableN"),
            choices=choices_bool,
        ),
    ]

    if getattr(shared.opts, "show_center_opt", False):
        extra_axis_options += [
            xyz_grid.AxisOption("[Diff. CG] C", float, apply_field("C")),
            xyz_grid.AxisOption("[Diff. CG] M", float, apply_field("M")),
            xyz_grid.AxisOption("[Diff. CG] Y", float, apply_field("Y")),
            xyz_grid.AxisOption("[Diff. CG] K", float, apply_field("K")),
            xyz_grid.AxisOption("[Diff. CG] L", float, apply_field("L")),
            xyz_grid.AxisOption("[Diff. CG] a", float, apply_field("a")),
            xyz_grid.AxisOption("[Diff. CG] b", float, apply_field("b")),
        ]

    xyz_grid.axis_options.extend(extra_axis_options)
