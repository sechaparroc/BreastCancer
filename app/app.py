import dash
import dash_labs as dl
import dash_bootstrap_components as dbc



### Dash instance ###
app = dash.Dash(__name__,
    use_pages=True,
    external_stylesheets=[dbc.themes.DARKLY], 
    update_title='Loading...'
)

### Define Navbar and App Layout ###
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink(page["name"], href=page["path"], active="exact"))
        for page in dash.page_registry.values()
        if page["module"] != "pages.not_found_404"
    ],
    brand="Breast Cancer Team-230",
    brand_href="#",
    color="primary",
    dark=True,
)

#Main layout
app.layout = dbc.Container(
    [
        navbar,
        dash.page_container,
    ],
    className="dbc",
    fluid=True,
)


# This call will be used with Gunicorn server
server = app.server

# Testing server, don't use in production, host
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8050, debug=True)
