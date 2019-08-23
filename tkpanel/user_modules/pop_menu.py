#!/usr/bin/env python3

import os
import collections
import glob
from xdg import DesktopEntry
from xdg import IconTheme
# to get the language
import locale

# the dirs to search the application files
app_dirs_user = [os.getenv("HOME")+"/.local/share/applications"]
app_dirs_system = ["/usr/share/applications"]

#######################
# main categories
# removed "Audio" e "Video" main categories
freedesktop_main_categories = ["AudioVideo","Development",
                              "Education","Game","Graphics","Network",
                              "Office","Settings","System","Utility"]

development_extended_categories = ["Building","Debugger","IDE","GUIDesigner",
                                  "Profiling","RevisionControl","Translation",
                                  "Database","WebDevelopment"]

office_extended_categories = ["Calendar","ContanctManagement","Office",
                             "Dictionary","Chart","Email","Finance","FlowChart",
                             "PDA","ProjectManagement","Presentation","Spreadsheet",
                             "WordProcessor","Engineering"]

graphics_extended_categories = ["2DGraphics","VectorGraphics","RasterGraphics",
                               "3DGraphics","Scanning","OCR","Photography",
                               "Publishing","Viewer"]

utility_extended_categories = ["TextTools","TelephonyTools","Compression",
                              "FileTools","Calculator","Clock","TextEditor",
                              "Documentation"]

settings_extended_categories = ["DesktopSettings","HardwareSettings",
                               "Printing","PackageManager","Security",
                               "Accessibility"]

network_extended_categories = ["Dialup","InstantMessaging","Chat","IIRCClient",
                              "FileTransfer","HamRadio","News","P2P","RemoteAccess",
                              "Telephony","VideoConference","WebBrowser"]

# added "Audio" and "Video" main categories
audiovideo_extended_categories = ["Audio","Video","Midi","Mixer","Sequencer","Tuner","TV",
                                 "AudioVideoEditing","Player","Recorder",
                                 "DiscBurning"]

game_extended_categories = ["ActionGame","AdventureGame","ArcadeGame",
                           "BoardGame","BlockGame","CardGame","KidsGame",
                           "LogicGame","RolePlaying","Simulation","SportGame",
                           "StrategyGame","Amusement","Emulator"]

education_extended_categories = ["Art","Construction","Music","Languages",
                                "Science","ArtificialIntelligence","Astronomy",
                                "Biology","Chemistry","ComputerScience","DataVisualization",
                                "Economy","Electricity","Geography","Geology","Geoscience",
                                "History","ImageProcessing","Literature","Math","NumericAnalysis",
                                "MedicalSoftware","Physics","Robots","Sports","ParallelComputing",
                                "Electronics"]

system_extended_categories = ["FileManager","TerminalEmulator","FileSystem",
                             "Monitor","Core"]

# named tuple
nt_ext_categ = collections.namedtuple("List", "main list", rename=False)

development_ext = nt_ext_categ("Development", development_extended_categories)
office_ext = nt_ext_categ("Office", office_extended_categories)
graphics_ext = nt_ext_categ("Graphics", graphics_extended_categories)
utility_ext = nt_ext_categ("Utility", utility_extended_categories)
settings_ext = nt_ext_categ("Settings", settings_extended_categories)
network_ext = nt_ext_categ("Network", network_extended_categories)
audiovideo_ext = nt_ext_categ("AudioVideo", audiovideo_extended_categories)
game_ext = nt_ext_categ("Game", game_extended_categories)
education_ext = nt_ext_categ("Education", education_extended_categories)
system_ext = nt_ext_categ("System", system_extended_categories)
# all the subcategories in one list
all_extend_list = [development_ext,office_ext,graphics_ext,utility_ext,
                  settings_ext,network_ext,audiovideo_ext,game_ext,
                  education_ext,system_ext]
                  

# for each desktop file
class catDesktop():
    name = ""
    categories = ""
    path = ""
    progexec = ""
    icon = ""

class getMenu():
    
    def __init__(self):
        
        # the default
        self.locale_lang = "en"
        try:
            self.locale_lang = locale.getlocale()[0].split("_")[0]
        except:
            self.locale_lang = "en"


        # list of all catDesktop - one for desktop file
        self.info_desktop = []
        # list of all desktop files found
        self.file_list = []
        # fill self.info_desktop
        self.fpop(app_dirs_system)
        self.fpop(app_dirs_user)
        
        ######****######
        
        # fill treeview 
        self.id_list = []
        # main categories
        for ccat in reversed(freedesktop_main_categories):
            self.id_list.append(ccat)
        # the category for missing entry
        self.id_list.append("Missed")
        # get the menu entries
        self.lists = self.fpop_lists()
        #print("lists::", self.lists)
        
    # return the lists
    def retList(self):
        return self.lists


#############################

##### FILL self.info_desktop ######
    def fpop(self, ap_dir):
        # the list of the desktop files
        self.file_list = self.list_app(ap_dir)
        # fill the lista
        self.pop_info_desktop()

    # fill self.file_list
    def list_app(self, llist):
        file_lista = []
        for ddir in llist:
            file_lista += glob.glob(ddir+"/*.desktop")
        
        return file_lista

    # fill self.info_desktop
    def pop_info_desktop(self):
        
        for ffile in self.file_list:
            
            try:
                entry = DesktopEntry.DesktopEntry(ffile)
                fname = entry.getName()
                fcategory = entry.getCategories()
                ftype = entry.getType()

                # both must exist
                if ftype == "Application" and fcategory != "":
                    dentry = catDesktop()
                    dentry.name = fname
                    dentry.categories = fcategory
                    dentry.path = ffile
                    self.info_desktop.append(dentry)
            except Exception as E:
                pass

######## FILL THE LISTS 
    def fpop_lists(self):
        list_one = []
        list_two = []
        #
        for item in  self.info_desktop:
            #
            ret = 0
            # main category
            ret = self.item_in_main2(item)
            if ret:
                # the id of the category
                idx_cat = self.id_list.index(ret)
                idx = self.id_list[idx_cat]
                pexec = DesktopEntry.DesktopEntry(item.path).getExec()
                icon = DesktopEntry.DesktopEntry(item.path).getIcon()
                list_one.append([item.name, item.path, idx, item.name.lower(), pexec, icon])
            else:
                # indirect main category
                ret = self.item_in_ext(item)
                
                if ret:
                    # the id of the category
                    idx_cat = self.id_list.index(ret)
                    idx = self.id_list[idx_cat]
                    pexec = DesktopEntry.DesktopEntry(item.path).getExec()
                    icon = DesktopEntry.DesktopEntry(item.path).getIcon()
                    list_one.append([item.name, item.path, idx, item.name.lower(), pexec, icon])
                else:
                    # Missed categoty
                    idx = "Missed"
                    pexec = DesktopEntry.DesktopEntry(item.path).getExec()
                    icon = DesktopEntry.DesktopEntry(item.path).getIcon()
                    list_two.append([item.name, item.path, idx, item.name.lower(), pexec, icon])
            
        # sorted by name
        list_one2 = sorted(list_one, key=lambda list_one: list_one[3], reverse=False)
        # sorted by category
        list_one3 = sorted(list_one2, key=lambda list_one2: list_one2[2], reverse=False)
        
        # not the missing category list
        return[list_one3]#, list_two2]

    # main category - first pass
    def item_in_main(self, item):
        
        try:
            if item.categories[0] in freedesktop_main_categories:
                return item.categories[0]
            else:
                return 0
        except:
            return 0
    
    # main category - second pass
    def item_in_main2(self, item):
        
        try:
            for iitem in item.categories:
                if iitem in freedesktop_main_categories:
                    return iitem

            return 0
        except:
            return 0
    
    # extended category - third pass
    def item_in_ext(self, item):
        
        try:
            for ccat in all_extend_list:
                for iitem in item.categories:
                    if iitem in ccat.list:
                        return ccat.main
            
            return 0
        except:
            return 0      

    # find an action in the desktop file
    def ffind_action(self, ffile, aaction):
        kws = []
        with open(ffile, 'r') as f:
            for line in f:
                if aaction+"=" in line:
                    kws = line.split("=")[1].split(";")[:-1]
        return kws

