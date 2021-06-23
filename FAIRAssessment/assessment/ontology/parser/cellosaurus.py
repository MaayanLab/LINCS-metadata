import xml.etree.ElementTree as ET
from .ontology import Ontology

class CellosaurusOntology(Ontology):
  @classmethod
  def parse(cls, source):
    root = ET.parse(source).getroot()
    return cls({
      accession.text.replace('_', ':'): {
        'id': accession.text.replace('_', ':'),
        'name': cell_line.find('name-list').find("name[@type='identifier']").text,
        'synonyms': {
          synonym.text
          for synonym in cell_line.find('name-list').iterfind("name[@type='synonym']")
        }
      }
      for cell_line in root.find('cell-line-list').iterfind('cell-line')
      for accession in cell_line.find('accession-list').iterfind('accession')
    })
