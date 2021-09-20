''' This constructs a thread-safe Sigcom Validator that
works in its own thread across any threads that access it.
'''
import json
from subprocess import Popen, PIPE, STDOUT
from threading import Thread, Event, Lock, get_ident
from queue import Queue, Empty
from contextlib import contextmanager

@contextmanager
def acquire_with_timeout(lock):
  assert lock.acquire(timeout=10), 'Timeout'
  yield lock
  lock.release()

class SigcomValidatorClient(Thread):
  def __init__(self):
    super().__init__()
    self._queue = Queue()
    self._data = {}
    self._data_lock = Lock()
    self._join = False
  #
  def run(self):
    with Popen(
      [
        'npx', '@dcic/signature-commons-schema',
        '/dcic/signature-commons-schema/v6/core/meta.json'
      ],
      bufsize=1,
      universal_newlines=True,
      stdin=PIPE,
      stderr=STDOUT,
      stdout=PIPE,
    ) as proc:
      # when _join is set, we'll exit the loop when the queue is empty
      while not self._join:
        # if nothing new is added to the queue in a second, we'll check if
        #  join was called
        try:
          item = self._queue.get(timeout=1)
          if item is None:
            self._queue.task_done()
            break
          # process an item on the queue
          proc.stdin.write(json.dumps(item)+'\n')
          ret = json.loads(proc.stdout.readline())
          # update data and trigger event
          with acquire_with_timeout(self._data_lock):
            evt = self._data[item['persistent_id']]
            self._data[item['persistent_id']] = ret
            evt.set()
          # move on
          self._queue.task_done()
        except Empty:
          pass
  #
  def join(self, timeout=None):
    self._join = True
    self._queue.put(None)
    super().join(timeout=timeout)
  #
  def fetch(self, item):
    with acquire_with_timeout(self._data_lock):
      if item['id'] in self._data:
        value = self._data[item['id']]
        if not isinstance(value, Event):
          return value
      else:
        value = self._data[item['id']] = Event()
        self._queue.put(item)
    #
    value.wait(timeout=10)
    return self.fetch(item)

class SigcomValidatorMultiClient:
  ''' Create a SigcomValidatorClient for each thread
  '''
  def __init__(self):
    self.clients = {}
  #
  def join(self):
    while self.clients:
      _, client = self.clients.popitem()
      client.join()
  #
  def fetch(self, item):
    thread_id = get_ident()
    if thread_id not in self.clients:
      self.clients[thread_id] = SigcomValidatorClient()
      self.clients[thread_id].start()
    return self.clients[thread_id].fetch(item)

@contextmanager
def create_sigcom_validator_client():
  sigcom_validator_client = SigcomValidatorMultiClient()
  yield sigcom_validator_client
  sigcom_validator_client.join()
