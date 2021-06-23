#!/usr/bin/env python3
''' The entrypoint of the assessment--collects all
documents and submits the document to be assessed by
each metric in the rubric.
'''

import sys
import click
from utils import try_json_loads
from ontology.client.ncbi_taxon import create_ncbi_taxon_client
from ontology.client.pubchem import create_pubchem_client
from ontology.client.sigcom_validator import create_sigcom_validator_client

def assess(signature, rubric, **kwargs):
  ''' A singular assessment of a file against a rubric.
  '''
  assessment = {
    '@type': 'Assessment',
    'target': signature,
    'rubric': rubric['@id'],
    'answers': []
  }
  # print(assessment)
  for metric in rubric['metrics'].values():
    # print('Checking {}...'.format(metric['name']))
    for answer in metric['func'](signature, **kwargs):
      # print(' => {}'.format(answer))
      assessment['answers'].append({
        'metric': { '@id': metric['@id'] },
        'answer': answer,
      })
  return assessment

def assess_all(signatures, output_file, max_workers=10):
  ''' A batch assessment of many files from a CFDE DerivaCompat client (online/offline/both).
  '''
  import os, os.path
  import json
  import time
  import concurrent.futures
  from rubric import rubric
  #
  if os.path.dirname(output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
  #
  if os.path.exists(output_file):
    # collect already assessed ids
    assessed = set(
      assessment['id']
      for assessment in map(try_json_loads, open(output_file, 'r'))
      if assessment is not None and assessment.get('id')
    )
  else:
    assessed = set()
  #
  with create_ncbi_taxon_client() as ncbi_taxon_client:
    with create_pubchem_client() as pubchem_client:
      with create_sigcom_validator_client() as sigcom_validator_client:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
          future_signature = {}
          future_signature.update({
            executor.submit(assess,
              signature, rubric,
              ncbi_taxon_client=ncbi_taxon_client,
              pubchem_client=pubchem_client,
              sigcom_validator_client=sigcom_validator_client,
            ): signature
            for signature in signatures
            if signature['id'] not in assessed
          })
          start = time.time()
          start_assessed = len(assessed)
          n_assessed = len(assessed)
          n_to_assess = len(future_signature) + len(assessed)
          with open(output_file, 'a') as fw:
            print('\rProgress {} / {}'.format(n_assessed, n_to_assess), end='')
            for future in concurrent.futures.as_completed(future_signature):
              signature = future_signature[future]
              try:
                assessment = future.result()
              except KeyboardInterrupt:
                break
              except Exception:
                import traceback; traceback.print_exc(file=sys.stderr)
                import ipdb; ipdb.post_mortem(sys.exc_info()[2])
              else:
                print(json.dumps(dict(assessment, id=signature['id'])), file=fw)
                n_assessed += 1
                ETA = ((time.time() - start) / (n_assessed - start_assessed)) * (n_to_assess - n_assessed)
                print('\rProgress {} / {} (ETA {:.3f}m)'.format(n_assessed, n_to_assess, ETA/60), end='')

@click.command(help='If offline/online packages are specified, will default to datapackages in this repository (../../../*/c2m2/output/datapackage.json)')
@click.option('-s', '--signature-file',
  type=click.File('r'),
  help='File containing signatures to assess, one per line (jsonl format)')
@click.option('-l', '--library-file',
  type=click.File('r'),
  help='File containing libraries, one per line (jsonl format)')
@click.option('-o', '--output-file',
  type=click.Path(),
  default='output.jsonl',
  help='Where to write the output using the .jsonl format')
@click.option('--max-workers',
  type=int,
  default=10,
  help='The maximum number of parallel assessments to perform at a time')
def cli(library_file, signature_file, output_file, max_workers):
  ''' Initialize the CFDE clients and assess all files accessible to those clients.
  '''
  libraries = {
    signature['id']: signature
    for signature in map(try_json_loads, library_file)
  }
  signatures = (
    dict(signature, library=libraries[signature['library']])
    for signature in map(try_json_loads, signature_file)
  )
  assess_all(
    signatures,
    output_file,
    max_workers=max_workers,
  )

if __name__ == '__main__':
  cli()
