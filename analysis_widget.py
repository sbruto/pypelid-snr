from ipywidgets import Text, Label, HTML, HBox, VBox, Layout, Button, BoundedFloatText, BoundedIntText, Dropdown, Output


class Analysis(object):
    style = {'description_width': '200px'}
    layout = {'width': '300px'}

    widgets = {
        'nloops': BoundedIntText(value=1000, min=1, max=1e6, step=1, description='Numer of realizations'),
    }

    def __init__(self):
        """ """
        for key, widget in self.widgets.items():
            widget.style = self.style
            widget.layout = self.layout

        self.widget = VBox([HTML('Statistics'), self.widgets['nloops']])
