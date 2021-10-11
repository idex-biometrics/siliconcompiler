import pya

import json
import os

filename = os.environ['SC_FILENAME']

# We read the manifest using the json library since KLayout bundles its own
# Python interpreter, and it's difficult to include third-party libraries.
with open('sc_manifest.json', 'r') as f:
    sc_cfg = json.load(f)

# Extract info from manifest
sc_stackup = sc_cfg['pdk']['stackup']['value'][0]
print(sc_stackup)
sc_mainlib = sc_cfg['asic']['targetlib']['value'][0]
print(sc_mainlib)
sc_libtype = sc_cfg['library'][sc_mainlib]['arch']['value']
print(sc_libtype)

tech_file = sc_cfg['pdk']['layermap'][sc_stackup]['def']['gds']['value'][0]
print(tech_file)

macro_lefs = []
if 'macrolib' in sc_cfg['asic']:
    sc_macrolibs = sc_cfg['asic']['macrolib']['value']
    for lib in sc_macrolibs:
        macro_lefs.append(sc_cfg['library'][lib]['lef']['value'][0])

tech_lef = sc_cfg['pdk']['aprtech'][sc_stackup][sc_libtype]['lef']['value'][0]
lib_lef = sc_cfg['library'][sc_mainlib]['lef']['value'][0]

# Load KLayout technology file
tech = pya.Technology()
tech.load(tech_file)
layoutOptions = tech.load_layout_options

lefs = []

lefs.extend(macro_lefs)

# Technology LEFs -- these are generally specified in the KLayout tech file, but
# we overwrite them with the paths in the manifest we don't have to worry if the
# paths in the tech file don't resolve right.
lefs.append(tech_lef)
lefs.append(lib_lef)

# Overwrite LEFs specified in tech file with the LEFs we took from the manifest.
layoutOptions.lefdef_config.lef_files = lefs

# These may be disabled in our KLayout tech file for reasons relating to GDS
# export, but for the purposes of viewing we'll hardcode them to True.
layoutOptions.lefdef_config.produce_blockages = True
layoutOptions.lefdef_config.produce_cell_outlines = True
layoutOptions.lefdef_config.produce_obstructions = True

# Display the file!
cell_view = pya.MainWindow.instance().load_layout(filename, layoutOptions, 0)
layout_view = cell_view.view()

# We assume the layer properties file is specified as a relative path in our
# technology file, and resolve it relative to the tech file's directory.
tech_file_dir = os.path.dirname(tech_file)
lyp_path = tech_file_dir + '/' + tech.layer_properties_file
print(lyp_path)

# Set layer properties -- setting second argument to True ensures things like
# KLayout's extra outline, blockage, and obstruction layers appear.
layout_view.load_layer_props(lyp_path, True)