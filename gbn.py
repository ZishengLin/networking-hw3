import udt
import config
import util

# Go-Back-N reliable transport protocol.
class GoBackN:
  # "msg_handler" is used to deliver messages to application layer
  # when it's ready.
  
  def __init__(self, local_ip, local_port,
               remote_ip, remote_port, msg_handler):
    self.network_layer = udt.NetworkLayer(local_ip, local_port,
                                          remote_ip, remote_port, self)
    self.msg_handler = msg_handler
    self.base = 1
    self.nextseqnum = 1
    self.expseqnum = 1
    self.timer = util.PeriodicClosure(self.timer_handler, config.TIMEOUT_MSEC / 1000)
    self.ls = []

  def timer_handler(self):
 
    if self.base == self.nextseqnum and self.base != 1:
      self.shutdown()
      return
    for i in range(self.base, self.nextseqnum):
      
      self.network_layer.send(self.ls[i - 1]) 
      # self.timer.stop()
      # self.timer.start()


  # "send" is called by application. Return true on success, false
  # otherwise.
  def send(self, msg):
    # TODO: impl protocol to send packet from application layer.
    # call self.network_layer.send() to send to network layer.

    if self.nextseqnum < self.base + config.WINDOW_SIZE:
     
      
      
      checksum = util.my_check_sum(config.MSG_TYPE_DATA, self.nextseqnum, msg)
      pkt = util.make_pkt(config.MSG_TYPE_DATA, self.nextseqnum, msg, checksum)
      self.ls.append(pkt)
      self.network_layer.send(pkt)
      
      if self.base == self.nextseqnum:
        self.timer.start()
      self.nextseqnum += 1
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
    print("base", self.base)
    if data_type == config.MSG_TYPE_ACK:
      if checksum == util.my_check_sum(data_type, seq_num, None): 
        if self.base == seq_num + 1:
          return
        self.base = seq_num + 1

        if self.base == self.nextseqnum:
          self.timer.stop()
        else:
          self.timer.stop()
          self.timer.start()
    else:
      if checksum == util.my_check_sum(data_type, seq_num, msg[6:]): 
        if seq_num == self.expseqnum:
          self.msg_handler(msg[6:])
          new_check_sum = util.my_check_sum(config.MSG_TYPE_ACK, self.expseqnum, None)

          pkt = util.make_pkt(config.MSG_TYPE_ACK, self.expseqnum, None, new_check_sum)
          self.network_layer.send(pkt)
          self.expseqnum += 1
        else:
          
          new_check_sum = util.my_check_sum(config.MSG_TYPE_ACK, self.expseqnum-1, None)
          pkt = util.make_pkt(config.MSG_TYPE_ACK, self.expseqnum-1, None, new_check_sum)
          self.network_layer.send(pkt)

  # Cleanup resources.
  def shutdown(self):
    # TODO: cleanup anything else you may have when implementing this
    # class.
    
    while True:
      if self.base == self.nextseqnum:
        break
      pass
    self.timer.stop()
    self.network_layer.shutdown()
