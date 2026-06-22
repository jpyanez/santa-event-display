import matplotlib
def configureMatplotlib():
    """ Configures matplotlib to produce readable figures """
    matplotlib.rc('axes', grid=True, titlesize = 10, labelsize = 8)
    matplotlib.rc('xtick', labelsize = 8 )
    matplotlib.rc('ytick', labelsize = 8 )
    
    matplotlib.rc('lines', linewidth=1, color='b')
    
    matplotlib.rc('figure.subplot', wspace =0.3 )
    matplotlib.rc('figure.subplot', hspace =0.3)
    #matplotlib.rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
    ## for Palatino and other serif fonts use:
    #rc('font',**{'family':'serif','serif':['Palatino']))
    #matplotlib.rc('text', usetex=True)
