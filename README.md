# Lunar-data-fusion
Deep learning model for lunar feature recognition, data preprocessing and automated database creation for nonexclusive use with the NASA-USGS PILOT platform.

The MATLAB code is coming.

In terms of setting up the database on your own computer, make sure to add your parent file path has the origin variable in the workflow script.
The global maps must be downloaded from http://imbrium.mit.edu/EXTRAS/SLDEM2015/TILES/JP2/ before running workflow script.
Your parent file should have the following structure. Keep in ming the "N site folders" will be automatically created.

  Data workspace
    |
    |
   _________________________________________________
      |                    |                      |
      ↓                    ↓                      ↓
  Original data       Preselected Data         Split data
      |                    |
      |                    ↓
      |              N site folders (e.g. "Site 1")
      |
      |
      _____________
      |          |
      |          ↓
      |       Global maps (32 lunar sections as .JP2 files)
      |
      |
      ↓
     Sort
      |
      ↓
      Any newly downloaded site data files
      
      View file 2D structure at: <img width="780" alt="File structure" src="https://user-images.githubusercontent.com/73500228/206111168-b211438a-4a26-4cef-8178-1cd15c99b00f.png">
