#!/opt/local/bin/python

import PIL
import pymorph
import numpy
import Image
import collada
import sys
import getopt

# pycollada - http://collada.in4lines.com/
# http://stackoverflow.com/questions/5793642/collada-files-viewer

def calculate_bounding_box(mesh):
  min_x = min_y = min_z = 100000000
  max_x = max_y = max_z = -100000000
  
  for geom in mesh.scene.objects('geometry'):
    for prim in geom.primitives():
      for tri in prim.triangles():
        for vertex in tri.vertices:
          # unpack the vertex
          x, y, z = vertex
          min_x = min(min_x, x)
          max_x = max(max_x, x)
          min_y = min(min_y, x)
          max_y = max(max_y, x)
          min_z = min(min_z, x)
          max_z = max(max_z, x)
  return [(min_x,max_x), (min_y, max_y), (min_z, max_z)]



def create_images(mesh):
  [(min_x,max_x), (min_y, max_y), (min_z, max_z)] = calculate_bounding_box(mesh)
  width = int(max_x - min_x)
  height = int(max_y - min_y)
  
  arrays = []
  
  # slice through the model at various z levels
  for z in range(min_z, max_z, 10):
    #start it all white
    array = numpy.ones((width,height),dtype='int8')
    for i in range(width):
      for j in range(height):
        array[i][j] = 255
  
    # xz plane
    plane = geo.Plane(geo.Point(0,1,z), geo.Point(1,0,z), geo.Point(0,0,z))
    intersecting_triangles = find_triangles_which_intersect(mesh, plane)
  
    for triangle in intersecting_triangles:
      # this is not right, but let's just try to get something working
    
      # project all 3 points down 
      for vertex in triangle.vertices:
        x, y, z = vertex[0], vertex[1], vertex[2]
      
        # ignore z component
        array[int(x + min_x)][int(y + min_y)] = 0
    
    arrays.append(array)
  
  return [Image.fromarray(array).convert("RGB") for array in arrays]
  
def save_images(image_list):
  for (i, img) in enumerate(image_list):
    file_handle = open("circle_%d.png" %i, "wb")
    img.save(file_handle)
    

#http://softsurfer.com/Archive/algorithm_0104/algorithm_0104.htm
def find_triangles_which_intersect(mesh, plane):
  intersecting_triangles = []
  
  
  # for each triangle, check whether any of the three line segments intersects the plane
  for geom in mesh.scene.objects('geometry'):
    for prim in geom.primitives():
      for tri in prim.triangles():
        p1, p2, p3 = [geo.Point(vertex) for vertex in tri.vertices]
        
        pairs = ( (p1, p2), (p1, p3), (p2, p3) )
        for pair in pairs:
          # if the plane separates the two points, then the line segment between them
          # intersects with the plane
          intersects = plane.separates(pair[0], pair[1])
          coplanar = geo.dot(pair[0].r - plane.r, plane.n) * geo.dot(pair[1].r - plane.r, plane.n) == 0
          if intersects or coplanar:
            intersecting_triangles.append(tri)
            break
  return intersecting_triangles
  
  # http://www.gamedev.net/topic/104528-triangleplane-intersection-points/
  # The idea is to test each and every edge (line) of the triangle to see if it collides with the plane. There are three lines:
  #   P0-P1
  #   P1-P2
  #   P2-P0
  # 
  #   For example, with P0-P1, any point on the line can be represented as a linear interpolation between P0-P1. Hence,
  # 
  #   P = P0 + t * (P1 - P0)
  # 
  #   If 0 < t < 1, then P is somewhere between P1 and P0. This is a vectorial equation, so there are three components. We can substitute them in the plane equation:
  # 
  #   Ax + By + Cz + D = 0
  #   A(P0.x + t * (P1.x - P0.x)) + B(P0.y + t * ... = 0
  # 
  #   Isolate t. Once you have it, you know that, if t>1 or t<0, the edge doesn''t intersect the plane. Else, you can find the intersection point by replacing t in the original equation.
  # 
  #   Hope this helps,
  # 
  pass


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