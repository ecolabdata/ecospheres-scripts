import sys
from lxml import etree
from saxonche import PySaxonProcessor

proc = sys.argv[1]
xsl_file = sys.argv[2]
xml_file = sys.argv[3]

if proc == 'lxml':
  xsl = etree.parse(xsl_file)
  transform = etree.XSLT(xsl)

  iso = etree.parse(xml_file)
  dcat = transform(iso, CoupledResourceLookUp="'disabled'")
  print(etree.tostring(dcat, pretty_print=True, encoding='unicode'))
  for error in transform.error_log:
    print(f"{error.message} (line {error.line})", file=sys.stderr)

elif proc == 'saxon':
  with PySaxonProcessor(license=False) as saxon_proc:
    xslt_proc = saxon_proc.new_xslt30_processor()

  xslt = xslt_proc.compile_stylesheet(stylesheet_file=xsl_file)
  xslt.set_property('!indent', 'yes')

  output = xslt.transform_to_string(source_file=xml_file)
  print(output)

else:
  print("Unknown processor:", proc)
