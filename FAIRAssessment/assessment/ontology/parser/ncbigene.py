import pandas as pd
from .ontology import Ontology

class NCBIGeneOntology(Ontology):
  @classmethod
  def parse(cls, source='ftp://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/Mammalia/Homo_sapiens.gene_info.gz'):
    def maybe_split(record):
      if record in {'', '-'} or pd.isna(record):
        return set()
      return set(record.split('|'))
    ncbi = pd.read_csv(source, sep='\t')
    return cls({
      f"ncbigene:{gene_info['GeneID']}": {
        'id': f"ncbigene:{gene_info['GeneID']}",
        'name': gene_info['Symbol'],
        'synonyms': set.union(
          maybe_split(gene_info['Synonyms']),
          maybe_split(gene_info['Symbol_from_nomenclature_authority']),
          maybe_split(gene_info['Other_designations']),
          maybe_split(gene_info['dbXrefs']),
        ),
      }
      for _, gene_info in ncbi.iterrows()
    })
