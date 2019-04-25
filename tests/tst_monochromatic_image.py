from __future__ import division, print_function
import os
from LS49.sim import step5_pad
from LS49.sim import step4_pad
from LS49.spectra import generate_spectra

ls49_big_data = os.environ["LS49_BIG_DATA"] # get absolute path from environment
step5_pad.big_data = ls49_big_data
step4_pad.big_data = ls49_big_data
generate_spectra.big_data = ls49_big_data

def run_monochromatic():
  from LS49.sim.step5_pad import tst_all
  tst_all(quick=True)

def compare_two_images(reference, test, tolerance_count=10):
  print ("Comparing",reference,test)
  from dxtbx.format.Registry import Registry
  beam=[]
  data = []
  detector =[]
  headers = []
  for i,fk in enumerate([reference,test]):
    format_instance = Registry.find(fk)
    instance = format_instance(fk)
    beam.append( instance.get_beam() )
    detector.append( instance.get_detector() )
    data.append( instance.get_raw_data() )
    if True: #optional test
      print (beam[-1])
      print (instance.get_goniometer())
      print (detector[-1])
      print (instance.get_scan())
    headers.append( instance.get_smv_header(fk) )

  if  headers[0]==headers[1]:
    print ("Both headers identical")
  else:
    #print headers[0]
    #print headers[1]
    for key in headers[0][1]:
      if key not in headers[1][1]:  print ("second data lacks key",key)
      elif headers[0][1][key] != headers[1][1][key]:
        print ("Key comparison:",key,headers[0][1][key], headers[1][1][key])

  assert len(data[1])==len(data[0])
  diff_data = data[1]-data[0]
  no_differences=True
  ndiff = 0
  for idiff,diff in enumerate(diff_data):
    if diff!=0:
      if ndiff < 200: print ("difference index %d:(%d,%d)"%(idiff,idiff//3000,idiff%3000),diff) # only print the first 200 differences
      ndiff += 1
      no_differences=False
  print("There are %d differences"%ndiff)
  #assert no_differences
  assert ndiff < tolerance_count, "There are %d differences"%ndiff

def compare_two_raw_images(reference, test):
  from six.moves import cPickle as pickle
  import numpy as np
  with open(reference,'rb') as F:
    reference_array = pickle.load(F)
  with open(test,'rb') as F:
    test_array = pickle.load(F)
  print("\nComparing raw image: '%s' with the reference: '%s'"%(test, reference))
  if (test_array == reference_array).all():
        print ("There are 0 differences\n")
  else:
    diff_array = test_array - reference_array
    print("\nThere are differences ranging from %.2E to %.2E"%(np.amin(diff_array), np.amax(diff_array)))
    print("Mean difference: %.2E; standard deviation: %.2E\n"%(np.mean(diff_array), np.std(diff_array)))

if __name__=="__main__":
  run_monochromatic()
  compare_two_images(reference=os.path.join(ls49_big_data,"reference","step5_000000.img.gz"), test="./step5_000000.img.gz")
  # test the raw photons due to Bragg scatter:
  compare_two_images(reference=os.path.join(ls49_big_data,"reference","step5_000000_intimage_001.img"), test="./step5_000000_intimage_001.img")
  # add in the effects of water scatter:
  compare_two_images(reference=os.path.join(ls49_big_data,"reference","step5_000000_intimage_002.img"), test="./step5_000000_intimage_002.img")
  # add in the effects of air scatter:
  compare_two_images(reference=os.path.join(ls49_big_data,"reference","step5_000000_intimage_003.img"), test="./step5_000000_intimage_003.img")
  print("OK")
