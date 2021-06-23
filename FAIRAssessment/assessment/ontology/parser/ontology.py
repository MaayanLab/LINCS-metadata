''' pronto has proven very inconsistent for our needs,
so here's our own ontology parsers.

All parsers construct a dictionary of the form:

{
  'ONTOID:id': {
    id: 'ONTOID:id',
    synonyms: [synonym1, synonym2, ...],
    ... # ontology specific
  },
  ...
}
'''

class Ontology(dict):
  def reversed(self):
    __reversed = getattr(self, '__reversed', None)
    if __reversed is None:
      __reversed = {
        node['name']: node_id
        for node_id, node in self.items()
        if 'name' in node
      }
      setattr(self, '__reversed', __reversed)
    return __reversed

  def reversed_synonyms(self):
    __reversed_synonyms = getattr(self, '__reversed_synonyms', None)
    if __reversed_synonyms is None:
      __reversed_synonyms = {
        name: node_id
        for node_id, node in self.items()
        if 'name' in node
        for name in (node['name'], *node['synonyms'])
      }
      setattr(self, '__reversed_synonyms', __reversed_synonyms)
    return __reversed_synonyms
