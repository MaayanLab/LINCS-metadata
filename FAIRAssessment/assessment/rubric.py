''' Here we define and codify the aspects of the FAIR assessment and mechanism by which
they will be evaluated.
'''

#%%
import requests
import urllib.parse
from ontology.parser.obo import OBOOntology
from ontology.parser.cellosaurus import CellosaurusOntology
from ontology.parser.ncbigene import NCBIGeneOntology
from utils import fetch_cache

metrics = {}
rubric = {
  '@id': 107,
  'name': 'NIH Common Fund Data Ecosystem: LINCS (CFDE-LINCS) FAIR Rubric',
  'description': 'This rubric identifies aspects of the metadata models which promote interoperable dataset querying and filtering',
  'metrics': metrics,
}

def url_join(*args):
  return '/'.join(arg.rstrip('/') for arg in args)

def _register_metric(schema):
  global metrics
  def wrapper(func):
    metrics[schema['@id']] = dict(schema, func=func)
  setattr(wrapper, '__name__', schema['name'])
  return wrapper

#%%
@_register_metric({
  # standardized metadata format (107), machine readable metadata (106)
  # metadata license (117) (c2m2 ?)
  '@id': 106,
  'name': 'Metadata conformance',
  'description': 'The metadata properly conforms with the metadata model specification',
  'principle': 'Findable',
})
def _(signature, sigcom_validator_client=None, **kwargs):
  if '$validator' in signature['meta']:
    if signature['meta']['$validator'] == '/dcic/signature-commons-schema/v5/core/unknown.json':
      yield { 'value': 0.0, 'comment': 'No schema specified' }
    else:
      result = sigcom_validator_client.fetch(dict(signature, library=signature['library']['@id']))
      if '$validator' in result:
        yield { 'value': 1.0, 'comment': 'Instance validates against its own validator' }
      else:
        yield { 'value': 0.0, 'comment': 'Validation failed with result: {}'.format(result) }

#%%
# Program name: LINCS

#%%
# Project name: LINCS

#%%
# PI Contact: Avi

#%%
@_register_metric({
  '@id': 138,
  'name': 'Responsible institution',
  'description': 'The institution that created this dataset is available',
  'principle': 'Findable',
})
def _(signature, **kwargs):
  if signature['library']['meta'].get('center'):
    yield { 'value': 1, 'comment': 'Center name is present in metadata' }
  else:
    yield { 'value': 0, 'comment': 'Center name is not present in metadata' }

#%%
@_register_metric({
  # Access protocol (110)
  '@id': 110,
  'name': 'Access protocol',
  'description': 'The protocol for accessing the data is available and described with a URI',
  'principle': 'Accessible',
})
def _(signature, **kwargs):
  # NOTE: this is convoluted, we will consider best coverage as 0.75
  #       because of the inconsistent access paradigm.
  import itertools as it
  candidates = it.chain(
    (
      ('#/meta/persistent_id', signature['meta'].get('persistent_id'),),
      ('#/meta/file_url', signature['meta'].get('file_url')),
    ),
    (
      (f'#/library/meta/{k}', v['file_url'])
      for k, v in signature['library']['meta'].items()
      if type(v) == dict and 'file_url' in v
    ),
  )
  is_any = False
  for ptr, candidate in candidates:
    if candidate is None: continue
    is_any = True
    access_scheme = urllib.parse.urlparse(candidate).scheme
    if access_scheme:
      yield {
        'value': 0.75,
        'comment': 'Access protocol ({}) is encoded in uri'.format(access_scheme),
        'url_comment': ptr,
      }
    else:
      yield {
        'value': 0.5,
        'comment': 'Link found but could not identify uri format',
        'url_comment': ptr,
      }
  if not is_any:
    yield {
      'value': 0.0,
      'comment': 'A way to access the data was not identified'
    }

#%%
OBI = OBOOntology.parse(
  fetch_cache(
    'https://raw.githubusercontent.com/obi-ontology/obi/master/views/obi.obo', 'OBI.obo'
  )
)

@_register_metric({
  '@id': 139,
  'name': 'Assay',
  'description': 'Assay is present and a proper CFDE-specified ontological term is found in the CFDE-specified ontologies.',
  'principle': 'Interoperable',
})
def _(signature, **kwargs):
  # NOTE: this is convoluted, we will consider best coverage as 0.75
  #       because of the inconsistent access paradigm.
  assay = signature['library']['meta'].get(
    'assay_type',
    signature['library']['meta'].get(
      'assay_name',
      signature['library']['meta'].get('assay')
    )
  )
  if not assay:
    yield {
      'value': 0.0,
      'comment': 'No assay_type found associated with the file',
    }
  elif OBI.get(assay) is not None:
    yield {
      'value': 0.75,
      'comment': 'Ontological IRI for Assay found in OBI.',
      'url_comment': assay,
    }
  else:
    assay_id = OBI.reversed_synonyms().get(assay)
    if assay_id:
      yield {
        'value': 0.5,
        'comment': 'Ontological IRI not found, but assay found in OBI ({}).'.format(assay_id),
        'url_comment': assay,
      }
    else:
      yield {
        'value': 0.25,
        'comment': 'Assay found but not verified in OBI.',
        'url_comment': assay,
      }

#%%
UBERON = OBOOntology.parse(fetch_cache('http://purl.obolibrary.org/obo/uberon.obo', 'uberon.obo'))

@_register_metric({
  '@id': 140,
  'name': 'Anatomical Part',
  'description': 'An anatomical part is present and the CFDE-specified ontological term is found in the CFDE-specified ontologies',
  'principle': 'Interoperable',
})
def _(signature, **kwargs):
  anatomy = signature['meta'].get(
    'anatomy',
  )
  if not anatomy:
    if signature['meta'].get('cellline', signature['meta'].get('cell_line')):
      yield {
        'value': 0.25,
        'comment': 'No anatomy found, but cell line is present thus it should be resolvable',
      }
    else:
      yield {
        'value': 0.0,
        'comment': 'No anatomy found associated with the file',
      }
  elif UBERON.get(str(anatomy)) is not None:
    yield {
      'value': 1.0,
      'comment': 'Ontological IRI for anatomy found in UBERON.',
      'url_comment': anatomy,
    }
  else:
    anatomy_id = UBERON.reversed_synonyms().get(str(anatomy))
    if anatomy_id:
      yield {
        'value': 0.75,
        'comment': 'Ontological IRI not found, but anatomy found in UBERON ({}).'.format(anatomy_id),
        'url_comment': anatomy,
      }
    else:
      yield {
        'value': 0.5,
        'comment': 'Anatomy found but not verified in UBERON.',
        'url_comment': anatomy,
      }

#%%
MONDO = OBOOntology.parse(fetch_cache('http://purl.obolibrary.org/obo/mondo.obo', 'mondo.obo'))

@_register_metric({
  '@id': 141,
  'name': 'Disease',
  'description': 'A disease is present and the CFDE-specified ontological term is found in the CFDE-specified ontologies',
  'principle': 'Interoperable',
})
def _(signature, **kwargs):
  if signature['meta'].get('cellline', signature['meta'].get('cell_line')):
    yield {
      'value': 0.25,
      'comment': 'No disease found, but cell line is present thus it might be resolvable',
    }
  else:
    yield {
      'value': 0.0,
      'comment': 'No disease found associated with the file',
    }

#%%
EDAM = OBOOntology.parse(fetch_cache('http://edamontology.org/EDAM.obo', 'EDAM.obo'))

@_register_metric({
  '@id': 142,
  'name': 'File type',
  'description': 'A file type is present and the CFDE-specified ontological term is found in the CFDE-specified ontologies',
  'principle': 'Interoperable',
})
def _(signature, **kwargs):
  file_format = signature['library']['meta'].get('file_format')
  if not file_format:
    yield {
      'value': 0.0,
      'comment': 'No standardized file format found associated with the file',
    }
  elif EDAM.get(str(file_format)) is not None:
    yield {
      'value': 0.75,
      'comment': 'Ontological IRI for file format found in EDAM.',
      'url_comment': str(file_format),
    }
  else:
    file_format_id = EDAM.reversed_synonyms().get(str(file_format))
    if file_format_id:
      yield {
        'value': 0.5,
        'comment': 'Ontological IRI not found, but file format found in EDAM ({}).'.format(file_format_id),
        'url_comment': str(file_format),
      }
    else:
      yield {
        'value': 0.25,
        'comment': 'File format found but not verified in EDAM.',
        'url_comment': str(file_format),
      }

#%%
# NCBITaxon = OBOOntology.parse(fetch_cache('http://purl.obolibrary.org/obo/ncbitaxon.obo', 'ncbitaxon.obo'))

@_register_metric({
  '@id': 143,
  'name': 'Taxonomy',
  'description': 'A taxonomy is present and the CFDE-specified ontological term is found in the CFDE-specified ontologies',
  'principle': 'Interoperable',
})
def _(signature, ncbi_taxon_client=None, **kwargs):
  taxon = signature['library']['meta'].get('taxonomy_id')
  if taxon:
    taxon_resolved = ncbi_taxon_client.fetch(str(taxon))
    if taxon_resolved is not None:
      yield {
        'value': 1,
        'comment': 'Taxonomy is present and validated in ncbi',
        'url_comment': str(taxon),
      }
    else:
      yield {
        'value': 0.5,
        'comment': 'Taxonomy is present but not NCBI',
        'url_comment': str(taxon),
      }
  else:
    yield {
      'value': 0.0,
      'comment': 'Taxonomy is not present',
    }

#%%
Cellosaurus = CellosaurusOntology.parse(fetch_cache('ftp://ftp.expasy.org/databases/cellosaurus/cellosaurus.xml', 'cellosaurus.xml'))

@_register_metric({
  '@id': 144,
  'name': 'Cell Line',
  'description': 'A cell line is present and the CFDE-specified ontological term is found in the CFDE-specified ontologies',
  'principle': 'Interoperable',
})
def _(signature, **kwargs):
  # NOTE: this is convoluted, we will consider best coverage as 0.75
  #       because of the inconsistent access paradigm.
  cell_line = signature['meta'].get('cellline', signature['meta'].get('cell_line'))
  if not cell_line:
    yield {
      'value': 0.0,
      'comment': 'No cell_line found associated with the signature',
    }
  elif Cellosaurus.get(str(cell_line)) is not None:
    yield {
      'value': 0.75,
      'comment': 'Ontological IRI for cell_line found in Cellosaurus.',
      'url_comment': str(cell_line),
    }
  else:
    cell_line_id = Cellosaurus.reversed_synonyms().get(str(cell_line))
    if cell_line_id:
      yield {
        'value': 0.5,
        'comment': 'Ontological IRI not found, but cell line found in Cellosaurus ({}).'.format(cell_line_id),
        'url_comment': str(cell_line),
      }
    else:
      yield {
        'value': 0.25,
        'comment': 'Cell line found but not verified in Cellosaurus.',
        'url_comment': str(cell_line),
      }

#%%
@_register_metric({
  # License (116)
  '@id': 116,
  'name': 'Data Usage License',
  'description': 'A Data usage license is described',
  'principle': 'Reusable',
})
def _(signature, **kwargs):
  yield {
    'value': 0,
    'comment': 'No information about data usage licenses are described'
  }

#%%
@_register_metric({
  # Persistent identifier (105)
  '@id': 104,
  'name': 'Persistent identifier',
  'description': 'Globally unique, persistent, and valid identifiers (preferrably DOIs) are present for the dataset',
  'principle': 'Findable',
})
def _(signature, **kwargs):
  yield {
    'value': 0,
    'comment': 'No persistent_id defined'
  }

#%%
@_register_metric({
  # Resource identifier (108)
  '@id': 108,
  'name': 'Resource identifier',
  'description': 'An identifier for the resource is present',
  'principle': 'Findable',
})
def _(signature, **kwargs):
  # This is guaranteed by sigcom
  yield {
    'value': 1,
    'comment': 'A resource id is present',
    'url_comment': signature['id'],
  }

#%%
@_register_metric({
  '@id': 145,
  'name': 'Landing Page',
  'description': 'A landing page exists and is accessible for the identifiers',
  'principle': 'Findable',
})
def _(signature, **kwargs):
  landing_page = f"https://ldp3.cloud/#/Signatures/{signature['id']}"
  meta_landing_page = f"https://ldp3.cloud/metadata-api/signatures/{signature['id']}"
  try:
    status_code = requests.get(meta_landing_page, headers={'User-Agent': None}).status_code
    if status_code >= 200 and status_code < 300:
      yield {
        'value': 1,
        'comment': 'valid and GET reports {}'.format(status_code),
        'url_comment': landing_page,
      }
    elif status_code >= 300 and status_code < 399:
      yield {
        'value': 0.5,
        'comment': 'valid url but GET reported {}, status cannot be determined'.format(status_code),
        'url_comment': landing_page,
      }
    elif status_code >= 400:
      yield {
        'value': 0.25,
        'comment': 'valid url but GET reported {}'.format(status_code),
        'url_comment': landing_page,
      }
  except requests.exceptions.MissingSchema:
    yield {
      'value': 0.25,
      'comment': 'does not seem to be a valid url'.format(landing_page),
      'url_comment': landing_page,
    }

#%%
NCBIGenes = NCBIGeneOntology()

@_register_metric({
  '@id': 311,
  'name': 'Gene ID',
  'description': 'An applicable gene id is present and the term is found in the NCBI',
  'principle': 'Interoperable',
})
def _(signature, **kwargs):
  # NOTE: this is convoluted, we will consider best coverage as 0.75
  #       because of the inconsistent access paradigm.
  targets = signature['meta'].get('clueIoGeneTargets', '')
  targets = [] if targets.lower() in {'','na'} else [f"ncbigene:{gene}" for gene in targets.split('|')]
  for ncbigene in targets:
    if NCBIGenes.get(ncbigene) is not None:
      yield {
        'value': 0.75,
        'comment': 'Ontological IRI for ncbigene found in NCBIGenes.',
        'url_comment': ncbigene,
      }
    else:
      cell_line_id = NCBIGenes.reversed_synonyms().get(ncbigene)
      if cell_line_id:
        yield {
          'value': 0.5,
          'comment': 'Ontological IRI not found, but cell line found in NCBIGenes ({}).'.format(cell_line_id),
          'url_comment': ncbigene,
        }
      else:
        yield {
          'value': 0.25,
          'comment': 'ncbigene found but not verified in NCBIGenes.',
          'url_comment': ncbigene,
        }

#%%
@_register_metric({
  '@id': 310,
  'name': 'Drug term',
  'description': 'An applicable drug term is uniquely resolvable in pubchem',
  'principle': 'Interoperable',
})
def _(signature, pubchem_client=None, **kwargs):
  # NOTE: this is convoluted, we will consider best coverage as 0.75
  #       because of the inconsistent access paradigm.
  # TODO: can we just check the pubchemid if present??
  # drug = signature['meta'].get('pubChemID',
  #   signature['meta'].get('perturbagenID')
  # )
  drug = signature['meta'].get('treatment')
  if drug:
    drug_resolved = pubchem_client.fetch(str(drug))
    if drug_resolved is not None:
      yield {
        'value': 1,
        'comment': 'Drug term is present and validated in pubchem',
        'url_comment': drug_resolved,
      }
    else:
      yield {
        'value': 0.5,
        'comment': 'Drug term is present but not pubchem verifiable',
        'url_comment': drug_resolved,
      }
