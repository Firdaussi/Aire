# Aire
Aire Logic

The program artistapi.py allows the user to query statistics about one or more musical artists. The statistics available are as follows:

  Mean
  Variance*
  Standard deviation*
  Minimum word length*
  Maximum word length*
  Median*
  Number of unique tracks*
  Number of words*
  Total number of characters*
  
* indicates optional statistics accessed by the command line 
  
In addition, an optional graph showing the relationship between the count and length of lyric words can be displayed.

Usage:
  python artistapi.py [--all] [--plot] Artist1 Artist2 ...
  
  where --all displays all statistics as listed above
  and   --plot displays the count/length graph
  
Requirements:
  See requirements.txt
  This is a python 3.9 module

Execution examples:
  To obtain the mean lyric word length of all tracks by "The Doors":
    python3 artistapi.py "The Doors"
    
  To obtain extended statistics of all tracks by "Genesis" and plot a chart or count/length
    python3 artistapi.py --all --plot "Genesis"
  
  As above but also for two further groups
    python3 artistapi.py --all --plot "Genesis" "The Beatles" "The Rolling Stones"
    
 Output:
   In addition to the statistical data, a notification is displayed for songs whose lyrics cannot be found.
  
  
