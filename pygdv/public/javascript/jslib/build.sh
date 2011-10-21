#/bin/sh

# Remember dir
OLDDIR=$PWD
DOJO_VERSION='1.6.1'
#DOJO_VERSION='1.4.2'

# Get source distribution (only once)

wget http://download.dojotoolkit.org/release-$DOJO_VERSION/dojo-release-$DOJO_VERSION-src.zip
unzip dojo-release-$DOJO_VERSION-src.zip
rm dojo-release-$DOJO_VERSION-src.zip


# Build
cd dojo-release-$DOJO_VERSION-src/util/buildscripts/ 
#java -classpath ../shrinksafe/custom_rhino.jar org.mozilla.javascript.tools.shell.Main build.js action=release,clean profileFile=../../../profile.js version=$DOJO_VERSION releaseDir=../../../builds
#(this line is for 1.4.2)
java -classpath ../shrinksafe/js.jar:../shrinksafe/shrinksafe.jar org.mozilla.javascript.tools.shell.Main build.js action=release,clean profileFile=../../../profile.js version=$DOJO_VERSION releaseDir=../../../created
# Compare
diff ../../../buildsdojo/dojo/jbrowse_dojo.js.uncompressed.js ../../../dojo/jbrowse_dojo.js.uncompressed.js

# Back
cd $OLDDIR
