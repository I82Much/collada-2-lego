#!/opt/local/bin/python

import PIL
import pymorph
import numpy

import collada
import sys
import getopt




def calculate_bounding_box(collada):
  min_x, min_y, min_z, max_x, max_y, max_z = [0] * 6
  
  for geom in collada.scene.objects('geometry'):
    for prim in geom.primitives():
      for tri in prim.triangles():
        vertices = tri.vertices
        for vertex in vertices:
          # unpack the vertex
          x, y, z = vertex
          min_x = min(min_x, x)
          max_x = max(max_x, x)
          min_y = min(min_y, x)
          max_y = max(max_y, x)
          min_z = min(min_z, x)
          max_z = max(max_z, x)  

  return [(min_x,max_x), (min_y, max_y), (min_z, max_z)]




def parse_model(path_to_model):
  """ Attempt to load the given collada model  """
  mesh = collada.Collada(path_to_model)
  return mesh
  
  # for geom in mesh.scene.objects('geometry'):
  #     for prim in geom.primitives():
  #       for tri in prim.triangles():
  #         print tri.vertices
  #   
  #   print mesh


def calculate_slice(image, width=1, fill=False):
  """
  image is a numpy binary array where element i is
  
  
  uses a greedy blobbing algorithm to assign the
  biggest pieces possible
  """
  pass

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