#!/usr/local/bin/python3

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import wishbone
import os
from platform import system as platform
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import pickle

class wishbone_gui(tk.Tk):
    def __init__(self,parent):
        tk.Tk.__init__(self,parent)
        self.parent = parent
        self.initialize()

    def initialize(self):
        self.grid()
        self.vals = None
        self.currentPlot = None

        #set up menu bar
        self.menubar = tk.Menu(self)
        self.fileMenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.fileMenu)
        self.fileMenu.add_command(label="Load data", command=self.loadData)

        self.analysisMenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Analysis", menu=self.analysisMenu)
        self.analysisMenu.add_command(label="Principal component analysis", state='disabled', command=self.runPCA)
        self.analysisMenu.add_command(label="tSNE", state='disabled', command=self.runTSNE)
        self.analysisMenu.add_command(label="Diffusion map", state='disabled', command=self.runDM)
        self.analysisMenu.add_command(label="GSEA", state='disabled', command=self.runGSEA)
        self.analysisMenu.add_command(label="Wishbone", state='disabled', command=self.runWishbone)

        self.visMenu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Visualization", menu=self.visMenu)
        self.visMenu.add_command(label="Principal component analysis", state='disabled', command=self.plotPCA)
        self.visMenu.add_command(label="tSNE", state='disabled', command=self.plotTSNE)
        self.visMenu.add_command(label="Diffusion map", state='disabled', command=self.plotDM)
        self.visMenu.add_command(label="GSEA Results", state='disabled', command=self.showGSEAResults)
        self.wishboneMenu = tk.Menu(self)
        self.visMenu.add_cascade(label="Wishbone", menu=self.wishboneMenu)
        self.wishboneMenu.add_command(label="On tSNE", state='disabled', command=self.plotWBOnTsne)
        self.wishboneMenu.add_command(label="Marker trajectory", state='disabled', command=self.plotWBMarkerTrajectory)
        self.wishboneMenu.add_command(label="Heat map", state='disabled', command=self.plotWBHeatMap)
        self.visMenu.add_command(label="Gene expression", state='disabled', command=self.plotGeneExpOntSNE)
        
        self.config(menu=self.menubar)

        #intro screen
        tk.Label(self, text=u"Wishbone", font=('Helvetica', 48), fg="black", bg="white", padx=100, pady=50).grid(row=0)
        tk.Label(self, text=u"To get started, select a data file by clicking File > Load Data", fg="black", bg="white", padx=100, pady=25).grid(row=1)

        #update
        self.grid_columnconfigure(0,weight=1)
        self.resizable(True,False)
        self.update()
        self.geometry(self.geometry())       
        self.focus_force()
    def loadData(self):
        self.dataFileName = filedialog.askopenfilename(title='Load data file', initialdir='~/.wishbone/data')

        #pop up data options menu
        self.fileInfo = tk.Toplevel()
        self.fileInfo.title("Data options")
        tk.Label(self.fileInfo, text=u"File name: ").grid(column=0, row=0)
        tk.Label(self.fileInfo, text=self.dataFileName.split('/')[-1]).grid(column=1, row=0)

        tk.Label(self.fileInfo,text=u"Name:" ,fg="black",bg="white").grid(column=0, row=1)
        self.fileNameEntryVar = tk.StringVar()
        tk.Entry(self.fileInfo, textvariable=self.fileNameEntryVar).grid(column=1,row=1)

        self.normalizeVar = tk.BooleanVar()
        tk.Checkbutton(self.fileInfo, text=u"Normalize", variable=self.normalizeVar).grid(column=0, row=2, columnspan=2)
        tk.Label(self.fileInfo, text=u"The normalize parameter is used for correcting for library size among cells.").grid(column=0, row=3, columnspan=2)

        tk.Button(self.fileInfo, text="Cancel", command=self.fileInfo.destroy).grid(column=0, row=4)
        tk.Button(self.fileInfo, text="Load", command=self.processData).grid(column=1, row=4)

        self.wait_window(self.fileInfo)

    def processData(self):
        #clear intro screen
        for item in self.grid_slaves():
            item.grid_forget()

        #load data
        self.scdata = wishbone.wb.SCData.from_csv(os.path.expanduser(self.dataFileName), 
                data_type='sc-seq', normalize=self.normalizeVar.get())
        #get genes
        self.genes = self.scdata.data.columns.values

        #display file name
        tk.Label(self,text=u"File name: " + self.fileNameEntryVar.get(), fg="black",bg="white").grid(column=0,row=0)

        #set up canvas for plots
        self.fig, self.ax = wishbone.wb.get_fig()
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=1, row=1, rowspan=17, columnspan=4, sticky='NS')

        #set up visualization buttons
        tk.Label(self, text=u"Visualizations:", fg='black', bg='white').grid(column=0, row=1)
        self.PCAButton = tk.Button(self, text=u"PCA", state='disabled', command=self.plotPCA)
        self.PCAButton.grid(column=0, row=2)
        self.tSNEButton = tk.Button(self, text=u"tSNE", state='disabled', command=self.plotTSNE)
        self.tSNEButton.grid(column=0, row=3)
        self.DMButton = tk.Button(self, text=u"Diffusion map", state='disabled', command=self.plotDM)
        self.DMButton.grid(column=0, row=4)
        self.GSEAButton = tk.Button(self, text=u"GSEA Results", state='disabled', command=self.showGSEAResults)
        self.GSEAButton.grid(column=0, row=5)
        self.WBButton = tk.Button(self, text=u"Wishbone", state='disabled', command=self.plotWBOnTsne)
        self.WBButton.grid(column=0, row=6)
        self.geneExpButton = tk.Button(self, text=u"Gene expression", state='disabled', command=self.plotGeneExpOntSNE)
        self.geneExpButton.grid(column=0, row=7)
        self.saveButton = tk.Button(self, text=u"Save plot", state='disabled', command=self.savePlot)
        self.saveButton.grid(column = 4, row=0)
        self.diff_component = tk.StringVar()
        self.diff_component.set('Component 1')
        self.component_menu = tk.OptionMenu(self, self.diff_component,
                                            'Component 1', 'Component 2', 'Component 3',
                                            'Component 4', 'Component 5', 'Component 6', 
                                            'Component 7', 'Component 8', 'Component 9')
        self.component_menu.config(state='disabled')
        self.component_menu.grid(row=0, column=2)
        self.updateButton = tk.Button(self, text=u"Update component", command=self.updateComponent, state='disabled')
        self.updateButton.grid(column=3, row=0)

        #enable buttons
        self.analysisMenu.entryconfig(0, state='normal')

        #destroy pop up menu
        self.fileInfo.destroy()

    def runPCA(self):
        self.scdata.run_pca()

        #enable buttons
        self.analysisMenu.entryconfig(1, state='normal')
        self.visMenu.entryconfig(0, state='normal')
        self.PCAButton.config(state='normal')

    def runTSNE(self):
        #pop up for # components
        self.tsneOptions = tk.Toplevel()
        self.tsneOptions.title("tSNE options")
        tk.Label(self.tsneOptions,text=u"Number of components:" ,fg="black",bg="white").grid(column=0, row=0)
        self.nCompVar = tk.IntVar()
        tk.Entry(self.tsneOptions, textvariable=self.nCompVar).grid(column=1,row=0)
        tk.Button(self.tsneOptions, text=u"Run", command=self.tsneOptions.destroy).grid(column=0, columnspan=2, row=1)
        self.wait_window(self.tsneOptions)

        self.scdata.run_tsne(n_components=self.nCompVar.get())

        #enable buttons
        self.analysisMenu.entryconfig(2, state='normal')
        self.visMenu.entryconfig(1, state='normal')
        self.visMenu.entryconfig(4, state='normal')
        self.tSNEButton.config(state='normal')
        self.geneExpButton.config(state='normal')

    def runDM(self):
        self.scdata.run_diffusion_map()

        #enable buttons
        self.analysisMenu.entryconfig(3, state='normal')
        self.visMenu.entryconfig(2, state='normal')
        self.DMButton.config(state='normal')

    def runGSEA(self):
        self.GSEAFileName = filedialog.askopenfilename(title='Select gmt File', initialdir='~/.wishbone/gsea')
        print(self.GSEAFileName)
        if self.GSEAFileName != None:
            self.scdata.run_diffusion_map_correlations()
            self.scdata.data.columns = self.scdata.data.columns.str.upper()
            self.outputPrefix = filedialog.asksaveasfilename(title='Input file prefix for saving output', initialdir='~/.wishbone/gsea')
            if 'mouse' in self.GSEAFileName:
                gmt_file_type = 'mouse'
            else:
                gmt_file_type = 'human'
            self.reports = self.scdata.run_gsea(output_stem= os.path.expanduser(self.outputPrefix), 
                     gmt_file=(gmt_file_type, self.GSEAFileName.split('/')[-1]))
            #enable buttons
            self.analysisMenu.entryconfig(4, state='normal')
            self.visMenu.entryconfig(3, state='normal')
            self.GSEAButton.config(state='normal')

    def runWishbone(self):
        #popup menu for wishbone options
        self.wbOptions = tk.Toplevel()
        self.wbOptions.title("Wishbone Options")

        #s
        tk.Label(self.wbOptions,text=u"Start cell:",fg="black",bg="white").grid(column=0,row=0)
        self.start = tk.StringVar()
        tk.Entry(self.wbOptions, textvariable=self.start).grid(column=1,row=0)

        #k
        tk.Label(self.wbOptions,text=u"k:",fg="black",bg="white").grid(column=0,row=1)
        self.k = tk.IntVar()
        tk.Entry(self.wbOptions, textvariable=self.k).grid(column=1,row=1)
        self.k.set(15)
        
        #components list
        tk.Label(self.wbOptions, text=u"Components list:", fg='black', bg='white').grid(column=0, row=2)
        self.compList = tk.StringVar()
        tk.Entry(self.wbOptions, textvariable=self.compList).grid(column=1, row=2)
        self.compList.set("1, 2, 3")

        #num waypoints
        tk.Label(self.wbOptions, text=u"Number of waypoints:", fg='black', bg='white').grid(column=0, row=3)
        self.numWaypoints = tk.IntVar()
        tk.Entry(self.wbOptions, textvariable=self.numWaypoints).grid(column=1, row=3)
        self.numWaypoints.set(250)

        #branch
        self.branch = tk.BooleanVar()
        tk.Checkbutton(self.wbOptions, text=u"Branch", variable=self.branch).grid(column=0, row=4, columnspan=2)

        tk.Button(self.wbOptions, text=u"Run", command=self.wbOptions.destroy).grid(column=0, columnspan=2, row=5)
        self.wait_window(self.wbOptions)

        self.wb = wishbone.wb.Wishbone(self.scdata)
        self.wb.run_wishbone(start_cell=self.start.get(), k=self.k.get(), components_list=[int(comp) for comp in self.compList.get().split(',')], num_waypoints=self.numWaypoints.get())

        #enable buttons
        self.wishboneMenu.entryconfig(0, state='normal')
        self.wishboneMenu.entryconfig(1, state='normal')
        self.WBButton.config(state='normal')

    def plotPCA(self):
        self.saveButton.config(state='normal')
        self.component_menu.config(state='disabled')
        self.updateButton.config(state='disabled')
        #pop up for # components
        self.PCAOptions = tk.Toplevel()
        self.PCAOptions.title("PCA Plot Options")
        tk.Label(self.PCAOptions,text=u"Max variance explained (ylim):",fg="black",bg="white").grid(column=0, row=0)
        self.yLimVar = tk.DoubleVar()
        tk.Entry(self.PCAOptions, textvariable=self.yLimVar).grid(column=1,row=0)
        tk.Label(self.PCAOptions, text=u"Number of components:", fg='black', bg='white').grid(column=0, row=1)
        self.compVar = tk.IntVar()
        tk.Entry(self.PCAOptions, textvariable=self.compVar).grid(column=1, row=1)
        tk.Button(self.PCAOptions, text=u"Plot", command=self.PCAOptions.destroy).grid(column=0, columnspan=2, row=2)
        self.wait_window(self.PCAOptions)

        self.resetCanvas()
        self.fig, self.ax = self.scdata.plot_pca_variance_explained(ylim=(0, self.yLimVar.get()), n_components=self.compVar.get())
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=1, row=1, rowspan=17, columnspan=4, sticky='NS') 
        self.currentPlot = 'pca'

        #enable buttons
        self.saveButton.config(state='normal')

    def plotTSNE(self):
        self.saveButton.config(state='normal')
        self.component_menu.config(state='disabled')
        self.updateButton.config(state='disabled')
        
        self.resetCanvas()
        self.fig, self.ax = self.scdata.plot_tsne()
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=1, row=1, rowspan=17, columnspan=4, sticky='NS') 
        self.currentPlot = 'tsne'

    def plotDM(self):
        self.saveButton.config(state='normal')
        self.component_menu.config(state='disabled')
        self.updateButton.config(state='disabled')
        
        self.resetCanvas()
        self.fig, self.ax = self.scdata.plot_diffusion_components()
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=1, row=1, rowspan=17, columnspan=4, sticky='NS') 
        self.currentPlot = 'dm_components'

    def showGSEAResults(self):
        self.saveButton.config(state='disabled')
        self.component_menu.config(state='normal')
        self.updateButton.config(state='normal')
        
        self.resetCanvas()
        self.canvas = tk.Canvas(self, width=600, height=300)
        self.canvas.grid(column=1, row=1, rowspan=17, columnspan=4,sticky='NS')
        self.outputText(1)
        self.currentPlot = 'GSEA_result_'+self.diff_component.get()

    def updateComponent(self):
        self.resetCanvas()
        self.canvas = tk.Canvas(self, width=600, height=300)
        self.canvas.grid(column=1, row=1, rowspan=17, columnspan=4,sticky='NS')
        self.outputText(int(self.diff_component.get().split(' ')[-1]))
        self.currentPlot = 'GSEA_result_'+self.diff_component.get()

    def outputText(self, diff_component):
        pos_text = str(self.reports[diff_component]['pos']).split('\n')
        pos_text = pos_text[1:len(pos_text)-1]
        pos_text = '\n'.join(pos_text)
        neg_text = str(self.reports[diff_component]['neg']).split('\n')
        neg_text = neg_text[1:len(neg_text)-1]
        neg_text = '\n'.join(neg_text)
        self.canvas.create_text(5, 5, anchor='nw', text='Positive correlations:\n\n', font=('Helvetica', 16, 'bold'))
        self.canvas.create_text(5, 50, anchor='nw', text=pos_text)
        self.canvas.create_text(5, 150, anchor='nw', text='Negative correlations:\n\n', font=('Helvetica', 16, 'bold'))
        self.canvas.create_text(5, 200, anchor='nw', text=neg_text)

    def plotWBOnTsne(self):
        self.saveButton.config(state='normal')
        self.component_menu.config(state='disabled')
        self.updateButton.config(state='disabled')
        
        self.resetCanvas()
        self.fig, self.ax = self.wb.plot_wishbone_on_tsne()
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=1, row=1, rowspan=17, columnspan=4, sticky='NS')
        self.currentPlot = 'wishbone_on_tsne'

    def plotWBMarkerTrajectory(self):
        self.saveButton.config(state='normal')
        self.component_menu.config(state='disabled')
        self.updateButton.config(state='disabled')
        
        self.getGeneSelection()
        if len(self.selectedGenes) < 1:
            print('Error: must select at least one gene')
        self.resetCanvas()
        self.vals, self.fig, self.ax = self.wb.plot_marker_trajectory(self.selectedGenes)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=1, row=1, rowspan=17, columnspan=4, sticky='NS')
        self.currentPlot = 'wishbone_marker_trajectory'

        #enable buttons
        self.wishboneMenu.entryconfig(2, state='normal')

    def plotWBHeatMap(self):
        self.saveButton.config(state='normal')
        self.component_menu.config(state='disabled')
        self.updateButton.config(state='disabled')
        
        self.resetCanvas()
        self.fig, self.ax = self.wb.plot_marker_heatmap(self.vals)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=1, row=1, rowspan=17, columnspan=4, sticky='NS')
        self.currentPlot = 'wishbone_marker_heatmap'

    def plotGeneExpOntSNE(self):
        self.saveButton.config(state='normal')
        self.component_menu.config(state='disabled')
        self.updateButton.config(state='disabled')
        self.getGeneSelection()
        if len(self.selectedGenes) < 1:
            print('Error: must select at least one gene')
        
        self.resetCanvas()
        self.fig, self.ax = self.scdata.plot_gene_expression(self.selectedGenes)
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.show()
        self.canvas.get_tk_widget().grid(column=1, row=1, rowspan=17, columnspan=4, sticky='NS')
        self.currentPlot = 'gene_expression_tsne'

    def getGeneSelection(self):
        #popup menu to get selected genes
        self.geneSelection = tk.Toplevel()
        self.geneSelection.title("Select Genes")
        tk.Label(self.geneSelection,text=u"Genes:",fg="black",bg="white").grid(row=0)

        self.geneInput = wishbone.autocomplete_entry.AutocompleteEntry(self.genes.tolist(), self.geneSelection, listboxLength=6)
        self.geneInput.grid(row=1)
        self.geneInput.bind('<Return>', self.AddToSelected)

        self.geneSelectBox = tk.Listbox(self.geneSelection, selectmode=tk.EXTENDED)
        self.geneSelectBox.grid(row=2, rowspan=10)
        self.geneSelectBox.bind('<BackSpace>', self.DeleteSelected)
        self.selectedGenes = []

        tk.Button(self.geneSelection, text=u"Use selected genes", command=self.geneSelection.destroy).grid(row=12)
        self.wait_window(self.geneSelection)
    
    def AddToSelected(self, event):
        self.selectedGenes.append(self.geneInput.get())
        self.geneSelectBox.insert(tk.END, self.selectedGenes[len(self.selectedGenes)-1])

    def DeleteSelected(self, event):
        selected = self.geneSelectBox.curselection()
        pos = 0
        for i in selected:
            idx = int(i) - pos
            self.geneSelectBox.delete( idx,idx )
            self.selectedGenes = self.selectedGenes[:idx] + self.selectedGenes[idx+1:]
            pos = pos + 1  

    def savePlot(self):
        self.plotFileName = filedialog.asksaveasfilename(title='Save Plot', defaultextension='.png', initialfile=self.fileNameEntryVar.get()+"_"+self.currentPlot)
        if self.plotFileName != None:
            self.fig.savefig(self.plotFileName)

    def resetCanvas(self):
        self.fig.clf()
        if type(self.canvas) is FigureCanvasTkAgg:
            for item in self.canvas.get_tk_widget().find_all():
                self.canvas.get_tk_widget().delete(item)
        else:
            for item in self.canvas.find_all():
                self.canvas.delete(item)

def launch():
    app = wishbone_gui(None)
    os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "python" to true' ''')
    app.title('Wishbone')
    app.mainloop()

if __name__ == "__main__":
    launch()
