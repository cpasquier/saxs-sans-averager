import sys
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
matplotlib.use('Qt5Agg')
import numpy as np
import os
import csv
import pandas as pd
from PyQt5.QtCore import Qt, QSize,QRegExp
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QSpinBox, QHBoxLayout, QWidget, QTableWidget, \
    QTableWidgetItem, QComboBox, QVBoxLayout, QLabel, QTextEdit, QDialogButtonBox, QMessageBox, QTableView, QLineEdit, QListWidgetItem, QListWidget
from PyQt5.QtGui import QRegExpValidator
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from datetime import date
from os import listdir
from os.path import isfile, join
from pathlib import Path

app = QApplication(sys.argv)
app.setStyle('Fusion')

class MainWindow(QMainWindow):
    def __init__(self):
        global Vwidget2, ax, ax2, df, tempdf
        super().__init__()
        self.setWindowTitle("SANS/SAXS viewer")
        self.setFixedSize(QSize(1680,950))

        dict = {'type':[],
        'number':[], 
        'name':[], 
        'q':[], 
        'i':[], 
        'e':[] 
        } 
        
        df = pd.DataFrame(dict) 
        tempdf = pd.DataFrame(dict) 

        # Figure
        Vwidget1 = QWidget(self)
        Vwidget1.setGeometry(700, 30, 950, 900)
        Vbox1 = QVBoxLayout(Vwidget1)
        Vbox1.setContentsMargins(0, 0, 0, 0)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        ax = self.figure.add_subplot(111)
        ax2 = ax.twinx()
        plt.tight_layout()
        Vbox1.addWidget(self.canvas)
        Vbox1.addWidget(NavigationToolbar(self.canvas, self))
        self.canvas.draw()

        # Panneau echantillons
        Vwidget2 = QListWidget(self)
        Vwidget2.setGeometry(40, 100, 600, 780)
        Vbox2 = QVBoxLayout(Vwidget2)
        Vbox2.setContentsMargins(0, 0, 0, 0)
        Vwidget2.setStyleSheet("background-color: white; border: 1px solid grey;")

        # Bouton de selection de fichiers     
        add_button = QPushButton("Add SAXS", self)
        add_button.clicked.connect(self.add_clicked)
        add_button.setGeometry(40, 30, 93, 28) 

        # Bouton remove 
        remv_button = QPushButton("Remove", self)
        remv_button.clicked.connect(self.remove_clicked)
        remv_button.setGeometry(155, 30, 93, 28) 

        # Bouton update graph
        updt_button = QPushButton("Update graph", self)
        updt_button.clicked.connect(self.update_clicked)
        updt_button.setGeometry(270, 30, 113, 28)

        # Bouton moyennage
        avr_button = QPushButton("Average", self)
        avr_button.clicked.connect(self.avr_clicked)
        avr_button.setGeometry(405, 30, 93, 28)

        # Bouton de sauvegarde  
        save_button = QPushButton("Save checked", self)
        save_button.clicked.connect(self.save_clicked2)
        save_button.setGeometry(520, 30, 113, 28)


    def add_clicked(self):
        global add_sel, mainfolder, saxsfolder, sansfolder, sans11afolder, ncol
        add_sel = QFileDialog.getOpenFileNames(self, "Select data files", ".", "all files (*);;dat (*.dat);;txt (*.txt)")
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax2.set_xscale('log')
        ax2.set_yscale('log')

        for addfile in add_sel[0]:
            mainfolder = os.path.dirname(os.path.dirname(addfile))
            saxsfolder = mainfolder+'/SAXS'
            sansfolder = mainfolder+'/SANS'
            sans11afolder = mainfolder+'/SANS_11A'

            read_file = open(addfile, 'r')
            read_lines = read_file.readlines()
            read_file.close()
            for line in read_lines:   
                if ('Subtitle:') in line:
                    a = line.split(":  ")
                    samplename = a[1].rstrip()    ### SAXS name          
            q1,i1, e1 = np.loadtxt(addfile, usecols=(0,1,2), unpack=True,skiprows=45)    ### SAXS q,i,e
            addfileshort = Path(addfile).stem
            samplenumber = addfileshort.split("_")[0]    ### SAXS number
            listWidgetItem = QListWidgetItem(samplename+"  ("+samplenumber+")",Vwidget2)
            listWidgetItem.setFlags(listWidgetItem.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            listWidgetItem.setCheckState(Qt.Checked)
            Vwidget2.addItem(listWidgetItem)
            df.loc[len(df.index)] = ['SAXS',samplenumber,samplename,q1,i1,e1]

            for sansfile in os.listdir(sansfolder):
                if Path(sansfile).stem.split("_")[0]==samplenumber:
                    q2,i2,e2 = np.loadtxt(mainfolder+'/SANS/'+sansfile, usecols=(0,1,2), unpack=True,skiprows=52)
                    df.loc[len(df.index)] = ['SANS',samplenumber,samplename,q2,i2,e2]

            for sans11afile in os.listdir(sans11afolder):
                if Path(sans11afile).stem.split("_")[0]==samplenumber:
                    q3,i3,e3 = np.loadtxt(mainfolder+'/SANS_11A/'+sans11afile, usecols=(0,1,2), unpack=True,skiprows=52)
                    df.loc[len(df.index)] = ['SANS',samplenumber,samplename,q3,i3,e3]

        for i in np.arange(0,len(df)):
            if df.loc[i]['type']=="SAXS":
                ax.plot(df.loc[i]['q'],df.loc[i]['i'],ls='-',marker='None',label=df.loc[i]['name']+"  ("+df.loc[i]['number']+")")
        #for i in np.arange(0,len(df)):
            if df.loc[i]['type']=="SANS":
                ax2.plot(df.loc[i]['q'],df.loc[i]['i'],ls='--',marker='None')
       
        ax.legend(loc=0)
        self.canvas.draw()


    def remove_clicked(self):
        droplist=[]
        currentrow = Vwidget2.currentRow()
        Vwidget2.takeItem(currentrow)
        ax.cla()
        ax2.cla()
        self.canvas.draw()
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        restfileshort = [Vwidget2.item(x).text() for x in range(Vwidget2.count())]
        for i in np.arange(0,len(df)):
            m=0
            for j in restfileshort:
                if (j==df.loc[i]['name']+"  ("+df.loc[i]['number']+")"):
                        if df.loc[i]['type']=="SAXS":
                            m=1
                            ax.plot(df.loc[i]['q'],df.loc[i]['i'],ls='-',marker='None',label=df.loc[i]['name']+"  ("+df.loc[i]['number']+")")
                        if df.loc[i]['type']=="SANS":
                            m=1
                            ax2.plot(df.loc[i]['q'],df.loc[i]['i'],ls='--',marker='None')
            if m==0:
                droplist.append(i)   # si on ne le trouve pas dans les trucs qui restent dans la liste, on le met dans les trucs à enlever de df

        for k in droplist:
            df.drop(axis=0,index=k,inplace=True)
        df.reset_index(drop=True, inplace=True)   # on remet les index correctement (sinon enleve des chiffres au milieu et le garde comme ca)
    
        ax.legend(loc=0)
        self.canvas.draw()


    def update_clicked(self):
        restf = []
        ax.cla()
        ax2.cla()
        self.canvas.draw()
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        for x in range(Vwidget2.count()):
            if Vwidget2.item(x).checkState()==2:    
                restf.append(Vwidget2.item(x).text())
        for i in np.arange(0,len(df)):
            for j in restf:
                if (j==df.loc[i]['name']+"  ("+df.loc[i]['number']+")") and (df.loc[i]['type']=="SAXS"):
                    ax.plot(df.loc[i]['q'],df.loc[i]['i'],ls='-',marker='None',label=df.loc[i]['name']+"  ("+df.loc[i]['number']+")")
                if (j==df.loc[i]['name']+"  ("+df.loc[i]['number']+")") and (df.loc[i]['type']=="SANS"):
                    ax2.plot(df.loc[i]['q'],df.loc[i]['i'],ls='--',marker='None')
        ax.legend(loc=0)
        self.canvas.draw()


    def avr_clicked(self):
        restf = []
        ilist_saxs = []
        ilist_sans = []
        summ = []
        meannumbers =""
        for x in range(Vwidget2.count()):
            if Vwidget2.item(x).checkState()==2:
                j = Vwidget2.item(x).text()
                for i in np.arange(0,len(df)):
                    if (df.loc[i]['name']+"  ("+df.loc[i]['number']+")"==j) and (df.loc[i]['type']=="SAXS"):
                        ilist_saxs.append(df.loc[i]['i'])
                        qsaxs = df.loc[i]['q']
                        if meannumbers!="":
                            meannumbers = str(meannumbers)+" "+str(df.loc[i]['number'])
                        else:
                            meannumbers = str(df.loc[i]['number'])
                    if (df.loc[i]['name']+"  ("+df.loc[i]['number']+")"==j) and (df.loc[i]['type']=="SANS"):
                        ilist_sans.append(df.loc[i]['i'])
                        qsans = df.loc[i]['q']

        dfsaxs = pd.DataFrame(ilist_saxs)
        dfsans = pd.DataFrame(ilist_sans)

        adfx = dfsaxs.mean()
        adfn = dfsans.mean()
        xarray= adfx.to_numpy(dtype=object)
        narray = adfn.to_numpy(dtype=object)

        df.loc[len(df.index)] = ['SAXS',str(meannumbers),"Mean",qsaxs,xarray,[0]]
        df.loc[len(df.index)] = ['SANS',str(meannumbers),"Mean",qsans,narray,[0]]

        mname = "Mean  ("+meannumbers+")"

        listWidgetItem1 = QListWidgetItem(mname,Vwidget2)
        listWidgetItem1.setFlags(listWidgetItem1.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        listWidgetItem1.setCheckState(Qt.Checked)
        Vwidget2.addItem(listWidgetItem1)
    
    def save_clicked2(self):    #alternative
        data_dict = {'0': []}
        sxdf = pd.DataFrame(data_dict)
        sndf = pd.DataFrame(data_dict)
        for x in range(Vwidget2.count()):
            if Vwidget2.item(x).checkState()==2:
                j = Vwidget2.item(x).text()
                for i in np.arange(0,len(df)):
                    if (df.loc[i]['name']+"  ("+df.loc[i]['number']+")"==j) and (df.loc[i]['type']=="SAXS"):
                        if i==0:
                            sxdf["q_x"] = df.iloc[i]['q']
                        sxdf["i_x_"+str(df.loc[i]['number'])] = df.iloc[i]['i']
                    if (df.loc[i]['name']+"  ("+df.loc[i]['number']+")"==j) and (df.loc[i]['type']=="SANS"):
                        if i==0:
                            sndf["q_n"] = df.iloc[i]['q']
                        sndf["i_n_"+str(df.loc[i]['number'])] = df.iloc[i]['i']

        sydf = pd.concat([sxdf, sndf], axis=1) 
        sydf = sydf.dropna(axis=1, how='all')

        sydf.to_csv('data2.txt', sep='\t', index=False)


window = MainWindow()
window.show()

app.exec()
