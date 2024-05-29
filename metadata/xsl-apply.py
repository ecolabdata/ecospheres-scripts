import sys
from saxonche import PySaxonProcessor

xsl_file = sys.argv[1]
xml_file = sys.argv[2]

with PySaxonProcessor(license=False) as saxon_proc:
    xslt_proc = saxon_proc.new_xslt30_processor()

xslt = xslt_proc.compile_stylesheet(stylesheet_file=xsl_file)
xslt.set_property('!indent', 'yes')

output = xslt.transform_to_string(source_file=xml_file)
print(output)
