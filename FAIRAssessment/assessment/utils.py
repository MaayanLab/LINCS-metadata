def filter_empty(val):
  ''' Attempt to catch some actual null values that aren't null
  '''
  return [
    v
    for v in val
    if v is not None and (
      type(v) != str or v.strip().lower() not in {
        '-',
        '-666',
        '',
        'empty',
        'n/a',
        'na',
        'nan',
        'nil',
        'none',
        'not defined',
        'null',
        'undef',
        'undefined',
      }
    )
  ]

def one_and_only(it):
  it = iter(it)
  one = next(it)
  try:
    next(it)
  except StopIteration:
    return one
  else:
    raise Exception('More than one, expected one and only')

def url_join(*args):
  return '/'.join(arg.rstrip('/') for arg in args)

def try_json_loads(s):
  import json
  try:
    return json.loads(s)
  except:
    return None

def fetch_cache(url, filename, cachedir='.cached'):
  import os, urllib.request
  os.makedirs(cachedir, exist_ok=True)
  if not os.path.exists(os.path.join(cachedir, filename)):
    urllib.request.urlretrieve(url, filename=os.path.join(cachedir, filename))
  return os.path.join(cachedir, filename)
