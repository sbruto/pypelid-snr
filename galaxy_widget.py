from ipywidgets import Text, Label, HTML, HBox, VBox, Layout, Button, BoundedFloatText, Dropdown


class Galaxy(object):
    """ """

    style = {'description_width': '200px'}
    layout = {'width': '300px'}

    widgets = {
        'redshift': BoundedFloatText(value=1, min=0, max=10, step=0.1, description="Redshift"),
        'bulge_scale': BoundedFloatText(value=0.5, min=0, max=10, step=0.1, description="bulge scale (arcsec)"),
        'disk_scale': BoundedFloatText(value=0.5, min=0, max=10, step=0.1, description="disk scale (arcsec)"),
        'bulge_fraction': BoundedFloatText(value=1, min=0, max=1, step=0.1, description="bulge fraction"),
        'axis_ratio': BoundedFloatText(value=1, min=0, max=1, step=0.1, description="axis ratio"),
        'velocity_dispersion': BoundedFloatText(value=0, min=0, max=1000, step=0.1, description="velocity dispersion (km/s)"),
        'flux_ha': BoundedFloatText(value=2, min=0, max=1000, step=0.1, description='Flux H$\\alpha$ 6565 ($10^{16}$ erg/cm2/s):'),
        'n2_ha_ratio': BoundedFloatText(value=0, min=0, max=10, step=0.1, description='NII/H$\\alpha$:'),
        'flux_n2a': BoundedFloatText(value=0, min=0, max=10, step=0.1, description='Flux NIIa 6550 ($10^{16}$ erg/cm2/s):'),
        'flux_n2b': BoundedFloatText(value=0, min=0, max=10, step=0.1, description='Flux NIIb 6585 ($10^{16}$ erg/cm2/s):'),
    }

    def __init__(self):
        for key, widget in self.widgets.items():
            widget.style = self.style
            widget.layout = self.layout

        self.widgets['flux_ha'].observe(self.flux_ha_change, names='value')
        self.widgets['n2_ha_ratio'].observe(self.n2_ha_ratio_change, names='value')
        self.widgets['flux_n2a'].observe(self.flux_n2a_change, names='value')
        self.widgets['flux_n2b'].observe(self.flux_n2b_change, names='value')

        title = HTML("<h2>Galaxy</h2>")
        n2box = HBox([self.widgets['n2_ha_ratio'], self.widgets['flux_n2a'], self.widgets['flux_n2b']])

        elements = []
        elements += [self.widgets['redshift']]
        elements += [HTML("<b>Size</b>"), self.widgets['bulge_scale'], self.widgets['disk_scale'], self.widgets['bulge_fraction'], self.widgets['axis_ratio']]
        elements += [HTML("<b>Emission lines</b>"), self.widgets['velocity_dispersion'], self.widgets['flux_ha'], n2box]

        self.widget = VBox(elements)


    def n2_ha_ratio_change(self, change):
        y = self.widgets['n2_ha_ratio'].value * self.widgets['flux_ha'].value
        self.widgets['flux_n2a'].value = y / 4.
        self.widgets['flux_n2b'].value = y * 3 / 4.

    flux_ha_change = n2_ha_ratio_change

    def flux_n2b_change(self, change):
        self.widgets['flux_n2a'].value = self.widgets['flux_n2b'].value / 3
        self.widgets['n2_ha_ratio'].value = (self.widgets['flux_n2a'].value + self.widgets['flux_n2b'].value) / self.widgets['flux_ha'].value

    def flux_n2a_change(self, change):
        self.widgets['flux_n2b'].value = self.widgets['flux_n2a'].value * 3.
        self.widgets['n2_ha_ratio'].value = (self.widgets['flux_n2a'].value + self.widgets['flux_n2b'].value) / self.widgets['flux_ha'].value

