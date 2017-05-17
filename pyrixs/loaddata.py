""" Methods for loading data.
This is separated for process1d and process2d in order to facilitate loading
data from different sources.
"""

import numpy as np
import matplotlib.pyplot as plt
import h5py
from nexusformat.nexus import nxload

def image_to_photon_events(image):
    """ Convert 2D image into photon_events

    Parameters
    -----------
    image : np.array
        2D image

    Returns
    -----------
    photon_events : np.array
        three column x, y, I photon locations and intensities
    """
    X, Y = np.meshgrid(np.arange(image.shape[1]) + 0.5, np.arange(image.shape[0]) + 0.5)
    return np.vstack((X.ravel(), Y.ravel(), image.ravel())).transpose()

def photon_events_to_image(photon_events):
    """ Convert photon_events into image. Opposite of image_to_photon_events"""
    x = photon_events[:,0]
    y = photon_events[:,1]
    I = photon_events[:,2]

    xind = (x-0.5).astype(int)
    yind = (y-0.5).astype(int)
    image = np.zeros((yind.max()+1, xind.max()+1))
    image[yind, xind] = I
    return image

def load_nxfile(filename):
    """Load nxs data from Soleil. Each file may
    contain more than 1 scan.
    
    Parameters
    -----------
    nxs file : string
        Contains multiple 2D images

    Returns
    -----------
    image : np.array
        Average 2D images from nxs file
    """
    fload = nxload(filename)

    for key in fload:
        if 'scan' in key:
            lb = key
                
    data = fload[lb].scan_data.data_01.nxdata
    
    print('NXS file {:s} contains {:d} image(s).'.format(filename.split('/')[-1],len(data)))
        
    image = []
    for i in range(len(data)):
          image.append(data[i])

    return image
                  
def get_image(filename):
    """Return list of photon events as X,Y,I columns
    where I is the number of photons

    files with .h5 are assumed to be SLS format
    
    files with .nxs are assumed to be Soleil format
    """
    if filename[-3:].lower() == '.h5':
        h5file = h5py.File(filename)
        XY = h5file['entry']['analysis']['events'].value
        I = np.ones((XY.shape[0],1))
        return np.hstack((XY, I))
    elif filename[-4:].lower() == '.tif':
        image = plt.imread(filename)
        return image_to_photon_events(image)
    elif filename[-4:].lower() == '.nxs':
        image = load_nxfile(filename)
        return [image_to_photon_events(im) for im in image]
    else:
        print('Unknown file extention {}'.format(filename))

def get_spectrum(filename):
    """ return spectrum as
    pixel intensity
    shape rows, 2

    .txt are compatible with np.loadtxt
    """
    if filename[-4:] == '.txt':
        return np.loadtxt(filename)
    elif filename[-4:] == '.dat':
        return np.loadtxt(filename)
    elif filename[-4:] == '.spec':
        return np.loadtxt(filename)
    elif filename[-3:].lower() == '.h5':
        h5file = h5py.File(filename)
        I = h5file['entry']['analysis']['spectrum'].value
        h5file.close()
        return np.vstack((np.arange(len(I)), I, I)).transpose()
    else:
        raise Exception('Wrong file extension')
