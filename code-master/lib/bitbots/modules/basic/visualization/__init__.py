def get_visualization_modules():
    try:
        import cairo
        return ["bitbots.modules.basic.visualization.visualization_module",
                "bitbots.modules.basic.visualization.ball_visualization_module",
                "bitbots.modules.basic.visualization.goal_visualization_module",
                "bitbots.modules.basic.visualization.legend_window_module",
        ]
    except ImportError:
        from bitbots.debug import Scope
        debug = Scope("Visualization")
        debug.warning("Deactivate Visualition: import of cairo faild")
        return []