from flask import Blueprint, current_app, jsonify
import inspect
import os

docs_bp = Blueprint("docs", __name__, url_prefix="/netcontrol/api/docs")


def collect_routes():
    routes = {}

    for rule in current_app.url_map.iter_rules():

        if rule.endpoint == "static":
            continue

        blueprint = rule.endpoint.split(".")[0] if "." in rule.endpoint else "main"
        view_func = current_app.view_functions[rule.endpoint]

        doc = inspect.getdoc(view_func) or ""
        methods = sorted(rule.methods - {"HEAD", "OPTIONS"})

        route_info = {
            "path": rule.rule,
            "methods": methods,
            "path_params": list(rule.arguments),
            "description": doc
        }

        routes.setdefault(blueprint, []).append(route_info)

    for bp in routes:
        routes[bp] = sorted(routes[bp], key=lambda x: x["path"])

    return routes


# ---------------- JSON ---------------- #

@docs_bp.route("", methods=["GET"])
def docs_json():
    if os.getenv("FLASK_ENV") == "production":
        return {"error": "Docs disabled"}, 403

    return jsonify(collect_routes())


# ---------------- HTML UI ---------------- #

@docs_bp.route("/ui", methods=["GET"])
def docs_ui():
    if os.getenv("FLASK_ENV") == "production":
        return {"error": "Docs disabled"}, 403

    routes = collect_routes()

    html_blocks = []

    for blueprint, items in routes.items():
        rows = ""
        for r in items:
            methods = ", ".join(r["methods"])
            params = ", ".join(r["path_params"]) if r["path_params"] else "-"
            description = r["description"] or "-"

            rows += f"""
                <tr>
                    <td>{r['path']}</td>
                    <td>{methods}</td>
                    <td>{params}</td>
                    <td>{description}</td>
                </tr>
            """

        html_blocks.append(f"""
            <h2>{blueprint}</h2>
            <table>
                <tr>
                    <th>Path</th>
                    <th>Methods</th>
                    <th>Path Params</th>
                    <th>Description</th>
                </tr>
                {rows}
            </table>
        """)

    return f"""
    <html>
    <head>
        <title>API Docs</title>
        <style>
            body {{
                font-family: monospace;
                background: #0f172a;
                color: #e2e8f0;
                padding: 40px;
            }}
            h1 {{
                margin-bottom: 40px;
            }}
            h2 {{
                margin-top: 40px;
                color: #38bdf8;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            th, td {{
                border: 1px solid #334155;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background: #1e293b;
            }}
            tr:hover {{
                background: #1e293b;
            }}
        </style>
    </head>
    <body>
        <h1>API Documentation</h1>
        {''.join(html_blocks)}
    </body>
    </html>
    """