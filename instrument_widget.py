import os
from ipywidgets import Text, Label, HTML, HBox, VBox, Layout, Button, BoundedFloatText, BoundedIntText, Dropdown, Output
from ipywidgets.widgets.interaction import show_inline_matplotlib_plots

import numpy as np

from pypelid import utils
from pypelid.survey import instrument

from matplotlib import pyplot as plt

configurations = {
    'Euclid NISP Red': {
            'exp_time': 565,
            'nexp': 4,
            'collecting_surface_area': 10000,
            'pix_size': 0.3,
            'pix_disp': 13.4,
            'psf_amp': 0.781749,
            'psf_sig1': 0.84454,
            'psf_sig2': 3.6498,
            'readnoise': 8.87,
            'darkcurrent': 0.019,
            'transmission': 'red_transmission.txt'
    },
    'Euclid NISP Blue': {
            'exp_time': 565,
            'nexp': 4,
            'collecting_surface_area': 10000,
            'pix_size': 0.3,
            'pix_disp': 13.4,
            'psf_amp': 0.781749,
            'psf_sig1': 0.84454,
            'psf_sig2': 3.6498,
            'readnoise': 8.87,
            'darkcurrent': 0.019,
            'transmission': 'blue_transmission.txt'
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
    return filelist


class Instrument(object):
    """ """
    style = {'description_width': '150px'}
    layout = {'width': '400px'}

    widgets = {
        'config': Dropdown(options=configurations.keys(), description='Configurations:'),
        'exp_time': BoundedFloatText(value=565, min=0, max=1e6, step=5, description='Exposure time (sec)'),
        'nexp': BoundedIntText(value=4, min=1, max=1000, step=1, description='Number or exposures'),
        'collecting_surface_area': BoundedFloatText(value=10000, min=0, max=1e6, step=10, description='Collecting area (cm2)'),
        'pix_size': BoundedFloatText(value=0.3, min=0, max=10, step=0.1, description='Pixel size (arcsec)'),
        'pix_disp': BoundedFloatText(value=13.4, min=0, max=100, step=0.1, description='Dispersion (A/pixel)'),
        'psf_amp': BoundedFloatText(value=0.781749, min=0, max=20, step=0.1, description='PSF amplitude'),
        'psf_sig1': BoundedFloatText(value=0.84454, min=0, max=20, step=0.1, description='PSF sigma 1 (pixels)'),
        'psf_sig2': BoundedFloatText(value=3.6498, min=0, max=20, step=0.1, description='PSF sigma 2 (pixels)'),
        'readnoise': BoundedFloatText(value=8.87, min=0, max=100, step=0.1, description='read noise (electrons)'),
        'darkcurrent': BoundedFloatText(value=0.019, min=0, max=100, step=0.1, description='dark current (elec/s/pix)'),
        'transmission': Dropdown(options=get_transmission_files(), description='Transmission table'),
        'plot': Output(),
    }

    def __init__(self):
        for key, widget in self.widgets.items():
            widget.style = self.style
            widget.layout = self.layout

        self.widgets['config'].observe(self.change_config, names='value')
        self.widgets['transmission'].observe(self.plot_transmission, names='value')
        for key, widget in self.widgets.items():
            if key in ['config','transmission','exp_time','nexp']:
                continue
            widget.observe(self.modify, names='value')

        title = HTML('<h2>Instrument<h2>')
        elements = []
        elements.append(self.widgets['config'])
        elements += [HTML('<b>Exposure</b>'), self.widgets['nexp'], self.widgets['exp_time']]
        elements += [HTML('<b>Optics</b>'), self.widgets['collecting_surface_area'], self.widgets['pix_size'], self.widgets['pix_disp'], self.widgets['transmission']]
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
        key = change['new']
        self.update(**configurations[key])

    def modify(self, change):
        """ """
        self.widgets['config'].value = 'custom'


    def plot_transmission(self, change=None):
        """ """
        if change:
            self.widgets['config'].value = 'custom'
        path = os.path.join(TRANSMISSION_DIR, self.widgets['transmission'].value)
        if not os.path.exists(path):
            return
        x, y = np.loadtxt(path, unpack=True)

        sel = y > (y.max()/10.)
        x = x[sel]
        y = y[sel]

        self.widgets['plot'].clear_output()
        with self.widgets['plot']:
            plt.plot(x, y, c='navy', lw=2, label=self.widgets['transmission'].value)
            plt.grid()
            plt.legend()
            plt.xlabel("Wavelength")
            plt.ylabel("Efficiency")
            show_inline_matplotlib_plots()

    def plot_psf(self, change=None):
        """ """
        pass

    def get_lambda_range(self):
        """"""
        path = os.path.join(TRANSMISSION_DIR, self.widgets['transmission'].value)
        x, y = np.loadtxt(path , unpack=True)
        sel = y > (y.max()/10.)
        x = x[sel]
        return x.min(), x.max()

    def get_config(self):
        """ """
        config = {}
        config['exp_time'] = self.widgets['exp_time'].value
        config['nexp'] = self.widgets['nexp'].value
        config['collecting_surface_area'] = self.widgets['collecting_surface_area'].value
        config['pix_size'] = self.widgets['pix_size'].value
        config['pix_disp'] = [1, self.widgets['pix_disp'].value, 1]
        config['psf_amp'] = self.widgets['psf_amp'].value
        config['psf_sig1'] = self.widgets['psf_sig1'].value
        config['psf_sig2'] = self.widgets['psf_sig2'].value
        config['readnoise'] = self.widgets['readnoise'].value
        config['darkcurrent'] = self.widgets['darkcurrent'].value
        config['grism_1_transmission'] = os.path.join(TRANSMISSION_DIR, self.widgets['transmission'].value)
        config['grism_0_transmission'] = os.path.join(TRANSMISSION_DIR, self.widgets['transmission'].value)
        config['grism_2_transmission'] = os.path.join(TRANSMISSION_DIR, self.widgets['transmission'].value)
        config['in_dir'] = '.'
        config['lambda_range'] = self.get_lambda_range()
        return config
