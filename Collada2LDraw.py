#!/opt/local/bin/python

import PIL
import pymorph
import numpy

import collada
import sys
import getopt

def parse_model(path_to_model):
  """ Attempt to load the given collada model  """
  mesh = collada.Collada(path_to_model)
  
  print mesh


def calculate_slice(image, width=1, fill=False):
  """
  image is a numpy binary array where element i is
  
  
  uses a greedy blobbing algorithm to assign the
  biggest pieces possible
  """
  piece_sizes = [
    # most common brick
    (4,2)
    (3,2)
    (2,2)
    
    (4,1)
    (3,1)
    (2,1)
    (1,1)
  ]
  
  



def main(argv):
  """
  
  TODO: replace getopt with argparse (http://docs.python.org/library/argparse.html#module-argparse)
  """
  try:                                
    opts, args = getopt.getopt(argv, "hm:", ["help", "model="]) 
  except getopt.GetoptError:
    usage()
    sys.exit(2)
  
  model = None
  for opt, arg in opts:                
    if opt in ("-h", "--help"):      
      usage()
      sys.exit()
    elif opt in ("-m", "--model"): 
      model = arg
  
  if model == None:
    print "Must include the path to a .dae model"
    usage()
    sys.exit()
  else:
    parse_model(model)
  
def usage():
  print "./Collada2LDraw --model=/path/to.dae"
  print "usage"
  

if __name__ == '__main__':
  main(sys.argv[1:])