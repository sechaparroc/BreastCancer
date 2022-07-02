import dash
import dash_labs as dl
import dash_bootstrap_components as dbc
from dash import html


### Dash instance ###
app = dash.Dash(__name__,
    use_pages=True,
    update_title='Loading...'
)

### Define Navbar and App Layout ###
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(page["name"], href=page["path"], active="exact"))
        for page in dash.page_registry.values()
        if page["module"] != "pages.not_found_404"
    ],
    brand="CANCER SEARCH",
    brand_href="/",
    color="dark",
    dark=True,
    style={"height":180, "fontSize":20},
    brand_style={"fontSize":35, "color":"hotpink"}
)

footer = html.Footer(
    children=[
        dbc.Nav(
        [
        dbc.NavItem(dbc.NavLink("All rights reserved", active=True, href="#")),
        ],
        style={"height":60, "fontSize":20, "color":"dark"},
        )
    ],
)

#Main layout
app.layout = dbc.Container(
    [
        navbar,
        dash.page_container,
        footer,
    ],
    className="dbc",
    fluid=True,
)


# This call will be used with Gunicorn server
server = app.server

# Testing server, don't use in production, host
if __name__ == "__main__":
    #app.run(host='0.0.0.0', port=8051, debug=True)
    app.run(debug=True)
