import random

# EXAMPLE STATE MACHINE
class MantisBrain:

  def __init__(self, body):
    self.body = body
    self.state = 'idle'
    self.target = None

  def handle_event(self, message, details):

    if self.state is 'idle':

      if message == 'timer':
        # go to a random point, wake up sometime in the next 10 seconds
        world = self.body.world
        x, y = random.random()*world.width, random.random()*world.height
        self.body.go_to((x,y))
        self.body.set_alarm(random.random()*10)

      elif message == 'collide' and details['what'] == 'Slug':
        # a slug bumped into us; get curious
        self.state = 'curious'
        self.body.set_alarm(1) # think about this for a sec
        self.body.stop()
        self.target = details['who']

    elif self.state == 'curious':

      if message == 'timer':
        # chase down what slug who bumped into us
        if self.target:
          if random.random() < 0.5:
            self.body.stop()
            self.state = 'idle'
          else:
            self.body.follow(self.target)
          self.body.set_alarm(1)
      elif message == 'collide' and details['what'] == 'Slug':
        # we meet again!
        slug = details['who']
        slug.amount -= 0.01 # take a tiny little bite
    
class SlugBrain:

  def __init__(self, body):
    self.body = body
    self.state = 'idle'
    self.prev_state = None
    self.target = None
    self.has_resource = False

  def handle_event(self, message, details):
    # TODO: IMPLEMENT THIS METHOD
    #  (Use helper methods and classes to keep your code organized where
    #  approprioate.)
    if self.state == 'idle':
        self.target = None
        self.body.stop()

    if message is 'order':
        if type(details) is type('z'):
            target_string = ''
            if details is 'i':
                self.state = 'idle'
                self.target = None
                self.body.stop()
            elif details is 'a':
                self.state = 'attack'
                target_string = 'Mantis'
            elif details is 'b':
                self.state = 'build'
                target_string = 'Nest'
            elif details is 'h':
                self.state = 'harvest'
                if self.has_resource:
                    target_string = 'Nest'
                else:
                    target_string = 'Resource'
            if target_string is not "":
                try:
                    self.target = self.body.find_nearest(target_string)
                    self.body.follow(self.target)
                    self.body.set_alarm(0.5)
                except ValueError:
                    self.state = 'idle'
                    self.body.set_alarm(0.5)
        else:
            self.state = 'move'
            self.body.go_to(details)

    elif message is 'timer':
        target_string = ""
        if self.state is 'attack':
            target_string = "Mantis"
        if self.state is 'build' or self.state is 'flee':
            target_string = "Nest"
        if self.state is 'harvest':
            if self.has_resource:
                target_string = "Nest"
            else:
                target_string = "Resource"
        if target_string is not "":
            try:
                self.target = self.body.find_nearest(target_string)
                self.body.follow(self.target)
                self.body.set_alarm(0.5)
            except ValueError:
                self.state = 'idle'
                self.body.set_alarm(0.5)

    elif message is 'collide':
        if self.state is 'attack' and details['what'] == 'Mantis':
            health = details['who']
            health.amount -= 0.04
        if self.state is 'build' and details['what'] == 'Nest':
            nest = details['who']
            nest.amount += 0.008
        if self.state is 'harvest':
            target_string = ''
            if self.has_resource and details['what'] == 'Nest':
                self.has_resource = False
                target_string = 'Resource'
            elif not self.has_resource and details['what'] == 'Resource':
                self.has_resource = True
                source = details['who']
                source.amount -= 0.2
                target_string = 'Nest'
        if self.state is 'flee' and details['what'] == 'Nest':
            self.body.amount = 1
            self.body.speed = 90
            self.state = self.prev_state
            self.prev_state = None

    if self.body.amount < 0.5:
        print("FUCK IM GETTING KILLED")
        self.state = 'flee'
        self.target = self.body.find_nearest("Nest")
        self.body.go_to(self.target)


world_specification = {
  'worldgen_seed': 12, # comment-out to randomize
  'nests': 2,
  'obstacles': 25,
  'resources': 5,
  'slugs': 5,
  'mantises': 4,
}

brain_classes = {
  'mantis': MantisBrain,
  'slug': SlugBrain,
}