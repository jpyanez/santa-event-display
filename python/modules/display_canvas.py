from . import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.font_manager import FontProperties

from .function_wrapper import *

from .santa_formulae import paramsFromTrack, mc_tgamma, mc_tgamma_bp
from .display_classes import textToArray


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=11, height=11, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_facecolor('white')
        plot_axes = self.fig.add_subplot(111)
        #plot_axes.hold(False)

        
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


class SantaCanvas(MplCanvas):
    def __init__(self, geometry, *args, **kwargs):
        MplCanvas.__init__(self, *args, **kwargs)
        self.markers   = ('o','x','v','^','s','D')
        self.colors    = ('C0','C1','C2','C3','C4','C5')
        self.base_font_size = QtWidgets.QApplication.font().pointSize()
        if self.base_font_size <= 0:
            self.base_font_size = 10
        self.font_scale = 1.5
        self.xsize = 4000.0
        self.detectorDepth = [-510, 510]
        self.fontP = FontProperties()
        self.fontP.set_size(self.get_font_size())

    def get_font_size(self):
        scaled = int(round(self.base_font_size * self.font_scale))
        return max(8, scaled)

    def set_font_scale(self, scale):
        self.font_scale = float(scale)
        self.fontP.set_size(self.get_font_size())

    def update_figure(self, frame, series_name_list, series_reco_list, 
                      main_series, stringLayout, logQ, integrateQ, scaleQ):

        # XX How much of this is really necessary to clean up? XX
        if len(self.fig.get_axes()) > 0:
            for one_axis in self.fig.get_axes():
                one_axis.set_xticklabels('')
            self.fig.clf(True)

        plot_map = self.getPlotLayout(stringLayout, frame, main_series)
        plot_map_xy = self.getStringsCoords(plot_map) 

        main_pulse_series = None
        for i in range (0, len(series_name_list)):
            main_hs = False                         
            one_series = series_name_list[i]
            if one_series == main_series:
                main_hs = True
                main_hs_name = one_series
            pulses = self.readPulses(frame, one_series, plot_map)
            if main_hs and plot_map.shape[1] == 1:
                main_pulse_series = pulses
            self.plotPulses(one_series, pulses, plot_map, self.markers[i % len(self.markers)], 
                            self.colors[i % len(self.colors)] , main_hs, logQ, integrateQ, scaleQ)


        for i in range(0, len(series_reco_list)):
            one_reco = series_reco_list[i]
            recoParams = self.getRecoParams(frame[one_reco], plot_map, plot_map_xy)
            self.plotRecos( one_reco, recoParams, plot_map, self.colors[i % len(self.colors)], main_pulse_series)
        
        # Check the counter
        handles, labels = self.plot_axes[0].get_legend_handles_labels()
        self.fig.legend(handles[::-1], labels[::-1], loc = 8, ncol = 4, prop=self.fontP)

        for ax in self.plot_axes:
            ax.tick_params(labelsize=self.get_font_size())
            ax.title.set_fontsize(self.get_font_size())

        # ylabels
        self.fig.text(0.03, 0.5, 'Z position [m]',
                      horizontalalignment='center',
                      verticalalignment='center',
                      rotation = 'vertical',
                      fontsize=self.get_font_size())
           
        # xlabel
        self.fig.text(0.5, 0.1, 'Time [nsec]',
                      horizontalalignment = 'center',
                      verticalalignment='center',
                      rotation = 'horizontal',
                      fontsize=self.get_font_size())   

        # title
        self.fig.text(0.5, 0.97, 'Hits recorded',
                      horizontalalignment = 'center',
                      verticalalignment='center',
                      rotation = 'horizontal',
                      fontsize=self.get_font_size())   
        
        self.fig.autofmt_xdate()
        self.draw()

    def getStringsCoords(self, plot_map):
        plot_map_xy = [[(nan, nan) for x in range(plot_map.shape[1])] for y in range(plot_map.shape[0])]
        figure_ylimit = zeros(2)
        stringKey = icetray.OMKey()
        for i in range(0, plot_map.shape[0]):
            for j in range(0, plot_map.shape[1]):
                if plot_map[i][j] == 0:
                    continue
                stringKey.string = int(plot_map[i][j])
                coords_retrieved = False
                # This is silly, but had to do it because GCD files for Upgrade skip modules
                for iom in range(1, 116):
                    if coords_retrieved:
                        break
                    stringKey.om = iom
                    if stringKey in self.detectorGeometry.omgeo:
                        plot_map_xy[i][j] = (dom_x(self.detectorGeometry, stringKey), dom_y(self.detectorGeometry, stringKey))
                        coords_retrieved = True

        return plot_map_xy


    def getRecoParams(self, reco, plot_map, plot_map_xy):
        """ Get the parameters of the reconstruction for each one of the strings """
        #print 'SANTA-display: Getting parameters from ', reco
        recoParamsList = [[None for x in range(plot_map.shape[1])] for y in range(plot_map.shape[0])]
        for i in range(0, plot_map.shape[0]):
            for j in range(0, plot_map.shape[1]):
                if plot_map[i][j] == 0:
                    continue            
                else:
                    recoParamsList[i][j] = paramsFromTrack(plot_map_xy[i][j], reco)
    
        return recoParamsList


    def plotRecos(self, one_reco, reco_params, plot_map, line_color, main_pulse_series):
        z = linspace(self.detectorDepth[0], self.detectorDepth[1], 1200)
        counter = -1
        for i in range(0, plot_map.shape[0]):
            for j in range(0, plot_map.shape[1]):
                if plot_map[i][j] == 0:
                    continue
                if reco_params[i][j] == None:
                    fitparams = dummyClass(uz = 0, zc = 0, dc = 1000, tc = -5000)
                else:
                    fitparams = reco_params[i][j]

                # Start plotting, first check: Track or cascade fit?
                counter += 1

                # Plot everything as a track for now
                if not isnan(fitparams.uz):
                    time = mc_tgamma(z, fitparams.uz, fitparams.zc, fitparams.dc, fitparams.tc, 
                                     0, dataclasses.I3Constants.c,  n_detector_specific)
                    chi2_text = ''
                    self.plot_axes[counter].plot(time, z, '-'+line_color, lw = 1.5, label = one_reco+chi2_text)
                    

    def plotPulses(self, one_series, pulses, plot_map, marker_symbol, marker_color,  main_hit_series, logQ, integrateQ, scaleQ):
        counter = -1
        markOMlevel = False
        if plot_map.shape[0] == 1 and plot_map.shape[1] == 1:
            markOMlevel = True

        # Calculate the "zero" time of the 
        time_zero = 10000 # Trigger time
        if main_hit_series and pulses:
            all_hit_times = [x.t for x in pulses]
            time_zero     = median(all_hit_times)
            #all_hit_z     = [x.z for x in pulses]
            #z_zero        = mean(all_hit_z)

        #if np.isnan(time_zero):
        #    print(time_zero, pulses)

        for i in range(0, plot_map.shape[0]):
            for j in range(0, plot_map.shape[1]):
                emptyString = True
                doms_with_hits = []
                if plot_map[i][j] == 0:
                    continue

                # Isolate the pulses from one string
                string_hits = [x for x in pulses if x.key.string == plot_map[i][j]]
                if len(string_hits) == 0:
                    # No hits in the string
                    hit_times = [-9999]
                    hit_depth = [-9999]
                    hit_charge = [1]
                    real_charge = 0
                else:
                    emptyString = False
                    hit_times   = array([x.t for x in string_hits])
                    hit_depth   = array([x.z for x in string_hits])
                    real_charge = array([x.q for x in string_hits])
                    doms_with_hits = [x.key.om for x in string_hits]

                    if integrateQ:
                        unique_dom_list  = unique(doms_with_hits)
                        total_dom_charge = zeros(len(unique_dom_list))
                        dom_depth        = zeros(len(unique_dom_list))
                        earliest_time    = zeros(len(unique_dom_list))
                        for dom_i, unique_dom in enumerate(unique_dom_list):
                            dom_pulses_index = where(doms_with_hits == unique_dom)[0]
                            total_dom_charge[dom_i] = np.sum(real_charge[dom_pulses_index])
                            dom_depth[dom_i]        = string_hits[dom_pulses_index[0]].z
                            earliest_time[dom_i]    = np.min(hit_times[dom_pulses_index])
                        
                        hit_times   = earliest_time
                        hit_depth   = dom_depth
                        real_charge = total_dom_charge
                        doms_with_hits = unique_dom_list

                        #print(hit_times)
                        #print(hit_depth)

                if logQ:
                    real_charge = log10(real_charge) #[(log10()+2.)**2 for x in string_hits]
                else:
                    real_charge = real_charge*scaleQ
            
                counter +=1

                # Plotting the hits
                # Why do I compute the real_charge above?
                self.plot_axes[counter].scatter(hit_times, hit_depth, real_charge,
                                                marker = marker_symbol, 
                                                c = marker_color, label = one_series)

                # if main_hit_series and plot_map.size <= 4 and len(string_hits) > 0:
                #     print 'STRING ',  plot_map[i][j]
                #     print 'time\tdepth \tcharge'
                #     for hcounter in range(0, len(hit_times)):
                #         print "%i" % hit_times[hcounter] +  '\t'+"%i" %  hit_depth[hcounter]+ '\t' +"%.2f" % real_charge[hcounter]
                                   
                if markOMlevel and main_hit_series and not emptyString:
                    for k in range(len(hit_times)):
                        self.plot_axes[counter].text(hit_times[k]+10, hit_depth[k]-7, 
                                                     "%i" % doms_with_hits[k], fontsize=7)
                xsize = self.xsize
                if emptyString:
                    #print(time_zero, xsize)
                    self.plot_axes[counter].set_xlim([time_zero-xsize/4,  
                                                      time_zero+3.*xsize/4])
                else:
                    self.plot_axes[counter].set_xlim([median(hit_times)-xsize/2, median(hit_times) + xsize/2])

                # Set these limits depending on the strings that were selected
                self.plot_axes[counter].set_ylim(self.detectorDepth)


    def readPulsesFast(self, frame, series_name):
        #print 'Main series: ', series_name
        ordered_strings = []

        hit_map = read_pulses(frame, series_name)
        #print(hit_map)

        if len(hit_map) == 0:
            print('SANTA-display: The series ', series_name, ' was empty!')
            return ordered_strings

        simple_hit_map = array([0,0])
        
        for om_key in hit_map:
            om_pulses = hit_map[om_key]
            charge = 0

            for one_hit in om_pulses:
                if type(one_hit) == dataclasses.I3DOMLaunch:
                    charge += 2.
                elif type(one_hit) == dataclasses.I3MCHit:
                    charge = one_hit.weight
                else:
                    charge = pulse_charge(one_hit)

            simple_hit_map = vstack((simple_hit_map, array([om_key.string, charge])))
       
        simple_hit_map = delete(simple_hit_map, (0), axis = 0)
        if len(simple_hit_map) == 0:
            return ordered_strings

        strings = unique(simple_hit_map[:,0])
        strings_charge = zeros(len(strings))
        
        for i in range(1, len(strings)):
            strings_charge[i] = np.sum(simple_hit_map[simple_hit_map[:,0] == strings[i], 1])

        ordered_strings = strings[argsort(strings_charge)[::-1]]

        return ordered_strings

    def readPulses(self, frame, series_name, plot_map):
        
        hit_map = read_pulses(frame, series_name)

        # Read all the pulses.
        pulses = []
        for om_key in hit_map:
            if len(where(om_key.string == plot_map)[0]) == 0:
                continue
            om_pulses = hit_map[om_key]
            for one_hit in om_pulses:
                if type(one_hit) == dataclasses.I3DOMLaunch:
                    charge = 2.
                elif type(one_hit) == dataclasses.I3MCHit:
                    charge = one_hit.weight
                else:
                    charge = pulse_charge(one_hit)

                pulses.append(dummyClass(key = om_key, 
                                         z=dom_z(self.detectorGeometry, om_key),
                                         t=pulse_time(one_hit),  q =charge, keep = False, source = 0))     


        return pulses

    def getPlotLayout(self, stringLayout, frame, main_series):
        strings = []

        if stringLayout[0] == 'Auto':
            number_of_strings = None
            try:
                number_of_strings = int(stringLayout[1])
            except:
                print('SANTA-display: could not convert ', stringLayout[1], ' into an integer! Switching to your default layout')
                stringLayout[0] = list(figureLayouts.keys())[0]

            if main_series and number_of_strings:
                ordered_strings = self.readPulsesFast(frame, main_series)[:number_of_strings]
                if len(ordered_strings) > 0:
                    strings = ordered_strings
                else:
                    stringLayout[0] = list(figureLayouts.keys())[0]
                    print('SANTA-display: No pulses found, switching to your default layout')
            else:
                print('SANTA-display: You need to pick a "main series" and give an integer to use the AUTO mode. Switching to your default layout')
                stringLayout[0] = list(figureLayouts.keys())[0]

        elif stringLayout[0] == 'Manual':
            strings = textToArray(str(stringLayout[1]))

        # If other was selected, or things simply did not work, go for the default one

        if len(strings)==0:
            if stringLayout[0] not in list(figureLayouts.keys()):
                print('SANTA-display: Problems with the layout. You selected ', stringLayout[0], ' which is not defined! Check the settings file.')
            else:
                strings = figureLayouts[str(stringLayout[0])]


        if len(strings.shape) == 1:
            noc = int(ceil(sqrt(len(strings))))
            nor = int(ceil(len(strings)*1.0/noc))
            strlist = append(strings,  [0]*((noc*nor) - len(strings)))
            strings = reshape(strlist, (nor, noc))
            self.fig.subplots_adjust(hspace=0.3)
            self.fig.subplots_adjust(wspace=0.3)
        else:
            self.fig.subplots_adjust(hspace=0.1)
            self.fig.subplots_adjust(wspace=0.1)


        nop = strings.shape[0]*strings.shape[1]
        self.plot_axes = []
        counter = 0
        for i in range(0, strings.shape[0]):
            for j in range(0, strings.shape[1]):
                counter += 1
                if strings[i][j] > 0:
                    #counter += 1
                    self.plot_axes.append(self.fig.add_subplot(strings.shape[0], 
                                                               strings.shape[1], counter))
                    #self.plot_axes[-1].hold(True)
                    self.plot_axes[-1].grid(True)

                    if nop <= 16:
                        self.plot_axes[-1].set_title('String '+ "%i" % strings[i][j], fontsize=self.get_font_size())
                    elif nop <= 50:
                        self.plot_axes[-1].set_title("%i" % strings[i][j], fontsize=self.get_font_size(), verticalalignment = 'bottom')
                        if i != strings.shape[0]-1:
                            self.plot_axes[-1].set_xticklabels([])
                        else:
                            for xlabel_i in self.plot_axes[-1].get_xticklabels(): 
                                xlabel_i.set_fontsize(self.get_font_size()) 
                        if j != 0:
                            self.plot_axes[-1].set_yticklabels([])
                        else:
                            for ylabel_i in self.plot_axes[-1].get_yticklabels(): 
                                ylabel_i.set_fontsize(self.get_font_size()) 
                    else:
                        self.plot_axes[-1].set_title("%i" % strings[i][j], fontsize=self.get_font_size(), verticalalignment = 'bottom')
                        self.plot_axes[-1].set_xticklabels([])
                        self.plot_axes[-1].set_yticklabels([])
                                                        

        return strings
