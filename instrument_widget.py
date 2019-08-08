import os
from ipywidgets import Text, Label, HTML, HBox, VBox, Layout, Button, BoundedFloatText, BoundedIntText, Dropdown, Output
from ipywidgets.widgets.interaction import show_inline_matplotlib_plots

import numpy as np

from pypelid import utils
from pypelid.survey import instrument

from matplotlib import pyplot as plt

configurations = {
    'Euclid NISP': {
            'collecting_surface_area': 10000,
            'pix_size': 0.3,
            'pix_disp': 13.4,
            'psf_amp': 0.781749,
            'psf_sig1': 0.84454,
            'psf_sig2': 3.6498,
            'readnoise': 8.87,
            'darkcurrent': 0.019,
            'transmission_red': 'red_transmission.txt',
            'transmission_blue': 'blue_transmission.txt',
    },
    'custom': {},
}

TRANSMISSION_DIR='in'

def get_transmission_files(dir=TRANSMISSION_DIR):
    filelist = []
    if not os.path.exists(dir):
        return filelist
    for filename in os.listdir(dir):
        if filename.endswith("txt"):
            filelist.append(filename)
    filelist += ['none']
    return filelist


class Instrument(object):
    """ """
    style = {'description_width': '150px'}
    layout = {'width': '400px'}

    widgets = {
        'config': Dropdown(options=configurations.keys(), description='Configurations:'),
        'collecting_surface_area': BoundedFloatText(value=10000, min=0, max=1e6, step=10, description='Collecting area (cm2)'),
        'pix_size': BoundedFloatText(value=0.3, min=0, max=10, step=0.1, description='Pixel size (arcsec)'),
        'pix_disp': BoundedFloatText(value=13.4, min=0, max=100, step=0.1, description='Dispersion (A/pixel)'),
        'psf_amp': BoundedFloatText(value=0.781749, min=0, max=20, step=0.1, description='PSF amplitude'),
        'psf_sig1': BoundedFloatText(value=0.84454, min=0, max=20, step=0.1, description='PSF sigma 1 (pixels)'),
        'psf_sig2': BoundedFloatText(value=3.6498, min=0, max=20, step=0.1, description='PSF sigma 2 (pixels)'),
        'readnoise': BoundedFloatText(value=8.87, min=0, max=100, step=0.1, description='read noise (electrons)'),
        'darkcurrent': BoundedFloatText(value=0.019, min=0, max=100, step=0.1, description='dark current (elec/s/pix)'),
        'transmission_red': Dropdown(options=get_transmission_files(), description='Red grism transmission'),
        'transmission_blue': Dropdown(options=get_transmission_files(), description='Blue grism transmission'),
        'plot': Output(),
    }

    def __init__(self):
        self._set_custom = True

        for key, widget in self.widgets.items():
            widget.style = self.style
            widget.layout = self.layout

        self.update(**configurations[self.widgets['config'].value])

        self.widgets['config'].observe(self.change_config, names='value')
        self.widgets['transmission_red'].observe(self.plot_transmission, names='value')
        self.widgets['transmission_blue'].observe(self.plot_transmission, names='value')

        for key, widget in self.widgets.items():
            if key in ['config', 'transmission_red', 'transmission_blue']:
                continue
            widget.observe(self.modify, names='value')

        title = HTML('<h2>Instrument<h2>')
        elements = []
        elements.append(self.widgets['config'])
        elements += [HTML('<b>Optics</b>'), self.widgets['collecting_surface_area'], self.widgets['pix_size'], self.widgets['pix_disp'],
        self.widgets['transmission_red'],self.widgets['transmission_blue']]
        elements += [HTML('<b>PSF</b>'), self.widgets['psf_amp'], self.widgets['psf_sig1'], self.widgets['psf_sig2']]
        elements += [HTML('<b>Detector</b>'), self.widgets['readnoise'], self.widgets['darkcurrent']]
        self.widget = HBox([VBox(elements), self.widgets['plot']])

        self.plot_transmission()

    def update(self, **kwargs):
        """ """
        for key, value in kwargs.items():
            if key in self.widgets:
                self.widgets[key].value = value

    def change_config(self, change):
        """ """
        self._set_custom = False
        key = change['new']
        self.update(**configurations[key])
        self._set_custom = True

    def modify(self, change):
        """ """
        if not self._set_custom:
            return
        self.widgets['config'].value = 'custom'


    def plot_transmission(self, change=None):
        """ """
        if change:
            self.widgets['config'].value = 'custom'

        colors = {'transmission_red':'r', 'transmission_blue': 'b'}

        with self.widgets['plot']:

            self.widgets['plot'].clear_output()

            for key in ['transmission_red', 'transmission_blue']:

                if not self.widgets[key].value:
                    continue

                if self.widgets[key].value == 'none':
                    continue

                path = os.path.join(TRANSMISSION_DIR, self.widgets[key].value)
                if not os.path.exists(path):
                    continue
                x, y = np.loadtxt(path, unpack=True)

                sel, = np.where(y > (y.max()/10.))
                a = max(0, sel[0] - 10)
                b = min(len(x), sel[-1] + 10)
                x = x[a:b]
                y = y[a:b]

                plt.plot(x, y, c=colors[key], lw=2, label=self.widgets[key].value)
            plt.grid()
            plt.legend()
            plt.xlabel("Wavelength")
            plt.ylabel("Efficiency")
            show_inline_matplotlib_plots()

    def plot_psf(self, change=None):
        """ """
        pass

    def get_lambda_range(self, key):
        """"""
        path = os.path.join(TRANSMISSION_DIR, self.widgets[key].value)
        x, y = np.loadtxt(path , unpack=True)
        sel = y > (y.max()/10.)
        x = x[sel]
        return x.min(), x.max()

    def get_config_list(self):
        """ """
        config_list = []
        for key in 'transmission_red', 'transmission_blue':
            config = {}
            config['collecting_surface_area'] = self.widgets['collecting_surface_area'].value
            config['pix_size'] = self.widgets['pix_size'].value
            config['pix_disp'] = [1, self.widgets['pix_disp'].value, 1]
            config['psf_amp'] = self.widgets['psf_amp'].value
            config['psf_sig1'] = self.widgets['psf_sig1'].value
            config['psf_sig2'] = self.widgets['psf_sig2'].value
            config['readnoise'] = self.widgets['readnoise'].value
            config['darkcurrent'] = self.widgets['darkcurrent'].value
            config['grism_1_transmission'] = os.path.join(TRANSMISSION_DIR, self.widgets[key].value)
            config['grism_0_transmission'] = os.path.join(TRANSMISSION_DIR, self.widgets[key].value)
            config['grism_2_transmission'] = os.path.join(TRANSMISSION_DIR, self.widgets[key].value)
            config['in_dir'] = '.'
            config['lambda_range'] = self.get_lambda_range(key)
            config_list.append(config)
        return config_list
