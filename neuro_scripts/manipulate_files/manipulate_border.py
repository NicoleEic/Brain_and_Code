import xml.etree.ElementTree as ET
import numpy as np
# read in border file using XML parser
tree = ET.parse('example_border.border')
root = tree.getroot()
# access the top-level border_class and update colour
border_class = root.getchildren()[0]
border_class.set('Red','1')
border_class.set('Green','0')
border_class.set('Blue','0')
# access the low-level border_name and update colour
border_name = border_class.getchildren()[0]
border_name.set('Red','1')
border_name.set('Green','0')
border_name.set('Blue','0')
# save changes to new file
tree.write('example_border_red.border')
