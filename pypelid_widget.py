import time
import numpy as np
from matplotlib import pyplot as plt

from ipywidgets import Text, Label, HTML, HBox, VBox, Layout, Button, BoundedFloatText, Dropdown, Tab, Output, IntProgress
from ipywidgets.widgets.interaction import show_inline_matplotlib_plots

import instrument_widget, foreground_widget, galaxy_widget, analysis_widget, survey_widget

import pypelid
from pypelid.utils import consts
from pypelid.survey import instrument, phot
from pypelid.spectra import galaxy, linesim

plt.ioff()

class PypelidWidget(object):
    """ """
    def __init__(self):
        self.instrument = instrument_widget.Instrument()
        self.foreground = foreground_widget.Foreground()
        self.galaxy = galaxy_widget.Galaxy()
        self.analysis = analysis_widget.Analysis()
        self.survey = survey_widget.Survey()
        self.progress = IntProgress(bar_style='success')
        self.plot = Output(layout={'width':'800px'})

    def run(self, button):
        """ """
        button.disabled = True

        emission_lines = [
            ('Ha', self.galaxy.widgets['flux_ha'].value * 1e-16),
            ('N2a', self.galaxy.widgets['flux_n2a'].value * 1e-16),
            ('N2b', self.galaxy.widgets['flux_n2b'].value * 1e-16),
            ('S2a', self.galaxy.widgets['flux_s2a'].value * 1e-16),
            ('S2b', self.galaxy.widgets['flux_s2b'].value * 1e-16),
            ('O3a', self.galaxy.widgets['flux_o3a'].value * 1e-16),
            ('O3b', self.galaxy.widgets['flux_o3b'].value * 1e-16),
            ('Hb', self.galaxy.widgets['flux_hb'].value * 1e-16),
            ('O2', self.galaxy.widgets['flux_o2'].value * 1e-16),

        ]


        nexp_list = self.survey.widgets['nexp_red'].value, self.survey.widgets['nexp_blue'].value
        exp_time = self.survey.widgets['exp_time'].value

        with self.plot:
            self.plot.clear_output()
            fig = plt.figure(figsize=(15, 4))

        colors = ['r', 'b']
        limits = []
        config_list = self.instrument.get_config_list()
        for i, config in enumerate(config_list):

            nexp = nexp_list[i]
            if nexp == 0:
                continue

            optics = instrument.Optics(config, seed=time.time()*1e6)

            L = linesim.LineSimulator(optics)

            det_bg = nexp * exp_time * config['darkcurrent'] + config['readnoise']**2

            det_bg += nexp * exp_time * self.foreground.widgets['foreground'].value

            gal = galaxy.Galaxy(
                z=self.galaxy.widgets['redshift'].value,
                bulge_scale=self.galaxy.widgets['bulge_scale'].value,
                disk_scale=self.galaxy.widgets['disk_scale'].value,
                bulge_fraction=self.galaxy.widgets['bulge_fraction'].value,
                axis_ratio=self.galaxy.widgets['axis_ratio'].value,
                velocity_disp=self.galaxy.widgets['velocity_dispersion'].value,
            )

            for line, flux in emission_lines:
                wavelength = (1 + gal.z) * consts.line_list[line]
                signal = phot.flux_to_photon(flux, optics.collecting_area, wavelength)
                signal *= exp_time * nexp
                signal *= optics.transmission(np.array([wavelength]), 1)[0]

                if signal <= 0:
                    continue

                line_variance = signal

                scale = flux / signal

                gal.append_line(
                    wavelength=consts.line_list[line],
                    flux=signal * scale,
                    variance=signal * scale**2,
                    background=det_bg * scale**2
                )
                gal.compute_obs_wavelengths(gal.z)

            if gal.line_count == 0:
                continue

            nloops = self.analysis.widgets['nloops'].value
            self.progress.min=0
            self.progress.max=nloops

            realizations = []
            with self.plot:
                for loop in range(nloops):
                    spectra = L.sample_spectrum(gal)
                    realizations.append(np.array(spectra[0]))
                    self.progress.value = loop

            m = np.mean(realizations, axis=0)
            var = np.var(realizations, axis=0)
            low, high = np.percentile(realizations, [25,75], axis=0)

            x = np.arange(L.npix) * L.dispersion + L.lambda_min

            x0 = gal.get_emission_lines()['wavelength_obs'][0]

            with self.plot:
                # sel = (x > (x0-150)) & (x < (x0 + 150))
                plt.fill_between(x, low, high, color=colors[i], alpha=0.2)
                plt.plot(x, m, lw=2, c=colors[i], zorder=10)
                plt.grid(True)
                limits.append((m.max(), np.mean(var)**.5))

                print "SNR: %g"%np.sqrt(np.sum(m**2/var))

        with self.plot:
            a, b = np.max(limits, axis=0)
            plt.ylim(-b, a+b)
            display(fig)
            # show_inline_matplotlib_plots()

        button.disabled = False

    def show(self):
        """ """
        display(HTML("Pypelid version: %s"%pypelid.__version__))
        tab = Tab([self.galaxy.widget, self.foreground.widget, self.instrument.widget, self.survey.widget, self.analysis.widget])
        tab.set_title(0, "Source")
        tab.set_title(1, "Foreground")
        tab.set_title(2, "Instrument")
        tab.set_title(3, "Survey")
        tab.set_title(4, "Analysis")

        display(tab)

        button = Button(description="Compute", icon='play')

        button.on_click(self.run)

        display(HBox([button, self.progress]))
        display(self.plot)