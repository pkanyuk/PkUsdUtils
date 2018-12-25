import sys, os
import argparse


progName = os.path.basename(sys.argv[0])

descr = """
$prog: This fixes what is likely a temporary situation where Apple's UsdSkel spec requires
an animationSource relationship on every skinned mesh, but the official UsdSkel
schema requires an animationSource relationship on the skeleton.  This inconsistency
will likely be fixed soon, but it doesn't hurt to have redundant relationships for now.
So, this script simply finds all the animationSource relationships on skeletons and
copies them over to the corresponding skinned meshes.  If exporting a UsdSkel asset
from Maya or another DCC/process, you can run this script afterwards for this temp fix.
"""

parser = argparse.ArgumentParser(usage=progName+" <in> <out>",description=descr.replace("$prog", progName))
parser.add_argument('inusd', help='input usd')
parser.add_argument('outusd', help='output usd')
args = parser.parse_args()


#------------------------------------------------------------------------------#

# Traverses up to the root for a given prim looking for the closest
# skel binding.  Note the skinningQuery is the better API but this is
# temporary until we get a python GetPrim() binding.
def FindSkelBindingRel(stage,prim):
    while(prim != stage.GetPseudoRoot() and prim != None):
        for rel in prim.GetRelationships():
            if rel.GetName() == "skel:skeleton":
                return(rel)
            else:
                prim = prim.GetParent()
        
def main():
    print("UsdSkelAppleFixup Begin.")
    
    # Create a new out usd file that sublayers the in usd file.  All edits
    # will go to the out usd file.  Start and end time is copied over.
    inFile = args.inusd
    outFile = args.outusd 
    
    from pxr import Usd, UsdGeom, UsdSkel, Sdf

    dstLyr = Sdf.Layer.CreateNew(outFile)
    srcLyr = Sdf.Layer.FindOrOpen(inFile)
    stage = Usd.Stage.Open(dstLyr)
    stage.SetEditTarget(dstLyr)
    
    layerStack = dstLyr.subLayerPaths
    layerStack.insert(len(layerStack),inFile)    
    
    start = int(srcLyr.startTimeCode)
    end = int(srcLyr.endTimeCode)
    stage.SetStartTimeCode(start)
    stage.SetEndTimeCode(end)
    
    # Find all the skinned meshes and copy over the animation source to them
    
    # The the skel, anim, and mesh prims.
    skelPrims = [prim for prim in Usd.PrimRange(stage.GetPseudoRoot()) if prim.IsA(UsdSkel.Skeleton)]
    meshPrims = [prim for prim in Usd.PrimRange(stage.GetPseudoRoot()) if prim.IsA(UsdGeom.Mesh)]
    
    for skelPrim in skelPrims:
    
        skelCache = UsdSkel.Cache()
        skel = UsdSkel.Skeleton(skelPrim)
        skelQuery = skelCache.GetSkelQuery(skel)
        skelAnimQuery = skelQuery.GetAnimQuery()
        skelAnim = UsdSkel.Animation(skelAnimQuery.GetPrim())
        for mesh in meshPrims:
            rel = FindSkelBindingRel(stage,mesh)
            if rel:
                for target in rel.GetTargets():
                    if target == skelPrim.GetPath():
                        print("Copying the animationSource relationship to "+mesh.GetName()) 
                        # wire up the skel anim for temporary compatbility with Apple's expectations
                        mesh.CreateRelationship(UsdSkel.Tokens.skelAnimationSource).AddTarget(skelAnim.GetPrim().GetPath())                            
                       
    dstLyr.Save()                       

#------------------------------------------------------------------------------#

if __name__ == "__main__":
    main()

