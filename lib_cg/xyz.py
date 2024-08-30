from modules import scripts


def grid_reference():
    for data in scripts.scripts_data:
        if data.script_class.__module__ in (
            "scripts.xyz_grid",
            "xyz_grid.py",
        ) and hasattr(data, "module"):
            return data.module

    raise SystemError("Could not find X/Y/Z Plot...")


def xyz_support(cache: dict):

    def apply_field(field):
        def _(p, x, xs):
            cache.update({field: x})

        return _

    def choices_bool():
        return ["False", "True"]

    xyz_grid = grid_reference()

    extra_axis_options = [
        xyz_grid.AxisOption(
            "[Diff. CG] Enable",
            str,
            apply_field("enable"),
            choices=choices_bool,
        ),
        xyz_grid.AxisOption(
            "[Diff. CG] Recenter",
            float,
            apply_field("rc_str"),
        ),
        xyz_grid.AxisOption(
            "[Diff. CG] Normalization",
            str,
            apply_field("normalization"),
            choices=choices_bool,
        ),
    ]

    extra_axis_options.extend(
        [
            xyz_grid.AxisOption("[Diff.CG] C", float, apply_field("C")),
            xyz_grid.AxisOption("[Diff.CG] M", float, apply_field("M")),
            xyz_grid.AxisOption("[Diff.CG] Y", float, apply_field("Y")),
            xyz_grid.AxisOption("[Diff.CG] K", float, apply_field("K")),
            xyz_grid.AxisOption("[Diff.CG] Y'", float, apply_field("Lu")),
            xyz_grid.AxisOption("[Diff.CG] Cb", float, apply_field("Cb")),
            xyz_grid.AxisOption("[Diff.CG] Cr", float, apply_field("Cr")),
        ]
    )

    xyz_grid.axis_options.extend(extra_axis_options)
