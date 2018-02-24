"""
This is the Learner class
"""

class Learner(object):
     def __init__(self, quorum, log = None):
         self.log = log
         self.count = {}
         self.maxCount = 0
         self.valForMaxCount = None
         self.quorum = quorum
         

     def countVote(self, msg):
         if msg['val'] not in self.count:
             self.count[msg['val']] = 1
         else:
             self.count[msg['val']] += 1

         if self.maxCount < self.count[msg['val']]:
            self.valForMaxCount = msg['val']
            self.maxCount = self.count[msg['val']]

     def checkQuorumSatisfied(self):
         if self.maxCount >= self.quorum:
            return True
         else:
            return False

     def commit(self):
         print("commit the value: %s"%(str(self.valForMaxCount)))

     def writeToLog(self, val, slot):
         self.log[slot] = val



