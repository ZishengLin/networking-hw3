import config
import dummy
import gbn
import ss
#import sr
import threading
import sys

# Factory method to construct transport layer.
# return DummyTransportLayer or GoBackN or StopAndWait
def get_transport_layer(sender_or_receiver,
                        transport_layer_name,
                        msg_handler):
  assert sender_or_receiver == 'sender' or sender_or_receiver == 'receiver'
  if sender_or_receiver == 'sender':
    return _get_transport_layer_by_name(transport_layer_name,
                                        config.SENDER_IP_ADDRESS,
                                        config.SENDER_LISTEN_PORT,
                                        config.RECEIVER_IP_ADDRESS,
                                        config.RECEIVER_LISTEN_PORT,
                                        msg_handler)
  if sender_or_receiver == 'receiver':
    return _get_transport_layer_by_name(transport_layer_name,
                                        config.RECEIVER_IP_ADDRESS,
                                        config.RECEIVER_LISTEN_PORT,
                                        config.SENDER_IP_ADDRESS,
                                        config.SENDER_LISTEN_PORT,
                                        msg_handler)


def _get_transport_layer_by_name(name, local_ip, local_port, 
                                 remote_ip, remote_port, msg_handler):
  assert name == 'dummy' or name == 'ss' or name == 'gbn' or name == 'sr'
  if name == 'dummy':
    return dummy.DummyTransportLayer(local_ip, local_port,
                                     remote_ip, remote_port, msg_handler)
  if name == 'ss':
    return ss.StopAndWait(local_ip, local_port,
                          remote_ip, remote_port, msg_handler)
  if name == 'gbn':
    return gbn.GoBackN(local_ip, local_port,
                       remote_ip, remote_port, msg_handler)
  if name == 'sr':
    return sr.SelectiveRepeat(local_ip, local_port,
                        remote_ip, remote_port, msg_handler)

def my_check_sum(type, seq_num, msg):
  sum = 0
  sum += type
  sum += seq_num
  if msg:
    for b in msg: 
        # b is int
        sum += b
        sum = sum % 65536
  
  return sum
  
# num: int, msg: bytes, chksum: int
def make_pkt(type, next_seq_num, msg, chksum):
  if msg:    
    return type.to_bytes(2, byteorder='big') \
          + next_seq_num.to_bytes(2, byteorder='big') \
          + chksum.to_bytes(2, byteorder='big') \
          + msg 
  else:
    return type.to_bytes(2, byteorder='big') \
          + next_seq_num.to_bytes(2, byteorder='big') \
          + chksum.to_bytes(2, byteorder='big')

# Convenient class to run a function periodically in a separate
# thread.
class PeriodicClosure:
  def __init__(self, handler, interval_sec):
    self._handler = handler
    self._interval_sec = interval_sec
    self._lock = threading.Lock()
    self._timer = None

  def _timeout_handler(self):
    with self._lock:
      self._handler()
      self.start()

  def start(self):
    self._timer = threading.Timer(self._interval_sec, self._timeout_handler)
    self._timer.start()

  def stop(self):
    with self._lock:
      if self._timer:
        self._timer.cancel()
