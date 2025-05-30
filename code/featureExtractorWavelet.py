from __future__ import print_function
import numpy as np
from scipy import signal
from parameterSetup import ParameterSetup
from featureExtractor import FeatureExtractor

class FeatureExtractorWavelet(FeatureExtractor):

    def __init__(self):
        self.extractorType = 'wavelet'

    def getFeatures(self, eegSegment, timeStampSegment=0, time_step=0, local_mu=0, local_sigma=0):
        params = ParameterSetup()
        widths = params.waveletWidths
        waveletTransformed = signal.cwt(eegSegment, signal.ricker, widths)
        return waveletTransformed
