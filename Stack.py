class Stack:

    def __init__(self):
        self.l = []
    
    def isEmpty(self):
        return len(self.l) == 0

    def push(self,a):
        self.l.append(a)

    def pop(self):
        if self.isEmpty():
            return None
        return self.l.pop()
        
    def top(self):
        return self.l[-1]