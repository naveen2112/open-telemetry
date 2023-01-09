from dash import html
import dash

dash.register_page(__name__)

#This is used to remove the page not found in index page,
#In future this will be removed, as report will be set as front page as index
layout = html.H1("")