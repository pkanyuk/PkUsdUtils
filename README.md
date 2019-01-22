# PkUsdUtils
Miscellaneous USD related utilities.  These are scripts I've put together for the benefit 
of the OpenSource USD community and not related to my professional work.

# usdSkelAppleFixup.py -- I hope to retire this as unnecessary soon.
#
This fixes what is likely a temporary situation where Apple's UsdSkel spec requires
an animationSource and skeleton relationship on every skinned mesh, but the official UsdSkel
schema requires an animationSource relationship on the skeleton, and skeleton relationships can
be inherited.  This inconsistency will likely be fixed soon, but it doesn't hurt to have 
redundant relationships for now. So, this script simply finds all the animationSource relationships 
on skeletons and copies them over to the corresponding skinned meshes.  Meshes also get a redundant
skeleton relationhip defined.  If exporting a UsdSkel asset from Maya or another DCC/process, 
you can run this script afterwards for this temp fix.

HUGE CAVEAT: At this time, iOS doesn't accept USDZ files with more than one skinned mesh.  maOS
should accept these files just fine though.

python usdSkelAppleFixup.py INPUT OUTPUT