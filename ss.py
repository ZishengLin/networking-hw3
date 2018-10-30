import udt
import util
import config

# Stop-And-Wait reliable transport protocol.
class StopAndWait:
  # "msg_handler" is used to deliver messages to application layer
  # when it's ready.
  def __init__(self, local_ip, local_port, 
               remote_ip, remote_port, msg_handler):
    self.network_layer = udt.NetworkLayer(local_ip, local_port,
                                          remote_ip, remote_port, self)
    self.msg_handler = msg_handler
    self.timer = util.PeriodicClosure(self.timer_handler, 1)
    self.nextseqnum = 0
    self.buffer = b''
    self.recv_buffer = b''
    self.expseqnum = 0
    self.can_sent = True
    self.can_end = False

  def timer_handler(self):
    if self.can_end:
      self.shutdown()
      return
    print("time out")
    self.network_layer.send(self.buffer)
    # self.timer.stop()
    # self.timer.start()

  # "send" is called by application. Return true on success, false
  # otherwise.
  def send(self, msg):
    # TODO: impl protocol to send packet from application layer.
    # call self.network_layer.send() to send to network layer.
    if self.can_sent:
      checksum = util.my_check_sum(config.MSG_TYPE_DATA, self.nextseqnum, msg)
      pkt = util.make_pkt(config.MSG_TYPE_DATA, self.nextseqnum, msg, checksum)
      self.buffer = pkt
      self.network_layer.send(pkt)
      self.nextseqnum = 1 - self.nextseqnum
      self.timer.start()
      self.can_sent = False
      self.can_end = False
      return True
    else:
      return False

  # "handler" to be called by network layer when packet is ready.
  def handle_arrival_msg(self):
    msg = self.network_layer.recv()
    # TODO: impl protocol to handle arrived packet from network layer.
    # call self.msg_handler() to deliver to application layer.
    data_type = int.from_bytes(msg[0:2], byteorder='big')
    seq_num = int.from_bytes(msg[2:4], byteorder='big')
    checksum = int.from_bytes(msg[4:6], byteorder='big')
    # data_type = struct.unpack('!h', msg[0:2])[0]
    # seq_num = struct.unpack('!h', msg[2:4])[0]
    # checksum = struct.unpack('!h', msg[4:6])[0]
    print("seq_num ", data_type)
    if data_type == config.MSG_TYPE_ACK:
      if checksum == util.my_check_sum(data_type, seq_num, None):
        if not self.can_sent and seq_num == 1 - self.nextseqnum:
          
          self.can_sent = True
          self.can_end = True
          self.timer.stop()
    else:
      if checksum == util.my_check_sum(data_type, seq_num, msg[6:]): 
        if seq_num == self.expseqnum:
          
          self.msg_handler(msg[6:])
          new_check_sum = util.my_check_sum(config.MSG_TYPE_ACK, self.expseqnum, None)
          pkt = util.make_pkt(config.MSG_TYPE_ACK, self.expseqnum, None, new_check_sum)
          self.recv_buffer = pkt
          self.network_layer.send(pkt)
          self.expseqnum = 1 - self.expseqnum
        else:
          self.network_layer.send(self.recv_buffer)
        




  # Cleanup resources.
  def shutdown(self):
    # TODO: cleanup anything else you may have when implementing this
    # class.
    while not self.can_end:
      pass
    self.timer.stop()
    self.network_layer.shutdown()
